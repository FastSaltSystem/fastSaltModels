"""Cross-view checks: shared edits, identity stability and provenance failures."""
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
ROOT=Path(__file__).resolve().parents[1]
HUB=ROOT.parent/'fastSalt'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models')]
from textual_graphics.shared_coolant import coolant
from textual_graphics.assembly_model import document,read
from coolant_assembly import build_model,reactor_interface
import wistr_installation as layout
spec=importlib.util.spec_from_file_location('pid_build_shared_test',HUB/'design/pids/coolant-system/build.py')
pid=importlib.util.module_from_spec(spec);spec.loader.exec_module(pid)

class SharedTests(unittest.TestCase):
    def test_one_source_edit_reaches_both_views(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub=Path(tmp)/'hub';eng=hub/'design/engineering'
            shutil.copytree(HUB/'design/engineering',eng)
            for source in layout.ENGINEERING['sources'].values():
                target=hub/source['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(HUB/source['path'],target)
            view=hub/'design/pids/coolant-system/coolant-system.toml'
            view.parent.mkdir(parents=True);shutil.copyfile(pid.ROOT/'coolant-system.toml',view)
            source=eng/'coolant-system.toml';text=source.read_text()
            self.assertIn('value = 0.025',text)
            source.write_text(text.replace('value = 0.025','value = 0.03'))
            model=pid.load(view);pid.validate(model,pid.load(pid.ROOT/'layout.toml'))
            self.assertEqual(model['lines']['L-101']['od_mm'],1485)
            self.assertEqual(model['lines']['L-201']['wall_mm'],30)
            output=Path(tmp)/'graphics.toml'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/resolve_coolant.py'),'--output',str(output),'--pid-model',str(view)],
                                  env={**os.environ,'FAST_SALT_HUB':str(hub)},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            graphics=read(output)
            for route in graphics['connections'].values():
                self.assertAlmostEqual(route['spec']['bare_od'],1.485)
                self.assertEqual(route['spec']['wall'],.03)
            self.assertEqual(graphics['metadata']['shared_engineering']['model_sha256'],model['shared_provenance']['model_sha256'])

    def test_adopted_duty_matches_checked_results_and_both_views(self):
        import json
        results=json.loads((HUB/'calculations/steam-generator/coolant-pump-itemized-results.json').read_text())['hurmet_checks']
        pressure=json.loads((HUB/'calculations/reactor/coolant-pressure-results.json').read_text())['hurmet_checks']
        view=pid.load(pid.ROOT/'coolant-system.toml')
        doc=document(build_model(layout,reactor_interface(layout,ROOT)))
        for i in (1,2,3):
            actual=doc['components'][f'leg_{i}.pump']['duty']
            record=view['equipment'][f'P-{100+i}']
            for field,key,scale in [('flow_m3_s','PumpVolumeFlow',1),('pressure_rise_pa','PumpRise',1000),
                                    ('hydraulic_kw','HydraulicPerPump',1),('shaft_kw','ShaftPerPump',1),
                                    ('electrical_kw','ElectricalPerPump',1)]:
                self.assertAlmostEqual(actual[field],results[key]*scale)
                self.assertEqual(actual[field],record[field])
            self.assertEqual(actual['motor_rating_kw'],2000)
            self.assertAlmostEqual(record['suction_pressure_bar_g'],pressure['BaseSuction'])
            self.assertAlmostEqual(record['discharge_pressure_bar_g'],pressure['BaseDischarge'])
        self.assertEqual(view['equipment']['R-101']['core_height_m'],3.4)
        self.assertEqual(view['equipment']['R-101']['mass_flow_kg_s'],18500)
        self.assertEqual(view['lines']['L-101']['temperature_C'],616.85)

    def test_full_loop_loss_change_reaches_both_views(self):
        from types import SimpleNamespace
        changed=deepcopy(layout.ENGINEERING)
        changed['cases']['normal']['pump_pressure_rise']['value']*=1.1
        other=SimpleNamespace(**{k:getattr(layout,k) for k in dir(layout) if k.isupper()})
        other.ENGINEERING=changed
        before=document(build_model(layout,reactor_interface(layout,ROOT)))
        after=document(build_model(other,reactor_interface(other,ROOT)))
        view=coolant.pid_projection(changed)
        for i in (1,2,3):
            a=after['components'][f'leg_{i}.pump']['duty'];b=before['components'][f'leg_{i}.pump']['duty']
            self.assertAlmostEqual(a['electrical_kw'],1.1*b['electrical_kw'])
            self.assertEqual(a['electrical_kw'],view['equipment'][f'P-{100+i}']['electrical_kw'])
        self.assertEqual(before['connections'],after['connections'])
        changed['cases']['normal']['total_mass_flow']['value']=19000
        with self.assertRaisesRegex(ValueError,'three leg flows'):coolant.validate(changed)

    def test_reordered_tables_keep_physical_assignment(self):
        from types import SimpleNamespace
        changed=deepcopy(layout.ENGINEERING)
        changed['connections']=dict(reversed(list(changed['connections'].items())))
        other=SimpleNamespace(**{k:getattr(layout,k) for k in dir(layout) if k.isupper()})
        other.ENGINEERING=changed
        before=document(build_model(layout,reactor_interface(layout,ROOT)))
        after=document(build_model(other,reactor_interface(other,ROOT)))
        self.assertEqual(before,after)

    def test_shared_override_rejected(self):
        view=tomllib.loads((pid.ROOT/'coolant-system.toml').read_text())
        view['lines']['L-101']['wall_mm']=99
        with self.assertRaisesRegex(ValueError,'override'):
            coolant.merge_pid(view,layout.ENGINEERING)

    def test_units_and_missing_ports_rejected(self):
        model=deepcopy(layout.ENGINEERING);model['specifications']['hot']['wall']['unit']='mm'
        with self.assertRaisesRegex(ValueError,'Expected unit m'):coolant.validate(model)
        model=deepcopy(layout.ENGINEERING);model['connections']['L-101']['to']='SG-101.missing'
        with self.assertRaisesRegex(ValueError,'endpoint'):coolant.validate(model)

    def test_unhandled_topology_rejected(self):
        model=deepcopy(layout.ENGINEERING);model['connections']['L-201']['via']=[]
        with self.assertRaisesRegex(ValueError,'unsupported'):coolant.graphics_legs(model)

    def test_changed_worksheet_is_not_silently_adopted(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub=Path(tmp);dest=hub/'design/engineering/coolant-system.toml'
            dest.parent.mkdir(parents=True);shutil.copyfile(coolant.DEFAULT_MODEL,dest)
            for source in layout.ENGINEERING['sources'].values():
                p=hub/source['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HUB/source['path'],p)
            p=hub/layout.ENGINEERING['sources']['pump']['path'];p.write_text(p.read_text()+'\nChanged worksheet\n')
            with self.assertRaisesRegex(ValueError,'worksheet changed'):coolant.read(dest)

if __name__=='__main__':unittest.main()
