"""Example visual assemblies. These add no mass, inertia, or solver elements."""

import math

import bpy

from .blender_adapter import _box, material


def _finish(obj, name, parent, collection, location, mat):
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.data.materials.append(mat)
    obj["visual_only"] = True
    obj["pms_attachment"] = parent.get("pms_name", parent.name)
    return obj


def detailed_link(parent, *, length, color, collection, label):
    """Two rails, cross braces, end bosses, bearing rings, and bolt heads.

    All vertices are local to the same body frame as the original PMS box.
    End bosses are centered exactly on the inner/outer marker locations.
    """
    name = parent["pms_name"] + ".detail"
    steel = material(name + ".steel", "#A9B7C5")
    steel.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = .75
    dark = material(name + ".dark", "#26364A")
    paint = material(name + ".paint", color)
    meshes = []

    def box(suffix, size, location, paint_color=color):
        obj = _box(name + suffix, size, parent, collection, paint_color, 1)
        obj.location = location
        bevel = obj.modifiers.new("Machined edges", "BEVEL")
        bevel.width = .008
        bevel.segments = 3
        obj["visual_only"] = True
        obj["pms_attachment"] = parent["pms_name"]
        meshes.append(obj)
        return obj

    for side in (-1, 1):
        box(f".rail{side}", (length - .10, .044, .075), (0, side * .061, 0))
    for index, fraction in enumerate((-.3, 0, .3)):
        box(f".brace{index}", (.045, .125, .06), (fraction * length, 0, -.01))

    for end, x in [("inner", -length / 2), ("outer", length / 2)]:
        for part, radius, depth, z, mat in [
            ("boss", .102, .085, 0, paint),
            ("bearing", .054, .095, .007, steel),
            ("shaft", .026, .115, .012, dark),
        ]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth)
            obj = _finish(bpy.context.object, f"{name}.{end}.{part}", parent,
                          collection, (x, 0, z), mat)
            bevel = obj.modifiers.new("Edge radius", "BEVEL")
            bevel.width = .004
            bevel.segments = 2
            meshes.append(obj)
        bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=12,
                                        major_radius=.039, minor_radius=.005)
        meshes.append(_finish(bpy.context.object, f"{name}.{end}.ring", parent,
                              collection, (x, 0, .059), steel))
        for index in range(6):
            angle = index * math.tau / 6
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.012, depth=.012)
            meshes.append(_finish(bpy.context.object, f"{name}.{end}.bolt{index}", parent,
                                  collection, (x + .077 * math.cos(angle),
                                               .077 * math.sin(angle), .049), steel))

    plate = box(".badge", (.19, .087, .014), (0, 0, .044), "#26364A")
    data = bpy.data.curves.new(name + ".label", "FONT")
    data.body = label
    data.size = .055
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    obj = bpy.data.objects.new(name + ".label", data)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = (0, 0, .053)
    obj.data.materials.append(material(name + ".lettering", "white"))
    obj["visual_only"] = True
    obj["pms_attachment"] = parent["pms_name"]
    meshes.append(obj)
    return meshes
