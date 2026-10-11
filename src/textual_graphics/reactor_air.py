"""Side supply/return plenums for vessel annular cooling; geometry, not airflow sizing."""
import math
import bpy
from mathutils import Vector


def air_dimensions(layout,d):
 a=layout.AIR_SYSTEM
 inner=d['hot_well_outer_radius']+.10
 return dict(base=d['top_z']-.75, port_z=d['top_z']-.75,
     manifold_inner=inner,manifold_outer=inner+1.40,
     mouth_width=3.20,mouth_height=1.05,box_width=3.60,box_height=2.30,
     stub_start=inner+1.40,stub_end=inner+2.40,
     lid_z=d['top_z']+.08,
     ports={kind:{'angle':a[kind+'_angle'],'point':[(inner+2.40)*math.cos(math.radians(a[kind+'_angle'])),(inner+2.40)*math.sin(math.radians(a[kind+'_angle'])),d['top_z']-.75],
                  'direction':[math.cos(math.radians(a[kind+'_angle'])),math.sin(math.radians(a[kind+'_angle'])),0]}
            for kind in ('hot','cold')})


def build_air_system(b,layout,d):
 from .reactor_geometry import arrow
 a=layout.AIR_SYSTEM;q=air_dimensions(layout,d);s=a['skin'];z=q['port_z']
 for name,color in [('air_hot_shell','#A76B42'),('air_cold_shell','#527F9E')]:b.material(name,color,metallic=.35)
 # Seal the annular passages at the top, without a hood over the pressure caps.
 lid=b.assembly('reactor.air_annulus_lid','Air collectors')
 b.annulus('closure',lid,d['hot_outer_radius']+.115,d['hot_well_inner_radius']+.02,q['lid_z']-s,q['lid_z'],'baffle',steps=128)
 ducts=b.assembly('reactor.air_ducts','Air ducts')
 for kind in ('hot','cold'):
  mat='air_'+kind+'_shell';ang=a[kind+'_angle'];rad=math.radians(ang)
  root=b.assembly('reactor.'+kind+'_air_manifold','Air collectors',angle=ang)
  root['service']='Vessel-to-baffle return' if kind=='hot' else 'Well-to-baffle downflow supply'
  x0=q['manifold_inner'];x1=q['manifold_outer'];w=q['box_width'];h=q['box_height']
  box=b.box('plenum',root,(x1-x0,w,h),((x0+x1)/2,0,z),mat)
  cut=b.box('cavity',root,(x1-x0-2*s,w-2*s,h-2*s),((x0+x1)/2,0,z),None);b.cut(box,cut)
  mouth=(q['mouth_width'],q['mouth_height'])
  cut=b.box('mouth',root,(.20,mouth[0],mouth[1]),(x0,0,z),None);b.cut(box,cut)
  cut=b.cylinder('round_outlet',root,a['duct_diameter']/2-a['duct_wall'],.20,(x1,0,z),None,vertices=64,bevel=0);cut.rotation_euler.y=math.pi/2;b.cut(box,cut)
  # A sealed rectangular sleeve crosses the cold passage only for hot exhaust.
  end_radius=d['hot_baffle_inner_radius'] if kind=='hot' else d['hot_well_inner_radius']
  sx=end_radius-.50;ex=x0+s
  sleeve=b.box('sealed_sleeve',root,(ex-sx,mouth[0]+2*s,mouth[1]+2*s),((sx+ex)/2,0,z),mat)
  cut=b.box('bore',root,(ex-sx+.2,mouth[0],mouth[1]),((sx+ex)/2,0,z),None);b.cut(sleeve,cut)
  # Clip the inner end to the cylindrical passage, avoiding an opening into its neighbour.
  cut=b.cylinder('curved_end',root,end_radius,5,(0,0,z),None,vertices=128,bevel=0);b.cut(sleeve,cut)
  for name in (['reactor.well.wall','reactor.baffle.vertical_sheet'] if kind=='hot' else ['reactor.well.wall']):
   cutter=b.box('wall_port',root,(ex-sx+.1,mouth[0],mouth[1]),((sx+ex)/2,0,z),None);b.cut(bpy.data.objects[name],cutter)
  stub=b.annulus(kind+'_stub',ducts,a['duct_diameter']/2-a['duct_wall'],a['duct_diameter']/2,0,1.0,mat,steps=64)
  # Local Z points radially outward; point metadata is independent of section bounds.
  stub.rotation_euler=(Vector(q['ports'][kind]['direction'])).to_track_quat('Z','Y').to_euler()
  stub.location=(x1*math.cos(rad),x1*math.sin(rad),z)
  stub['terminal_local']=(0,0,1.0);stub['outside_diameter']=a['duct_diameter'];stub['open_ends']=True
  fl=b.annulus(kind+'_stub_flange',ducts,a['duct_diameter']/2,a['duct_diameter']/2+.07,.95,1.0,'steel',steps=64);fl.location=stub.location;fl.rotation_euler=stub.rotation_euler
  flow=b.assembly('reactor.'+kind+'_side_flow','Air path arrows',angle=ang)
  points=[(end_radius-.06,0,z),(q['stub_end']-.1,0,z)]
  if kind=='cold':points.reverse()
  arrow(b,'flow',flow,points,'air' if kind=='cold' else 'hot',.045)
 return q


def check_air_system(b,layout,d):
 from .reactor_checks import closed_mesh
 q=air_dimensions(layout,d);a=layout.AIR_SYSTEM
 bpy.context.view_layer.update()
 for category in ('Air collectors','Air ducts'):
  for ob in b.collection(category).objects:
   if ob.type=='MESH':closed_mesh(ob)
 def hit(obj,origin,direction,distance):
  inv=obj.matrix_world.inverted()
  return obj.ray_cast(inv@Vector(origin),inv.to_3x3()@Vector(direction),distance=distance)
 for kind in ('hot','cold'):
  port=q['ports'][kind];direction=Vector(port['direction']);start=Vector(port['point'])+direction*.05
  stub=bpy.data.objects['reactor.air_ducts.'+kind+'_stub']
  assert not hit(stub,start,-direction,1.15)[0]
  box=bpy.data.objects['reactor.'+kind+'_air_manifold.plenum']
  assert not hit(box,start,-direction,3.0)[0]
  wall=bpy.data.objects['reactor.well.wall'];result=hit(wall,start,-direction,4)
  assert not result[0]
  baffle=bpy.data.objects['reactor.baffle.vertical_sheet'];result=hit(baffle,start,-direction,4)
  assert result[0] == (kind=='cold'),(kind,'baffle isolation')
  assert q['port_z']+q['mouth_height']/2<q['lid_z']
 assert not any(o.name.startswith('reactor.hot_air_hood') for o in bpy.data.objects)
 return dict(dimensions=q,parameters=a,side_manifolds=True,open_supply_and_exhaust=True,
  hot_sleeve_separates_crossed_cold_passage=True,cold_port_does_not_cut_baffle=True,
  hood_removed=True,thermal_or_airflow_analysis=False,
  limitations=['Plenum sizes and rectangular-to-round transitions are provisional','No pressure-drop, natural-draft, structural opening or heat-removal qualification'])
