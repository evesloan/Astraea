"""Astraea suite205 connected garden-court SOURCE-ONLY design study.
Global Blender coordinates=(world X,-world Z,world Y). Never writes Game/Catalogue.
Run only on the coordinated source authoring slot, Blender -b -t 2 --python.
"""
import bpy,bmesh,json,math,hashlib,random,os,sys,argparse
from mathutils import Vector,Matrix
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=Path(args.output_dir).resolve();assert not OUT.exists(),'Fresh output directory required';OUT.mkdir(parents=True)
CAT=Path(os.environ['ASTRAEA_CATALOGUE_ROOT']).resolve() if os.environ.get('ASTRAEA_CATALOGUE_ROOT') else next(p for p in Path(__file__).resolve().parents if (p/'catalogue_manifest.json').is_file())
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

# 1. Genuine lower court platform and accessible end link, never an inferred old floor.
base_poly=rounded(8.20,28.96,-332.90,-308.10,.65,4)
slab('GARDEN_ProposedBase',base_poly,83.72,84.0,'warm_stone','02')
slab('LOWER_EndCrosslink',[(4,-333),(8.7,-333),(8.7,-330),(4,-330)],83.76,84.0,'warm_stone','02')
# Under-garden triangulated transfer frames: all proposed. No anchor capacity claim.
for i,z in enumerate([-331.5,-325.1,-316.6,-309.5]):
 box('SUP_D12_receiver_'+str(i),3.70,4.28,78,78.22,z-.38,z+.38,'champagne_metal','01','receiver')
 box('SUP_D13_edge_collar_'+str(i),4.0,4.30,83.76,84.0,z-.38,z+.38,'champagne_metal','01','receiver')
 box('SUP_D13_under_shoe_'+str(i),3.70,4.30,83.53,83.76,z-.38,z+.38,'champagne_metal','01','receiver')
 beam('SUP_transfer_upper_'+str(i),(4.08,83.48,z),(28.72,83.48,z),.45,.48,'ivory_enamel','01')
 beam('SUP_diagonal_lower_'+str(i),(4.14,78.25,z),(28.72,83.48,z),.38,.38,'warm_walnut','01')
 beam('SUP_spine_mast_'+str(i),(4.14,78.2,z),(4.14,83.55,z),.30,.30,'warm_walnut','01')
 for j,x in enumerate([8.4,14.0,20.0]):
  lo=78.25+(x-4.14)/(28.72-4.14)*(83.48-78.25)
  beam('SUP_web_%s_%s'%(i,j),(x,lo,z),(x,83.48,z),.22,.22,'champagne_metal','01')
 contacts.extend([{'a':'SUP_D12_receiver_'+str(i),'b_existing':'D12_fore_route','contact':'top face','point_world_xyz':[3.85,78,z],'capacity':'UNRESOLVED: actual spine slab load and fastening design require structural review'}, {'a':'SUP_D13_under_shoe_'+str(i),'b_existing':'D13_fore_route','contact':'underside face','point_world_xyz':[3.85,83.76,z],'capacity':'UNRESOLVED: source geometric face contact only'}, {'a':'SUP_transfer_upper_'+str(i),'b':'GARDEN_ProposedBase','contact':'top beam to underside slab','point_world_xyz':[18,83.72,z]}])
for x in [8.45,14.1,21.6,28.70]:
 beam('SUP_longitudinal_'+str(x),(x,83.56,-332.25),(x,83.56,-308.75),.26,.32,'ivory_enamel','01')
# Separate planter curbs and sculpted, room-sized destinations.
beds=[('CentralCanopy',ellipse(19,-323.7,3.65,2.9),84.32),('ArrivalFern',rounded(14.8,19.4,-330.6,-327.5,.7),84.34),('EastQuietPlanting',rounded(26.05,28.88,-331.6,-309.4,.6),84.34),('SouthCanopy',ellipse(21.0,-311.6,3.45,2.10),84.34)]
for name,poly,soil in beds:
 slab('BED_'+name,poly,84.0,soil+.08,'ivory_enamel','02','planter')
 cx=sum(p[0]for p in poly)/len(poly);cz=sum(p[1]for p in poly)/len(poly);inner=[(cx+(x-cx)*.945,cz+(z-cz)*.965)for x,z in poly]
 slab('SOIL_'+name,inner,soil-.05,soil,'botanical_soil','02','soil')
