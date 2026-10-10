"""Bounded actual breakroom mouth, reused branch and exact street successor."""
from pathlib import Path
import hashlib,json,struct,sys,copy
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');GAME=ROOT/'Game';CAT=ROOT/'BlenderCatalogue';FIRST=CAT/'assets/group3_crew_service_20261009';PLAT=CAT/'assets/crew_service_platform';BREAK=CAT/'assets/received_sections_20261008/B/06_custodian_breakroom'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
previous=FIRST/'extensions/d03_port2_branch_batch007';assert sha(previous/'SHA256SUMS.txt')=='4e43dce68f61a13d97b4a91da2f131134a229903a2822c35e23cbf754e9809f6'
for line in (previous/'SHA256SUMS.txt').read_text().splitlines():h,n=line.split('  ',1);assert sha(previous/n)==h
cat=json.loads((CAT/'catalogue_manifest.json').read_text());row=next(q for q in cat['assets']if q['catalogue_id']=='AST-STF-010')
for aid in ['AST-STF-G3-009','AST-STF-G3-010','AST-STF-G3-011']:assert not any(q['catalogue_id']==aid and q.get('family')!='group3_crew_service_20261009'for q in cat['assets'])
for key in ['export','source']:assert sha(CAT/row[key])==row[key+'_sha256']
received=json.loads((GAME/'data/architecture/received_sections.json').read_text());received=received['sections'];rr=next(q for q in received if q['programme_key']=='D03_directory_02')
assert rr['translation_xyz']==[8,12,-466] and rr['rotation_y']==0
breakexport=GAME/'assets/models/SOL_D03_directory_02_source001.glb';assert sha(breakexport)=='2b95b4951e121811d70db9497f6568b2a5b6161ce627c04b3d8edf1463448c5e'
pinpaths=[GAME/'AGENTS.md',GAME/'docs/CURRENT_STATUS.md',GAME/'docs/master_source/MASTER_CURRENT_APPLICATION.json',GAME/'docs/master_source/MASTER_FULL_CONTENT_INDEX.json',GAME/'data/architecture/received_sections.json',GAME/'data/architecture/packages/received_sections/crew_connections/D03_directory_02.json',breakexport,BREAK/'source/native.blend',BREAK/'build_used.py',BREAK/'build_metadata.json',PLAT/'source/geometry_parts.json',PLAT/'source/section_contract.json',PLAT/'source/make_contract.py',PLAT/'source/build_crew_service_platform.py',CAT/row['source'],CAT/row['export'],CAT/row['manifest'],FIRST/'source/CREW_STREETS.json',FIRST/'exports/AST-STF-G3-001.glb',FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json',GAME/'data/generated/structural_meshes.json',GAME/'data/whole_ship_layout.json',GAME/'data/spatial_layout.json',GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json',CAT/'materials/staff/manifest.json',CAT/'catalogue_manifest.json']
# Folder paths are retained exactly; locate the original received builder where present.
for i,p in enumerate(pinpaths):
 if not p.exists() and p.name in ['build_used.py','build_metadata.json']:pinpaths[i]=BREAK/'source'/p.name
pins={str(p.relative_to(ROOT)):sha(p)for p in pinpaths}
base={'schema':1,'family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; D03 Y12','material_contract':'retained_lower_staff_network','fixtures':[],'source_pins':pins,'automatic_runtime_adoption':False,'new_people_berth_stop_stock_cart_or_save_identities':0,'protected_fore_port_blank_D04_D07_preserved':True}
faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
parts=[]
def cube(name,a,role,category):parts.append({'name':name,'aabb':a,'role':role,'category':category,'batch_cell':'breakroom'})
def wedge(name,x0,x1,z0,z1,bot0,bot1,top0,top1,role,category):
 v=[[x,(bot0 if x==x0 else bot1),z]for z in [z0,z1]for x in [x0,x1]]+[[x,(top0 if x==x0 else top1),z]for z in [z0,z1]for x in [x0,x1]]
 parts.append({'name':name,'vertices_godot':v,'faces':faces,'role':role,'category':category,'batch_cell':'breakroom'})
