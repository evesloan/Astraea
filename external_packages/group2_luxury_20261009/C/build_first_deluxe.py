"""First bounded Group2 luxury prototype; source-only, compiler floors excluded.
Run via heavy.py. All locations in metre-scale world coordinates, GLB zero origin.
"""
import bpy,bmesh,math,json,pathlib,hashlib,sys
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent; I=R/'inputs'; C=I/'BlenderCatalogue'
O=R/'sections'/'876_deluxe'; O.mkdir(parents=True,exist_ok=True)
inventory=json.loads((R/'LUXURY_81_INVENTORY.json').read_text(encoding='utf-8'))
row=next(x for x in inventory['records'] if x['identity']['source_envelope_index']==876)
reservation=row['reservation']; assert reservation['proposed_floor_boundary']==[[-43.0,-459.0],[-43.0,-449.0],[-61.0,-449.0],[-61.0,-459.0]]
catalogue=json.loads((C/'catalogue_manifest.json').read_text(encoding='utf-8')); assets={x['catalogue_id']:x for x in catalogue['assets']}
receipt=json.loads((R/'INPUT_PIN_RECEIPT.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=800;scene.render.resolution_y=450;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.025,.035,.055,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.16
parts=[];imports=[];markers=[];lights=[];counter=0
def xyz(u,v,h):return Vector((-43-u,459-v,102+h))
def w(u,v,h):return [-43-u,102+h,-459+v]
def remember(ob,kind='architecture'):
 ob['source_scope']='Group2/876';ob['source_envelope_index']=876;ob['group2_kind']=kind;parts.append(ob);return ob
def asset(aid,u,v,h=0,yaw=0,label=None):
 global counter
 item=assets[aid];p=C/item['source'];assert p.exists(),p
 pin=sha(p)
 if item.get('source_sha256'):assert pin==item['source_sha256'],aid
 with bpy.data.libraries.load(str(p),link=False) as (a,b):b.objects=list(a.objects)
 loaded=[x for x in b.objects if x is not None and x.type not in {'CAMERA','LIGHT'} and not x.hide_render]
 placement=Matrix.Translation(xyz(u,v,h))@Matrix.Rotation(math.pi+yaw,4,'Z')
 counter+=1;prefix=f'{label or aid}_{counter:02d}_'
 for ob in loaded:
  if ob.name not in scene.collection.objects:bpy.context.collection.objects.link(ob)
  ob.name=prefix+ob.name
 bpy.context.view_layer.update()
 matrices={x:x.matrix_world.copy() for x in loaded}
 # Apply the placement exactly once at each hierarchy root. Native child basis
 # and parent-inverse matrices remain intact, including hinges and welt paths.
 for ob in loaded:
  if ob.parent not in loaded:
   ob.parent=None;ob.matrix_world=placement@matrices[ob]
  ob['retained_catalogue_id']=aid;remember(ob,'retained_furniture' if 'DOR' not in aid else 'door_source')
 bpy.context.view_layer.update()
 for ob in loaded:
  target=placement@matrices[ob]
  assert max(abs(ob.matrix_world[a][b]-target[a][b]) for a in range(4) for b in range(4))<.0001,(aid,ob.name,'hierarchy placement discrepancy')
 repairs=[]
 if aid=='AST-HSP-003':
  for ob in loaded:
   if ob.type=='MESH' and any(t in ob.name for t in ['rear_service_panel','dark_control_fascia']):
    thickness=min(max(v.co[k] for v in ob.data.vertices)-min(v.co[k] for v in ob.data.vertices) for k in range(3))
    for mod in ob.modifiers:
     if mod.type=='BEVEL' and mod.width>thickness*.22:
      before=mod.width;mod.width=thickness*.22;repairs.append({'part':ob.name,'modifier':mod.name,'before_width':before,'after_width':mod.width,'reason':'Inherited bevel exceeded thin panel thickness, producing24 zero-area triangles. Isolated derivative only; retained original unchanged.'})
 imports.append({'catalogue_id':aid,'source_path':str(p.relative_to(I)),'source_sha256':pin,'world_xyz':w(u,v,h),'source_yaw':math.pi+yaw,'part_names':[x.name for x in loaded],'isolated_derivative_repairs':repairs})
 return loaded
for aid in ['AST-FUR-001','AST-FUR-002','AST-FUR-003']:
 item=assets[aid];p=C/item['source'];assert sha(p)==item['source_sha256']
 with bpy.data.libraries.load(str(p),link=False) as (a,b):b.materials=list(a.materials)
 imports.append({'catalogue_id':aid,'purpose':'retained material palette only','source_path':str(p.relative_to(I)),'source_sha256':sha(p)})
mats={name:bpy.data.materials.get('ASTRAEA_'+name) for name in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','oatmeal_weave','clay_weave','dark_rubber']}
assert all(mats.values()),[(k,v) for k,v in mats.items() if not v]
def new_mat(name,color,rough=.5,alpha=1,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,alpha);p.inputs['Roughness'].default_value=rough;p.inputs['Alpha'].default_value=alpha
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
mats['glass']=new_mat('G2_SealedCourtGlass',(.30,.48,.48),.24,.22);mats['glass'].surface_render_method='DITHERED';mats['glass'].use_transparency_overlap=False
mats['lens']=new_mat('G2_WarmFixtureLens',(1,.73,.39),.3,1,3)
def mesh(name,local,faces,role,kind='architecture'):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(*v) for v in local],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled')
 for p in me.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
  for li in p.loop_indices:
   pt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pt.dot(u),pt.dot(v))
 return remember(ob,kind)
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,u0,u1,v0,v1,h0,h1,role,kind='architecture'):
 return mesh(name,[(u,v,h) for h in [h0,h1] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],faces,role,kind)
