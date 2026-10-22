"""Editable full-cap architectural ceiling; no structural slab or void edits."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((P/'evidence/PREREQUISITES.json').read_text())
for path,digest in pre['source_pins'].items():assert sha(G/path)==digest,path
old=json.loads((G/'night_garden_court_completion_20261022/evidence/BUILD_R003.json').read_text())
assert sha(R/old['native'])==old['native_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
names=['NGRC_WarmLimestone','NGRC_PorcelainStructure','NGRC_HoneyWalnut','NGRC_BrushedChampagne','NGRC_OpalFixture']
with bpy.data.libraries.load(str(R/old['native']),link=False)as(a,b):b.materials=list(names)
stone,cream,wood,metal,glow=[bpy.data.materials[n]for n in names]
objects=[];lights=[]
def mesh(name,vs,fs,m):
 data=bpy.data.meshes.new(name);data.from_pydata([(x,-z,y)for x,y,z in vs],[],fs);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(m);o['physical_contact']=True;objects.append(o)
 uv=data.uv_layers.new(name='AtriumFinishUV')
 for face in data.polygons:
  skip=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=skip]
  for li in face.loop_indices:
   co=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]*.35,co[axes[1]]*.35)
 return o
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(n,a,b,m):
 x,y,z=a;X,Y,Z=b
 return mesh(n,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],faces,m)
def arc(n,rx,rz,width,lo,hi,m,start=0,end=math.tau,steps=96):
 vs=[];fs=[]
 for i in range(steps+1):
  a=start+(end-start)*i/steps
  for y in [lo,hi]:
   for d in [-width/2,width/2]:vs.append(((rx+d)*math.cos(a),y,(rz+d)*math.sin(a)))
 for i in range(steps):
  a=i*4;b=a+4
  fs.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 fs.extend([(0,1,3,2),(steps*4,steps*4+2,steps*4+3,steps*4+1)])
 return mesh(n,vs,fs,m)
# Twelve broad ceiling fields are supported by the existing opaque cap, not a new roof.
for ix in range(3):
 for iz in range(4):
  x=-48+ix*32;z=-64+iz*32
  box(f'CapField_{ix}_{iz}',[x,106.17,z],[x+32,106.255,z+32],cream)
# Architectural relief has a quiet central field, nested elliptical coves and deep perimeter bays.
for i,(rx,rz)in enumerate([(16,28),(28,44),(40,57)]):
 arc(f'OvalCoffer_{i}_Body',rx,rz,.64,105.78,106.18,cream)
 arc(f'OvalCoffer_{i}_Walnut',rx,rz,.34,105.72,105.80,wood)
 arc(f'OvalCoffer_{i}_Champagne',rx+.29,rz+.29,.07,105.76,105.86,metal)
 arc(f'OvalCoffer_{i}_Opal',rx-.29,rz-.29,.065,105.785,105.825,glow)
# Radial transition ribs connect the outer oval to perimeter; none becomes a floor/bridge.
for k in range(24):
 a=math.tau*k/24;ca,sa=math.cos(a),math.sin(a);t=min(47.65/max(abs(ca),1e-6),63.65/max(abs(sa),1e-6));a0=Vector((40*ca,0,57*sa));b0=Vector((t*ca,0,t*sa));v=b0-a0
 side=Vector((-v.z,0,v.x)).normalized()*.22
 vs=[]
 for y in [105.90,106.19]:
  for q in [a0-side,b0-side,b0+side,a0+side]:vs.append((q.x,y,q.z))
 mesh(f'PerimeterBayRib_{k:02}',vs,faces,wood)
for s in [-1,1]:
 for x,z,X,Z in [(-47.95,-63.95,47.95,-63.35),(-47.95,63.35,47.95,63.95),(-47.95,-63.35,-47.35,63.35),(47.35,-63.35,47.95,63.35)]:
  if s==1:box('PerimeterCornice_'+str(len(objects)),[x,105.88,z],[X,106.18,Z],wood)
# Fixtures are physically attached to the cap. The existing source budget remains eight.
for side in [-1,1]:
 for z in [-54,-36,-18,0,18,36,54]:
  x=side*46.5;n=f'GalleryWash_{side}_{z}'
  box(n+'_Housing',[x-.32,105.62,z-.54],[x+.32,106.18,z+.54],metal)
  box(n+'_Opal',[x-.26,105.60,z-.45],[x+.26,105.625,z+.45],glow)
  lights.append({'name':n,'position':[x,105.58,z],'target':[side*49.5,102.02,z],'anchor':[x,105.595,z],'energy':3.2,'range':16,'angle':68})
for side in [-1,1]:
 for x in [-36,-18,0,18,36]:
  z=side*62.5;n=f'EndGalleryWash_{side}_{x}'
  box(n+'_Housing',[x-.54,105.62,z-.32],[x+.54,106.18,z+.32],metal)
  box(n+'_Opal',[x-.45,105.60,z-.26],[x+.45,105.625,z+.26],glow)
  lights.append({'name':n,'position':[x,105.58,z],'target':[x,102.02,side*65.5],'anchor':[x,105.595,z],'energy':3.2,'range':16,'angle':68})
bpy.context.view_layer.update();records=[]
for o in objects:
 pts=[o.matrix_world@Vector(v)for v in o.bound_box];pts=[(v.x,v.z,-v.y)for v in pts]
 records.append({'name':o.name,'bounds':[[min(v[k]for v in pts)for k in range(3)],[max(v[k]for v in pts)for k in range(3)]],'material':o.data.materials[0].name})
native=R/'BlenderCatalogue/assets/atrium_ceiling_completion_20261022/AtriumLanternCeiling_r001.blend';out=P/'runtime/AtriumLanternCeiling_r001.glb'
assert not native.exists()and not out.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
receipt={'native':str(native.relative_to(R)),'native_sha256':sha(native),'runtime':str(out.relative_to(G)),'runtime_sha256':sha(out),'source_material_native_sha256':old['native_sha256'],'parts':records,'lights':lights,'cap_area_m2':12288,'new_floor_or_roof':False,'protected_void_changes':0,'room_or_capacity_changes':0,'visual_accepted':False}
(P/'evidence/BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ATRIUM_CEILING_AUTHORED',len(records),len(lights))
