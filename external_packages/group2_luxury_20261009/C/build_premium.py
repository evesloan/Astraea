"""Three-branch Premium household composition in exact irregular reservations.
Source-only, no preview slab, exterior opening, registry or controller adoption.
Run only through heavy.py. Retained furniture is rigid; fitted shapes follow
the actual allocation profile and every saved/exported vertex is checked.
"""
import bpy,bmesh,pathlib,json,hashlib,math,sys,runpy
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from premium_frame import PremiumFrame
from source_paths import section
from editable_label import repair_label
unit=int(sys.argv[sys.argv.index('--')+1]);target_row,target_o,_,_=section(unit)
assert target_row['reservation']['tier']=='premium' and target_row['identity']['existing_partial_construction'] is None
assert not (target_o/f'{unit}_premium.blend').exists(),'Preserve existing source candidate'
# Use the already inspected pinned importer/palette/primitives without executing
# its876 architecture, views or output writes. __file__ remains this recipe.
seed=R/'build_first_deluxe.py';seed_sha=hashlib.sha256(seed.read_bytes()).hexdigest()
exec(compile(seed.read_text().split('# Weighted compartment envelope')[0],str(seed),'exec'),globals())
row=target_row;reservation=row['reservation'];O=target_o;O.mkdir(parents=True,exist_ok=True)
assert len(row['identity']['proposed_rest_slot_ids'])==6
screen=next(x for x in json.loads((R/'ALL_81_NEIGHBOUR_SCREEN.json').read_text())['records'] if x['source_envelope_index']==unit)
if screen['screen_status']!='NO_AABB_INTERSECTIONS':
 p=next(x for x in json.loads((R/'PRECISE_RETAINED_TIDAL_INTERSECTIONS.json').read_text())['records'] if x['source_envelope_index']==unit)
 assert p['status']=='AABB_CANDIDATE_CLEARED_BY_ACTUAL_TRIANGLES' and not screen['structural_mesh_aabb_contacts']
frame=PremiumFrame(reservation['proposed_floor_boundary']);assert abs(frame.length-14)<.001
def xyz(u,v,h):return Vector(frame.blender(u,v,h))
def w(u,v,h):return frame.world(u,v,h)
def put(aid,u,v,h=0,yaw=0,label=None):return asset(aid,u,v,h,yaw+frame.angle(v)-math.pi,label)
def rigid_box(name,u,v,du0,du1,dv0,dv1,h0,h1,role,kind='fitted_privacy'):
 points=[frame.inverse(frame.rigid(u,v,du,dv,h)) for h in [h0,h1] for du,dv in [(du0,dv0),(du1,dv0),(du1,dv1),(du0,dv1)]]
 return mesh(name,points,faces,role,kind)
def fixture(name,u,v,h,target,mount,energy=160):
 ob=box(name+'_Bracket',u-.09,u+.09,v-.09,v+.09,h,mount+.025,'champagne_metal','fixture');ob['source_mount_target']=target
 box(name+'_Lens',u-.22,u+.22,v-.22,v+.22,h-.04,h+.015,'lens','fixture')
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=(1,.78,.53);d.shape='DISK';d.size=1.1;ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=xyz(u,v,h-.07);lights.append(ob);marker(name+'_Light',u,v,h-.07,'fixture_light',energy_w=energy)
def profile_band(name,u0,u1,v0,v1,h0,h1,role,kind='architecture'):
 # Include every actual profile knot; custom fitted meshes may follow it.
 vs=sorted({v0,v1,*[(z-frame.start)/frame.vsign for x,z in frame.poly if v0<(z-frame.start)/frame.vsign<v1]})
 polygon=[(u0,v) for v in vs]+[(min(u1,frame.depth(v)-.30),v) for v in reversed(vs)]
 return prism(name,polygon,h0,h1,role,kind)
