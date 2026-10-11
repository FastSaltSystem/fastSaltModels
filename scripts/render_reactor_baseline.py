"""Refresh selected views from the preserved reactor scene without rebuilding it.

Run with Blender --background --python this_file -- --views cutaway air-section.
The preserved .blend is only read; outputs go to a separate working directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from build_reactor import select_view

CAMERAS={
    'cutaway':'View.ReactorCutaway',
    'section':'View.ReactorSection',
    'plan':'View.ReactorPlan',
    'air-section':'View.AirCircuit',
    'air-system':'View.AirCollectors',
    'core-removal':'View.CoreRemoval',
    'cap-service':'View.CapService',
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--views',nargs='+',choices=CAMERAS,default=['cutaway','air-section','core-removal'])
    parser.add_argument('--draft',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/workshop-reactor')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    folder=ROOT/'baselines/wistr-reactor-handling-2026-10-08'
    source=folder/'wistr-reactor-study.blend'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==json.loads((folder/'manifest.json').read_text())['files'][source.name]['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source))
    b=SceneBuilder()
    b.collections={c.name:c for c in bpy.context.scene.collection.children}
    b.assemblies={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY' and 'assembly_id' in o}
    cameras={key:bpy.data.objects[value] for key,value in CAMERAS.items()}
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU'
    scene.cycles.samples=16 if args.draft else 48
    scene.cycles.use_denoising=True
    scene.render.resolution_percentage=50 if args.draft else 100
    args.output.mkdir(parents=True,exist_ok=True)
    records={}
    for view in args.views:
        select_view(b,cameras,[],view)
        target=args.output/f'reactor-{view}{"-draft" if args.draft else ""}.png'
        scene.render.filepath=str(target)
        bpy.ops.render.render(write_still=True)
        records[view]={'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (args.output/'render-manifest.json').write_text(json.dumps({
        'source':str(source.relative_to(ROOT)),'source_sha256':digest,
        'render_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'view_setup_sha256':hashlib.sha256((ROOT/'scripts/build_reactor.py').read_bytes()).hexdigest(),
        'draft':args.draft,'images':records},indent=2)+'\n')
    print('BASELINE_VIEWS_OK',list(records))

if __name__=='__main__':
    main()