def prism(name,poly,lo,hi,role,kind='architecture'):
 n=len(poly);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)];return mesh(name,[(u,v,h) for h in [lo,hi] for u,v in poly],fs,role,kind)
def wall(name,a,b,lo,hi,width,role,kind='architecture'):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*width/2;return prism(name,[a+n,b+n,b-n,a-n],lo,hi,role,kind)
def arc(name,center,r0,r1,start,end,lo,hi,role):
 n=14;points=[(center[0]+r*math.cos(start+(end-start)*k/n),center[1]+r*math.sin(start+(end-start)*k/n)) for r,ks in [(r1,range(n+1)),(r0,range(n,-1,-1))] for k in ks];return prism(name,points,lo,hi,role,'fitted_conversation')
def marker(name,u,v,h,kind,**extra):
 ob=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(ob);ob.location=xyz(u,v,h);ob['kind']=kind
 for k,val in extra.items():ob[k]=val
 remember(ob,'marker');markers.append({'name':ob.name,'world_xyz':w(u,v,h),'kind':kind,**extra});return ob
def lamp(name,u,v,h,energy=160,size=1.5):
 mount=2.88 if name=='BathOpal' else 2.72 if name.startswith('RestReading') else 3.25+(u-.40)/7.60*.50 if u<=8 else 3.75+(u-8)/9.54*.53
 box(name+'_Bracket',u-.09,u+.09,v-.09,v+.09,h,mount+.025,'champagne_metal','fixture')
 box(name+'_Lens',u-.22,u+.22,v-.22,v+.22,h-.04,h+.015,'lens','fixture')
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=(1,.78,.53);data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=xyz(u,v,h-.07);lights.append(ob);marker(name+'_Light',u,v,h-.07,'fixture_light',energy_w=energy)
# Weighted compartment envelope within the approved candidate, with a deep arrival.
box('NorthAcousticWall',.06,17.94,.06,.30,0,4.28,'ivory_enamel')
box('SouthAcousticWall',.06,17.94,9.70,9.94,0,4.28,'ivory_enamel')
# Entry is recessed at u1, away from the retained public neighbour. The outer
# portal only occupies this reservation, and has no proposed public-floor claim.
for name,v0,v1 in [('EntryForeReturn',.30,3.55),('EntryAftReturn',7.05,9.70)]:box(name,.12,.40,v0,v1,0,3.30,'ivory_enamel')
box('EntryHeader',.12,.40,3.55,7.05,2.80,3.30,'ivory_enamel')
asset('AST-DOR-002',1.05,5.30,0,math.pi/2,'PrivateEntry')
box('EntryPocketFore',.48,1.80,3.35,3.63,0,2.85,'warm_walnut');box('EntryPocketAft',.48,1.80,6.97,7.25,0,2.85,'warm_walnut')
box('EntryPocketCrown',.48,2.55,3.35,7.25,2.85,3.12,'ivory_enamel')
marker('entry',1.10,5.30,0,'proposed_shared_RMB_focus_E_entry',controller_adoption='Root only; existing door vocabulary retained')
# Fitted bath is enclosed. Its 1.18m retained door aperture has no conflicting
# invented input or privacy promise for the separate court-facing bedrooms.
box('BathRear',1.90,5.05,.60,.82,0,2.88,'ivory_enamel');box('BathWest',1.90,2.12,.60,3.90,0,2.88,'ivory_enamel');box('BathEast',4.83,5.05,.60,3.90,0,2.88,'ivory_enamel')
box('BathFrontLeft',1.90,2.88,3.68,3.90,0,2.88,'ivory_enamel');box('BathFrontRight',4.02,5.05,3.68,3.90,0,2.88,'ivory_enamel');box('BathDoorHead',2.88,4.02,3.68,3.90,2.29,2.88,'ivory_enamel')
asset('AST-DOR-001',3.45,3.80,0,0,'BathPrivacy')
asset('AST-SAN-001',4.85,2.80,0,math.pi,'Vanity');asset('AST-SAN-002',2.49,2.80,0,-math.pi/2,'Toilet');asset('AST-SAN-003',3.55,1.54,0,0,'Shower')
box('ShowerRearServiceFacing',2.91,4.19,.82,.865,.03,2.38,'ivory_enamel','bath_service')
box('BathAcousticCover',1.90,5.05,.60,3.90,2.88,3.06,'ivory_enamel');lamp('BathOpal',3.48,2.27,2.75,95,.75)
# Two rest alcoves with real retained double frames/bedding and four separate
# proposed reservations. The identity ledger preserves original source markers.
for n,u in enumerate([7.55,13.10]):
 asset('AST-SLP-002',u,2.38,0,math.pi,f'RestAlcove{n+1}')
 box(f'RestHeadBacking{n}',u-1.43,u+1.43,.37,.68,0,2.86,'warm_walnut')
 box(f'RestSideCheek{n}',u-1.58,u-1.36,.68,4.15,0,2.72,'ivory_enamel')
 box(f'RestCrown{n}',u-1.58,u+1.50,.68,4.15,2.72,2.95,'ivory_enamel')
 asset('AST-GST-003',u+1.63,1.28,0,math.pi/2,f'PersonalStow{n}')
 for j,du in enumerate([-.46,.46]):marker(f'rest_{n*2+j+1:02}',u+du,2.38,.68875,'proposed_rest_anchor',reservation_id=row['identity']['proposed_rest_slot_ids'][n*2+j],support_pending='Actual retained quilt contact measured by saved-native QA; no occupancy assigned')
 lamp(f'RestReading{n}',u,2.40,2.60,85,.65)