# A deep inner threshold opens to a branching household gallery, with three
# separated rest niches and a high outer conversation room.
for label,v0,v1 in [('InnerForePartyReturn',.06,4.85),('InnerAftPartyReturn',8.65,13.94)]:profile_band(label,.06,.30,v0,v1,0,4.28,'ivory_enamel')
profile_band('ArrivalHeader',.06,.30,4.85,8.65,2.80,4.28,'ivory_enamel')
put('AST-DOR-002',1.05,6.80,0,math.pi/2,'PrivateEntry')
box('ArrivalForePocket',.48,1.80,4.72,5.00,0,2.85,'warm_walnut');box('ArrivalAftPocket',.48,1.80,8.50,8.78,0,2.85,'warm_walnut')
box('ArrivalLoweredCrown',.48,2.55,4.72,8.78,2.85,3.12,'ivory_enamel');marker('entry',1.10,6.80,0,'proposed_shared_RMB_focus_E_entry',controller_adoption='Root existing vocabulary only')
for label,v0,v1 in [('ForePartyWall',.06,.30),('AftPartyWall',13.70,13.94)]:profile_band(label,.06,100,v0,v1,0,4.28,'ivory_enamel')
# The outward enclosure is opaque: the atlas is a plan guide, not proof of
# per-height real exterior frontage. Root/Group7 own aperture coordination.
vs=sorted({.30,13.70,*[(z-frame.start)/frame.vsign for x,z in frame.poly if .30<(z-frame.start)/frame.vsign<13.70]})
outer=[(frame.depth(v)-.30,v) for v in vs]+[(frame.depth(v)-.06,v) for v in reversed(vs)];prism('HeldFrontageOpaqueEnclosure',outer,0,4.28,'ivory_enamel')
# Rigid private bath frame fits its assets and actual wall mount plane.
bu,bv=3.70,2.87
bath_shapes=[('BathRear',1.90,5.05,.60,.82),('BathWest',1.90,2.12,.60,3.90),('BathEast',4.83,5.05,.60,3.90),('BathFrontLeft',1.90,2.88,3.68,3.90),('BathFrontRight',4.02,5.05,3.68,3.90)]
for name,a,b,c,d in bath_shapes:rigid_box(name,bu,bv,a-3.48,b-3.48,c-2.27,d-2.27,0,2.88,'ivory_enamel')
rigid_box('BathDoorHead',bu,bv,2.88-3.48,4.02-3.48,3.68-2.27,3.90-2.27,2.29,2.88,'ivory_enamel')
def bath_put(aid,u,v,yaw,label):
 p=frame.inverse(frame.rigid(bu,bv,u-3.48,v-2.27,0));return asset(aid,*p,yaw+frame.angle(bv)-math.pi,label)
