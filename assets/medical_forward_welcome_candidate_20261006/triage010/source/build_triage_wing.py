"""Connected eight-pod medical source candidate. No Game/Catalogue writes or floor slab."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys,runpy
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');BASE=C/'assets/medical_forward_welcome_candidate_20261006/finish008';RUN='009'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();PIN=json.loads((R/'qa/INPUT_PINS.json').read_text())
for p,h in PIN['inputs'].items():assert sha(p)==h,('Input drift',p)
SOURCE=R/'source/D05_medical_connected_triage_009.blend';EXPORT=R/'exports/D05_medical_connected_architecture_009.glb';assert not SOURCE.exists()and not EXPORT.exists()
bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/D05_forward_welcome_008.blend'));SCENE=bpy.context.scene
MATS={n:bpy.data.materials.get(n)for n in ['quiet_ivory','sage_acoustic','warm_sand','warm_walnut','champagne_metal','dark_rubber','ivory_enamel','clinical_ink','opal_lens']};assert all(MATS.values())
PARTS=[o for o in SCENE.objects if o.type=='MESH'and o.get('source_package')=='D05_forward_welcome_candidate'];OLD=json.loads((BASE/'qa/SOURCE_MANIFEST_008.json').read_text());RETAINED=json.loads(json.dumps(OLD['retained_component_instances']));FIXTURES=json.loads(json.dumps(OLD['fixture_sources']));RECEIVERS=json.loads(json.dumps(OLD['receiver_markers']));ROOMS=[];DOORS=[];CHANGES=[]
exec(compile((R/'source/source_helpers.py').read_text(),str(R/'source/source_helpers.py'),'exec'))

def remove(name):
 o=bpy.data.objects.get(name);assert o is not None,name
 if o in PARTS:PARTS.remove(o)
 bpy.data.objects.remove(o,do_unlink=True);CHANGES.append(name)

def clone_asset(prototype,tag,at,yaw,child):
 original=bpy.data.objects['INSTANCE_'+prototype];objects=[original]+list(original.children_recursive);mapping={}
 for old in objects:
  new=old.copy();SCENE.collection.objects.link(new);new.name='INSTANCE_'+tag if old==original else tag+'__'+old.name.split('__',1)[-1];mapping[old]=new
 for old,new in mapping.items():
  new.parent=mapping.get(old.parent);new.matrix_parent_inverse=old.matrix_parent_inverse.copy();new.matrix_basis=old.matrix_basis.copy();new['programme_child']=child
 root=mapping[original];root.location=at;root.rotation_euler=(0,0,yaw);root.scale=(1,1,1)
 source=next(x for x in OLD['retained_component_instances']if x['instance']==prototype);record=dict(source);record.update(instance=tag,translation_source_xyz=list(at),translation_world_xyz=world(at),yaw_source_z_radians=yaw,programme_child=child,objects=len(objects)-1,shared_editable_mesh_data=True)
 RETAINED.append(record);return root

# One honest receiving change, only in this new source derivative.
for name in ['ADMISSION_north_end','ADMISSION_end_direction_receiver','ADMISSION_end_direction_field','ADMISSION_end_waiting_turn','ADMISSION_end_care_turn']:remove(name)
box('TRIAGE_receiving_left_shoulder',14,15.2,3.76,4,0,4.2)
box('TRIAGE_receiving_right_shoulder',18.8,20,3.76,4,0,4.2)
box('TRIAGE_receiving_lintel',15.2,18.8,3.76,4,3.0,4.2,'sage_acoustic')
box('ADMISSION_end_direction_receiver',15.6,18.4,3.60,3.76,3.05,4.12,'warm_walnut',.025)
box('ADMISSION_end_direction_field',15.75,18.25,3.575,3.60,3.18,3.98,'sage_acoustic',.012)
text('ADMISSION_end_waiting_turn','TRIAGE  01-08',(17,3.56,3.77),.24,role='ivory_enamel')
text('ADMISSION_end_care_turn','<  WAITING  /  ASSISTANCE',(17,3.555,3.42),.12,role='ivory_enamel')
marker('triage_receiving_centre',(17,3.88,0),'proposed_source_receiving_opening',(0,1,0),'TRIAGE_receiving_lintel')

# Main admission extension occupies only its recorded parent allocation.
box('TRIAGE_admission_outer',19.8,20,4,20,0,4.2)
for label,y0,y1 in [('aft',4,10),('fore',14,20)]:box('TRIAGE_admission_inner_'+label,14,14.2,y0,y1,0,4.2)
box('TRIAGE_admission_fore_cap',14,20,19.8,20,0,4.2)
for i,(y0,y1)in enumerate([(4,9.95),(9.95,14.05),(14.05,20)]):
 box('TRIAGE_admission_ceiling_'+str(i),14.2,19.8,y0,y1,4.20,4.36)
 y=(y0+y1)/2
 box('TRIAGE_admission_housing_'+str(i),16.05,17.95,y-.31,y+.31,4.18,4.35,'warm_walnut')
 box('TRIAGE_admission_lens_'+str(i),16.15,17.85,y-.22,y+.22,4.15,4.18,'opal_lens',.008)
 FIXTURES.append({'name':'TRIAGE_admission_lens_'+str(i),'source_exit':(17,y,4.13),'aim':(17,y,0),'energy':350,'size':1.5,'profile':'guest_lounge','programme_child':'D05_directory_01_admission_clinical_route'})
# Recessed cross-corridor landmark is actually at the new junction, never a fake door.
box('TRIAGE_junction_map_back',19.58,19.80,10.35,13.65,1.2,2.85,'warm_walnut')
text('TRIAGE_junction_map_title','TRIAGE  01-08',(19.55,12,2.40),.30,(math.pi/2,0,-math.pi/2),role='ivory_enamel')
text('TRIAGE_junction_map_secondary','CARE ROOMS  /  STAFF ASSISTANCE',(19.54,12,1.88),.12,(math.pi/2,0,-math.pi/2),role='ivory_enamel')
# West source receiving remains physically capped pending the separate service network.
box('TRIAGE_west_service_cap',-14,-13.80,10,14,0,4.2,'sage_acoustic')
text('TRIAGE_service_receiver_label','STAFF CONNECTION  /  NOT IN SERVICE',(-13.78,12,2.15),.11,(math.pi/2,0,math.pi/2),role='ivory_enamel')
for i,x in enumerate([-10.5,-3.5,3.5,10.5]):
 for side,ya,yb in [('south',10,11.75),('north',12.25,14)]:
  low=[(x-3.5,ya,4.20 if ya==10 else 4.55),(x+3.5,ya,4.20 if ya==10 else 4.55),(x+3.5,yb,4.55 if yb==11.75 else 4.20),(x-3.5,yb,4.55 if yb==11.75 else 4.20)]
  mesh(f'TRIAGE_cross_vault_{i}_{side}',low+[(a,b,c+.14)for a,b,c in low],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'quiet_ivory')
 box('TRIAGE_cross_light_back_'+str(i),x-3.5,x+3.5,11.75,12.25,4.54,4.70,'warm_walnut')
 box('TRIAGE_cross_lens_'+str(i),x-1.1,x+1.1,11.82,12.18,4.49,4.54,'opal_lens',.008)
 FIXTURES.append({'name':'TRIAGE_cross_lens_'+str(i),'source_exit':(x,12,4.47),'aim':(x,12,0),'energy':430,'size':1.8,'profile':'guest_lounge','programme_child':'D05_directory_01_triage_cross_corridor'})

profile=[(10,4.16),(14,4.16),(14,4.20),(12.25,4.55),(11.75,4.55),(10,4.20)]
for label,xa,xb in [('west',-14,-13.80),('junction',13.90,14.20)]:
 n=len(profile);mesh('TRIAGE_cross_upper_closure_'+label,[(x,y,z)for x in[xa,xb]for y,z in profile],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'quiet_ivory')

# A full clinical room module with a free central manoeuvre square and separate service edge.
for number in range(1,9):
 column=(number-1)%4;upper=number<=4;cx=10.5-7*column;front=14 if upper else 10;angle=0 if upper else math.pi;ident=f'D05_directory_01_triage_pod_{number:02}';tag=f'TRIAGE_{number:02}';begin=len(PARTS)
 def P(u,v,z):return (cx+math.cos(angle)*u-math.sin(angle)*v,front+math.sin(angle)*u+math.cos(angle)*v,z)
 def local_mesh(name,verts,faces,role='quiet_ivory',bevel=.012):
  ob=mesh(tag+'_'+name,[P(*v)for v in verts],faces,role,bevel);ob['programme_child']=ident;return ob
 def B(name,u0,u1,v0,v1,z0,z1,role='quiet_ivory',bevel=.015):
  return local_mesh(name,[(u,v,z)for z in[z0,z1]for u,v in[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)
 def L(name,label,u,v,z,size=.18,role='clinical_ink',face_room=False):
  ob=text(tag+'_'+name,label,P(u,v,z),size,(math.pi/2,0,angle+(math.pi if face_room else 0)),role);ob['programme_child']=ident;return ob
 def path_local(name,points,width,z0,z1,role):
  transformed=[P(u,v,0)[:2]for u,v in points];ob=path(tag+'_'+name,transformed,width,z0,z1,role);ob['programme_child']=ident;return ob
 B('left_wall',-3.5,-3.3,0,5.36,0,4.2);B('right_wall',3.3,3.5,0,5.36,0,4.2)
 back=[(-3.4,5.30),(-3.28,5.58),(-3.00,5.82),(-2.80,5.90),(2.80,5.90),(3.00,5.82),(3.28,5.58),(3.4,5.30)]
 path_local('shaped_care_back',back,.20,0,4.2,'quiet_ivory');path_local('back_work_dado',back,.215,.12,.86,'sage_acoustic');path_local('back_service_cove',back,.22,3.46,4.05,'sage_acoustic')
 B('front_service_pier',-3.5,-.8,0,.20,0,4.2);B('front_other_pier',2.8,3.5,0,.20,0,4.2);B('portal_head',-.8,2.8,0,.20,2.65,4.2,'sage_acoustic')
 B('portal_left_receiver',-1.0,-.8,-.08,.26,0,2.72,'champagne_metal',.008);B('portal_right_receiver',2.8,3.0,-.08,.26,0,2.72,'champagne_metal',.008)
 # Source-open opaque paired leaves; no operating mechanism or pressure acceptance is claimed.
 for side,u0,u1 in [('left',-.90,-.82),('right',2.82,2.90)]:
  ob=B('privacy_leaf_'+side,u0,u1,.25,2.13,.08,2.57,'sage_acoustic',.022);ob['proposed_state']='source_open_inward';ob['operational_acceptance']=False
  B('leaf_'+side+'_upper_field',u0-.004,u1+.004,.35,2.02,1.65,2.37,'quiet_ivory',.01)
  B('leaf_'+side+'_kick_receiver',u0-.007,u1+.007,.30,2.07,.10,.28,'champagne_metal',.004)
  for v in [.42,1.93]:B('leaf_'+side+'_bearing_'+str(v),u0-.01,u1+.01,v-.045,v+.045,.38,2.35,'champagne_metal',.004)
 B('room_identity_back',-3.07,-1.20,-.065,0,1.48,2.60,'warm_walnut',.025)
 L('identity',f'TRIAGE  {number:02}',-2.14,-.079,2.23,.25,'ivory_enamel');L('identity_secondary','ADAPTABLE CARE',-2.14,-.081,1.83,.11,'ivory_enamel')
 DOORS.append({'programme_child':ident,'clear_width':3.6,'clear_height':2.65,'open_pose_leaf_stow_bands_local_u':[[-.90,-.82],[2.82,2.90]],'state':'Source-open prototype; shared-controller adoption and swept motion untested','portal_center_source':P(1,0,0)})
 # A shaped documentation console fills the service edge without entering the3.6m square.
 B('documentation_base',-3.10,-1.08,.30,.87,0,.80,'sage_acoustic',.04)
 poly=[(-3.18,.22),(-1.02,.22),(-1.02,.90),(-1.30,1.10),(-2.82,1.10),(-3.18,.90)];n=len(poly)
 local_mesh('documentation_ledge',[(u,v,z)for z in[.80,.89]for u,v in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'warm_walnut',.028)
 B('documentation_receiver',-2.88,-1.40,.23,.43,.89,1.52,'champagne_metal',.012);B('documentation_screen',-2.74,-1.54,.43,.455,1.08,1.43,'sage_acoustic',.012)
 L('documentation_state','CARE LINK / IDLE',-2.14,.466,1.26,.08,'ivory_enamel',True)
 for i,u in enumerate([-2.72,-2.44,-2.16,-1.88,-1.60]):B('source_control_'+str(i),u-.065,u+.065,.92,1.02,.90,.96,'champagne_metal',.012)
 # Clinical headwall is useful layered equipment architecture, not a painted stripe.
 B('headwall_back',-.48,2.82,5.70,5.80,.85,2.84,'sage_acoustic',.025)
 for u in [-.38,2.72]:B('headwall_receiver_'+str(u),u-.06,u+.06,5.60,5.72,.78,2.94,'champagne_metal',.009)
 B('headwall_upper_storage',-.30,2.62,5.40,5.71,2.30,2.78,'ivory_enamel',.025)
 for i,u in enumerate([.20,1.10,2.00]):
  B('headwall_cabinet_front_'+str(i),u-.39,u+.39,5.34,5.40,2.35,2.71,'quiet_ivory',.014);B('headwall_pull_'+str(i),u-.12,u+.12,5.29,5.34,2.48,2.54,'champagne_metal',.009)
 L('headwall_label','ASSISTANCE / SUPPORT',1.1,5.28,2.08,.10,'ivory_enamel')
 # Rear wash receiving matches the retained source's real back face.
 B('wash_receiver',-2.65,-.85,5.80,6.0,.08,1.62,'sage_acoustic')
 for z in [.6,1.25]:B('wash_receiver_crossbar_'+str(z),-2.57,-.93,5.76,5.80,z,z+.08,'champagne_metal',.006)
 for prototype,suffix,u,v,yaw in [('WashSupply','Wash',-1.75,5.42,0),('SupportPlatform','Platform',1.0,4.55,math.pi/2),('SupplyTrolley','SupplyTrolley',-2.80,4.48,0),('PrivacyReturn','StoredPrivacyReturn',-2.84,2.60,math.pi/2)]:clone_asset(prototype,f'Triage{number:02}_{suffix}',P(u,v,0),angle+yaw,ident)
 # Room canopy surfaces and visible fixture housings have real receivers.
 for j,(u0,u1)in enumerate([(-3.30,-.35),(.35,3.30)]):
  z0=4.26 if u0==-3.30 else 4.58;z1=4.58 if u1==-.35 else 4.26
  low=[(u0,.20,z0),(u1,.20,z1),(u1,5.80,z1),(u0,5.80,z0)]
  local_mesh('vault_'+str(j),low+[(u,v,z+.14)for u,v,z in low],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'quiet_ivory')
 profile=[(-3.30,4.20),(3.30,4.20),(3.30,4.26),(.35,4.58),(-.35,4.58),(-3.30,4.26)];n=len(profile)
 for end,v0,v1 in [('front',.05,.22),('rear',5.76,5.90)]:local_mesh('vault_end_receiver_'+end,[(u,v,z)for v in[v0,v1]for u,z in profile],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'quiet_ivory')
 B('vault_slot_receiver',-.35,.35,.20,5.80,4.57,4.73,'champagne_metal',.01)
 B('opal_housing',-.34,.34,1.45,3.45,4.47,4.60,'sage_acoustic',.02)
 B('opal_lens',-.25,.25,1.58,3.32,4.43,4.47,'opal_lens',.008)
 FIXTURES.append({'name':tag+'_opal_lens','source_exit':P(0,2.45,4.41),'aim':P(.15,3.0,0),'energy':430,'size':1.6,'profile':'staff_work','programme_child':ident})
 clone_asset('WaitingSconce_0',f'Triage{number:02}_TaskSconce',P(-1.75,5.80,2.40),angle,ident)
 FIXTURES.append({'name':f'Triage{number:02}_TaskSconce','source_exit':P(-1.75,5.56,2.45),'aim':P(-1.75,4.20,.80),'energy':85,'size':.25,'profile':'staff_work','programme_child':ident})
 # Lower roof bearing covers the perimeter join without a coplanar second underside.
 for side,u0,u1 in [('left',-3.40,-3.22),('right',3.22,3.40)]:B('ceiling_bearing_'+side,u0,u1,.20,5.35,4.20,4.38,'warm_walnut',.009)
 ROOMS.append({'programme_child':ident,'module_center_source_x':cx,'front_source_y':front,'orientation_z':angle,'gross_dimensions_m':[7,6],'source_parts':len(PARTS)-begin,'clear_interior_manoeuvre_local_uv':[[-.8,.25],[2.8,3.85]],'manoeuvre_height_m':2.4,'proposed_equipment_fit_only':True,'clinical_operation_accepted':False})

SCENE['scope']='Connected eight-pod source009 candidate plus retained008 welcome context. Unbuilt pod layout revision only; no Game/floor/compiler adoption or clinical gameplay.'
SCENE['preserved_existing_children']='D05_directory_01_local_waiting_and_escort_01;D05_directory_01_local_diagnostic_support_01'
SCENE['new_room_ids']=';'.join(x['programme_child']for x in ROOMS);SCENE['floor_ownership']='Existing compiler owner unchanged; proposed544m2additive union requires later owner-preserving compilation. No source floor slab.'
bpy.context.view_layer.update();records=[]
for ob in PARTS:
 v=[ob.matrix_world@p.co for p in ob.data.vertices];records.append({'name':ob.name,'programme_child':ob.get('programme_child'),'bounds_source_xyz':[list(map(min,zip(*v))),list(map(max,zip(*v)))],'vertices':len(v)})
REPORT={'run':RUN,'scope':SCENE['scope'],'source_frame':'Blender XYZ up, world=(sx-28,sz+21,-sy-446)','source_preimage':str(BASE/'source/D05_forward_welcome_008.blend'),'source_preimage_sha256':sha(BASE/'source/D05_forward_welcome_008.blend'),'proposed_unbuilt_layout_file':str(R/'qa/UNBUILT_TRIAGE_ARRANGEMENT_PROPOSAL.json'),'unchanged_existing_floor_owners':True,'explicit_existing_source_changes':CHANGES,'new_editable_parts':len(PARTS),'new_part_records':records,'retained_component_instances':RETAINED,'fixture_sources':FIXTURES,'receiver_markers':RECEIVERS,'rooms':ROOMS,'door_sources':DOORS,'clinical_targets_preserved':[20,4,12,8,6,2],'operational_acceptance':False,'capacity_acceptance':False,'runtime_adopted':False}
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE));bpy.ops.object.select_all(action='DESELECT')
for ob in PARTS:ob.select_set(True)
for ob in SCENE.objects:
 if ob.name.startswith('DATUM_')and ob.get('source_package')=='D05_forward_welcome_candidate':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',export_yup=True,use_selection=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
REPORT.update(source=str(SOURCE),source_sha256=sha(SOURCE),architecture_export=str(EXPORT),export_sha256=sha(EXPORT),generator_sha256=sha(__file__))
(R/'qa/SOURCE_MANIFEST_009.json').write_text(json.dumps(REPORT,indent=2)+'\n')
runpy.run_path(str(R/'source/check_loaded_wing.py'))
for p,h in PIN['inputs'].items():assert sha(p)==h,('Input changed during source build',p)
print('CONNECTED_TRIAGE_SOURCE009_READY',len(ROOMS),len(PARTS),len(RETAINED),str(SOURCE),flush=True)