# Shaped kitchen is an inhabited edge, with useful counter height and a separated
# clean/preparation side, appliance, wash and refuse locations.
asset('AST-HSP-001',2.40,8.92,0,0,'FittedKitchen');asset('AST-HSP-003',4.50,8.90,.90,0,'Beverage')
box('KitchenTallColdStorage',1.15,2.20,8.75,9.55,0,2.30,'warm_walnut','kitchen')
box('ColdStorageDoor',1.10,1.14,8.80,9.49,.12,2.22,'ivory_enamel','kitchen')
box('ColdStorageHandle',1.03,1.10,9.25,9.30,.90,1.60,'champagne_metal','kitchen')
box('KitchenHobTop',3.00,3.86,8.61,9.22,.91,.96,'dark_rubber','kitchen')
for j in range(2):
 for k in range(2):box(f'HobPad{j}{k}',3.07+j*.40,3.33+j*.40,8.66+k*.29,8.86+k*.29,.96,.968,'champagne_metal','kitchen')
box('KitchenOvenFront',2.94,3.95,8.56,8.62,.19,.76,'dark_rubber','kitchen')
box('KitchenExtraction',2.94,3.95,8.51,9.30,2.30,2.50,'ivory_enamel','kitchen')
box('KitchenUsedReturn',5.61,6.38,8.79,9.49,0,.90,'warm_walnut','kitchen')
lamp('KitchenWork',4.15,8.05,3.25,190,1.4)
marker('kitchen_work',4.00,7.20,0,'care_and_preparation_stance');marker('used_return',5.90,7.85,0,'used_return_approach')
# A real four-place household dining activity sits between preparation and the
# salon. Its position leaves a deliberate continuous aisle at v5.0.
oval=[(7.2+1.2*math.cos(2*math.pi*k/28),6.8+.65*math.sin(2*math.pi*k/28)) for k in range(28)]
prism('FittedOvalDiningTop',oval,.72,.79,'warm_stone','private_dining')
for k,u in enumerate([6.60,7.80]):
 box(f'DiningPedestalFoot{k}',u-.36,u+.36,6.42,7.18,0,.075,'warm_walnut','private_dining')
 prism(f'DiningSplayedPedestal{k}',[(u-.20,6.50),(u+.20,6.50),(u+.30,7.10),(u-.30,7.10)],.075,.72,'warm_walnut','private_dining')
