"""Blender playback tests with analytically known poses and saved-result checks."""

import copy
import json
import math
from pathlib import Path
import sys
import unittest

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from textual_graphics.blender_adapter import import_document
from textual_graphics.playback import Motion, bake_motion


def motion_document():
    return {"format": "SimpView", "version": 4, "dimension": "spatial", "choices": [{
        "label": "Result", "times": [5, 6], "scene": {
            "follow_targets": [{"name": "body", "track": "body_frame:body"}],
            "tracks": [{"id": "body_frame:body", "position": [[1,2,3], [3,2,3]],
                        "quaternion": [[0,0,0,1], [0,0,1,0]], "scale": [[1,1,1]]}],
        }}]}


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def assertVector(self, actual, expected):
        self.assertLess((Vector(actual) - Vector(expected)).length, 1e-5)

    def test_midpoint_uses_slerp_and_xyzw_conversion(self):
        motion = Motion(motion_document())
        position, rotation = motion.pose("body", 5.5)
        self.assertVector(position, (2, 2, 3))
        self.assertVector(rotation @ Vector((1,0,0)), (0,1,0))

    def test_antipodal_quaternions_do_not_spin(self):
        doc = motion_document()
        doc["choices"][0]["scene"]["tracks"][0]["quaternion"] = [[0,0,0,1], [0,0,0,-1]]
        _, rotation = Motion(doc).pose("body", 5.5)
        self.assertVector(rotation @ Vector((1,0,0)), (1,0,0))

    def test_compacted_constant_positions(self):
        doc = motion_document()
        doc["choices"][0]["scene"]["tracks"][0]["position"] = [[7,8,9]]
        self.assertVector(Motion(doc).pose("body", 6)[0], (7,8,9))

    def test_baked_frames_move_local_markers_and_meshes(self):
        model = {"model": {"dimension": "spatial"}, "body": {"type": "rigid_body",
            "tip": {"type": "marker", "position": [1,0,0]},
            "graphics": {"shape": "box", "size": [2,.2,.2]}}}
        imported = import_document(model)
        count = bake_motion(imported, Motion(motion_document()), fps=2)
        self.assertEqual(count, 3)
        bpy.context.scene.frame_set(2)
        self.assertVector(imported.frames["body.tip"].matrix_world.translation, (2,3,3))
        mesh = imported.graphics["body.graphics"][0]
        self.assertVector(mesh.matrix_world @ Vector((1,0,0)), (2,3,3))

    def test_rejects_out_of_range_time_and_invalid_samples(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            Motion(motion_document()).pose("body", 4)
        for field, value in [("scale", [[2,1,1]]), ("quaternion", [[0,0,0,0]]),
                             ("position", [[0,0,0]] * 3)]:
            doc = motion_document()
            doc["choices"][0]["scene"]["tracks"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                Motion(doc)

    def test_multi_choice_requires_explicit_selection(self):
        doc = motion_document()
        doc["choices"].append(copy.deepcopy(doc["choices"][0]))
        doc["choices"][1]["label"] = "Dynamic"
        with self.assertRaisesRegex(ValueError, "explicitly"):
            Motion(doc)
        self.assertEqual(Motion(doc, choice="Dynamic").times, [5,6])

    def test_body_name_mismatch_does_not_silently_skip_motion(self):
        imported = import_document({"model": {"dimension": "spatial"},
                                    "other": {"type": "rigid_body"}})
        with self.assertRaisesRegex(ValueError, "do not match"):
            bake_motion(imported, Motion(motion_document()))

    def test_saved_pms_result_tracks_are_valid(self):
        path = ROOT / "outputs/motion/double-pendulum.motion.json"
        if not path.exists():
            self.skipTest("Run prepare_motion.py for real-result integration check")
        motion = Motion(json.loads(path.read_text()))
        self.assertEqual(len(motion.times), 241)
        self.assertEqual(set(motion.tracks), {"pendulum.first_link", "pendulum.second_link"})
        # First sample matches the known authored pose. Later motion is nonzero.
        self.assertVector(motion.pose("pendulum.first_link", 0)[0], (.5,0,0))
        self.assertGreater(abs(motion.pose("pendulum.first_link", .5)[0].y), .1)


result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(PlaybackTests))
if not result.wasSuccessful():
    raise RuntimeError("Playback checks failed")
