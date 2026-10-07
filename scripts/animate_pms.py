"""Blender comparison: basic and detailed geometry driven by one PMS result."""

import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from textual_graphics.blender_adapter import import_document, material, _box
from textual_graphics.detail_assets import detailed_link
from textual_graphics.playback import Motion, bake_motion
from render_pms import aim, text_on_camera


def panel(imported, name, x):
    root = bpy.data.objects.new(name, None)
    imported.collection.objects.link(root)
    root.location = (x, 0, 0)
    for frame in imported.frames.values():
        if frame.parent is None:
            frame.parent = root
    for objects in imported.graphics.values():
        for obj in objects:
            if obj.get("pms_owner") == "ground.pin":
                obj.hide_render = True
                obj.hide_set(True)
    support = _box(name + ".support", (.45, .16, .11), imported.frames["ground"],
                   imported.collection, "#708296", 1)
    support.location = (0, .16, -.06)
    return root


def setup_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    collection = bpy.data.collections.new("Presentation")
    scene.collection.children.link(collection)
    data = bpy.data.cameras.new("Comparison camera")
    camera = bpy.data.objects.new("Comparison camera", data)
    collection.objects.link(camera)
    camera.location = (0, 1.0, 12)
    aim(camera, (0, -.65, 0))
    data.type, data.ortho_scale = "ORTHO", 9.4
    scene.camera = camera
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.23))
    backdrop = bpy.context.object
    backdrop.name = "Presentation.backdrop"
    for owner in list(backdrop.users_collection):
        owner.objects.unlink(backdrop)
    collection.objects.link(backdrop)
    backdrop.data.materials.append(material("Backdrop", "#E9EEF3"))
    for name, location, energy, size in [("Key", (-3, 3, 6), 1100, 6),
                                          ("Fill", (4, -2, 5), 700, 5)]:
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy, light_data.shape, light_data.size = energy, "DISK", size
        light = bpy.data.objects.new(name, light_data)
        collection.objects.link(light)
        light.location = location
        aim(light, (0, -.7, 0))
    scene.world = bpy.data.worlds.new("Studio world")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.8, .85, .95, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .4
    text_on_camera("Title", "Same motion. More detail.", -4.18, 2.22, .28, camera, collection)
    text_on_camera("Subtitle", "One PMS simulation drives both views", -4.16, 1.85, .13,
                   camera, collection, "#556579")
    text_on_camera("Basic heading", "ORIGINAL GEOMETRY", -4.12, 1.30, .13,
                   camera, collection, "#556579")
    text_on_camera("Detail heading", "ATTACHED VISUAL ASSEMBLIES", .30, 1.30, .13,
                   camera, collection, "#556579")
    text_on_camera("Footer", "Blue: first link    Orange: second link    |    4 seconds of simulated motion",
                   -4.16, -2.05, .115, camera, collection, "#556579")
    text_on_camera("Footer2", "Added visual detail does not change the mechanical model.",
                   -4.16, -2.30, .115, camera, collection, "#556579")
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.render.resolution_x, scene.render.resolution_y = 1200, 720
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"


def verify(basic, detailed, roots, assets, motion, frames, fps):
    scene = bpy.context.scene
    max_pose_error = max_geometry_error = max_joint_gap = 0.0
    for frame in range(1, frames + 1):
        scene.frame_set(frame)
        time = motion.times[0] + (frame - 1) / fps
        for name in motion.tracks:
            position, rotation = motion.pose(name, time)
            expected = Matrix.LocRotScale(position, rotation, Vector((1, 1, 1)))
            for imported, root in zip((basic, detailed), roots):
                actual = root.matrix_world.inverted() @ imported.frames[name].matrix_world
                max_pose_error = max(max_pose_error, max(abs(actual[i][j] - expected[i][j])
                                                         for i in range(4) for j in range(4)))
            # Compare the original box's basis to each detailed object's basis
            # after removing its fixed local shape placement and panel offset.
            original = roots[0].matrix_world.inverted() @ basic.graphics[name + ".graphics"][0].matrix_world
            for obj in assets[name]:
                recovered = (roots[1].matrix_world.inverted() @ obj.matrix_world
                             @ obj.matrix_basis.inverted())
                max_geometry_error = max(max_geometry_error,
                    max(abs(original[i][j] - recovered[i][j]) for i in range(4) for j in range(4)))
        for a, b in [("ground.pin", "pendulum.first_link.inner"),
                     ("pendulum.first_link.outer", "pendulum.second_link.inner")]:
            gap = (detailed.frames[a].matrix_world.translation -
                   detailed.frames[b].matrix_world.translation).length
            max_joint_gap = max(max_joint_gap, gap)
    if max_pose_error > 2e-5 or max_geometry_error > 2e-5 or max_joint_gap > 2e-3:
        raise AssertionError(f"Motion mismatch: {max_pose_error}, {max_geometry_error}, {max_joint_gap}")
    return {"frames_checked": frames, "fps": fps,
            "maximum_pose_matrix_error": max_pose_error,
            "maximum_visual_attachment_matrix_error": max_geometry_error,
            "maximum_joint_gap_m": max_joint_gap,
            "detail_objects": sum(map(len, assets.values())),
            "note": "Motion sampled with linear positions and quaternion SLERP; panel offsets removed for comparison"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "outputs/motion")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--animation", action="store_true", help="Render movie after writing scene and preview")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    output = args.input_dir.resolve()
    model = json.loads((output / "double-pendulum.model.json").read_text())
    motion = Motion(json.loads((output / "double-pendulum.motion.json").read_text()))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    basic = import_document(model, collection_name="Original PMS geometry")
    detailed = import_document(model, collection_name="Detailed visual assemblies")
    roots = [panel(basic, "Original panel", -2.35), panel(detailed, "Detailed panel", 2.05)]
    assets = {}
    for short, length, color, label in [("first_link", 1, "steelblue", "L1"),
                                       ("second_link", .8, "darkorange", "L2")]:
        name = "pendulum." + short
        for obj in detailed.graphics[name + ".graphics"]:
            obj.hide_render = True
            obj.hide_set(True)
        assets[name] = detailed_link(detailed.frames[name], length=length, color=color,
                                     collection=detailed.collection, label=label)
        # Put the two decorative end assemblies on adjacent depth planes to
        # avoid coplanar bearing faces at the shared elbow. This offset is local
        # visual placement, not a change to the simulated body or joint frame.
        for obj in assets[name]:
            obj.location.z += .06 if short == "first_link" else -.06
    setup_scene()
    frames = bake_motion(basic, motion, fps=args.fps)
    bake_motion(detailed, motion, fps=args.fps)
    report = verify(basic, detailed, roots, assets, motion, frames, args.fps)
    report["simulation_samples"] = len(motion.times)
    report["simulation_duration_s"] = motion.times[-1] - motion.times[0]
    report["source"] = json.loads((output / "provenance.json").read_text())
    (output / "playback.report.json").write_text(json.dumps(report, indent=2) + "\n")
    scene = bpy.context.scene
    scene.frame_set(16)  # Half-second overview shows both links clearly.
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output / "comparison.png")
    bpy.ops.render.render(write_still=True)
    # Save with movie settings ready for Render > Render Animation.
    scene.frame_set(1)
    if hasattr(scene.render.image_settings, "media_type"):
        scene.render.image_settings.media_type = "VIDEO"
    else:
        scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = str(output / "double-pendulum-motion.mp4")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "double-pendulum-motion.blend"))
    if args.animation:
        bpy.ops.render.render(animation=True)
    print("PLAYBACK_OK " + json.dumps(report))


if __name__ == "__main__":
    main()