# A lower shared sitting crescent overlooks the principal planted island.
slab('LOWER_ReadingPocket',rounded(11.1,15.8,-325.5,-318.0,1.35),84,84.025,'warm_walnut','02')
# Full boundary closures stop a void backdrop, but stay away from all guest allocations.
box('ENC_LowerPrivateBack',28.84,28.98,84,88.38,-332.1,-308.9,'ivory_enamel','05')
box('ENC_WindowAboveHeader',28.84,28.98,92.42,92.62,-332.1,-308.9,'ivory_enamel','05')
box('ENC_BackGalleryWall',8.20,8.38,84,92.62,-330.0,-308.75,'ivory_enamel','05')
for z in [-332.86,-308.24]:
 box('ENC_EndWall_'+str(z),8.65,28.70,84,92.62,z-.08,z+.08,'ivory_enamel','05')
 # Timber field panels give end walls a deliberate scale; no borrowed view image.
 for x in [11.5,16,20.5,25]:box('ENC_EndPanel_%s_%s'%(z,x),x-1.5,x+1.5,85.05,90.8,z-.095,z+.095,'warm_walnut','05')
# 2. Upper gallery with shaped stopping pockets and free circulation on spine side.
gallery=[(8.2,-333),(12.2,-333),(12.2,-327.6),(13.6,-327.0),(14.1,-326.2),(14.1,-320.7),(13.6,-320.0),(12.2,-319.5),(12.2,-314.2),(13.5,-313.7),(14.1,-312.9),(14.1,-309.2),(13.5,-308.1),(8.2,-308.1)]
slab('GALLERY_UpperDeck',gallery,88.18,88.50,'warm_stone','03')
slab('UPPER_EndCrosslink',[(4,-333),(8.7,-333),(8.7,-330),(4,-330)],88.26,88.5,'warm_stone','03')
for i,z in enumerate([-331.5,-325.1,-316.6,-309.5]):
 for x in [8.6,11.85]:
  zz=-330.0 if i==0 and x==8.6 else z
  box('GAL_column_%s_%s'%(i,x),x-.17,x+.17,84,91.97,zz-.17,zz+.17,'warm_walnut','03','column')
  box('GAL_column_base_%s_%s'%(i,x),x-.26,x+.26,84,84.25,zz-.26,zz+.26,'ivory_enamel','03','column')
 beam('GAL_upper_crossbeam_'+str(i),(8.42,87.98,z),(14.07 if i in [1,3] else 12.2,87.98,z),.33,.4,'ivory_enamel','03')
 contacts.append({'a':'GAL_upper_crossbeam_'+str(i),'b':'GALLERY_UpperDeck','point_world_xyz':[10.5,88.18,z],'contact':'beam top to deck underside'})
# The displaced arrival column retains real local transfer contacts at both levels.
beam('GAL_ArrivalFloorTransfer',(8.6,87.98,-331.5),(8.6,87.98,-330.0),.30,.40,'warm_walnut','03')
beam('GAL_ArrivalRoofTransfer',(8.6,91.88,-331.5),(8.6,91.88,-330.0),.30,.32,'warm_walnut','05')
# Rounded solid coping and spaced vertical balusters maintain a readable edge.
guard('GAL_MainGardenEdge',[(12.2,-332.94)]+gallery[2:9],88.5)
guard('GAL_SouthGardenEdge',gallery[9:14],88.5)
guard('GAL_EndSouth',[(14.1,-308.15),(8.30,-308.15)],88.5)
guard('GAL_EndNorth',[(8.65,-332.93),(12.15,-332.93)],88.5)
guard('GAL_StairNorthReturn',[(12.2,-319.5),(12.2,-316.4)],88.5)
guard('GAL_StairSouthReturn',[(12.2,-314.6),(12.2,-314.2)],88.5)
for z in [-332.78,-330.22]:
 beam('LINK_D14_bearing_'+str(z),(3.75,88.04,z),(8.62,88.04,z),.28,.44,'warm_walnut','01')
 contacts.append({'a':'LINK_D14_bearing_'+str(z),'b_existing':'D14_fore_route','point_world_xyz':[3.85,88.26,z],'contact':'beam top to existing spine underside','capacity':'UNRESOLVED receiver capacity; source contact only'})
