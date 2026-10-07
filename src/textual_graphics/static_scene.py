"""Small Blender geometry toolkit for named static visual assemblies."""

import math
import bpy
import bmesh
from mathutils import Vector

from .blender_adapter import color_rgba


class SceneBuilder:
    def __init__(self):
        self.collections = {}
        self.materials = {}
        self.assemblies = {}

    def collection(self, name):
        if name not in self.collections:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
            self.collections[name] = collection
        return self.collections[name]

    def material(self, name, color, *, metallic=0, roughness=.45, concrete=False):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        rgba = color_rgba(color)
        mat.diffuse_color = rgba
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = rgba
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
        if concrete:
            noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 5
            bump = mat.node_tree.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = .16
            bump.inputs["Distance"].default_value = .045
            mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
            mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
        self.materials[name] = mat
        return mat

    def assembly(self, name, category, position=(0,0,0), angle=0):
        if name in self.assemblies:
            raise ValueError(f"Duplicate assembly name {name}")
        root = bpy.data.objects.new(name, None)
        self.collection(category).objects.link(root)
        root.location = position
        root.rotation_euler.z = math.radians(angle)
        root.empty_display_size = .25
        root["assembly_id"] = name
        root["category"] = category
        root["units"] = "metres"
        self.assemblies[name] = root
        return root

    def finish(self, obj, name, parent, mat, position=(0,0,0), bevel=0):
        obj.name = parent.name + "." + name
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
        parent.users_collection[0].objects.link(obj)
        obj.parent = parent
        obj.location = position
        obj["assembly_id"] = parent["assembly_id"]
        if mat:
            obj.data.materials.append(self.materials[mat])
        if bevel:
            modifier = obj.modifiers.new("Edge highlights", "BEVEL")
            modifier.width, modifier.segments = bevel, 2
        return obj

    def box(self, name, parent, size, position, mat, bevel=0):
        x, y, z = [s/2 for s in size]
        verts = [(a*x,b*y,c*z) for a,b,c in
                 [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                  (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        return self.mesh(name, parent, verts,
                         [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],
                         mat, position, bevel)

    def mesh(self, name, parent, vertices, faces, mat, position=(0,0,0), bevel=0):
        mesh = bpy.data.meshes.new(parent.name + "." + name)
        mesh.from_pydata(vertices, [], faces)
        bm=bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(parent.name + "." + name, mesh)
        return self.finish(obj, name, parent, mat, position, bevel)

    def cylinder(self, name, parent, radius, depth, position, mat, vertices=64, bevel=.02):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
        return self.finish(bpy.context.object, name, parent, mat, position, bevel)

    def tube(self, name, parent, points, radius, mat):
        data = bpy.data.curves.new(parent.name + "." + name, "CURVE")
        data.dimensions = "3D"
        data.resolution_u = 12
        data.bevel_depth, data.bevel_resolution = radius, 3
        data.use_fill_caps = True
        spline = data.splines.new("POLY")
        spline.points.add(len(points)-1)
        for vertex, point in zip(spline.points, points):
            vertex.co = (*point, 1)
        return self.finish(bpy.data.objects.new(data.name, data), name, parent, mat)

    def rounded_pipe(self, name, parent, points, radius, mat, bend=.6):
        """Round the corners of a presentation polyline with quadratic curves."""
        points = [Vector(p) for p in points]
        result = [points[0]]
        for a, b, c in zip(points, points[1:], points[2:]):
            distance = min(bend, (a-b).length*.4, (c-b).length*.4)
            u = b + (a-b).normalized()*distance
            v = b + (c-b).normalized()*distance
            result.append(u)
            for i in range(1,9):
                t = i/8
                result.append((1-t)**2*u + 2*(1-t)*t*b + t*t*v)
        result.append(points[-1])
        return self.tube(name, parent, result, radius, mat)

    def beam(self, name, parent, a, b, radius, mat):
        a, b = Vector(a), Vector(b)
        obj = self.cylinder(name, parent, radius, (b-a).length, (a+b)/2, mat, vertices=16, bevel=0)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector((0,0,1)).rotation_difference((b-a).normalized())
        return obj

    def ring(self, name, parent, radius, z, tube_radius, mat, start=0, end=360, steps=128):
        points = [(radius*math.cos(math.radians(start+(end-start)*i/steps)),
                   radius*math.sin(math.radians(start+(end-start)*i/steps)), z)
                  for i in range(steps+1)]
        return self.tube(name, parent, points, tube_radius, mat)

    def annulus(self, name, parent, inner, outer, bottom, top, mat, start=0, end=360, steps=128):
        verts=[]
        closed=abs(end-start-360)<1e-8
        for i in range(steps if closed else steps+1):
            angle=math.radians(start+(end-start)*i/steps)
            for radius,z in [(inner,bottom),(outer,bottom),(outer,top),(inner,top)]:
                verts.append((radius*math.cos(angle),radius*math.sin(angle),z))
        faces=[]
        for i in range(steps):
            for side in range(4):
                a=i*4+side; b=i*4+(side+1)%4
                next_i=(i+1)%steps if closed else i+1
                faces.append((a,b,next_i*4+(side+1)%4,next_i*4+side))
        if not closed:
            faces.extend([(3,2,1,0),(steps*4,steps*4+1,steps*4+2,steps*4+3)])
        return self.mesh(name,parent,verts,faces,mat)

    def dome(self, name, parent, radius, rise, base, thickness, mat, start=0, end=180):
        # Closed, thick half-ellipsoidal shell. Angular rows stop just below the
        # apex to avoid degenerate quads, then cap the small remaining opening.
        nu,nv=80,32
        verts=[]
        for inside in (False,True):
            r=radius-(thickness if inside else 0)
            h=rise-(thickness if inside else 0)
            for j in range(nv+1):
                latitude=(math.pi/2-.001)*j/nv
                for i in range(nu+1):
                    longitude=math.radians(start+(end-start)*i/nu)
                    verts.append((r*math.cos(latitude)*math.cos(longitude),
                                  r*math.cos(latitude)*math.sin(longitude),base+h*math.sin(latitude)))
        n=(nu+1)*(nv+1); faces=[]
        for layer in (0,1):
            for j in range(nv):
                for i in range(nu):
                    a=layer*n+j*(nu+1)+i
                    face=(a,a+1,a+nu+2,a+nu+1)
                    faces.append(face if layer==0 else tuple(reversed(face)))
        for j in (0,nv):
            for i in range(nu):
                a=j*(nu+1)+i
                faces.append((a,a+n,a+n+1,a+1))
        for i in (0,nu):
            for j in range(nv):
                a=j*(nu+1)+i; b=a+nu+1
                faces.append((a,b,b+n,a+n))
        obj=self.mesh(name,parent,verts,faces,mat)
        for polygon in obj.data.polygons:
            if polygon.index<2*nu*nv: polygon.use_smooth=True
        return obj

    def cut(self, obj, cutter):
        bpy.context.view_layer.update()
        modifier=obj.modifiers.new("Presentation opening", "BOOLEAN")
        modifier.operation="DIFFERENCE"
        modifier.solver="EXACT"
        modifier.object=cutter
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter,do_unlink=True)

    def rail(self, name, parent, points, mat="rail", height=1.0):
        for level in (height*.5,height):
            self.tube(name+f".rail{level}",parent,[(x,y,z+level) for x,y,z in points],.025,mat)
        for i,(x,y,z) in enumerate(points):
            self.beam(name+f".post{i}",parent,(x,y,z),(x,y,z+height),.027,mat)
