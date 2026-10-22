"""Coordinated paired-court native finish successor; original geometry retained."""
import bpy,json,hashlib,math,random
from pathlib import Path
from mathutils import Vector
import numpy as np
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;OLD=G/'night_garden_receiving_courts_20261022';N=R/'BlenderCatalogue/assets/night_garden_court_completion_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(v):return Vector((v[0],-v[2],v[1]))
def god(v):return [v.x,v.z,-v.y]
def bounds(o):
 v=[god(o.matrix_world@Vector(c))for c in o.bound_box];return [[min(x[k]for x in v)for k in range(3)],[max(x[k]for x in v)for k in range(3)]]
def geom(o):return hashlib.sha256(repr(([list(r)for r in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])).encode()).hexdigest()
b=json.loads((OLD/'evidence/BUILD_R003.json').read_text());assert sha(R/b['native'])==b['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(R/b['native']));bpy.context.preferences.filepaths.save_version=0
before={o.name:geom(o)for o in bpy.context.scene.objects if o.type=='MESH'};extras=[]
stone=bpy.data.materials['NGRC_WarmLimestone'];ivory=bpy.data.materials['NGRC_PorcelainStructure'];wood=bpy.data.materials['NGRC_HoneyWalnut'];metal=bpy.data.materials['NGRC_BrushedChampagne'];glow=bpy.data.materials['NGRC_OpalFixture'];soil=bpy.data.materials['NGRC_PlantingBed']
# Keep authored texture detail; tint via a multiply node so the palette is editable.
for m,color in [(stone,(1.30,1.25,1.13,1)),(wood,(1.08,1.04,.97,1))]:
 bs=m.node_tree.nodes.get('Principled BSDF');links=list(bs.inputs['Base Color'].links)
 if links:
  original=links[0].from_socket;m.node_tree.links.remove(links[0]);mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=color;m.node_tree.links.new(original,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])
ivory.diffuse_color=(.86,.77,.61,1);ivory.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=ivory.diffuse_color
leaf=bpy.data.materials.new('NGRC_UnderstorySage');leaf.diffuse_color=(.24,.39,.18,1);leaf.use_nodes=True;leaf.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=leaf.diffuse_color;leaf.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78
leaf2=leaf.copy();leaf2.name='NGRC_UnderstoryDeepJade';leaf2.diffuse_color=(.12,.28,.16,1);leaf2.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=leaf2.diffuse_color
faces_box=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,vertices,faces,material,contact=True):
 data=bpy.data.meshes.new(name);data.from_pydata([xyz(v)for v in vertices],[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(material);o['physical_contact']=contact;extras.append(o);return o
def box(name,lo,hi,m,contact=True):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],faces_box,m,contact)
def strip(name,a,b,low,high,width,m,contact=True):
 a=Vector(a);b=Vector(b);d=b-a;side=Vector((-d.z,0,d.x)).normalized()*width/2
 points=[a-side+Vector((0,low,0)),b-side+Vector((0,low,0)),b+side+Vector((0,low,0)),a+side+Vector((0,low,0)),a-side+Vector((0,high,0)),b-side+Vector((0,high,0)),b+side+Vector((0,high,0)),a+side+Vector((0,high,0))]
 return mesh(name,points,faces_box,m,contact)
# Profile every existing guard segment without removing its tested bar/contact geometry.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not o.name.endswith('_Top'):continue
 coords=np.array([god(o.matrix_world@v.co)for v in o.data.vertices]);center=coords.mean(axis=0);_,_,axes=np.linalg.svd(coords-center,full_matrices=False);axis=axes[0];t=(coords-center)@axis;a=center+axis*t.min();c=center+axis*t.max();a[1]-=1.1;c[1]-=1.1
 strip('Resort_'+o.name+'_Dado',a,c,.10,.57,.055,ivory)
 strip('Resort_'+o.name+'_TimberCap',a,c,1.075,1.145,.078,wood)
 strip('Resort_'+o.name+'_ChampagneReveal',a,c,.57,.60,.062,metal)