for name,u,v,yaw in [('N',7.2,6.40,math.pi),('S',7.2,8.00,0),('W',5.55,6.8,math.pi/2),('E',8.85,6.8,-math.pi/2)]:asset('AST-FUR-002',u,v,0,yaw,'PrivateDiningChair'+name)
lamp('PrivateDiningOpal',7.2,6.8,3.38,190,1.5)
# Conversation focus: a shallow sheltered crescent, paired existing chairs and
# a useful central table. Court glazing is internal, not a fabricated hull view.
arc('CrescentBenchPlinth',(15.42,7.25),1.00,1.86,-1.00,1.00,0,.34,'warm_walnut')
arc('CrescentBenchCushion',(15.42,7.25),.96,1.86,-1.00,1.00,.34,.50,'teal_weave')
arc('CrescentBenchBack',(15.42,7.25),1.74,1.97,-1.00,1.00,.50,1.18,'oatmeal_weave')
asset('AST-FUR-002',12.2,5.90,0,math.pi/2,'ConversationChairA');asset('AST-FUR-002',12.2,8.60,0,math.pi/2,'ConversationChairB');asset('AST-FUR-003',14.55,7.25,0,0,'ConversationTable')
asset('AST-BOT-002',16.65,4.90,.14,0,'CourtPlant');box('PlantPlinth',16.11,17.20,4.52,5.30,0,.14,'warm_stone')
box('ReadingCounter',8.10,10.30,8.95,9.52,0,.78,'warm_walnut','activity');asset('AST-FUR-002',9.18,7.98,0,math.pi,'ReadingChair');asset('AST-LIB-006',9.28,9.18,.78,0,'ReadingBooks')
box('ReadingBayBacking',8.10,10.30,9.50,9.70,.78,2.90,'warm_walnut','activity')
for k,h in enumerate([1.25,1.83,2.41]):
 box(f'ReadingShelf{k}',8.10,10.30,9.10,9.50,h,h+.075,'warm_walnut','activity')
 for j,u in enumerate([8.45,9.15,9.80]):asset('AST-LIB-006',u,9.26,h+.075,0,f'ReadingShelfStock{k}{j}')