for name,z0,z1 in [('North',-421.98,-421.8),('South',-418.2,-418.02)]:
 cube('ActualGap'+name+'Lower',[48.1,50.02,12,13.03,z0,z1],'staff_bluegrey_paint','screen_wall')
 wedge('ActualGap'+name+'Upper',48.1,50.02,z0,z1,13.03,13.03,15.25,15.2,'staff_white_paint','screen_wall')
 # Wall protection uses the existing service-platform profile and has no new interaction.
 if name=='North':zlo,zhi=-421.8,-421.77
 else:zlo,zhi=-418.23,-418.2
 cube('ActualGap'+name+'Bumper',[48.1,50.02,12.72,12.86,zlo,zhi],'staff_rubber','wall_protection')
# The first 0.1 m nib contacts the folded roof at its actual X48 edge.
cube('ReceivedFoldedRoofEdgeNib',[48,48.1,15.25,15.45,-421.98,-418.02],'staff_bluegrey_paint','overhead')
wedge('ActualGapRoofTransition',48.1,50.02,-421.98,-418.02,15.25,15.2,15.45,15.34,'staff_bluegrey_paint','overhead')
collar=dict(base,catalogue_id='AST-STF-G3-009',parts=parts,receiver={'programme_key':'D03_directory_02','actual_received_outer_wall_x':48.1,'actual_folded_roof_edge_x':48,'retained_platform_outer_jamb_x':50.02,'retained_platform_clear_port_x':50.2,'missing_enclosure_length_m':1.92,'center_z':-420,'clear_width_m':3.6,'ceiling_underside_endpoint_y':[15.25,15.2],'existing_reserved_gate_pose':[54,12,-420],'gate_and_controller_adoption':'Held; nominal gate clear height2.65 does not redefine existing physical ceiling'},actual_received_section_preserved=True,main_inboard_portal_preserved=[8,12,-432],floor_exported=False)
write(HERE/'source/BREAKROOM_COLLAR.json',collar)
original=json.loads((PLAT/'source/geometry_parts.json').read_text());selected=[]
for q in original:
 n=q['name'];keep=any(n.startswith('CRW_Wall_2_0_'+s)for s in ['59_0_0_','59_0_1_','60_0_0_','60_1_0_','61_0_0_','61_0_1_'])or n in ['CRW_Cap_27_9','CRW_Cap_28_9','CRW_Cap_29_9','CRW_Cap_30_9']or n.startswith('CRW_Task_2_0_')
 if not keep:continue
 a=copy.deepcopy(q['world_aabb']);old=copy.deepcopy(a)
 if n.startswith('CRW_Wall_2_0_59_0_1_')or n.startswith('CRW_Wall_2_0_61_0_1_'):a[1]=min(a[1],55.06)
 if n=='CRW_Cap_30_9':a[1]=55.2
 selected.append({'name':n,'aabb':a,'role':q['role'],'category':'overhead'if q['kind']=='ceiling_cap'else('lighting_fixture'if n.startswith('CRW_Task_')else'screen_wall'),'batch_cell':'breakroom','retained_source_semantic_name':n,'retained_original_world_aabb':old,'exact_clip':'Xmax55.06 first-street outer wall'if a[1]==55.06 and a!=old else('Xmax55.2 first-street roof edge'if a!=old else'unchanged')})