# Existing gallery edge support depth and a supported open crown; no new roof/void closure.
lights=[]
for sign,side in [(-1,'Fore'),(1,'Aft')]:
 def block(name,lo,hi,m,contact=True):
  a=[lo[0],lo[1],min(sign*lo[2],sign*hi[2])];c=[hi[0],hi[1],max(sign*lo[2],sign*hi[2])];return box(side+'_'+name,a,c,m,contact)
 for y in [93,97.5]:
  block('ProfiledGalleryFascia_'+str(y),[57.12,y-.37,35],[57.27,y-.08,90.3],ivory)
  block('FasciaTimberReveal_'+str(y),[57.25,y-.24,35],[57.29,y-.15,90.3],wood)
 for x in [55.4,58.7,63.65,68.4]:block('CrownLongitudinal_'+str(x),[x-.10,101.20,37.35],[x+.10,101.45,90.1],wood)
 for z in [42,49.4,56.8,64.2,71.6,79,86.4]:
  block('OpenCrownRib_'+str(z),[55.3,101.1,z-.11],[68.5,101.40,z+.11],ivory)
  block('CrownOpal_'+str(z),[55.65,101.07,z-.08],[58.7,101.1,z+.08],glow,False)
 # Planters project outside the walking lane and outside the inclined walk interval.
 for y in [93,97.5]:
  for z in [42,86]:
   block('BuiltInPlanter_'+str(y)+'_'+str(z),[57.25,y-.12,z-1.45],[58.45,y+.48,z+1.45],stone)
   block('PlanterSoil_'+str(y)+'_'+str(z),[57.36,y+.48,z-1.33],[58.34,y+.50,z+1.33],soil,False)
   for zz in [z-1.2,z+1.2]:block('PlanterBracket_'+str(y)+'_'+str(zz),[56.9,y-.38,zz-.07],[58.35,y-.16,zz+.07],metal)
 def fern(name,center,size,seed):
  rng=random.Random(seed);vertices=[];faces=[]
  for i in range(15):
   angle=i*2.39996+rng.uniform(-.15,.15);length=size*rng.uniform(.65,1.15)
   for j in range(5):
    t0=j/5;t1=(j+1)/5
    def point(t,edge):
     radius=length*t*.72;w=length*.14*math.sin(math.pi*t)*edge
     return [center[0]+math.cos(angle)*radius-math.sin(angle)*w,center[1]+length*(1.15*t-.72*t*t),center[2]+math.sin(angle)*radius+math.cos(angle)*w]
    offset=len(vertices);vertices.extend([point(t0,-1),point(t0,1),point(t1,1),point(t1,-1)]);faces.extend([(offset,offset+1,offset+2),(offset,offset+2,offset+3),(offset+2,offset+1,offset),(offset+3,offset+2,offset)])
  return mesh(name,vertices,faces,leaf if seed%2 else leaf2,False)
 for y in [93,97.5]:
  for z in [42,86]:
   for i in range(7):fern(side+'_PlanterFern_'+str(y)+'_'+str(z)+'_'+str(i),[57.85,y+.50,sign*(z-1.1+i*.366)],.75,1000+int(y*10)+z+i)
 for z in [48,77]:
  for i in range(16):
   angle=i*math.tau/16;fern(side+'_IslandUnderstory_'+str(z)+'_'+str(i),[63.65+2.2*math.cos(angle),84.96,sign*z+2.2*math.sin(angle)],1.15,z*100+i)
 # Suspended three-ring lantern between groves; structurally tied to the portal crown.
 z=sign*60.5
 for ring,(radius,y) in enumerate([(1.35,98.65),(1.8,99.15),(2.25,99.65)]):
  for tag,tube,m in [('Frame',.09,metal),('Opal',.055,glow)]:
   vs=[];fs=[]
   for i in range(64):
    a=i*math.tau/64
    for j in range(8):
     t=j*math.tau/8;rr=radius+tube*math.cos(t);vs.append([63.65+rr*math.cos(a),y+tube*math.sin(t)-(0.04 if tag=='Opal'else 0),z+rr*math.sin(a)])
   for i in range(64):
    for j in range(8):a=i*8+j;c=((i+1)%64)*8+j;fs.append((a,c,((i+1)%64)*8+(j+1)%8,i*8+(j+1)%8))
   mesh(side+'_CrownLantern_'+str(ring)+'_'+tag,vs,fs,m,False)
 for x in [62.7,64.6]:box(side+'_LanternSupport_'+str(x),[x-.025,98.7,z-.025],[x+.025,101.2,z+.025],metal,False)
 lights.append({'name':side+'_CrownLanternSource','position':[63.65,99.3,z],'target':[63.65,89,z],'anchor':[63.65,94,z],'energy':3.2,'range':22,'angle':62})
 for z in [42,64.2,86.4]:lights.append({'name':side+'_CrownGallerySource_'+str(z),'position':[57.2,100.98,sign*z],'target':[57.2,93,sign*z],'anchor':[57.2,97,sign*z],'energy':2.2,'range':16,'angle':58})
# Existing fixtures gain physically tested illuminated receivers; no budget increase.
for row in b['lights']:
 row['anchor']=row['target'][:]
 if '_Grove_'in row['name']:row['anchor'][1]=94;row['energy']=3.1
lights=b['lights']+lights
bpy.context.view_layer.update()
for name,digest in before.items():assert geom(bpy.data.objects[name])==digest,name
records=[{'name':o.name,'bounds':bounds(o),'contact':bool(o.get('physical_contact',False))}for o in extras]
for row in records:
 lo,hi=row['bounds'];assert lo[1]>=83.75 and hi[1]<=101.5,(row['name'],lo,hi)
native=N/'NightGardenResortCourts_r001.blend';out=P/'runtime/NightGardenResortCourts_r001.glb';assert not native.exists() and not out.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Compact runtime drawing by guard side, canopy grove/material and fern planting bed.
for side in ['Fore','Aft']:
 groups={}
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  key=None
  if o.name.startswith(side)and'_Baluster_'in o.name:key=side+'_GuardBalusters'
  elif o.name.startswith(side+'_Canopy_'):key='_'.join(o.name.split('_')[:3])+'_'+o.data.materials[0].name
  elif o.name.startswith(side)and('PlanterFern_'in o.name or 'IslandUnderstory_'in o.name):key='_'.join(o.name.split('_')[:-1])+'_'+o.data.materials[0].name
  if key:groups.setdefault(key,[]).append(o)
 for key,group in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:o.select_set(True)
  bpy.context.view_layer.objects.active=group[0]
  if len(group)>1:bpy.ops.object.join()
  group[0].name=key
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
receipt={'native':str(native.relative_to(R)),'native_sha256':sha(native),'runtime':str(out.relative_to(G)),'runtime_sha256':sha(out),'source_native':b['native'],'source_native_sha256':b['native_sha256'],'original_meshes_geometry_unchanged':len(before),'new_parts':records,'lights':lights,'original_room_ids_changed':0,'capacity_change':0,'protected_slab_cuts':0,'hull_changes':0,'visual_accepted':False}
(P/'evidence/BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESORT_COURTS_AUTHORED',len(before),len(records),len(lights))