for y,label in [(84,'LOWER'),(88.5,'UPPER')]:
 guard(label+'_LinkNorth',[(4.05,-332.93),(8.65,-332.93)],y)
 guard(label+'_LinkSouth',[(4.05,-330.07),(8.20,-330.07)],y)
# 3. Two bounded straight flights make the relationship legible from suite205.
z0,z1=-316.4,-314.6;run=4.16;rise=2.25;N=13
for i,(start,top)in enumerate([(12.7,88.5),(18.66,86.25)]):
 for j in range(N):
  x0=start+j*run/N;x1=start+(j+1)*run/N;ytop=top-(j+1)*rise/N
  box('STAIR_%s_tread_%02d'%(i,j),x0,x1,ytop-.18,ytop,z0,z1,'warm_stone','04','stair_tread')
  # Riser bridges the exact previous top to this tread; no open unbounded fall.
  box('STAIR_%s_riser_%02d'%(i,j),x0,x0+.035,ytop,ytop+rise/N,z0,z1,'ivory_enamel','04','stair_riser')
  box('STAIR_%s_nosing_%02d'%(i,j),x0,x0+.045,ytop,ytop+.007,z0+.07,z1-.07,'champagne_metal','04','stair_nosing')
 for z in [z0+.07,z1-.07]:
  beam('STAIR_stringer_%s_%s'%(i,z),(start,top-.22,z),(start+run,top-rise-.22,z),.15,.27,'warm_walnut','04')
  beam('STAIR_handrail_%s_%s'%(i,z),(start,top+1.08,z),(start+run,top-rise+1.08,z),.07,.07,'champagne_metal','04','guard')
  for j in range(N+1):
   x=start+j*run/N;y=top-j*rise/N
   beam('STAIR_post_%s_%s_%s'%(i,z,j),(x,y-.07,z),(x,y+1.08,z),.04,.04,'warm_walnut','04','guard')
   if j<N:
    # Closely spaced secondary pickets bound the sides of both flights.
    for k in [1,2]:
     xx=x+k*run/N/3;yy=y-k*rise/N/3
     beam('STAIR_picket_%s_%s_%s_%s'%(i,z,j,k),(xx,yy-.06,z),(xx,yy+1.03,z),.017,.022,'warm_walnut','04','guard')
slab('STAIR_TopLanding',[(12.05,z0),(12.7,z0),(12.7,z1),(12.05,z1)],88.2,88.5,'warm_stone','04')
slab('STAIR_MiddleLanding',[(16.86,z0),(18.66,z0),(18.66,z1),(16.86,z1)],85.98,86.25,'warm_stone','04')
slab('STAIR_BottomLanding',[(22.82,z0),(25.45,z0),(25.45,z1),(22.82,z1)],83.80,84,'warm_stone','04')
for z in [z0+.07,z1-.07]:
 guard('STAIR_MidEdge_'+str(z),[(16.86,z),(18.66,z)],86.25)
 guard('STAIR_TopEdge_'+str(z),[(12.15,z),(12.7,z)],88.5)
for x in [16.99,18.52]:
 for z in [z0+.16,z1-.16]:box('STAIR_MidLandingPier_%s_%s'%(x,z),x-.10,x+.10,84,85.98,z-.10,z+.10,'champagne_metal','04','support')
