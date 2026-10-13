"""Blender integration: direct document and TOML paths build identical equipment."""
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.assembly_model import document,write,read
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.coolant_scene import build_coolant
from coolant_assembly import build_model,reactor_interface
from build_wistr import palette,steam_generator
import wistr_installation as layout

def build(doc):
    bpy.ops.wm.read_factory_settings(use_empty=True);b=SceneBuilder();palette(b)
    integration=reactor_interface(layout,ROOT);build_coolant(b,doc,integration)
    for i,angle in enumerate(layout.STEAM_GENERATORS['angles'],1):steam_generator(b,i,angle,doc)
    bpy.context.view_layer.update()
    meshes={o.name:{'matrix':[list(row) for row in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]} for o in bpy.context.scene.objects if o.type=='MESH'}
    return b,integration,meshes

class BlenderTests(unittest.TestCase):
    def test_round_trip_meshes_and_ports(self):
        doc=document(build_model(layout,reactor_interface(layout,ROOT)))
        with tempfile.TemporaryDirectory() as tmp:
            parsed=read(write(doc,Path(tmp)/'model.toml'))
            _,_,direct=build(doc);b,integration,via_file=build(parsed)
            self.assertEqual(direct,via_file)
        for name,c in parsed['connections'].items():
            obj=bpy.data.objects[parsed['components'][c['frame']]['blender_name']+'.'+c['blender_name']]
            pts=obj.data.splines[0].points
            for actual,expected in [(pts[0],c['world_points_m'][0]),(pts[-1],c['world_points_m'][-1])]:
                self.assertLess(((obj.matrix_world @ Vector(actual.co[:3]))-Vector(expected)).length,1e-5)
            self.assertEqual(obj['pid_line'],c['pid_line'])
        self.assertEqual(len(integration['pumps']),3)
        self.assertEqual(len(integration['routes']),6)
        # Verify physical collector mouths against the semantic generator ports.
        for i in range(1,4):
            for suffix,kind,key in [('salt_inlet','hot','port_minus_local'),('salt_outlet','cold','port_plus_local')]:
                obj=bpy.data.objects[f'equipment.steam_generator_{i}.{kind}_manifold']
                actual=obj.matrix_world @ Vector(obj[key]);expected=Vector(parsed['ports'][f'leg_{i}.generator.{suffix}']['world_position_m'])
                self.assertLess((actual-expected).length,1e-5)
        out=ROOT/'outputs/coolant-assembly';out.mkdir(parents=True,exist_ok=True)
        write(parsed,out/'coolant.resolved.toml')
        bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
        bpy.context.scene['scope']='Coolant equipment assembly only; detailed reactor is represented by connection ports in the resolved document'
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'coolant-equipment.blend'))
        (out/'assembly-check.json').write_text(json.dumps({'components':len(doc['components']),'routes':len(doc['connections']),'meshes':len(via_file),'direct_vs_TOML':'identical meshes','port_tolerance_m':1e-5},indent=2)+'\n')

suite=unittest.defaultTestLoader.loadTestsFromTestCase(BlenderTests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise RuntimeError('Coolant assembly Blender checks failed')
