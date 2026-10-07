"""Decode the rendered movie with Blender and export six frames for visual QA."""

import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / "outputs/motion"
movie = output / "double-pendulum-motion.mp4"
if not movie.is_file():
    raise FileNotFoundError(movie)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
editor = scene.sequence_editor_create()
strip = editor.strips.new_movie("Rendered comparison", str(movie), channel=1, frame_start=1)
if strip.frame_duration != 121:
    raise AssertionError(f"Expected 121 decoded frames, got {strip.frame_duration}")
scene.render.resolution_x, scene.render.resolution_y = 1200, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Standard"
scene.render.use_sequencer = True
qa = output / "decoded-frames"
qa.mkdir(exist_ok=True)
for frame in (1, 16, 31, 61, 91, 121):
    scene.frame_set(frame)
    scene.render.filepath = str(qa / f"frame-{frame:03d}.png")
    bpy.ops.render.render(write_still=True)
(output / "movie-verification.json").write_text(json.dumps({
    "movie": str(movie), "decoded_frames": strip.frame_duration,
    "fps": strip.fps, "sampled_frames": [1, 16, 31, 61, 91, 121],
    "size_bytes": movie.stat().st_size,
}, indent=2) + "\n")
print("MOVIE_DECODE_OK")