assert len(selected)==32
light={'name':'CRW_TASK_LIGHT_DATUM_150','position':[52.7,15.03,-420],'source_existing_semantic_fixture':'CRW_Task_2_0; no new controller','native_extras':{'catalogue_id':'AST-STF-010','datum_kind':'supported_staff_task_light','world_direction_godot_xyz':[0.,-1.,0.],'source_housing':'CRW_Task_2_0_Housing','source_supports_json':json.dumps(['CRW_Task_2_0_Hanger0','CRW_Task_2_0_Hanger1']),'source_role_family':'AST-STF-009 supported task fixture profile; AST-STF-006 role family','lowest_fixture_y':15.015,'controller_owner':'parent runtime light integration; not installed'}}
branch=dict(base,catalogue_id='AST-STF-G3-010',parts=selected,fixtures=[light],retained_source_catalogue_id='AST-STF-010',retained_source_export=str((CAT/row['export']).relative_to(ROOT)),retained_source_export_sha256=row['export_sha256'],retained_source_blend=str((CAT/row['source']).relative_to(ROOT)),retained_source_blend_sha256=row['source_sha256'],retained_selected_semantic_names=[q['name']for q in selected],exact_clipped_semantic_names=[q['name']for q in selected if q['aabb']!=q['retained_original_world_aabb']],no_full_staff_platform_adoption=True,adoption_rule='Use this bounded thirty-two-component retained branch subset. Do not also load AST-STF-010 or its matching branch meshes. The first crew street owns the longitudinal corridor and roof from X55.2; only its two blocking wall nodes are replaced by the separate exact successor.')
write(HERE/'source/BREAKROOM_REUSED_BRANCH.json',branch)
street=json.loads((FIRST/'source/CREW_STREETS.json').read_text());old=[q for q in street['parts']if q['name']in ['StreetWallLow_6_-53_0','StreetWallHigh_6_-53_0']];assert len(old)==2
new=[]
for q in old:
 for suffix,z0,z1 in [('north',-424,-422.5),('south',-417.5,-416)]:new.append({'name':q['name']+'_'+suffix,'aabb':[55.06,55.2,*q['y'],z0,z1],'role':q['role'],'category':'screen_wall','batch_cell':'6_-53','original_semantic_name':q['name']})