# 4. Authored opaque garden ceiling: this is an internal outlook, no star panels.
roof_poly=rounded(8.2,28.98,-332.90,-308.10,.65,4)
slab('ROOF_OpaqueGardenCap',roof_poly,92.42,92.70,'ivory_enamel','05','roof')
for i,z in enumerate([-331.5,-325.1,-316.6,-309.5]):
 # Near-suite posts align with bay breaks, not the center of the window.
 box('ROOF_EastPier_'+str(i),28.46,28.78,84,92.04,z-.15,z+.15,'warm_walnut','05','column')
 beam('ROOF_TransferRib_'+str(i),(8.4,92.13,z),(28.74,92.13,z),.32,.58,'warm_walnut','05')
 contacts.append({'a':'ROOF_TransferRib_'+str(i),'b':'ROOF_OpaqueGardenCap','point_world_xyz':[18,92.42,z],'contact':'top beam to cap underside'})
# Staggered lower gallery canopy and integrated light/coffer edges.
for i,(za,zb)in enumerate([(-332.6,-327.6),(-327.25,-319.2),(-314.1,-308.5)]):
 slab('GAL_ShapedCanopy_'+str(i),rounded(8.40,14.25 if i!=0 else 12.65,za,zb,.52),91.88,92.08,'warm_walnut','05','roof')
 slab('GAL_AcousticSoffit_'+str(i),rounded(8.55,14.0 if i!=0 else 12.4,za+.15,zb-.15,.40),91.84,91.88,'oatmeal_weave','05','roof')
# Recessed larger opal cassettes, actual interior fixtures, not skylight claims.
for i,z in enumerate([-329.0,-321.0,-312.4]):
 box('ROOF_LightCassette_'+str(i),16.0,22.5,92.32,92.42,z-1.25,z+1.25,'champagne_metal','08','light_fixture')
 box('ROOF_OpalCeilingPanel_'+str(i),16.18,22.32,92.295,92.32,z-1.10,z+1.10,'lens','08','light_fixture')
 # Matching downward area light just beneath the visible diffuser.
 d=bpy.data.lights.new('CourtOpal_'+str(i),'AREA');d.energy=1100;d.shape='RECTANGLE';d.size=6;d.size_y=2;d.color=(1,.86,.66)
 o=bpy.data.objects.new('CourtOpal_'+str(i),d);collections['08'].objects.link(o);o.location=xyz((19.25,92.26,z));lights.append({'name':o.name,'world_xyz':[19.25,92.26,z],'watts_source':1100,'type':'AREA'})
for i,z in enumerate([-331,-325.5,-321,-310.8]):fixture('GalleryDownlight_'+str(i),(10.9,91.80,z),energy=170,size=1.6,target=(11,88.5,z))
for i,p in enumerate([(13.0,87.7,-323.0),(24.3,87.4,-326.8),(23.9,87.4,-310.8)]):
 box('GardenLantern_Mast_'+str(i),p[0]-.045,p[0]+.045,84,p[1]-.10,p[2]-.045,p[2]+.045,'warm_walnut','08','light_fixture')
 box('GardenLantern_Foot_'+str(i),p[0]-.13,p[0]+.13,84,84.11,p[2]-.13,p[2]+.13,'champagne_metal','08','light_fixture')
 fixture('GardenLantern_'+str(i),p,kind='POINT',energy=95,size=.20)
# 5. Useful reading/social clusters, with the main passing lane kept west.
for i,(x,z,yaw)in enumerate([(12.0,-325.2,70),(12.0,-322.7,110),(12.15,-311.9,70),(12.15,-310.0,110)]):
 asset('AST-FUR-002','UpperReadingChair_'+str(i),(x,88.5,z),yaw,group='07',category='furniture',purpose='Faces planted canopy and lower garden, outside the continuous circulation lane')
for i,z in enumerate([-323.95,-310.95]):
 asset('AST-FUR-003','UpperSharedTable_'+str(i),(13.1,88.5,z),90,group='07',category='furniture')
 asset('AST-LIB-007','UpperOpenFolio_'+str(i),(13.1,89.165,z),0,.8,group='07',category='prop')
