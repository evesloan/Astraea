"""Astraea suite205 connected garden-court SOURCE-ONLY design study.
Global Blender coordinates=(world X,-world Z,world Y). Never writes Game/Catalogue.
Run only on the coordinated source authoring slot, Blender -b -t 2 --python.
"""
import bpy,bmesh,json,math,hashlib,random
from mathutils import Vector,Matrix
from pathlib import Path
OUT=Path(__file__).resolve().parent
CAT=next(q for q in Path(__file__).resolve().parents if (q/'catalogue_manifest.json').is_file())
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
REF=Path('/workspace/shared/astraea-recovery-20261005/DesignArchive/References')
random.seed(205)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.threads_mode='FIXED';scene.render.threads=2
collections={}
for name in ['01_ProposedTransferSupport','02_GardenFloorAndEdges','03_UpperGallery','04_StairAndGuards','05_RoofAndEnclosure','06_Planting','07_ReadingAndSeating','08_VisibleLightFixtures','09_InterfaceDatums']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name[:2]]=c
parts=[];instances=[];contacts=[];lights=[];materials={};templates={};deps={};expected_parts={};template_evidence={}
cat_manifest=json.loads((CAT/'catalogue_manifest.json').read_text())
assets={a['catalogue_id']:a for a in cat_manifest['assets']}
mat_records=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(p):return(p[0],-p[2],p[1])
def world(p):return(p[0],p[2],-p[1])
def mat(role):
 if role in materials:return materials[role]
 m=bpy.data.materials.new('COURT_'+role);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF')
 if role=='lens':
  n.inputs['Base Color'].default_value=(1,.83,.50,1);n.inputs['Emission Color'].default_value=(1,.76,.38,1);n.inputs['Emission Strength'].default_value=2;n.inputs['Roughness'].default_value=.6
 elif role=='glass':
  n.inputs['Base Color'].default_value=(.37,.52,.46,1);n.inputs['Transmission Weight'].default_value=.55;n.inputs['Roughness'].default_value=.18;n.inputs['IOR'].default_value=1.46
 else:
  record=mat_records.get(role,{});n.inputs['Roughness'].default_value=record.get('roughness',.84);n.inputs['Metallic'].default_value=record.get('metallic',0)
  p=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
  if not p.exists(): raise ValueError('Missing material '+str(p))
  deps[str(p)]=sha(p);im=bpy.data.images.load(str(p),check_existing=True);im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.interpolation='Closest';t.extension='REPEAT';m.node_tree.links.new(t.outputs['Color'],n.inputs['Base Color'])
  m['meters_per_tile_uv']=record.get('meters_per_tile_uv',[1,1])
 materials[role]=m;return m

def mesh(name,verts_world,faces,role,group,category='architecture'):
 d=bpy.data.meshes.new(name);d.from_pydata([xyz(p) for p in verts_world],[],faces);d.update()
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(name,d);collections[group].objects.link(o);o.data.materials.append(mat(role));o['source_status']='PROPOSED_SOURCE_ONLY';o['court_category']=category;o['frame']='Blender global (X,-worldZ,worldY)';parts.append(o)
 uv=d.uv_layers.new(name='MetreScaled');scale=mat(role).get('meters_per_tile_uv',[1,1])
 for f in d.polygons:
  n=f.normal;u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def box(name,x0,x1,y0,y1,z0,z1,role,group,category='architecture'):
 vs=[(x,y,z)for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,group,category)

def slab(name,poly,bottom,top,role,group,category='floor'):
 n=len(poly);vs=[(x,y,z)for y in [bottom,top]for x,z in poly]
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 return mesh(name,vs,fs,role,group,category)

def beam(name,a,b,width,depth,role,group,category='support'):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();s=Vector((0,0,1)) if abs(t.z)<.95 else Vector((1,0,0));s=(s-t*s.dot(t)).normalized();u=t.cross(s).normalized()
 vs=[tuple(p+s*w+u*h)for p in [a,b]for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
 return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,group,category)

def ellipse(cx,cz,rx,rz,n=24):return[(cx+rx*math.cos(i*2*math.pi/n),cz+rz*math.sin(i*2*math.pi/n))for i in range(n)]
def rounded(x0,x1,z0,z1,r=.5,n=5):
 pts=[]
 for cx,cz,a in [(x1-r,z1-r,0),(x0+r,z1-r,90),(x0+r,z0+r,180),(x1-r,z0+r,270)]:
  for i in range(n+1):
   angle=math.radians(a+i*90/n);pts.append((cx+r*math.cos(angle),cz+r*math.sin(angle)))
 return pts

def datum(name,p,kind,extra=None):
 o=bpy.data.objects.new(name,None);collections['09'].objects.link(o);o.location=xyz(p);o.empty_display_size=.2;o['kind']=kind;o['world_xyz']=p
 if extra:o['detail']=json.dumps(extra)
 return o