bath_put('AST-DOR-001',3.45,3.80,0,'BathPrivacy');bath_put('AST-SAN-001',4.85,2.80,math.pi,'Vanity')
normal=Vector((math.cos(frame.angle(bv)),0,-math.sin(frame.angle(bv))));mount=frame.rigid(bu,bv,4.83-3.48,2.80-2.27,0)
imports[-1]['mount_contact_plane']={'normal_xyz':list(normal),'point_xyz':[mount[0],mount[2],-mount[1]],'support_object':'BathEast'}
bath_put('AST-SAN-002',2.49,2.80,-math.pi/2,'Toilet');bath_put('AST-SAN-003',3.55,1.54,0,'Shower')
rigid_box('ShowerRearServiceFacing',bu,bv,2.91-3.48,4.19-3.48,.82-2.27,.865-2.27,.03,2.38,'ivory_enamel')
rigid_box('BathAcousticCover',bu,bv,1.90-3.48,5.05-3.48,.60-2.27,3.90-2.27,2.88,3.06,'ivory_enamel');fixture('BathOpal',bu,bv,2.75,'BathAcousticCover',2.88,95)
# Fore, outer fore and aft-facing rest branches preserve six proposed IDs.
rest_specs=[(7.30,2.70,1),(13.00,3.50,1),(7.30,11.25,-1)]
for j,(u,v,facing) in enumerate(rest_specs):
 put('AST-SLP-002',u,v,0,math.pi if facing==1 else 0,f'RestAlcove{j+1}')
 dv0,dv1=sorted([-1.65*facing,-1.43*facing]);rigid_box(f'RestHeadBacking{j}',u,v,-1.50,1.50,dv0,dv1,0,2.86,'warm_walnut')
 rigid_box(f'RestSideCheek{j}',u,v,-1.58,-1.36,-1.65,1.62,0,2.72,'ivory_enamel');rigid_box(f'RestCrown{j}',u,v,-1.58,1.50,-1.65,1.62,2.72,2.95,'ivory_enamel')
 p=frame.inverse(frame.rigid(u,v,1.63,-1.10*facing,0));asset('AST-GST-003',*p,math.pi/2+frame.angle(v)-math.pi,f'PersonalStow{j}')
 for k,du in enumerate([-.46,.46]):
  p=frame.inverse(frame.rigid(u,v,du,0,.69));marker(f'rest_{j*2+k+1:02}',*p,'proposed_rest_anchor',reservation_id=row['identity']['proposed_rest_slot_ids'][j*2+k])
 fixture(f'RestReading{j}',u,v,2.60,f'RestCrown{j}',2.72,85)
