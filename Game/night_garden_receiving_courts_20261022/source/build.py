"""Native architectural finish successor. Original geometry/allocations remain pinned."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; G=P.parent; R=G.parent
OLD=G/'night_garden_panoramic_suites_20261022'
N=R/'BlenderCatalogue/assets/night_garden_receiving_courts_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(p):return Vector((p[0],-p[2],p[1]))
def bounds(o):
 bpy.context.view_layer.update();v=[o.matrix_world@Vector(c)for c in o.bound_box];v=[(p.x,p.z,-p.y)for p in v]
 return [[min(p[k]for p in v)for k in range(3)],[max(p[k]for p in v)for k in range(3)]]
def geometry(o):return hashlib.sha256(repr(([list(r)for r in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])).encode()).hexdigest()
def mat(name,color,rough=.6,metal=0,emission=0,pattern=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
 if pattern:
  image=bpy.data.images.new(name+'_original_pattern',width=128,height=128);pixels=[]
  for y in range(128):
   for x in range(128):
    if pattern=='timber':v=1+.09*math.sin(x*.3+math.sin(y*.05))+.035*math.sin(x*1.7+y*.03)
    elif pattern=='weave':v=1+.025*((x%4<2)-(y%4<2))
    else:v=1+.018*math.sin(x*1.7+y*2.3)
    pixels.extend([min(1,c*v)for c in color]+[1])
  image.pixels=pixels;image.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 return m
def uv(o):
 layer=o.data.uv_layers.active or o.data.uv_layers.new(name='FinishUV')
 for poly in o.data.polygons:
  n=poly.normal;skip=max(range(3),key=lambda k:abs(n[k]));axes=[k for k in range(3)if k!=skip]
  for li in poly.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=(co[axes[0]]*.4,co[axes[1]]*.4)
def box(name,lo,hi,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz([(a+b)/2 for a,b in zip(lo,hi)]));o=bpy.context.object;o.name=name
 o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material);uv(o)
 if bevel:
  modifier=o.modifiers.new('CraftedEdge','BEVEL');modifier.width=bevel;modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
 return o
pre=json.loads((P/'evidence/PREREQUISITES.json').read_text())
for path,digest in pre['source_pins'].items():assert sha(R/path)==digest
native=N/'NightGardenReceivingCourts_r001.blend';out=P/'runtime/NightGardenReceivingCourts_r001.glb'
assert not native.exists() and not out.exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
stone=mat('NGRC_WarmLimestone',(.53,.47,.37),.8,pattern='plaster')
ivory=mat('NGRC_PorcelainStructure',(.78,.73,.62),.67)
wood=mat('NGRC_HoneyWalnut',(.38,.205,.09),.48,pattern='timber')
metal=mat('NGRC_BrushedChampagne',(.55,.39,.19),.33,.65)
soil=mat('NGRC_PlantingBed',(.12,.095,.06),1)
glow=mat('NGRC_OpalFixture',(1,.72,.38),.5,emission=2.2)
parts=[];lights=[]
def add(name,lo,hi,m,contact=True,bevel=.025):
 o=box(name,lo,hi,m,bevel);o['physical_contact']=contact;parts.append(o);return o
def prism(name,vertices,faces,m,contact=True):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([xyz(v)for v in vertices],[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(m);uv(o);o['physical_contact']=contact;parts.append(o);return o
# Exact missing-only foundation: retain the original D13 window terrace.
for i,t in enumerate(pre['base_triangles_xz']):
 v=[[x,83.76,z]for x,z in t]+[[x,84,z]for x,z in t]
 prism('Base_%03d'%i,v,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],stone)
def beam(name,a,b,width,m,contact=True):
 aa,bb=xyz(a),xyz(b);d=bb-aa
 bpy.ops.mesh.primitive_cube_add(size=1,location=(aa+bb)/2);o=bpy.context.object;o.name=name;o.dimensions=(width,width,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);uv(o);o['physical_contact']=contact;parts.append(o);return o
def rail(name,a,b):
 beam(name+'_Top',[a[0],a[1]+1.1,a[2]],[b[0],b[1]+1.1,b[2]],.055,metal)
 beam(name+'_Lower',[a[0],a[1]+.25,a[2]],[b[0],b[1]+.25,b[2]],.04,metal)
 n=max(1,math.ceil(math.dist(a,b)/.14))
 for i in range(n+1):
  t=i/n;c=[a[k]+(b[k]-a[k])*t for k in range(3)];beam(name+'_Baluster_%03d'%i,c,[c[0],c[1]+1.08,c[2]],.022,metal)
# Paired courts with continuous west galleries and a real visible sloping promenade.
for sign,side in [(-1,'Fore'),(1,'Aft')]:
 def point(x,y,z):return [x,y,sign*z]
 def block(tag,x0,y0,z0,x1,y1,z1,m=stone,contact=True):
  zz=sorted([sign*z0,sign*z1]);return add(side+'_'+tag,[x0,y0,zz[0]],[x1,y1,zz[1]],m,contact)
 for level in [93,97.5]:
  block('Gallery_'+str(level),55,level-.24,35,57.2,level,90.3)
  rail(side+'_West_'+str(level),point(55.04,level,35),point(55.04,level,90.3))
  # Garden-side guard except actual promenade/landing interfaces.
  if level==93:
   rail(side+'_GardenLowerA',point(57.16,level,35),point(57.16,level,48))
   rail(side+'_GardenLowerB',point(57.16,level,79),point(57.16,level,90.3))
  else:
   rail(side+'_GardenUpperA',point(57.16,level,35),point(57.16,level,77))
   rail(side+'_GardenUpperB',point(57.16,level,79),point(57.16,level,90.3))
  rail(side+'_End_'+str(level),point(55.04,level,90.25),point(57.16,level,90.25))
 # D15 connects to the existing avenue west edge; no room/screen or atrium guard cut.
 block('D15_ReceivingBridge',57.2,92.76,34.6,81.95,93,36.8)
 rail(side+'_BridgeNear',point(57.2,93,34.64),point(81.90,93,34.64))
 rail(side+'_BridgeFar',point(59.2,93,36.76),point(81.90,93,36.76))
 # Low landing, 1:6 inclined walk, high landing. No hidden ramp over stair geometry.
 block('RampLowerLanding',57.2,92.76,48,59.2,93,50)
 block('RampUpperLanding',57.2,97.26,77,59.2,97.5,79)
 v=[point(x,y,z)for x,y,z in [(57.2,92.76,50),(59.2,92.76,50),(59.2,97.26,77),(57.2,97.26,77),(57.2,93,50),(59.2,93,50),(59.2,97.5,77),(57.2,97.5,77)]]
 prism(side+'_InclinedPromenade',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone)
 for x in [57.24,59.16]:rail(side+'_RampRail_'+str(x),point(x,93,50),point(x,97.5,77))
 rail(side+'_RampLandingLowEdge',point(59.16,93,48),point(59.16,93,50))
 rail(side+'_RampLandingHighEdge',point(59.16,97.5,77),point(59.16,97.5,79))
 # Portal frames terminate at the new/retained base, not in mid-air.
 for z in [35.25,60.5,90.1]:
  for x in [55.35,68.45]:
   block('Pier_'+str(x)+'_'+str(z),x-.16,84,z-.16,x+.16,101.15,z+.16,ivory)
   block('PierFoot_'+str(x)+'_'+str(z),x-.3,84,z-.3,x+.3,84.24,z+.3,stone)
  block('CrownBeam_'+str(z),55.19,100.8,z-.18,68.61,101.2,z+.18,ivory)
  for x,endx in [(55.35,57.35),(68.45,66.45)]:beam(side+'_Knee_'+str(x)+'_'+str(z),point(x,98.4,z),point(endx,100.9,z),.20,ivory)
 # Gallery beams and piers tie each walking surface into the portal rhythm.
 for y in [92.60,97.10]:block('GalleryStringer_'+str(y),55.1,y,35,55.5,y+.16,90.3,wood)
 for z in [48,77]:
  block('RampSupport_'+str(z),58.9,84,z-.14,59.18,93 if z==48 else 97.5,z+.14,ivory)
 for z in [48,77]:
  # Broad island and integrated curved planter/bench surround.
  center=point(63.65,84.45,z)
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=3.0,depth=.9,location=xyz(center));o=bpy.context.object;o.name=side+'_Island_'+str(z);o.data.materials.append(stone);o['physical_contact']=True;parts.append(o)
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=2.72,depth=.08,location=xyz(point(63.65,84.91,z)));o=bpy.context.object;o.name=side+'_Soil_'+str(z);o.data.materials.append(soil);o['physical_contact']=False;parts.append(o)
  # Original native canopy reused as a planted grove, immutable source retained.
  old=set(bpy.data.objects)
  with bpy.data.libraries.load(str(R/'BlenderCatalogue/assets/atrium_canopy/source/AST-BOT-011.blend'),link=False)as(src,dst):dst.objects=src.objects
  imported=[o for o in dst.objects if o is not None and o.type=='MESH']
  for o in imported:
   if o.name not in bpy.context.scene.objects:bpy.context.collection.objects.link(o)
  bb=[bounds(o)for o in imported];lo=[min(b[0][k]for b in bb)for k in range(3)];hi=[max(b[1][k]for b in bb)for k in range(3)]
  scale=[8/(hi[0]-lo[0]),13.4/(hi[1]-lo[1]),8/(hi[2]-lo[2])]
  from mathutils import Matrix
  center0=xyz([(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2]);target=xyz(point(63.65,84.95,z));s=Matrix.Diagonal((scale[0],scale[2],scale[1],1))
  transform=Matrix.Translation(target)@s@Matrix.Translation(-center0)
  for j,o in enumerate(imported):o.matrix_world=transform@o.matrix_world;o.name=side+'_Canopy_'+str(z)+'_'+str(j);o['physical_contact']=False;parts.append(o)
  for offset in [-2.5,2.5]:
   block('GroveLight_'+str(z)+'_'+str(offset),63.47,84.95,z+offset-.10,63.83,85.06,z+offset+.10,metal)
   block('GroveLens_'+str(z)+'_'+str(offset),63.50,85.06,z+offset-.07,63.80,85.075,z+offset+.07,glow,False)
   lights.append({'name':side+'_Grove_'+str(z)+'_'+str(offset),'position':point(63.65,85.15,z+offset),'target':point(63.65,95,z),'energy':2.4,'range':18,'angle':48})
 for z in [42,64,86]:
  block('GalleryLantern_'+str(z),55.55,96.0,z-.2,55.85,96.4,z+.2,metal)
  block('GalleryOpal_'+str(z),55.60,96.04,z-.21,55.8,96.32,z+.21,glow,False)
  lights.append({'name':side+'_Gallery_'+str(z),'position':point(55.72,96,z),'target':point(57,93,z),'energy':1.3,'range':9,'angle':65})
# Editability retained before any runtime batching.
records=[{'name':o.name,'bounds':bounds(o),'contact':bool(o.get('physical_contact',False))}for o in parts]
for rec in records:
 lo,hi=rec['bounds'];assert lo[1]>=83.75 and hi[1]<=101.5,(rec['name'],lo,hi)
 assert lo[0]>=54.99 and hi[0]<=81.96,(rec['name'],lo,hi)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Keep individual architectural interfaces; combine decorative balusters by side for practical draw count.
for side in ['Fore','Aft']:
 group=[o for o in parts if o.name.startswith(side) and '_Baluster_'in o.name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();group[0].name=side+'_GuardBalusters';group[0]['physical_contact']=True
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
receipt={'native':str(native.relative_to(R)),'native_sha256':sha(native),'runtime':str(out.relative_to(G)),'runtime_sha256':sha(out),'objects':records,'lights':lights,'source_pins':pre['source_pins'],'preserved_existing_base_area_m2':pre['existing_base_area_preserved_m2'],'new_ids':0,'capacity_change':0,'protected_slab_cuts':0,'main_integrated':False,'visual_accepted':False,'engineering_accessibility_acceptance':False}
(P/'evidence/BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('RECEIVING_COURTS_AUTHORED',len(records))