# Built-in low book banks and small shelves define the inhabited far edge.
for i,z in enumerate([-324.8,-322.4,-311.1]):
 box('BOOKCASE_Back_'+str(i),8.40,8.48,88.68,90.85,z-.85,z+.85,'warm_walnut','07','furniture')
 for side in [-1,1]:box('BOOKCASE_Jamb_%s_%s'%(i,side),8.40,8.76,88.5,90.85,z+side*.82-.04,z+side*.82+.04,'warm_walnut','07','furniture')
 for j,y in enumerate([88.66,89.18,89.7,90.22,90.78]):
  box('BOOKCASE_Shelf_%s_%s'%(i,j),8.40,8.76,y-.045,y,z-.8,z+.8,'warm_walnut','07','furniture')
  if j<4:
   for k,dz in enumerate([-.48,.34]):asset('AST-LIB-006','Books_%s_%s_%s'%(i,j,k),(8.59,y,z+dz),90,.7,group='07',category='prop')
# Lower seats face the tree/waterless planted heart rather than a blank wall.
for i,(x,z,yaw)in enumerate([(13.0,-324.0,70),(13.0,-320.7,110),(22.6,-328.6,-30),(24.0,-312.6,-90)]):asset('AST-FUR-002','LowerGardenChair_'+str(i),(x,84.025 if x==13 else 84,z),yaw,group='07',category='furniture')
for i,(x,z)in enumerate([(14.1,-322.3),(23.6,-327.6),(23.8,-311.3)]):asset('AST-FUR-003','LowerGardenTable_'+str(i),(x,84.025 if x<16 else 84,z),0,group='07',category='furniture')
asset('AST-FUR-001','GardenSouthBench',(18.4,84,-308.85),180,group='07',category='furniture',purpose='Faces the quieter south canopy island')
# Three independent scale layers, existing authored catalogue foliage only.
for i,(x,z,s,rot)in enumerate([(19,-324.0,.385,20),(20.9,-311.7,.31,145),(17.0,-329.0,.255,280)]):asset('AST-BOT-011','CanopySpecimen_'+str(i),(x,84.34,z),rot,s)
for i,(x,z,s)in enumerate([(27.3,-330.2,.9),(27.55,-325.5,1.03),(27.30,-320.7,1.12),(27.5,-315.5,.92),(27.45,-310.8,.90)]):asset('AST-BOT-001','QuietStripTree_'+str(i),(x,84.34,z),i*67,s)
# Generate point clusters within actual bed interiors, never across walking paths.
plant_points=[]
for name,poly,soil in beds:
 if name=='CentralCanopy':
  for k in range(25):
   a=random.random()*math.tau;r=math.sqrt(random.random());plant_points.append((19+3.10*r*math.cos(a),soil,-323.7+2.40*r*math.sin(a),name))
 elif name=='ArrivalFern':
  for k in range(14):plant_points.append((random.uniform(15.2,19.0),soil,random.uniform(-330.15,-327.95),name))
 elif name=='EastQuietPlanting':
  for k in range(40):plant_points.append((random.uniform(26.48,28.28),soil,random.uniform(-331.1,-310.0),name))
 else:
  for k in range(22):
   a=random.random()*math.tau;r=math.sqrt(random.random());plant_points.append((21+2.9*r*math.cos(a),soil,-311.6+1.65*r*math.sin(a),name))
for i,(x,y,z,bed)in enumerate(plant_points):
 aid=['AST-BOT-002','AST-BOT-003','AST-BOT-003','AST-BOT-009'][i%4]
 asset(aid,'Understory_%03d'%i,(x,y,z),random.random()*360,random.uniform(.82,1.18),purpose='Rooted in '+bed)
