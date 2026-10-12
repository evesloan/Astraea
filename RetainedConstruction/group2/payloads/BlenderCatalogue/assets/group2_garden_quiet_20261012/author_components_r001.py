"""Contained hydroponic equipment and voluntary quiet nook on actual source floors."""
import bpy,bmesh,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
survey=json.loads((P/'evidence/SITE_SURVEY001.json').read_text());assert all(not r['occupied_source_surface_hits'] and abs(r['area_m2']-r['actual_floor_covered_m2'])<1e-6 for r in survey['rows'])
bpy.ops.wm.read_factory_settings(use_empty=True);materials={};metrics=[];objects={};lights=[]
for role,color in [('ivory',(.73,.72,.63,1)),('walnut',(.33,.20,.11,1)),('teal',(.13,.32,.33,1)),('plant',(.18,.38,.20,1)),('metal',(.56,.49,.33,1)),('lens',(1,.89,.64,1))]:
 m=bpy.data.materials.new('G2Q_'+role);m.diffuse_color=color;materials[role]=m
def box(kind,name,x0,x1,h0,h1,z0,z1,role):
 v=[(x,-z,97.5+h)for h in [h0,h1]for z in [z0,z1]for x in [x0,x1]];d=bpy.data.meshes.new('G2Q_'+kind+'_'+name);d.from_pydata(v,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>1e-7;bm.to_mesh(d);bm.free();o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);d.materials.append(materials[role]);objects.setdefault(kind,[]).append(o);metrics.append({'name':o.name,'closed_manifold':True,'positive_volume_m3':vol});return o
def fixture(kind,name,x,z,h):
 box(kind,name+'Mount',x-.04,x+.04,h,h+.15,z-.04,z+.04,'metal');box(kind,name+'Body',x-.4,x+.4,h-.1,h,z-.1,z+.1,'metal');box(kind,name+'Lens',x-.35,x+.35,h-.12,h-.1,z-.07,z+.07,'lens');lights.append({'kind':kind,'source_mesh':'G2Q_'+kind+'_'+name+'Lens','world_xyz':[x,97.5+h-.13,z],'range':4,'energy':.7})
k='family_hydroponics'
for x in [93.4,95.6]:
 for z in [383.15,384.0]:box(k,'RackPost'+str(x)+str(z),x,x+.06,0,2.25,z,z+.06,'metal')
for tier,h in enumerate([.45,1.05,1.65]):
 box(k,'Shelf'+str(tier),93.4,95.66,h-.06,h,383.15,384.06,'metal')
 for j,x in enumerate([93.50,94.58]):
  name='Tray'+str(tier)+'_'+str(j);box(k,name+'Bottom',x,x+.95,h,h+.025,383.25,383.95,'ivory')
  for n,(a,b)in enumerate([(x,x+.03),(x+.92,x+.95)]):box(k,name+'Side'+str(n),a,b,h+.025,h+.15,383.25,383.95,'ivory')
  box(k,name+'Front',x+.03,x+.92,h+.025,h+.15,383.25,383.28,'ivory');box(k,name+'Back',x+.03,x+.92,h+.025,h+.15,383.92,383.95,'ivory')
  box(k,name+'RootMedium',x+.05,x+.90,h+.025,h+.09,383.30,383.90,'walnut')
  for plant in range(3):
   px=x+.12+plant*.29;box(k,name+'Stem'+str(plant),px,px+.025,h+.09,h+.34,383.53,383.56,'plant');box(k,name+'LeafA'+str(plant),px-.06,px+.09,h+.23,h+.25,383.48,383.61,'plant');box(k,name+'LeafB'+str(plant),px-.08,px+.08,h+.30,h+.32,383.50,383.59,'plant')
 box(k,'Supply'+str(tier),93.43,95.58,h+.10,h+.14,383.98,384.03,'metal')
box(k,'ContainedNutrientCabinet',93.4,94.1,0,1.15,384.1,384.75,'walnut');box(k,'ClosedReservoir',93.50,94.0,.08,.8,384.20,384.65,'ivory')
box(k,'ServiceDisplay',93.39,93.4,.55,.95,384.20,384.60,'teal');box(k,'IsolationManifold',93.55,93.95,1.15,1.3,384.20,384.6,'metal')
box(k,'ReturnRiser',95.62,95.67,.15,1.85,383.98,384.03,'metal');box(k,'ContainedReturnHeader',93.65,95.67,.15,.20,384.03,384.08,'metal')
box(k,'LearningPanel',95.2,95.7,0,1.1,384.20,384.70,'walnut');box(k,'LearningPanelFace',95.19,95.2,.55,1.0,384.24,384.66,'teal')
fixture(k,'GrowWorkLight',94.55,383.55,2.4)
k='quiet_meditation'
box(k,'QuietBacking',80,86,0,2.45,-361.5,-361.35,'ivory')
for name,x in [('West',80),('East',85.85)]:box(k,name+'AcousticSide',x,x+.15,0,2.45,-361.35,-358.1,'walnut')
for j,(x,z)in enumerate([(81.1,-360.3),(84.9,-360.3),(81.1,-358.1),(84.9,-358.1)]):
 box(k,'RestSupport'+str(j),x-.52,x+.52,0,.12,z-.58,z+.58,'walnut');box(k,'SoftRest'+str(j),x-.48,x+.48,.12,.20,z-.54,z+.54,'teal')
box(k,'PersonalClosedStore',82.25,83.75,0,.70,-361.20,-360.80,'walnut')
box(k,'QuietSeat',80.45,81.75,0,.42,-357.35,-356.75,'walnut');box(k,'QuietSeatPad',80.45,81.75,.42,.53,-357.35,-356.75,'teal')
box(k,'NeutralFocusShelf',82.3,83.7,1.3,1.42,-361.35,-361.15,'ivory')
fixture(k,'QuietLight',83,-359.0,2.65)
exports=[]
for kind,objs in objects.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];path=ROOT/f'Game/assets/group2_garden_quiet/{kind}_r001.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True);exports.append({'kind':kind,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
native=P/'source/GARDEN_QUIET_r001.blend';native.parent.mkdir(exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
data={'schema':'astraea.group2_garden_quiet_source.v1','parent_checkpoint':'6b9e16b0147572ec7222ba3323de0157971d13b5','rows':survey['rows'],'exports':exports,'lights':lights,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'parent_proposals':{'family_hydroponics':'D16_directory_06','quiet_meditation':'D16_directory_02'},'ame_ids':['AME-176','AME-178','AME-179'],'no_floor_roof_original_props_or_room_ids_changed':True,'new_capacity':0,'operation_claim':'Physical contained growing equipment and voluntary quiet supports only; no crop/food/pressure/nutrient simulation','admission_proposal':'Inclusive voluntary household/garden/quiet use; no species or luxury exclusion, no new gate','service_proposal':'Group3 exact capped isolated nutrient clean/return and custodial joins; no pipe through retained homes or connection claimed','production_adoption':False,'agriculture_body_acoustic_egress_structural_or_final_art_accepted':False}
out=ROOT/'Game/data/group2_garden_quiet/COMPONENTS_r001.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n');(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'original_sources_modified':False},indent=2)+'\n');print('PASS actual-site garden equipment and quiet source nook')
