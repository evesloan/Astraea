"""Authored salon shell and coordinated section; source stays editable.
Requires Blender4.3.2; no project-generation or third-party assets.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];plan=json.loads((ROOT/'source/salon_profile.json').read_text());AX,AZ=plan['anchor_xz']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','dark_rubber','teal_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.72
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('SAL_PerceivableGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.19,.37,.38,1);b.inputs['Alpha'].default_value=.28;b.inputs['Roughness'].default_value=.3;m.surface_render_method='DITHERED';mats['glass']=m
m=bpy.data.materials.new('SAL_WarmLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.92,.8,1);b.inputs['Emission Color'].default_value=(1,.9,.75,1);b.inputs['Emission Strength'].default_value=1.6;mats['lens']=m
parts=[]
def h(x,z):
 low=plan['low_reading_ceiling'];high=plan['gathering_ceiling'];front=plan['front_gallery_ceiling']
 hz=low if z<=-24 else (high if z>=-18 else low+(z+24)*(high-low)/6)
 return min(hz,front+(x-52)*.25)
def mesh(name,points,faces,role,close=True):
 vertices=[(x-AX,-(z-AZ),y) for x,y,z in points];d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update()
 if close:
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.5,q.y*.5) if abs(p.normal.z)>.5 else ((q.x+q.y)*.5,q.z*.5)
 return o
def prism(name,poly,low,high,role):
 n=len(poly);v=[(x,low,z) for x,z in poly]+[(x,high,z) for x,z in poly]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,role)
def strip(name,a,b,width,low,high,role):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();n=Vector((v.y,-v.x))*width*.5
 return prism(name,[a+n,b+n,b-n,a-n],low,high,role)
# Deliberately softened outer boundary stays inside the existing faceted floor envelope.
P=[Vector(p) for p in plan['boundary_xz']];path=[P[0]]
for i in range(1,len(P)-1):
 prev,p,nex=P[i-1],P[i],P[i+1];r=min(1.4,(p-prev).length*.2,(nex-p).length*.2);a=p+(prev-p).normalized()*r;b=p+(nex-p).normalized()*r
 for k in range(5):t=k/4;path.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
path.append(P[-1])
def wall_band(name,low,high,role,depth):
 for i in range(len(path)-1):
  a,b=path[i],path[i+1];direction=(b-a).normalized();inside=Vector((-direction.y,direction.x))*depth
  points=[a,b,b+inside,a+inside];v=[(p.x,low,p.y) for p in points]+[(p.x,h(p.x,p.y) if high is None else high,p.y) for p in points]
  mesh(name+'_'+str(i),v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
wall_band('SAL_StonePlinth',0,.22,'warm_stone',.30)
wall_band('SAL_WalnutDado',.22,1.10,'warm_walnut',.25)
wall_band('SAL_UpperWall',1.10,None,'ivory_enamel',.22)
# Glazed court-facing gallery, existing portal's clear opening preserved.
mullions=set()
for lo,hi in [(-34,-27),(-27,-21),(-21,-15),(-15,-9),(-9,-2.64),(2.64,4)]:
 prism('SAL_WindowSill_'+str(lo),[(52,lo),(52.32,lo),(52.32,hi),(52,hi)],0,.83,'ivory_enamel')
 if hi-lo>2:
  prism('SAL_Glass_'+str(lo),[(52.08,lo+.14),(52.105,lo+.14),(52.105,hi-.14),(52.08,hi-.14)],.94,min(h(52,lo),h(52,hi))-.18,'glass')
 for z in [lo,hi]:
  z=max(-33.91,min(3.91,z))
  if z in mullions:continue
  mullions.add(z)
  prism('SAL_ProfiledMullion_'+str(z),[(52,z-.09),(52.24,z-.09),(52.31,z),(52.24,z+.09),(52,z+.09)],.8,h(52,z),'champagne_metal')
 prism('SAL_WindowHeader_'+str(lo),[(52,lo),(52.25,lo),(52.25,hi),(52,hi)],min(h(52,lo),h(52,hi))-.18,max(h(52,lo),h(52,hi))+.04,'ivory_enamel')
prism('SAL_PortalTransom',[(52,-2.64),(52.35,-2.64),(52.35,2.64),(52,2.64)],3.56,4.66,'ivory_enamel')
# Ceiling clipped into true plan cells; each cell follows the same sectional rule.
def clean(poly):
 result=[]
 for p in poly:
  if not result or (p-result[-1]).length>1e-6:result.append(p)
 if len(result)>1 and (result[0]-result[-1]).length<1e-6:result.pop()
 return result
def clip(poly,axis,bound,keep_greater):
 out=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];ia=(a[axis]>=bound-1e-7) if keep_greater else (a[axis]<=bound+1e-7);ib=(b[axis]>=bound-1e-7) if keep_greater else (b[axis]<=bound+1e-7)
  if ia:out.append(a)
  if ia!=ib:
   t=(bound-a[axis])/(b[axis]-a[axis]);out.append(a+(b-a)*t)
 return clean(out)
for ix,(x0,x1) in enumerate(zip([52,56,60,68],[56,60,68,76])):
 for iz,(z0,z1) in enumerate(zip([-34,-30,-24,-18,-12,-6,0],[-30,-24,-18,-12,-6,0,4])):
  poly=list(P)
  for axis,bound,greater in [(0,x0,True),(0,x1,False),(1,z0,True),(1,z1,False)]:
   if poly:poly=clip(poly,axis,bound,greater)
  if len(poly)<3:continue
  pieces=[poly]
  if ix==0 and iz==2:
   # Split at the exact crease where the rising ceiling meets the lower gallery plane.
   def plane_value(p):return plan['low_reading_ceiling']+(p.y+24)*(plan['gathering_ceiling']-plan['low_reading_ceiling'])/6-(plan['front_gallery_ceiling']+(p.x-52)*.25)
   pieces=[]
   for sign in [-1,1]:
    piece=[]
    for i,a in enumerate(poly):
     b=poly[(i+1)%len(poly)];va=plane_value(a)*sign;vb=plane_value(b)*sign
     if va>=-1e-7:piece.append(a)
     if (va>=0)!=(vb>=0):piece.append(a+(b-a)*(va/(va-vb)))
    piece=clean(piece)
    if len(piece)>=3:pieces.append(piece)
  for part,poly in enumerate(pieces):
   v=[(p.x,h(p.x,p.y),p.y) for p in poly]+[(p.x,h(p.x,p.y)+.18,p.y) for p in poly];n=len(poly)
   faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
   mesh(f'SAL_SectionalCeiling_{ix}_{iz}_{part}',v,faces,'warm_walnut' if iz in [1,3] and ix>0 else 'ivory_enamel')
# Recessed, downward optical housings coordinated with the ceiling bands.
for i,(x,z) in enumerate([(55,-29),(55,-19),(55,-10),(64,-20),(68,-11),(64,-3)]):
 y=h(x,z);prism('SAL_LightRecess_'+str(i),[(x-.66,z-.25),(x+.66,z-.25),(x+.66,z+.25),(x-.66,z+.25)],y-.12,y,'champagne_metal')
 prism('SAL_LightLens_'+str(i),[(x-.55,z-.18),(x+.55,z-.18),(x+.55,z+.18),(x-.55,z+.18)],y-.14,y-.12,'lens')
 o=bpy.data.objects.new('DATUM_ceiling_light_'+str(i),None);bpy.context.collection.objects.link(o);o.location=(x-AX,-(z-AZ),y-.25)
# A low curved acoustic divider shapes the oblique arrival without sealing a corridor.
q=[Vector((58,-3)),Vector((58.3,-6)),Vector((59.2,-8.5)),Vector((61,-10))]
for i in range(len(q)-1):strip('SAL_ArrivalAcousticFin_'+str(i),q[i],q[i+1],.22,0,1.35,'teal_weave')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-SAL-007.blend';glb=ROOT/'exports/AST-SAL-007.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-SAL-007.manifest.json').write_text(json.dumps({'catalogue_id':'AST-SAL-007','name':'Court-facing conversation salon sectional shell','source':'source/AST-SAL-007.blend','export':'exports/AST-SAL-007.glb','support_files':['source/salon_profile.json'],'triangles':tri,'status':'Draft; requires import, optical, route and visual checks','room_identity':'D09_salon5','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('SALON_SHELL_CREATED',tri)
