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