# Raised upper-garden planting stops at pocket ends; middle view remains open.
for i,z in enumerate([-326.65,-320.1,-313.4,-309.0]):
 box('GAL_Planter_'+str(i),12.35,13.65,88.5,88.98,z-.30,z+.30,'ivory_enamel','03','planter')
 box('GAL_Soil_'+str(i),12.43,13.57,88.90,88.93,z-.22,z+.22,'botanical_soil','03','soil')
 for j,x in enumerate([12.65,13.2]):asset('AST-BOT-008','GalleryTrailing_%s_%s'%(i,j),(x,88.93,z),90,.72)
# Intent markers stay as empties and are not invented people/extra passenger slots.
for i,p in enumerate([(12,88.97,-325.2),(12,88.97,-322.7),(13,84.5,-324)]):datum('POSE_ReadingUse_'+str(i),p,'use pose proposal, no guest identity')
for name,p in [('D14_spine_arrival',[4,88.5,-331.5]),('D13_spine_arrival',[4,84,-331.5]),('Suite205_real_window_target',[29.17,89.7,-320.6]),('LowerGardenDestination',[22.8,84,-319.2])]:datum('IFACE_'+name,p,'source connection/target')

# Dependencies and accountable source evidence.
bpy.context.view_layer.update()
records=[];overall=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in parts:
 ev=o.evaluated_get(dg);me=ev.to_mesh();pts=[world(ev.matrix_world@v.co)for v in me.vertices];tris=sum(len(f.vertices)-2 for f in me.polygons);ev.to_mesh_clear()
 if not pts:continue
 lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)];overall.extend([lo,hi])
 records.append({'name':o.name,'source_object_type':o.type,'category':o.get('court_category'),'catalogue_id':o.get('catalogue_id'),'instance':o.get('court_instance'),'bounds_world_min_xyz':lo,'bounds_world_max_xyz':hi,'evaluated_triangles':tris,'matrix_world_blender':[list(r)for r in o.matrix_world]})
assert max(p[1]for p in overall)<93,'D15 intrusion';assert min(p[1]for p in overall)>=77.99,'Below permitted D12 support plane';assert max(p[0]for p in overall)<29.05,'Guest allocation intrusion'
# Independently compare placed geometry to frozen evaluated source-asset geometry, not to our own GLB alone.
placement_audit=[]
for r in records:
 if r['name']not in expected_parts:continue
 e=expected_parts[r['name']];delta=max(abs(a-b)for a,b in zip(r['bounds_world_min_xyz']+r['bounds_world_max_xyz'],e['expected_world_min_xyz']+e['expected_world_max_xyz']))
 matrix_delta=max(abs(a-b)for rr,ee in zip(r['matrix_world_blender'],e['expected_blender_matrix'])for a,b in zip(rr,ee))
 placement_audit.append({'name':r['name'],'catalogue_id':e['catalogue_id'],'source_part':e['source_part'],'bounds_error_m':delta,'matrix_error':matrix_delta,'pass':delta<.0002 and matrix_delta<.0001})
assert all(r['pass']for r in placement_audit),'Retained asset transform failed'
for aid,e in template_evidence.items():
 lo=[min(p['source_bounds_min_xyz'][i]for p in e['parts'])for i in range(3)];hi=[max(p['source_bounds_max_xyz'][i]for p in e['parts'])for i in range(3)];dims=[hi[i]-lo[i]for i in range(3)];reference=assets[aid].get('dimensions_blender_xyz_m')
 e['evaluated_source_bounds']=[lo,hi];e['source_dimensions']=dims;e['catalogue_dimensions']=reference
 if reference:
  e['catalogue_dimension_error_m']=max(abs(a-b)for a,b in zip(dims,reference));assert e['catalogue_dimension_error_m']<.0002,(aid,'retained catalogue dimension mismatch',dims,reference)
 if aid in ['AST-FUR-001','AST-FUR-002','AST-FUR-003']:
  e['floor_pivot_error_m']=abs(lo[2]);assert abs(lo[2])<.0002,(aid,'source feet do not meet soil/floor datum')
