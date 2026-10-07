"""Run with Blender --background --python scripts/render_pms.py -- [options]."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import tomllib

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from textual_graphics.blender_adapter import import_document, material


def aim(obj, target):
    forward = (Vector(target) - obj.location).normalized()
    right = forward.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(forward)
    obj.rotation_euler = Matrix((right, up, -forward)).transposed().to_euler()


def text_on_camera(name, text, x, y, size, camera, collection, color="#26364A"):
    data = bpy.data.curves.new(name, "FONT")
    data.body = text
    data.size = size
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = camera
    obj.location = (x, y, -3)
    # Emission keeps typography independent of studio illumination.
    mat = material(name + ".material", color)
    shader = mat.node_tree.nodes.new("ShaderNodeEmission")
    shader.inputs["Color"].default_value = mat.diffuse_color
    mat.node_tree.links.new(shader.outputs[0],
                            mat.node_tree.nodes.get("Material Output").inputs["Surface"])
    obj.data.materials.append(mat)
    return obj


def presentation(imported):
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("Presentation")
    scene.collection.children.link(collection)
    camera_data = bpy.data.cameras.new("Overview")
    camera = bpy.data.objects.new("Overview", camera_data)
    collection.objects.link(camera)
    camera.location = (1.6, 1.7, 5.2)
    aim(camera, (.84, .05, 0))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.9
    scene.camera = camera

    # Neutral photographic backdrop; not part of the engineering model.
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.13))
    backdrop = bpy.context.object
    backdrop.name = "Presentation.backdrop"
    for owner in list(backdrop.users_collection):
        owner.objects.unlink(backdrop)
    collection.objects.link(backdrop)
    backdrop.data.materials.append(material("Backdrop", "#E9EEF3"))

    for name, location, power, size in [
        ("Key", (-1, 2, 4), 450, 4),
        ("Fill", (3, -2, 3), 220, 3),
    ]:
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy = power
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        collection.objects.link(light)
        light.location = location
        aim(light, (.8, 0, 0))

    # Small dots expose marker coincidence; they are presentation helpers.
    for name in ["ground.pin", "pendulum.first_link.outer", "pendulum.second_link.outer"]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.025)
        dot = bpy.context.object
        dot.name = "Presentation.marker." + name
        for owner in list(dot.users_collection):
            owner.objects.unlink(dot)
        collection.objects.link(dot)
        dot.parent = imported.frames[name]
        dot.location = (0, 0, .045)
        dot["source_marker"] = name
        dot.data.materials.append(material(dot.name + ".material", "#26364A"))
        for polygon in dot.data.polygons:
            polygon.use_smooth = True

    text_on_camera("Title", "One model. Two tools.", -1.24, .68, .105, camera, collection)
    text_on_camera("Subtitle", "PMS Python model  /  Blender presentation", -1.23, .55, .042,
                   camera, collection, "#556579")
    text_on_camera("First label", "FIRST LINK", -.98, -.36, .045, camera, collection, "steelblue")
    text_on_camera("First detail", "1.00 m   /   pendulum.first_link", -.98, -.44, .033,
                   camera, collection)
    text_on_camera("Second label", "SECOND LINK", .32, -.36, .045, camera, collection, "#B75B00")
    text_on_camera("Second detail", "0.80 m   /   pendulum.second_link", .32, -.44, .033,
                   camera, collection)
    text_on_camera("Footer", "Authored initial pose  |  metres  |  no simulation run", -1.23, -.70,
                   .032, camera, collection, "#556579")

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.8, .85, .95, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .35
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 950
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    bpy.context.view_layer.update()
    # Open the saved file directly in the composed camera view.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"


def verify_example(imported):
    expected = {
        "ground.pin": (0, 0, 0),
        "pendulum.first_link": (.5, 0, 0),
        "pendulum.first_link.inner": (0, 0, 0),
        "pendulum.first_link.outer": (1, 0, 0),
        "pendulum.second_link": (1.4, 0, 0),
        "pendulum.second_link.inner": (1, 0, 0),
        "pendulum.second_link.outer": (1.8, 0, 0),
    }
    for name, position in expected.items():
        actual = imported.frames[name].matrix_world.translation
        if (actual - Vector(position)).length > 1e-6:
            raise AssertionError(f"Incorrect world position for {name}: {actual}")
    for name, length in [("first_link", 1), ("second_link", .8)]:
        graphic = imported.graphics[f"pendulum.{name}.graphics"][0]
        if (graphic.dimensions - Vector((length, .08, .08))).length > 1e-6:
            raise AssertionError(f"Incorrect dimensions for {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pms-root", type=Path, default=Path(os.environ.get(
        "PRACTICAL_MECHANICAL_SIMULATION_ROOT", str(ROOT.parent / "PracticalMechanicalSimulation"))))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    pms_root = args.pms_root.resolve()
    source = pms_root / "examples/spatial/python_api_double_pendulum.py"
    sys.path.insert(0, str(pms_root / "python/src"))
    from practical_mechanical_simulation import Sim3D
    namespace = runpy.run_path(str(source))
    model = namespace["build_model"]()
    document = Sim3D.document(model)

    # This command owns its Blender process; start a new scene deterministically.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    imported = import_document(document)
    verify_example(imported)
    presentation(imported)

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "double-pendulum.model.json").write_text(json.dumps(document, indent=2) + "\n")
    canonical = json.dumps(document, sort_keys=True).encode()
    report = {
        "source_example": str(source),
        "pms_version": tomllib.loads((pms_root / "Project.toml").read_text())["version"],
        "blender_version": bpy.app.version_string,
        "model_sha256": hashlib.sha256(canonical).hexdigest(),
        "pose": "authored initial pose, no solver correction or simulation",
        "checks": "body positions, box dimensions, and coincident joint markers passed",
        "frames": {name: {"world_position": list(obj.matrix_world.translation),
                           "parent": obj.parent.get("pms_name") if obj.parent else None}
                   for name, obj in imported.frames.items()},
        "graphics": list(imported.graphics),
        "mechanics_not_rendered": imported.skipped_elements,
    }
    (output / "double-pendulum.report.json").write_text(json.dumps(report, indent=2) + "\n")
    bpy.context.scene.render.filepath = str(output / "double-pendulum.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "double-pendulum.blend"))
    bpy.ops.render.render(write_still=True)
    print("TEXTUALGRAPHICS_OK " + str(output))


if __name__ == "__main__":
    main()