# A six-chair private table between the three branches, with a real full
# kitchen along the inner edge and separate preparation/used-return stances.
put('AST-HSP-001',1.70,9.40,0,math.pi/2,'FittedKitchen')
bev=frame.inverse(frame.rigid(1.70,9.40,.02,2.10,.90));asset('AST-HSP-003',*bev,math.pi/2+frame.angle(9.40)-math.pi,'Beverage')
box('KitchenTallColdStorage',.80,1.85,12.30,13.30,0,2.30,'warm_walnut','kitchen');box('ColdStorageDoor',1.86,1.90,12.35,13.25,.12,2.22,'ivory_enamel','kitchen');box('KitchenUsedReturn',.80,1.85,8.30,9.10,0,.90,'warm_walnut','kitchen')
box('KitchenHobTop',1.40,2.10,10.00,10.90,.90,.96,'dark_rubber','kitchen');box('KitchenOvenFront',2.11,2.16,10.00,10.90,.19,.76,'dark_rubber','kitchen');box('KitchenExtraction',1.20,2.20,10.00,10.90,2.30,2.50,'ivory_enamel','kitchen')
oval=[(7.20+1.40*math.cos(2*math.pi*k/28),7.0+math.sin(2*math.pi*k/28)) for k in range(28)];prism('FittedOvalDiningTop',oval,.72,.79,'warm_stone','private_dining')
for j,u in enumerate([6.60,7.80]):box(f'DiningPedestalFoot{j}',u-.36,u+.36,6.60,7.40,0,.075,'warm_walnut','private_dining');box(f'DiningPedestal{j}',u-.22,u+.22,6.65,7.35,.075,.72,'warm_walnut','private_dining')
for name,u,v,yaw in [('N',7.2,5.70,math.pi),('S',7.2,8.30,0),('W1',5.5,6.4,math.pi/2),('W2',5.5,7.6,math.pi/2),('E1',9.1,6.4,-math.pi/2),('E2',9.1,7.6,-math.pi/2)]:put('AST-FUR-002',u,v,0,yaw,'PrivateDiningChair'+name)
arc('CrescentBenchPlinth',(14.80,10.20),1.00,1.86,-1.00,1.00,0,.34,'warm_walnut');arc('CrescentBenchCushion',(14.80,10.20),.96,1.86,-1.00,1.00,.34,.50,'teal_weave');arc('CrescentBenchBack',(14.80,10.20),1.74,1.97,-1.00,1.00,.50,1.18,'oatmeal_weave')
put('AST-FUR-002',11.85,9.00,0,math.pi/2,'ConversationChairA');put('AST-FUR-002',11.85,11.80,0,math.pi/2,'ConversationChairB');put('AST-FUR-003',14.0,10.2,0,0,'ConversationTable')
box('ReadingCounter',9.40,11.25,12.85,13.50,0,.78,'warm_walnut','activity');put('AST-FUR-002',10.35,11.70,0,math.pi,'ReadingChair');put('AST-LIB-006',10.35,13.15,.78,0,'ReadingBooks');box('ReadingBayBacking',9.40,11.25,13.50,13.70,.78,2.90,'warm_walnut','activity')
for j,h in enumerate([1.25,1.83,2.41]):box(f'ReadingShelf{j}',9.40,11.25,13.10,13.50,h,h+.075,'warm_walnut','activity');put('AST-LIB-006',10.25,13.28,h+.075,0,f'ReadingShelfStock{j}')
put('AST-BOT-002',16.70,7.30,.14,0,'PrivatePlant');box('PlantPlinth',16.15,17.25,6.92,7.70,0,.14,'warm_stone')
# Two ceiling fields make the branching inner gallery visibly lower than the
# outer conversation room; rest and bath covers establish further local scale.
profile_band('InnerLivingCeiling',.30,11.55,.30,13.70,3.55,3.73,'ivory_enamel','roof');profile_band('OuterConversationCeiling',11.55,100,.30,13.70,4.10,4.28,'ivory_enamel','roof');profile_band('LivingCeilingStep',11.40,11.55,.30,13.70,3.55,4.10,'ivory_enamel','roof_bearing')
profile_band('PremiumPressureClosure',.06,100,.06,13.94,4.28,4.45,'ivory_enamel','roof')
for j,v in enumerate([5.2,8.5,12.3]):profile_band(f'InnerCeilingBearing{j}',.30,11.55,v-.09,v+.09,3.40,3.57,'warm_walnut','roof_bearing')
fixture('ArrivalOpal',3.00,6.80,3.34,'InnerLivingCeiling',3.55,170);fixture('PrivateDiningOpal',7.2,7.0,3.34,'InnerLivingCeiling',3.55,210);fixture('KitchenWork',3.1,10.1,3.34,'InnerLivingCeiling',3.55,190);fixture('ConversationOpal',14.8,10.2,3.90,'OuterConversationCeiling',4.10,310)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for rec in markers:
 if rec['kind']!='proposed_rest_anchor':continue
 ob=bpy.data.objects[rec['name']];hits=[]
 for part in parts:
  if part.type!='MESH' or 'REST_Quilt' not in part.name or 'seam' in part.name:continue
  ev=part.evaluated_get(dg);inv=ev.matrix_world.inverted();hit,loc,norm,ix=ev.ray_cast(inv@(ob.location+Vector((0,0,1))),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((ev.matrix_world@loc).z)
 assert hits;ob.location.z=max(hits);rec['world_xyz'][1]=max(hits)
bpy.context.view_layer.update()
curve=bpy.data.curves.new('SmallDoorLabel','FONT');curve.body=f'PREMIUM {unit}';curve.size=.11;curve.extrude=.001;curve.materials.append(mats['champagne_metal']);sign=bpy.data.objects.new('SmallDoorLabel',curve);scene.collection.objects.link(sign);sign.location=xyz(.44,8.45,1.55);sign.rotation_euler=(math.pi/2,0,(math.pi/2 if frame.star else -math.pi/2)+frame.angle(6.8)-(0 if frame.star else math.pi));repair_label(sign);remember(sign,'editable_sign')
for ob in parts:ob['source_scope']=f'Group2/{unit}';ob['source_envelope_index']=unit
scene.cycles.samples=4
preview=profile_band('PREVIEW_COMPILER_FLOOR',.01,100,.01,13.99,-.18,0,'warm_stone','preview_floor');parts.remove(preview)
context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb';before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context=set(scene.objects)-before
cams=[('arrival',(2.65,6.8,1.65),(13.8,10.2,1.4)),('main_programme',(10.4,7.1,1.65),(16.7,10.2,1.4)),('sleeping',(8.9,5.0,1.65),(7.3,2.7,1.1)),('sleeping_second',(8.8,9.0,1.65),(7.3,11.25,1.1)),('kitchen_service',(5.0,9.0,1.65),(1.7,11.0,1.1)),('bath_privacy',frame.inverse(frame.rigid(bu,bv,.05,1.21,1.65)),frame.inverse(frame.rigid(bu,bv,.05,-1.07,1.1)))]
cam=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.lens=20;cam.data.clip_start=.05;cam.data.clip_end=100;views=[]
for name,pos,target in cams:
 cam.location=xyz(*pos);cam.rotation_euler=(xyz(*target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);views.append({'name':name,'file':name+'.png','sha256':sha(O/(name+'.png')),'camera_world_xyz':w(*pos),'target_world_xyz':w(*target),'height_above_local_floor':1.65})
for ob in context:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);bpy.data.objects.remove(cam,do_unlink=True);scene.camera=None;bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
native=O/f'{unit}_premium.blend';export=O/f'{unit}_premium.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
world_routes=[('main_loaded_cart',[w(2.65,6.8,0),w(4.0,6.8,0),w(4.0,9.2,0)],.82),('outer_gallery_body',[w(10.4,6.8,0),w(10.4,10.2,0),w(13.0,10.2,0)],.38),('kitchen_body',[w(3.4,9.2,0),w(3.4,11.0,0)],.38)]
def bath_world(u,v):
 p=frame.rigid(bu,bv,u-3.48,v-2.27,0);return [p[0],p[2],-p[1]]
bath_routes=[('bath_vanity_stance',[bath_world(3.53,3.30),bath_world(3.53,2.80),bath_world(3.84,2.80)],.38),('bath_toilet_stance',[bath_world(3.53,3.30),bath_world(3.45,2.80)],.38),('shower_approach_and_tray',[bath_world(3.53,3.30),bath_world(3.55,2.80),bath_world(3.55,1.85)],.38)]
contract={'schema':'astraea.group2_source_section.v1','status':'BUILT_PREMIUM_PENDING_QA_AND_ACTUAL_PIXELS','identity':row['identity'],'reservation':reservation,'architecture':'Three rest branches around a six-chair household dining gallery, rigid enclosed bath, edge kitchen, private library and high crescent conversation room; fitted meshes follow the actual irregular allocation','floor_owner':'Root compiler only; preview floor omitted','floor_proposal':{'boundary':frame.poly,'floor_y':102,'thickness':.24,'status':'HELD Root support/adoption'},'imports':imports,'markers':markers,'source_views':views,'native_sha256':sha(native),'export_sha256':sha(export),'rebuild_source_sha256':sha(pathlib.Path(__file__)),'geometry_rebuild_dependencies':{'build_first_deluxe.py':seed_sha,'premium_frame.py':sha(R/'premium_frame.py'),'editable_label.py':sha(R/'editable_label.py')},'source_routes_world':world_routes,'internal_bath_routes_world':bath_routes,'species_assignment':None,'rest_contact_mesh_tokens':['REST_Quilt'],'private_frontage_status':'HELD: no exterior aperture authored; atlas plan vector is not per-height frontage proof. Root/Group7 final enclosing frontage/opening acceptance required.','remaining':['Actual saved-native/export fit and normal-height pixels','Root support/floors, genuine frontage/windows and external connections','Root controller/actor/physical-cart and rest ledger adoption','Installed Godot normal-arrival, streaming, persistence, regression and final art acceptance']}
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2));runpy.run_path(str(R/'verify_first_native.py'),run_name='__main__');runpy.run_path(str(R/'verify_first_export.py'),run_name='__main__');print('PREMIUM SOURCE QA PASS',unit,flush=True)
