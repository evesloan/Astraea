"""Original Orchard food-hall architecture shaped around communal dining and serving pavilions."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave','retail_terracotta_enamel','staff_white_paint','staff_floor']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/(('botanical/'if role.startswith('botanical') else 'retail/'if role.startswith('retail') else 'staff/'if role.startswith('staff') else '')+role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def extrusion(name,outline,bottom,top,role):
 n=len(outline);v=[(x,y,z)for z in [bottom,top]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)

def beam(name,points,width,depth,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));side=(side-t*t.dot(side)).normalized();up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p



AID='AST-DIN-008';D=json.loads((ROOT/'source/plan_contract.json').read_text());F=61
assert all(a['catalogue_id']!=AID or a['family']=='orchard_foodhall'for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x-8,-(z+250),y-F)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[(x0-8,-z0-250),(x1-8,-z0-250),(x1-8,-z1-250),(x0-8,-z1-250)],lo-F,hi-F,role)
def wall(name,a,b,lo,hi,width,role):
 ax,az=a;bx,bz=b;dx=bx-ax;dz=bz-az;length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2
 v=[xyz(x+sign*nx,y,z+sign*nz)for sign in [-1,1]for x,y,z in [(ax,lo,az),(bx,lo,bz),(bx,hi,bz),(ax,hi,az)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
def lerp_profile(value,profile):
 for(a,ya),(b,yb)in zip(profile,profile[1:]):
  if a<=value<=b:return ya+(yb-ya)*(value-a)/(b-a)
 return profile[0][1]if value<profile[0][0]else profile[-1][1]
def roof(x,z):return min(lerp_profile(x,D['ceiling_x_profile']),lerp_profile(z,D['ceiling_z_profile']))
# The actual court supplies the north-west glazed wall. Main entrance joins
# existing spine floor; no false window is cut through neighbouring programmes.
ring=D['boundary']
for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
 if max(a[0],b[0])<=8.01 and min(a[0],b[0])<7.99:continue
 if abs(a[0]-24)<.001 and abs(b[0]-24)<.001 and max(a[1],b[1])<=-233:continue
 if abs(a[1]+233)<.001 and abs(b[1]+233)<.001 and max(a[0],b[0])<=24:continue
 staff=min(a[0],b[0])>=49
 wall('ORCH_PerimeterDado_'+str(i),a,b,F,F+.78,.20,'staff_floor'if staff else'warm_walnut')
 wall('ORCH_PerimeterWall_'+str(i),a,b,F+.78,F+7.6,.20,'staff_white_paint'if staff else'ivory_enamel')
for i,tri in enumerate(D['ceiling_triangles']):
 v=[xyz(x,roof(x,z)+dz,z)for dz in [0,.12]for x,z in tri]
 mesh('ORCH_ShapedCeiling_'+str(i),v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'ivory_enamel')
# Broad public portal, integrated with the lower western ceiling.
for z in [-221,-211]:slab('ORCH_EntryReveal_'+str(z),7.9,8.55,z-.15,z+.15,F,F+4.3,'retail_terracotta_enamel')
slab('ORCH_EntryHeader',7.9,8.55,-221,-211,F+3.8,F+4.3,'retail_terracotta_enamel')
# Hidden staff circulation is connected behind the two serving pavilions.
for a,b in [(-245,-215.25),(-212.75,-202.9),(-200.1,-187)]:
 wall('ORCH_StaffBoundary_'+str(a),(49,a),(49,b),F,F+4.5,.16,'ivory_enamel')
for z in [-214,-201.5]:wall('ORCH_StaffHeader_'+str(z),(49,z-1.4),(49,z+1.4),F+2.64,F+4.5,.16,'ivory_enamel')
datum('staff_door',xyz(49,F,-214))
wall('ORCH_BackSpinePublicFace',(42,-232),(42,-203.1),F,F+3.5,.16,'ivory_enamel')
wall('ORCH_BackSpineNorth',(38,-232),(42,-232),F,F+3.5,.16,'staff_white_paint')
wall('ORCH_BackSpineBetweenPavilions',(38,-218),(38,-214),F,F+3.5,.16,'ivory_enamel')
for z in [-203.1,-199.9]:wall('ORCH_ServiceCross_'+str(z),(42 if z==-203.1 else 38,z),(49,z),F,F+3.3,.16,'ivory_enamel')
slab('ORCH_BackSpineCeiling',38,42,-232,-203.1,F+3.5,F+3.62,'staff_white_paint')
slab('ORCH_ServiceCrossCeiling',38,54,-203.1,-199.9,F+3.3,F+3.42,'staff_white_paint')
slab('ORCH_ServiceCeilingTransition',38,42,-203.15,-203.05,F+3.3,F+3.62,'staff_white_paint')
for i,tri in enumerate(D['staff_floor_triangles']):
 v=[xyz(x,F+offset,z)for offset in [.003,.007]for x,z in tri]
 mesh('ORCH_StaffFloorFinish_'+str(i),v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'staff_floor')
# Distinct lower serving pavilions: counter wraps frame their public faces,
# with a real enclosed staff work bay and door on the back-circulation side.
for index,(north,south)in enumerate([(-229,-218),(-214,-203)]):
 center=(north+south)/2
 for label,x0,x1,z0,z1 in [('front',29,30.05,north+.85,south-.85),('north',30.05,37.9,north,north+.95),('south',30.05,37.9,south-.95,south)]:
  slab('ORCH_CounterPlinth_%s_%s'%(index,label),x0+.05,x1-.05,z0+.04,z1-.04,F,F+.80,'warm_walnut')
  slab('ORCH_CounterTop_%s_%s'%(index,label),x0-.045,x1+.045,z0-.04,z1+.04,F+.80,F+.92,'warm_stone')
 # Angled counter ends ease the queue's change in direction, rather than add furniture.
 for z,sign in [(north,1),(south,-1)]:
  outline=[(29,north+.85),(29.8,north),(30.1,north+.95)]if sign==1 else[(29,south-.85),(30.1,south-.95),(29.8,south)]
  extrusion('ORCH_CounterCorner_%s_%s'%(index,sign),[(x-8,-zz-250)for x,zz in outline],0,.92,'warm_stone')
 for a,b in [(north,center-1.25),(center+1.25,south)]:wall('ORCH_PavilionBack_%s_%s'%(index,a),(38,a),(38,b),F,F+3.8,.16,'staff_white_paint')
 wall('ORCH_PavilionDoorHeader_'+str(index),(38,center-1.25),(38,center+1.25),F+2.64,F+3.8,.16,'staff_white_paint')
 datum('pavilion_door_'+str(index),xyz(38,F,center))
 outline=[(28.8,north+1),(29.8,north-.2),(38.2,north-.2),(38.2,south+.2),(29.8,south+.2),(28.8,south-1)]
 extrusion('ORCH_ServeryCanopy_'+str(index),[(x-8,-z-250)for x,z in outline],3.8,3.96,'ivory_enamel')
 for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):wall('ORCH_CanopyEdge_%s_%s'%(index,i),a,b,F+3.70,F+3.96,.10,'warm_walnut')
 for z in [north+1,south-1]:slab('ORCH_CounterBearing_%s_%s'%(index,z),29.30,29.50,z-.10,z+.10,F+.92,F+3.8,'champagne_metal')
 datum('beverage_'+str(index),xyz(29.55,F+.92,center));datum('serviceware_'+str(index),xyz(35.5,F,center+2.7))
 datum('counter_contact_'+str(index),xyz(29.55,F+.92,center))
# Communal dining uses an original repeated rib/canopy construction family.
# The vaults create table-sized rooms within the taller hall and leave main lanes open.
for g in D['candidate_groups']:
 if g['kind']!='communal10':continue
 z=g['z'];idx=g['index']
 slab('ORCH_CommunalFloorInset_'+str(idx),13.6,21.4,z-2.075,z+2.075,F+.003,F+.007,'warm_walnut')
 profile=[(13.8,F+2.9),(14.6,F+3.5),(16,F+3.8),(19,F+3.8),(20.4,F+3.5),(21.2,F+2.9)]
 for side in [-1,1]:
  zz=z+side*1.9
  beam('ORCH_CommunalRib_%s_%s'%(idx,side),[xyz(13.8,F,zz)]+[xyz(x,y,zz)for x,y in profile]+[xyz(21.2,F,zz)],.22,.24,'warm_walnut')
 n=len(profile);v=[xyz(x,y+offset,zz)for zz in [z-1.9,z+1.9]for offset in [0,.10]for x,y in profile];f=[]
 for i in range(n-1):f.extend([(i,i+1,2*n+i+1,2*n+i),(n+i,3*n+i,3*n+i+1,n+i+1),(i,n+i,n+i+1,i+1),(2*n+i,2*n+i+1,3*n+i+1,3*n+i)])
 f.extend([(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]);mesh('ORCH_AcousticVault_'+str(idx),v,f,'oatmeal_weave')
# Actual sources hang from their intended canopy/roof and illuminate usable places.
fixtures=[('arrival_'+str(i),8.23,F+3.8,z,True)for i,z in enumerate([-219,-216,-213])]
for g in D['candidate_groups']:
 x,z=g['x'],g['z'];top=F+3.8 if g['kind']=='communal10'else roof(x,z)
 y=top if g['kind']=='communal10'else min(top,F+3.5)
 if y<top:slab('ORCH_PendantTie_'+str(g['index']),x-.02,x+.02,z-.02,z+.02,y,top,'champagne_metal')
 fixtures.append(('table_'+str(g['index']),x,y,z,True))
for i,z in enumerate([-223.5,-208.5]):fixtures.append(('serving_'+str(i),31,F+3.8,z,True));fixtures.append(('work_'+str(i),36,F+3.8,z,False))
for i,z in enumerate([-228,-214,-201.5]):fixtures.append(('staff_'+str(i),40,F+(3.3 if i==2 else 3.5),z,False))
for key,x,top,z,warm in fixtures:
 slab('ORCH_FixtureCase_'+key,x-.30,x+.30,z-.24,z+.24,top-.14,top,'champagne_metal')
 slab('ORCH_FixtureLens_'+key,x-.25,x+.25,z-.19,z+.19,top-.155,top-.14,'lens')
 datum('light_'+key,xyz(x,top-.18,z))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Orchard food hall serving pavilions, communal vaults and staff circulation','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original programme-shaped architecture; runtime access, capacity and art review pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
