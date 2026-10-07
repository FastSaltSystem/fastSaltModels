"""Closed extruded meshes with polygonal through-bores, using Blender's CDT."""
import math
from collections import Counter
from functools import lru_cache
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt


def inside_polygon(point,outline):
    x,y=point;inside=False
    for (ax,ay),(bx,by) in zip(outline,outline[1:]+outline[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:
            inside=not inside
    return inside


@lru_cache(maxsize=32)
def perforated_profile(outline,holes,segments):
    vertices=list(outline);edges=[(i,(i+1)%len(outline)) for i in range(len(outline))]
    for x,y,r in holes:
        start=len(vertices)
        vertices.extend((x+r*math.cos(i*math.tau/segments),y+r*math.sin(i*math.tau/segments)) for i in range(segments))
        edges.extend((start+i,start+(i+1)%segments) for i in range(segments))
    points,_,triangles,*_=delaunay_2d_cdt([Vector(v) for v in vertices],edges,[],0,1e-8,False)
    kept=[];step=math.tau/segments
    for triangle in triangles:
        cx=sum(points[i].x for i in triangle)/3;cy=sum(points[i].y for i in triangle)/3
        if not inside_polygon((cx,cy),outline):continue
        in_hole=False
        for x,y,r in holes:
            dx=cx-x;dy=cy-y;distance2=dx*dx+dy*dy
            if distance2>=r*r:continue
            angle=math.atan2(dy,dx)%step-step/2
            if math.sqrt(distance2)*math.cos(angle)<r*math.cos(step/2)+1e-9:
                in_hole=True;break
        if not in_hole:kept.append(triangle)
    used=sorted({i for face in kept for i in face});remap={old:new for new,old in enumerate(used)}
    vertices=[tuple(points[i]) for i in used]
    faces=[tuple(remap[i] for i in face) for face in kept]
    counts=Counter(tuple(sorted((a,b))) for face in faces for a,b in zip(face,face[1:]+face[:1]))
    boundary=[(a,b) for face in faces for a,b in zip(face,face[1:]+face[:1]) if counts[tuple(sorted((a,b)))]==1]
    assert all(count in (1,2) for count in counts.values())
    return vertices,faces,boundary


def perforated_prism(b,name,parent,outline,holes,bottom,top,mat,axis='Z',segments=16,position=(0,0,0)):
    points,triangles,boundary=perforated_profile(tuple(outline),tuple(holes),segments)
    n=len(points)
    vertices=[(x,y,z) if axis=='Z' else (x,z,y) for z in (bottom,top) for x,y in points]
    faces=[tuple(reversed(face)) for face in triangles]+[tuple(i+n for i in face) for face in triangles]
    faces.extend((a,b,b+n,a+n) for a,b in boundary)
    obj=b.mesh(name,parent,vertices,faces,mat,position)
    obj['through_hole_count']=len(holes)
    return obj
