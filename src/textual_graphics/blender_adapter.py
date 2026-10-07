"""Render a literal PMS spatial model document in Blender.

This module runs in Blender's Python. The input is detached ordinary data from
Sim3D.document(model); neither PMS nor a solver is imported here.
"""

from dataclasses import dataclass, field
import math

import bpy
from mathutils import Matrix, Vector


class UnsupportedModel(ValueError):
    """The document needs model expansion or a representation not yet supported."""


@dataclass
class ImportResult:
    collection: object
    frames: dict = field(default_factory=dict)
    graphics: dict = field(default_factory=dict)
    skipped_elements: list = field(default_factory=list)


COLORS = {
    "steelblue": (70 / 255, 130 / 255, 180 / 255),
    "darkorange": (1.0, 140 / 255, 0.0),
    "white": (1.0, 1.0, 1.0),
    "black": (0.0, 0.0, 0.0),
    "red": (0.85, 0.12, 0.10),
    "green": (0.12, 0.60, 0.24),
    "blue": (0.12, 0.32, 0.85),
}


def color_rgba(value, opacity=1.0):
    """Small explicit color vocabulary; reject unrecognized names."""
    if isinstance(value, str):
        if value in COLORS:
            rgb = COLORS[value]
        elif value.startswith("gray") and value[4:].isdigit():
            rgb = (int(value[4:]) / 100,) * 3
        elif value.startswith("#") and len(value) == 7:
            rgb = tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
        else:
            raise UnsupportedModel(f"Unsupported color {value!r}; use #RRGGBB")
    else:
        rgb = tuple(value)
    if len(rgb) != 3 or not all(0 <= c <= 1 for c in (*rgb, opacity)):
        raise ValueError("Color and opacity must be in [0, 1]")
    # PMS colors are sRGB; shader colors are scene-linear.
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055)**2.4
                 for c in rgb) + (opacity,)


