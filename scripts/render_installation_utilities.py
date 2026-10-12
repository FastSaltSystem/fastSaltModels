"""Render isolated utility details without changing the saved installation scene."""
from pathlib import Path
from types import SimpleNamespace
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from build_wistr import camera
from render_pms import text_on_camera
out=ROOT/'outputs/installation-under-cover-bundles'
for view in ('coolant-transfer','nitrogen'):
    bpy.ops.wm.open_mainfile(filepath=str(out/'wistr-installation.blend'))
    scene=bpy.context.scene;scene['section_cutaway']=False;scene.update_tag()
    keep={'Presentation','Structure','Utility piping'}|({'Coolant storage','Coolant transfer'} if view=='coolant-transfer' else {'Nitrogen supply'})
    for c in bpy.data.collections:c.hide_render=c.name not in keep;c.hide_viewport=False
    for ob in bpy.data.objects:
        if ob.name.startswith('connections.nitrogen.'):ob.hide_render=view!='nitrogen'
        if ob.name.startswith('connections.coolant_transfer.') and ob.type=='MESH':ob.hide_render=view!='coolant-transfer'
        if ob.get('utility_opening_tool') or ob.get('utility_route'):ob.hide_render=True
    collection=bpy.data.collections.new('Utility detail');scene.collection.children.link(collection)
    class Builder:
        def collection(self,name):return collection
    b=Builder()
    if view=='coolant-transfer':
        # Actual vessel bottom plate and penetrations retained as location context.
        ob=bpy.data.objects['reactor.vessel.bottom_plate'];copy=ob.copy();copy.data=ob.data.copy()
        transform=ob.matrix_world.copy();copy.parent=None;copy.matrix_world=transform;collection.objects.link(copy)
        copy.hide_render=False;copy.hide_viewport=False
        cam=camera(b,'View.CoolantTransfer',(-8,-26,8),(7,-3,-4.5),29)
        title='WISTR | Coolant transfer and insulated storage'
        note='50 mm OD heated line / pump / bottom entry / 350 mm tank insulation'
        footer='Reactor bottom plate isolated for routing inspection; surrounding equipment hidden'
        x,y,size=-12.8,9.5,.44
    else:
        cam=camera(b,'View.Nitrogen',(37,-32,4),(24,-16,-5.0),18)
        title='WISTR | Nitrogen supply concept'
        note='Liquid nitrogen tank > ambient vaporizer > regulated gas header'
        footer='Provisional envelopes; capacity, pressure and consumer branches remain to size'
        x,y,size=-8,5.8,.32
    text_on_camera('Utility.Title',title,x,y,size,cam,collection)
    text_on_camera('Utility.Note',note,x,y-.65,size*.55,cam,collection,'#4C5C68')
    text_on_camera('Utility.Footer',footer,x,-y,size*.48,cam,collection,'#4C5C68')
    scene.camera=cam;scene.cycles.samples=16
    scene.render.resolution_x=2400;scene.render.resolution_y=1800;scene.render.resolution_percentage=50
    scene.render.filepath=str(out/f'wistr-{view}-draft.png')
    bpy.ops.render.render(write_still=True)
print('UTILITY_DETAILS_OK')