arc('ConversationHood',(15.42,7.25),1.97,2.30,-1.08,1.08,2.95,3.18,'ivory_enamel')
arc('ConversationHoodInnerLip',(15.42,7.25),1.95,2.05,-1.08,1.08,2.82,2.96,'warm_walnut')
for k,v in enumerate([5.22,9.28]):box(f'ConversationEndBearing{k}',16.28,16.50,v-.10,v+.10,0,3.18,'warm_walnut','roof_bearing')
# Window bays and deep mullion/ceiling returns track the view edge. Root owns
# the adjoining court and its final outlook; no exterior aperture is authored.
box('CourtWallNorth',17.54,17.93,.30,.90,0,4.28,'ivory_enamel');box('CourtWallSouth',17.54,17.93,9.10,9.70,0,4.28,'ivory_enamel')
box('CourtSill',17.54,17.93,.90,9.10,0,.45,'warm_stone');box('CourtHead',17.54,17.93,.90,9.10,3.65,4.28,'ivory_enamel')
for k,(v0,v1) in enumerate([(.90,3.30),(3.50,6.10),(6.30,9.10)]):box(f'CourtSealedPane{k}',17.78,17.80,v0,v1,.46,3.65,'glass','internal_court_glazing')
for k,v in enumerate([3.30,6.10]):box(f'CourtDeepMullion{k}',17.36,17.93,v,v+.20,.45,3.65,'warm_walnut')
# Main roof rises away from the compressed threshold; bedroom and wash covers
# provide purposeful local heights. The fan is joined to boundary walls.
roof=[(u,v,h) for v in [.30,9.70] for u,h in [(.40,3.25),(8,3.75),(17.54,4.28),(17.54,4.45),(8,3.92),(.40,3.42)]]
n=6;fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
mesh('RisingLivingRoof',roof,fs,'ivory_enamel','roof')
box('UpperPressureClosure',.06,17.94,.06,9.94,4.28,4.45,'ivory_enamel','roof')
for k,u in enumerate([2.8,6.6,10.5,14.4]):
 h=3.25+(min(u,8)/8)*.5+max(0,u-8)/9.54*.53
 box(f'LivingRoofBearing{k}',u-.10,u+.10,.30,9.70,h-.16,h+.08,'warm_walnut','roof_bearing')