def material(name, color, opacity=1.0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    rgba = color_rgba(color, opacity)
    result.diffuse_color = rgba
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = .34
    shader.inputs["Alpha"].default_value = opacity
    return result


def vector3(value, label):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise UnsupportedModel(f"{label}: expected three literal numbers")
    if any(isinstance(x, bool) or not isinstance(x, (int, float))
           or not math.isfinite(x) for x in value):
        raise UnsupportedModel(f"{label}: expected three finite literal numbers")
    return Vector(value)


def rotation(value):
    if value is None:
        return Matrix.Identity(4)
    if len(value) == 4:
        angle, *axis = value
        if isinstance(angle, str):
            text = angle.strip()
            if text.endswith("deg"):
                angle = math.radians(float(text[:-3]))
            elif text.endswith("°"):
                angle = math.radians(float(text[:-1]))
            else:
                raise UnsupportedModel(f"Unsupported angle {angle!r}")
        if not isinstance(angle, (int, float)) or not math.isfinite(angle):
            raise ValueError("Orientation angle must be finite")
        direction = vector3(axis, "orientation axis")
        if direction.length == 0:
            raise ValueError("Orientation axis must be nonzero")
        return Matrix.Rotation(angle, 4, direction.normalized())
    if len(value) == 3:
        result = Matrix([vector3(row, "orientation row") for row in value])
        identity = result.transposed() @ result
        error = max(abs(identity[i][j] - (i == j))
                    for i in range(3) for j in range(3))
        if error > 1e-5 or abs(result.determinant() - 1) > 1e-5:
            raise ValueError("Orientation must be a proper orthonormal matrix")
        return result.to_4x4()
    raise UnsupportedModel("Orientation must be axis-angle or a 3x3 matrix")


def transform(table):
    return (Matrix.Translation(vector3(table.get("position", [0, 0, 0]), "position"))
            @ rotation(table.get("orientation")))


def _entries(document, prefix=""):
    for key, value in document.items():
        if not isinstance(value, dict) or key == "graphics":
            continue
        name = f"{prefix}.{key}" if prefix else key
        if "type" in value:
            yield name, value
        yield from _entries(value, name)


def _link_object(obj, collection):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def _empty(name, collection, parent=None, matrix=None):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.parent = parent
    obj.matrix_basis = matrix if matrix is not None else Matrix.Identity(4)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = .06
    obj["pms_name"] = name
    return obj


def _box(name, size, parent, collection, color, opacity):
    size = vector3(size, name + ".size")
    if min(size) <= 0:
        raise ValueError(f"{name}: box dimensions must be positive")
    # Vertices encode dimensions; object transforms keep PMS frame semantics.
    vertices = [(x * size.x / 2, y * size.y / 2, z * size.z / 2)
                for x, y, z in [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                                (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(0,3,2,1), (4,5,6,7), (0,1,5,4),
                                      (1,2,6,5), (2,3,7,6), (3,0,4,7)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = parent
    obj.data.materials.append(material(name + ".material", color, opacity))
    return obj


def _arrow(name, axis, length, parent, collection, color):
    pieces = []
    for tip in (False, True):
        depth = length * (.18 if tip else .82)
        if tip:
            bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=length * .045,
                                           radius2=0, depth=depth)
        else:
            bpy.ops.mesh.primitive_cylinder_add(vertices=24,
                                               radius=length * .016, depth=depth)
        obj = bpy.context.object
        obj.name = name + (".head" if tip else ".shaft")
        _link_object(obj, collection)
        obj.parent = parent
        obj.location = axis * length * (.91 if tip else .41)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis)
        obj.data.materials.append(material(obj.name + ".material", color))
        pieces.append(obj)
    return pieces


def import_document(document, *, collection_name="PMS Model"):
    """Import authored spatial frames and explicit graphics, in metres.

    Mechanics are recorded as skipped elements, not interpreted. This function
    does not solve constraints, expand assemblies, or correct initial conditions.
    Existing scene objects are never deleted. Blender may suffix display names
    on repeat imports; pms_name properties retain the exact source identity.
    """
    if document.get("model", {}).get("dimension") != "spatial":
        raise UnsupportedModel("This adapter currently accepts spatial models only")
    entries = dict(_entries(document))
    for name, table in entries.items():
        if table["type"] in {"assembly", "flexible_beam"}:
            raise UnsupportedModel(f"{name}: {table['type']} needs expansion/deformation support")
        if any(key in table for key in ("position_in", "orientation_in", "frame")):
            raise UnsupportedModel(f"{name}: unresolved frame reference")
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    result = ImportResult(collection)
    for name, table in entries.items():
        if table["type"] in {"ground", "rigid_body"}:
            if table["type"] == "ground" and any(k in table for k in ("position", "orientation")):
                raise UnsupportedModel(f"{name}: ground frame must be global")
            obj = _empty(name, collection, matrix=transform(table))
            obj["pms_type"] = table["type"]
            result.frames[name] = obj
        elif table["type"] != "marker":
            result.skipped_elements.append({"name": name, "type": table["type"]})
    for name, table in entries.items():
        if table["type"] != "marker":
            continue
        owner = name.rsplit(".", 1)[0]
        if owner not in result.frames:
            raise UnsupportedModel(f"{name}: expected a body or ground owner")
        obj = _empty(name, collection, result.frames[owner], transform(table))
        obj["pms_type"] = "marker"
        result.frames[name] = obj

    for name, table in entries.items():
        graphics = table.get("graphics", {})
        if not graphics:
            continue
        if name not in result.frames:
            if "shape" in graphics:
                raise UnsupportedModel(f"{name}: graphics on this element are unsupported")
            continue
        if not graphics.get("visible", True):
            continue
        specs = []
        if "shape" in graphics and graphics.get("show_default", True):
            specs.append((name + ".graphics", graphics))
        specs.extend((name + ".graphics." + key, {**{k: v for k, v in graphics.items()
                                                     if not isinstance(v, dict) and k != "shape"}, **value})
                     for key, value in graphics.items() if isinstance(value, dict))
        for graphic_name, spec in specs:
            if not spec.get("visible", True):
                continue
            shape = spec.get("shape")
            if shape not in {"box", "xy_frame"}:
                raise UnsupportedModel(f"{graphic_name}: unsupported graphic shape {shape!r}")
            frame_name = spec.get("marker", name)
            if frame_name not in result.frames:
                raise ValueError(f"{graphic_name}: missing marker {frame_name}")
            if "marker" in spec and (entries[frame_name]["type"] != "marker"
                                     or frame_name.rsplit(".", 1)[0] != name):
                raise ValueError(f"{graphic_name}: marker must belong to {name}")
            parent = result.frames[frame_name]
            if shape == "box":
                obj = _box(graphic_name, spec["size"], parent, collection,
                           spec.get("color", "steelblue"), spec.get("opacity", 1.0))
                objects = [obj]
            else:
                if table["type"] != "marker":
                    raise ValueError(f"{graphic_name}: xy_frame must belong to a marker")
                length = float(spec.get("axis_length", .35))
                plane_size = float(spec.get("plane_size", .45 * length))
                if not math.isfinite(length) or not math.isfinite(plane_size) or min(length, plane_size) <= 0:
                    raise ValueError(f"{graphic_name}: frame sizes must be finite and positive")
                root = _empty(graphic_name, collection, parent)
                root["label"] = spec.get("label", "")
                objects = [root]
                for axis, direction, color in [("x", (1,0,0), "red"),
                                                ("y", (0,1,0), "green"),
                                                ("z", (0,0,1), "blue")]:
                    objects.extend(_arrow(graphic_name + "." + axis,
                                          Vector(direction), length, root, collection, color))
                plane = _box(graphic_name + ".plane", (plane_size, plane_size, .0002),
                             root, collection, spec.get("plane_color", "gray65"),
                             spec.get("opacity", .18))
                plane.location = (plane_size / 2, plane_size / 2, 0)
                objects.append(plane)
            for obj in objects:
                obj["pms_name"] = graphic_name
                obj["pms_owner"] = name
            result.graphics[graphic_name] = objects
    bpy.context.view_layer.update()
    return result