def guard(name,points,floor,height=1.12,group='04',infill=True):
 for i,(a,b) in enumerate(zip(points,points[1:])):
  a=Vector((a[0],floor,a[1]));b=Vector((b[0],floor,b[1]));length=(b-a).length
  beam(name+'_shoe_'+str(i),a+Vector((0,.10,0)),b+Vector((0,.10,0)),.11,.18,'warm_walnut',group,'guard')
  beam(name+'_rail_'+str(i),a+Vector((0,height,0)),b+Vector((0,height,0)),.075,.09,'champagne_metal',group,'guard')
  N=max(1,math.ceil(length/1.2))
  for j in range(N+1):
   p=a.lerp(b,j/N);beam(name+'_post_%s_%s'%(i,j),p+Vector((0,.12,0)),p+Vector((0,height,0)),.06,.06,'champagne_metal',group,'guard')
  if infill:
   for j in range(max(1,math.ceil(length/.12))):
    p=a.lerp(b,(j+.5)/max(1,math.ceil(length/.12)));beam(name+'_picket_%s_%s'%(i,j),p+Vector((0,.20,0)),p+Vector((0,height-.07,0)),.018,.026,'warm_walnut',group,'guard')

def template(aid):
 if aid not in templates:
  a=assets[aid];p=CAT/a['source'];h=sha(p);assert h==a['source_sha256'],(aid,h,a['source_sha256']);deps[str(p)]=h
  with bpy.data.libraries.load(str(p),link=False)as(src,dst):dst.objects=list(src.objects)
  # Library-loaded matrices are not authoritative until all parents/children are linked and evaluated.
  staging=bpy.data.collections.new('TEMPLATE_EVALUATION_'+aid);scene.collection.children.link(staging)
  loaded=[o for o in dst.objects if o]
  for o in loaded:staging.objects.link(o)
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  frozen=[];evidence=[]
  for o in loaded:
   if o.type not in {'MESH','CURVE'}:continue
   local=o.matrix_world.copy();ev=o.evaluated_get(dg);me=ev.to_mesh();source_points=[tuple(local@v.co)for v in me.vertices];ev.to_mesh_clear()
   frozen.append((o,local,source_points));evidence.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'evaluated_source_matrix':[list(r)for r in local],'source_bounds_min_xyz':[min(v[i]for v in source_points)for i in range(3)],'source_bounds_max_xyz':[max(v[i]for v in source_points)for i in range(3)]})
  templates[aid]=frozen;template_evidence[aid]={'source_sha256':h,'parts':evidence,'method':'All source objects linked, dependency graph updated, then evaluated world matrices/vertices frozen before unlinking.'}
  for o in loaded:staging.objects.unlink(o)
  bpy.data.collections.remove(staging)
 return templates[aid]
def asset(aid,name,p,yaw=0,scale=1,group='06',category='plant',purpose=None):
 T=Matrix.Translation(Vector(xyz(p)))@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Diagonal(Vector((scale,scale,scale,1)))
 obs=[]
 for src,local,source_points in template(aid):
  o=src.copy();o.parent=None;collections[group].objects.link(o);o.matrix_world=T@local;o.name=name+'__'+src.name;o['catalogue_id']=aid;o['court_instance']=name;o['court_category']=category;o['source_status']='PROPOSED_SOURCE_ONLY';parts.append(o);obs.append(o)
  points=[world(T@Vector(p))for p in source_points]
  expected_parts[o.name]={'catalogue_id':aid,'source_part':src.name,'expected_world_min_xyz':[min(v[i]for v in points)for i in range(3)],'expected_world_max_xyz':[max(v[i]for v in points)for i in range(3)],'expected_blender_matrix':[list(r)for r in T@local]}
 instances.append({'name':name,'catalogue_id':aid,'source':assets[aid]['source'],'source_sha256':assets[aid]['source_sha256'],'origin_world_xyz':p,'yaw_blender_z_deg':yaw,'uniform_scale':scale,'purpose':purpose,'objects':[o.name for o in obs]})
 return obs

def fixture(name,p,kind='AREA',energy=140,size=2.0,target=None):
 # Lights are real local luminaires for source review, not a new game light budget.
 box(name+'_housing',p[0]-.23,p[0]+.23,p[1]-.10,p[1]+.04,p[2]-.23,p[2]+.23,'champagne_metal','08','light_fixture')
 box(name+'_lens',p[0]-.19,p[0]+.19,p[1]-.115,p[1]-.095,p[2]-.19,p[2]+.19,'lens','08','light_fixture')
 d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=(1,.78,.50)
 if kind=='AREA':d.shape='DISK';d.size=size
 else:d.shadow_soft_size=size
 o=bpy.data.objects.new(name,d);collections['08'].objects.link(o);o.location=xyz((p[0],p[1]-.14,p[2]));target=target or(p[0],84,p[2]);o.rotation_euler=(Vector(xyz(target))-o.location).to_track_quat('-Z','Y').to_euler();lights.append({'name':name,'world_xyz':world(o.location),'watts_source':energy,'type':kind,'target':target})