(OUT/'RETAINED_ASSET_PLACEMENT_CHECKS.json').write_text(json.dumps({'method':'Compare every placed mesh/curve to evaluated retained-source vertices after link all -> update -> freeze source matrices, including nonzero local offsets and parent roots.','source_assets':template_evidence,'placed_part_checks':placement_audit,'pass':all(r['pass']for r in placement_audit)},indent=2)+'\n')
# Pack all materials and preserve independent named editable parts.
bpy.ops.file.pack_all();scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.06,.07,.075,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.20
scene['status']='Source-only connected three-bay garden-court; not installed, not structurally certified'
scene['units']='metres';scene['world_coordinate_contract']='Blender(X,-worldZ,worldY); GLB Y-up yields actual Godot world axes'
scene['stable_suite']='AST-UNIT-D14-fbfbe316e3a58c68';scene['no_adoption']='No Game/Catalogue source, import, runtime or identity writes'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source.blend'))
# Export selected meshes and fixtures only; unused source template objects are not linked.
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:o.select_set(o.type in {'MESH','CURVE','EMPTY','LIGHT'})
bpy.ops.export_scene.gltf(filepath=str(OUT/'source.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=True,export_apply=True)
(OUT/'PARTS.json').write_text(json.dumps({'frame':'world xyz, metres; Blender transform rows also provided','objects':records,'bounds_world_min_xyz':[min(p[i]for p in overall)for i in range(3)],'bounds_world_max_xyz':[max(p[i]for p in overall)for i in range(3)],'evaluated_triangles':sum(r['evaluated_triangles']for r in records)},indent=2)+'\n')
(OUT/'ASSET_TRANSFORMS.json').write_text(json.dumps({'source_assets_unchanged':True,'instances':instances,'dependencies':deps},indent=2)+'\n')
(OUT/'CONTACTS.json').write_text(json.dumps({'status':'Proposed geometric contacts only, not structural capacity certification','existing_receiver_owners':['D12_fore_route','D13_fore_route','D14_fore_route'],'contacts':contacts,'unresolved':['Existing spine slab resistance, anchorage, stiffness, loading and fire/MEP coordination require engineering resolution before adoption.','No hidden supporting garden floor or certified 25m cantilever is claimed.','The receiving structure is explicitly the actual compiled spine geometry. New trusses are source proposals.']},indent=2)+'\n')
(OUT/'LIGHTS.json').write_text(json.dumps({'status':'Source-review local fixtures; runtime light budgeting and motion not evaluated','lights':lights},indent=2)+'\n')
(OUT/'ROUTES.json').write_text(json.dumps({'status':'Source geometry routes; no runtime traversal or species/cart certification','routes':[{'id':'upper_spine_to_gallery','points_world_xyz':[[3.8,88.5,-331.5],[7.0,88.5,-331.5],[9.65,88.5,-331.5],[9.65,88.5,-310]],'design_minimum_clear_width_m':1.75,'destination':'Reading gallery and real lower garden outlook'},{'id':'lower_spine_to_garden','points_world_xyz':[[3.8,84,-331.5],[7,84,-331.5],[10.0,84,-331.5],[10.0,84,-318.7],[23.8,84,-318.7],[23.8,84,-314.7]],'design_minimum_clear_width_m':1.7,'destination':'Lower planted garden and stair landing'},{'id':'court_stair','width_m':1.8,'risers':26,'riser_height_m':2.25/13,'tread_depth_m':4.16/13,'intermediate_landing_depth_m':1.8,'points_world_xyz':[[12.7,88.5,-315.5],[16.86,86.25,-315.5],[18.66,86.25,-315.5],[22.82,84,-315.5]]}],'private_strip_x':[26,29.05],'accessible_lower_route':'D13 spine crosslink is level. D14 gallery has its own level crosslink. No new local accessible lift or complete tested interdeck access is claimed.','core_sidewalls':'Unchanged and closed; neither crosslink intersects a core span.'},indent=2)+'\n')
print('COURT_SOURCE_READY',len(records),'parts',sum(r['evaluated_triangles']for r in records),'triangles')