lamp('ArrivalOpal',3.1,5.30,3.02,170,1.2);lamp('LivingOpal',10.6,6.40,3.49,280,2);lamp('ViewBayOpal',15.20,7.25,3.85,310,2)
marker('maintenance_park',2.55,6.20,0,'proposed_cart_park');marker('conversation_approach',13.4,7.25,0,'proposed_body_approach')
# Derive reservation contact heights from actual evaluated quilt surfaces, not
# the asset's maximum crown height at a different horizontal position.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for rec in markers:
 if rec['kind']!='proposed_rest_anchor':continue
 ob=bpy.data.objects[rec['name']];hits=[]
 for part in parts:
  if part.type!='MESH' or 'REST_Quilt' not in part.name or 'seam' in part.name:continue
  ev=part.evaluated_get(dg);inv=ev.matrix_world.inverted();hit,loc,norm,idx=ev.ray_cast(inv@(ob.location+Vector((0,0,1))),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((ev.matrix_world@loc).z)
 assert hits,rec['name'];ob.location.z=max(hits);rec['world_xyz'][1]=max(hits);rec['contact_source']='Actual evaluated retained quilt triangle at this reservation XY'
# Small built-in editable source label; exported parity is separately checked.
curve=bpy.data.curves.new('SmallDoorLabel','FONT');curve.body='DELUXE 876';curve.size=.11;curve.extrude=.001;curve.materials.append(mats['champagne_metal']);sign=bpy.data.objects.new('SmallDoorLabel',curve);scene.collection.objects.link(sign);sign.location=xyz(.44,6.82,1.55);sign.rotation_euler=(math.pi/2,0,-math.pi/2);remember(sign,'editable_sign')
# No preview floor persists in the native or export. It exists only during
# rendering, then is deleted before final save/export and containment checks.
preview=box('PREVIEW_COMPILER_FLOOR',.01,17.99,.01,9.99,-.18,0,'warm_stone','preview_floor');parts.remove(preview)
context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb'
before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context_parts=set(scene.objects)-before
cams=[('arrival',(2.65,5.30,1.65),(13.8,7.25,1.55)),('main_programme',(10.1,6.30,1.65),(16.75,7.2,1.45)),('sleeping',(9.2,4.9,1.65),(8.5,2.2,1.25)),('sleeping_second',(14.75,4.90,1.65),(13.45,2.2,1.25)),('kitchen_service',(7.0,6.8,1.65),(3.8,8.8,1.1)),('bath_privacy',(3.53,3.48,1.65),(3.53,1.20,1.10))]
camera=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=20;camera.data.clip_start=.05;camera.data.clip_end=100
render_receipts=[]
for name,pos,target in cams:
 camera.location=xyz(*pos);camera.rotation_euler=(xyz(*target)-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);render_receipts.append({'name':name,'camera_world_xyz':w(*pos),'target_world_xyz':w(*target),'height_above_local_floor':1.65,'file':name+'.png','sha256':sha(O/(name+'.png'))})
for ob in context_parts:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);bpy.data.objects.remove(camera,do_unlink=True)
# Save packed editable source, then export exactly source objects, lights excluded.
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
 if ob.name in scene.objects:ob.select_set(True)
scene.camera=None
native=O/'876_deluxe.blend';export=O/'876_deluxe.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
contract={'schema':'astraea.group2_source_section.v1','status':'BUILT_CANDIDATE_PENDING_QA_AND_VISUAL_REVIEW','identity':row['identity'],'reservation':reservation,'zero_origin_GLByup_world_placement':[0,0,0],'architecture':'Offset private vestibule, two lowered sleeping alcoves, enclosed washroom, fitted preparation edge, four-place private dining activity, fitted reading library and sheltered crescent conversation bay under a rising roof','floor_owner':'Root compiler only; render-only slab removed before native save and GLB export','floor_proposal':{'boundary':reservation['proposed_floor_boundary'],'floor_y':102,'thickness':.24,'status':'HELD: root support/ownership and court/street integration required'},'imports':imports,'markers':markers,'source_views':render_receipts,'render_only_context':{'path':str(context_path.relative_to(I)),'sha256':sha(context_path),'objects_removed_before_native_and_export':len(context_parts),'scope':'Exact retained neighbouring receiving candidate only; source review context, no installed acceptance and no authored neighbour changes'},'native_sha256':sha(native),'export_sha256':sha(export),'rebuild_source_sha256':sha(pathlib.Path(__file__)),'references_applied':['master original housing blueprint: neighbourhood/court hierarchy, printed counts ignored in favor of overlay','premium broad-view image: living/dining/bed hierarchy and coordinated ceiling/light','8079: deep fitted threshold framing the outlook','8077: warm timber/private entry/support edge','master diorama: inhabited edges and sightlines, no literal four-level adoption'],'remaining':['Saved-native and raw-export QA','Actual normal-height visual review of these six matching views','Root floor/support ownership, adjoining court outlook and public/private approach','Door/lights integration through existing controllers','Species/body/pose and physical loaded-cart acceptance','Installed Godot normal-arrival, streaming, persistence, regression and final visual acceptance']}
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2),encoding='utf-8');print('BUILT FIRST DELUXE',native,export,flush=True)