names={q['role']:'screen_wall_'+q['role']+'_6_-53'for q in old}
raw=(FIRST/'exports/AST-STF-G3-001.glb').read_bytes();native=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);assert all(sum(q.get('name')==n for q in native['nodes'])==1 for n in names.values())
patch=dict(base,catalogue_id='AST-STF-G3-011',parts=new,runtime_batch_name_by_role=names,retained_runtime_node_extras={'source_asset':'AST-STF-G3-001','construction_wip':True,'batch_cell':'6_-53'},original_semantic_parts=old,native_mesh_batches_to_omit_only_during_root_adoption=list(names.values()),original_export_path=str((FIRST/'exports/AST-STF-G3-001.glb').relative_to(ROOT)),original_export_sha256=sha(FIRST/'exports/AST-STF-G3-001.glb'),preserved_other_native_meshes=sum('mesh'in q for q in native['nodes'])-2,opening={'wall_x':[55.06,55.2],'clear_z':[-422.5,-417.5],'clear_y':[12,15.2]},automatic_source_replacement=False,adoption_rule='At root adoption omit exactly the two named original crew-street wall meshes and substitute these two successor meshes. Keep all other original meshes, floor proposals and light markers. Do not load original walls alongside this opening.')
write(HERE/'source/CREW_STREET_BREAKROOM_PATCH.json',patch)
compiledpath=GAME/'data/generated/structural_meshes.json';compiled=json.loads(compiledpath.read_text());actual=unary_union([Polygon(t)for q in compiled['regions']if q['deck']=='D03'for t in q['triangles']]);crew=json.loads((FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').read_text());prior=unary_union([Polygon(q['boundary'],q['holes'])for q in crew['floor_proposal']['polygons']])
requested=box(48,-421.98,50.02,-418.02).union(box(50.02,-422.68,55.2,-417.32));missing=requested.difference(actual.union(prior));rows=lambda g:[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(g)if p.geom_type=='Polygon'and p.area>1e-8]
floor={'deck':'D03','floor_y':12,'thickness':.24,'requested_area_m2':requested.area,'actual_compiled_overlap_m2':requested.intersection(actual).area,'frozen_first_street_proposed_overlap_only_m2':requested.difference(actual).intersection(prior).area,'new_missing_only_area_m2':missing.area,'polygons':rows(missing),'source_pins':pins,'general_floor_exported_or_installed':False,'adoption':'Root composes actual D03 cap, frozen first-crew-street held floor and only this additional missing support. Actual bearing and hull supports remain separate acceptance.'}
write(HERE/'source/BREAKROOM_MISSING_SUPPORT_PROPOSAL.json',floor)
body=json.loads((GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text());inner=Polygon(next(q for q in body['levels']if q['deck']=='D03')['inner_reservation_boundary']);spatial=json.loads((GAME/'data/spatial_layout.json').read_text());voids={q['id']:requested.intersection(Polygon(q['boundary'])).area for q in spatial['voids']if'D03'in q['decks']};crew_overlap=sum(requested.intersection(box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])).area for q in crew['instances'])
layout=json.loads((GAME/'data/whole_ship_layout.json').read_text());otherprogrammes=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']=='D03'and q['programme_key']!='D03_directory_02'])
checks={'status':'PASS','actual_missing_enclosure_length_m':1.92,'new_collar_parts':len(parts),'reused_branch_components':len(selected),'reused_components_explicitly_clipped':len(branch['exact_clipped_semantic_names']),'street_original_semantic_parts_replaced':2,'street_successor_parts':len(new),'street_native_meshes_to_omit':list(names.values()),'other_original_native_meshes_preserved':patch['preserved_other_native_meshes'],'protected_200_crew_envelope_overlap_m2':crew_overlap,'other_D03_programme_overlap_m2':requested.intersection(otherprogrammes).area,'outside_conservative_hull_m2':requested.difference(inner).area,'protected_void_overlap_m2':voids,'new_missing_support_area_m2':missing.area,'duplicate_actual_or_previously_proposed_support_m2':missing.intersection(actual.union(prior)).area,'new_collar_floor_fully_actual_supported':box(48,-421.98,50.02,-418.02).difference(actual).area<1e-8,'source_only':True}
assert all(checks[k]<1e-7 for k in ['protected_200_crew_envelope_overlap_m2','other_D03_programme_overlap_m2','outside_conservative_hull_m2','duplicate_actual_or_previously_proposed_support_m2']) and all(v<1e-7 for v in voids.values()) and checks['new_collar_floor_fully_actual_supported']
write(HERE/'qa/BREAKROOM_PLAN_CHECKS.json',checks)
sections=[]
for y in [12.31,12.8,13.01,13.04,14.8,15.19]:
 for role in names:
  before=unary_union([Polygon(q['boundary'],q['holes'])for q in old if q['role']==role and q['y'][0]<y<q['y'][1]]);after=unary_union([box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])for q in new if q['role']==role and q['aabb'][2]<y<q['aabb'][3]]);error=after.symmetric_difference(before.difference(box(55.06,-422.5,55.2,-417.5))).area;sections.append({'world_y':y,'role':role,'source_cross_section_error_m2':error,'pass':error<1e-8})
assert all(q['pass']for q in sections)
floors=actual.union(prior).union(missing);points=[[47.5,12,-420],[48.1,12,-420],[49,12,-420],[50.2,12,-420],[52.7,12,-420],[54.5,12,-420],[55.3,12,-420],[57,12,-420],[57,12,-422.6],[57,12,-417.4]];feet=[]
for p in points:
 f=Point(p[0],p[2]).buffer(.28);outside=f.difference(floors).area;feet.append({'floor_point':p,'actual_compiled_supported':f.difference(actual).area<1e-8,'outside_actual_or_explicit_proposed_floor_m2':outside,'pass':outside<1e-8})
assert all(q['pass']for q in feet)
tri=[]
for p in shapely.get_parts(floors.intersection(box(42,-427,60,-413))):
 if p.geom_type=='Polygon':tri.extend([list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms])
write(HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json',{'status':'PASS','retained_street_cross_sections':sections,'bounded_floor_footprints':feet,'diagnostic_floor_triangles':tri,'floor_y':12,'floors_exported_or_installed':False})
print(json.dumps(checks))
