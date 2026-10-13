"""Plain-Python checks for hierarchical authoring and interchange."""
from copy import deepcopy
import math
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models')]
from textual_graphics.assembly_model import Model,document,write,read,distance,point
from coolant_assembly import build_model,reactor_interface
import wistr_installation as layout

class AssemblyTests(unittest.TestCase):
    def test_nested_rotated_port(self):
        m=Model('test');m.component('root',position=(10,0,0),rotation_deg=(0,0,90));m.component('child',parent='root',position=(2,0,0),rotation_deg=(0,90,0));m.port('child','tip',(0,0,1))
        d=document(m)
        self.assertLess(distance(d['ports']['child.tip']['world_position_m'],[10,3,0]),1e-10)

    def test_detached_copy(self):
        m=Model('test');m.component('a',parameters={'values':[1,2]});d=document(m);d['components']['a']['parameters']['values'][0]=99
        self.assertEqual(document(m)['components']['a']['parameters']['values'],[1,2])

    def test_geometric_mating(self):
        m=Model('test');m.component('a',position=(4,5,6));m.port('a','target',(0,0,0));m.component('frame',rotation_deg=(0,0,90));m.component('b',parent='frame',rotation_deg=(0,90,0));m.port('b','tip',(0,0,2))
        m.place_port_at('b','tip','a.target');d=document(m)
        self.assertLess(distance(d['ports']['b.tip']['world_position_m'],[4,5,6]),1e-10)

    def test_duplicate_and_missing_reference(self):
        m=Model('test');m.component('a')
        with self.assertRaises(ValueError):m.component('a')
        with self.assertRaises(ValueError):m.component('b',parent='missing')
        with self.assertRaises(ValueError):m.connect('bad','missing','missing',frame='a')

    def test_cycle_rejected(self):
        m=Model('test');m.component('a');m.component('b',parent='a');m.components['a']['parent']='b'
        with self.assertRaisesRegex(ValueError,'Cyclic'):document(m)

    def test_real_model_toml_round_trip_and_flow(self):
        m=build_model(layout,reactor_interface(layout,ROOT));d=document(m)
        self.assertEqual(len(d['connections']),9)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read(write(m,Path(tmp)/'resolved.toml')),d)
        for i in range(1,4):
            cold=d['connections'][f'leg_{i}.cold_inlet']
            self.assertEqual(cold['flow_from'],f'leg_{i}.pump.discharge')
            self.assertTrue(cold['flow_to'].startswith('reactor.cold_inlet'))
            suction=d['connections'][f'leg_{i}.cold_suction']['world_points_m']
            self.assertGreater(suction[-1][2],suction[-2][2])
            self.assertAlmostEqual(suction[-1][0],suction[-2][0])
            self.assertAlmostEqual(suction[-1][1],suction[-2][1])

    def test_reposition_component_reconnects_endpoint(self):
        m=build_model(layout,reactor_interface(layout,ROOT));before=document(m)
        m.components['leg_1.generator']['position_m'][0]+=1
        after=document(m);name='leg_1.hot_outlet'
        self.assertGreater(distance(before['connections'][name]['world_points_m'][-1],after['connections'][name]['world_points_m'][-1]),.99)
        self.assertLess(distance(after['connections'][name]['world_points_m'][-1],after['ports']['leg_1.generator.salt_inlet']['world_position_m']),1e-10)

    def test_tampered_toml_route_rejected(self):
        from textual_graphics.assembly_model import dumps
        d=document(build_model(layout,reactor_interface(layout,ROOT)));d['connections']['leg_1.hot_outlet']['world_points_m'][0][0]+=1
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.toml';p.write_text(dumps(d))
            with self.assertRaisesRegex(ValueError,'Inconsistent route'):read(p)

if __name__=='__main__':unittest.main()
