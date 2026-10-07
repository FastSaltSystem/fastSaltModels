"""Blender integration checks: --background --python-exit-code 1 --python this_file."""

import math
from pathlib import Path
import sys
import unittest

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from textual_graphics.blender_adapter import UnsupportedModel, import_document


def document(body):
    return {"model": {"dimension": "spatial"}, "assembly": {"body": body}}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def assertVector(self, actual, expected):
        self.assertLess((Vector(actual) - Vector(expected)).length, 1e-5)

    def test_rotated_body_marker_and_box_use_reference_origin_not_cm(self):
        data = document({
            "type": "rigid_body", "position": [3, 4, 5],
            "orientation": ["90 deg", 0, 0, 2],
            "center_of_mass": "assembly.body.cm",
            "cm": {"type": "marker", "position": [.5, 0, 0]},
            "tip": {"type": "marker", "position": [2, 0, 0],
                    "orientation": [[1,0,0], [0,0,-1], [0,1,0]]},
            "graphics": {"shape": "box", "size": [2, .4, .6],
                         "marker": "assembly.body.tip"},
        })
        result = import_document(data)
        tip = result.frames["assembly.body.tip"]
        box = result.graphics["assembly.body.graphics"][0]
        self.assertVector(tip.matrix_world.translation, (3, 6, 5))
        self.assertVector(box.matrix_world.translation, (3, 6, 5))
        self.assertVector(box.matrix_world.to_3x3() @ Vector((0, 1, 0)), (0, 0, 1))
        self.assertEqual(box["pms_name"], "assembly.body.graphics")
        self.assertEqual(data["assembly"]["body"]["orientation"][0], "90 deg")

    def test_axis_angle_radians_and_matrix_equivalence(self):
        first = import_document(document({"type": "rigid_body",
                                           "orientation": [math.pi / 2, 0, 0, 1]}))
        second = import_document(document({"type": "rigid_body",
                                            "orientation": [[0,-1,0], [1,0,0], [0,0,1]]}))
        a = first.frames["assembly.body"].matrix_world.to_3x3()
        b = second.frames["assembly.body"].matrix_world.to_3x3()
        self.assertVector(a @ Vector((1,0,0)), b @ Vector((1,0,0)))

    def test_named_graphic_survives_show_default_false(self):
        result = import_document(document({"type": "rigid_body", "graphics": {
            "show_default": False, "color": "darkorange",
            "member": {"shape": "box", "size": [1, 2, 3]},
        }}))
        self.assertEqual(list(result.graphics), ["assembly.body.graphics.member"])

    def test_hidden_graphics_omitted_but_frames_retained(self):
        result = import_document(document({"type": "rigid_body", "graphics": {
            "visible": False, "shape": "box", "size": [1, 2, 3]}}))
        self.assertFalse(result.graphics)
        self.assertIn("assembly.body", result.frames)

    def test_rejects_missing_marker(self):
        with self.assertRaisesRegex(ValueError, "missing marker"):
            import_document(document({"type": "rigid_body", "graphics": {
                "shape": "box", "size": [1, 2, 3], "marker": "missing"}}))

    def test_rejects_unsupported_shape(self):
        with self.assertRaisesRegex(UnsupportedModel, "unsupported graphic shape"):
            import_document(document({"type": "rigid_body", "graphics": {"shape": "gear"}}))

    def test_rejects_unexpanded_assembly_and_flexible_beam(self):
        for kind in ("assembly", "flexible_beam"):
            with self.subTest(kind=kind), self.assertRaises(UnsupportedModel):
                import_document(document({"type": kind}))

    def test_rejects_planar_input(self):
        with self.assertRaisesRegex(UnsupportedModel, "spatial"):
            import_document({"model": {"dimension": "planar"}})

    def test_rejects_improper_rotation(self):
        with self.assertRaisesRegex(ValueError, "orthonormal"):
            import_document(document({"type": "rigid_body",
                                      "orientation": [[1,0,0], [0,1,0], [0,0,-1]]}))

    def test_frame_axes_and_plane_follow_marker(self):
        result = import_document({"model": {"dimension": "spatial"}, "ground": {
            "type": "ground", "pin": {"type": "marker", "position": [2,3,4],
                "orientation": ["90°", 0,0,1], "graphics": {"shape": "xy_frame"}}}})
        objects = result.graphics["ground.pin.graphics"]
        shaft = next(obj for obj in objects if obj.name.endswith("x.shaft"))
        self.assertVector(shaft.matrix_world.translation, (2, 3 + .35 * .41, 4))


suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise RuntimeError("Blender adapter integration tests failed")
