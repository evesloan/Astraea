"""Bounded preserved-source care receiver; no original room opening is cut."""
from pathlib import Path
import hashlib,json,math,struct,sys,copy
sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/shared/astraea_python_deps');sys.path.insert(0,str(Path(__file__).resolve().parent))
import shapely
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');GAME=ROOT/'Game';CAT=ROOT/'BlenderCatalogue';FIRST=CAT/'assets/group3_crew_service_20261009';PLAT=CAT/'assets/crew_service_platform';CARE=CAT/'assets/received_sections_20261008/B/05_crew_care';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
previous=FIRST/'extensions/dining_receiving_batch009';assert sha(previous/'SHA256SUMS.txt')=='1db77bab338ba034eb3e65e3375b6fe65e6d3771b05ea5f1392c24ab93389928'
for line in(previous/'SHA256SUMS.txt').read_text().splitlines():h,n=line.split('  ',1);assert sha(previous/n)==h
cat=json.loads((CAT/'catalogue_manifest.json').read_text());platform=next(q for q in cat['assets']if q['catalogue_id']=='AST-STF-010')
for aid in ['AST-STF-G3-015','AST-STF-G3-016','AST-STF-G3-017']:assert not any(q['catalogue_id']==aid and q.get('family')!='group3_crew_service_20261009'for q in cat['assets'])
for key in ['source','export']:assert sha(CAT/platform[key])==platform[key+'_sha256']
carepath=GAME/'assets/models/SOL_D03_directory_09_source001.glb';assert sha(carepath)=='5182dabca335a69a33ee935b207d30974c25085f3f9fe5690ea5a3d20ecb9712';care=GLB(carepath)
received=json.loads((GAME/'data/architecture/received_sections.json').read_text());row=next(q for q in received['sections']if q['programme_key']=='D03_directory_09');assert row['translation_xyz']==[-8,12,398]and row['rotation_y']==0
pinpaths=[GAME/'AGENTS.md',GAME/'docs/CURRENT_STATUS.md',GAME/'docs/master_source/MASTER_CURRENT_APPLICATION.json',GAME/'docs/master_source/MASTER_FULL_CONTENT_INDEX.json',GAME/'data/architecture/received_sections.json',GAME/'data/architecture/packages/received_sections/crew_connections/D03_directory_09.json',carepath,CARE/'source/native.blend',CARE/'source/build_used.py',CARE/'source/build_metadata.json',CARE/'docs/floor_proposal.json',PLAT/'source/geometry_parts.json',PLAT/'source/section_contract.json',PLAT/'source/make_contract.py',PLAT/'source/build_crew_service_platform.py',CAT/platform['source'],CAT/platform['export'],CAT/platform['manifest'],FIRST/'source/CREW_STREETS.json',FIRST/'exports/AST-STF-G3-001.glb',FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json',GAME/'data/generated/structural_meshes.json',GAME/'data/generated/received_structural_meshes.json',GAME/'scripts/received_sections_bootstrap.gd',GAME/'data/whole_ship_layout.json',GAME/'data/spatial_layout.json',GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json',CAT/'materials/staff/manifest.json',CAT/'catalogue_manifest.json']
pins={str(p.relative_to(ROOT)):sha(p)for p in pinpaths};base={'schema':1,'family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; D03 Y12','material_contract':'retained_lower_staff_network','fixtures':[],'source_pins':pins,'automatic_runtime_adoption':False,'new_people_berth_stop_stock_cart_or_save_identities':0,'protected_fore_port_blank_D04_D07_preserved':True}
original=json.loads((PLAT/'source/geometry_parts.json').read_text());selected=[];original_selected=[];targetroof=box(-55.2,420.02,-11.82,423.98)
for q in original:
 a,b,lo,hi,c,d=q['world_aabb'];shape=box(a,c,b,d);n=q['name'];out=None
 horizontal=n.startswith('CRW_Wall_')and b-a>.18 and d-c<=.181 and c>=420.02-1e-8 and d<=423.98+1e-8 and b>-55.06 and a<-12
 if horizontal:
  out=[max(a,-55.06),min(b,-12),lo,hi,c,d]
  # Only the north-side final wall/protection interval changes for the dogleg.
  if d<=420.2+1e-8:out[1]=min(out[1],-13.8)
 elif q['kind']=='ceiling_cap'and shape.intersection(targetroof).area>1e-8:
  clip=shape.intersection(targetroof);aa,cc,bb,dd=clip.bounds;out=[aa,bb,lo,hi,cc,dd]
 elif n.startswith('CRW_Task_')and c>421.7 and d<422.3 and a>-55.2 and b<-11.82:out=copy.deepcopy(q['world_aabb'])
 if out is None:continue
 original_selected.append(q)
 if min(out[1]-out[0],out[3]-out[2],out[5]-out[4])<=1e-8:continue
 selected.append({'name':n,'aabb':out,'role':q['role'],'category':'overhead'if q['kind']=='ceiling_cap'else('lighting_fixture'if n.startswith('CRW_Task_')else'screen_wall'),'batch_cell':'care_branch','retained_source_semantic_name':n,'retained_original_world_aabb':q['world_aabb'],'explicitly_clipped':out!=q['world_aabb']})
assert len([q for q in selected if q['name'].endswith('_Housing')])==3
contract=json.loads((PLAT/'source/section_contract.json').read_text());fixtures=[]
for i,l in enumerate(contract['light_markers']):
 x,y,z=l['xyz']
 if z!=422 or not -55.2<x<-11.82:continue
 housing=next(q for q in original_selected if q['name'].endswith('_Housing')and abs((q['world_aabb'][0]+q['world_aabb'][1])/2-x)<1e-6);stem=housing['name'].rsplit('_Housing',1)[0]
 fixtures.append({'name':f'CRW_TASK_LIGHT_DATUM_{i:03}','position':l['xyz'],'native_extras':{'catalogue_id':'AST-STF-010','datum_kind':'supported_staff_task_light','world_direction_godot_xyz':[0.,-1.,0.],'source_housing':housing['name'],'source_supports_json':json.dumps([stem+'_Hanger0',stem+'_Hanger1']),'source_role_family':l['catalogue_source'],'lowest_fixture_y':l['lowest_y'],'controller_owner':'parent runtime light integration; not installed'}})
branch=dict(base,catalogue_id='AST-STF-G3-016',parts=selected,fixtures=fixtures,retained_source_catalogue_id='AST-STF-010',retained_source_export=str((CAT/platform['export']).relative_to(ROOT)),retained_source_export_sha256=platform['export_sha256'],retained_source_blend=str((CAT/platform['source']).relative_to(ROOT)),retained_source_blend_sha256=platform['source_sha256'],retained_selected_original_components=original_selected,retained_selected_semantic_names=[q['name']for q in original_selected],exact_clipped_semantic_names=[q['name']for q in selected if q['explicitly_clipped']],exact_fully_omitted_selected_semantic_names=[q['name']for q in original_selected if q['name']not in {p['name']for p in selected}],north_side_dogleg_clip={'x':[-13.8,-12],'z':[420.02,420.2],'y':[12,15.2]},no_full_staff_platform_adoption=True,existing_reserved_gate_pose=[-54,12,422],original_full_port_preserved={'x':-12,'clear_z':[420.2,423.8]},adoption_rule='Load only this bounded retained branch subset, with explicit first-street end clips, selected cap clips and the north-side final dogleg aperture. Never also load the full AST-STF-010 or matching original component meshes. Existing room walls and the full original platform port remain unchanged.')
write(HERE/'source/CARE_REUSED_BRANCH.json',branch)
street=json.loads((FIRST/'source/CREW_STREETS.json').read_text());old=[q for q in street['parts']if q['name']in ['StreetWallLow_-7_52_0','StreetWallHigh_-7_52_0']];assert len(old)==2
patchparts=[]
for q in old:
 remaining=Polygon(q['boundary'],q['holes']).difference(box(-55.2,420.2,-55.06,423.8))
 for k,p in enumerate(shapely.get_parts(remaining)):
  if p.geom_type!='Polygon':continue
  x0,z0,x1,z1=p.bounds;patchparts.append({'name':q['name']+f'_retained_{k}','aabb':[x0,x1,*q['y'],z0,z1],'role':q['role'],'category':'screen_wall','batch_cell':q['batch_cell'],'original_semantic_name':q['name']})
names={q['role']+'|'+q['batch_cell']:'screen_wall_'+q['role']+'_'+q['batch_cell']for q in old};raw=(FIRST/'exports/AST-STF-G3-001.glb').read_bytes();native=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);assert all(sum(q.get('name')==n for q in native['nodes'])==1 for n in names.values())
patch=dict(base,catalogue_id='AST-STF-G3-017',parts=patchparts,runtime_batch_name_by_role_cell=names,retained_runtime_node_extras={'source_asset':'AST-STF-G3-001','construction_wip':True},original_semantic_parts=old,native_mesh_batches_to_omit_only_during_root_adoption=list(names.values()),original_export_path=str((FIRST/'exports/AST-STF-G3-001.glb').relative_to(ROOT)),original_export_sha256=sha(FIRST/'exports/AST-STF-G3-001.glb'),preserved_other_native_meshes=sum('mesh'in q for q in native['nodes'])-2,opening={'wall_x':[-55.2,-55.06],'clear_z':[420.2,423.8],'clear_y':[12,15.2]},automatic_source_replacement=False)
write(HERE/'source/CREW_STREET_CARE_PATCH.json',patch)
# The old port receives a same-width short pocket; it is never narrowed or
# silently closed. No five-metre terminal bay or room is invented.
route=[[-12,422],[-12,412],[-13.9,412]];clear=LineString(route).buffer(1.8,cap_style=2,join_style=2).union(box(-12,420.2,-10.2,423.8))
clear=clear.union(Polygon([[-13.9,410],[-12,410.2],[-12,413.8],[-13.9,414]])).union(box(-13.9,414,-13.8,418))
roomwalls=[];oldroof=[];retained_wall_components=[]
for q in care.doc['nodes']:
 if'mesh'not in q:continue
 a,b,lo,hi,c,d=care.bounds(q['name'],(-8,12,398))
 if q['name']in ['Pod_open_lower','Pod_open_upper']:roomwalls.append(box(round(a,6),round(c,6),round(b,6),round(d,6)));retained_wall_components.append({'name':q['name'],'actual_native_aabb':[a,b,lo,hi,c,d]})
 if q.get('extras',{}).get('role')=='folded_ceiling':
  vs=care.geometry(q['name'])[0];oldroof.append(Polygon([(v[0]-8,v[2]+398)for v in vs]).convex_hull)
oldroof=unary_union(oldroof);roomwalls=unary_union(roomwalls);branchwalls=unary_union([box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])for q in selected if q['category']=='screen_wall']);branchroof=unary_union([box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])for q in selected if q['category']=='overhead'])
existingbranchclear=box(-55.2,420.2,-12,423.8);wall=clear.buffer(.14,join_style=2).difference(clear.union(existingbranchclear)).difference(roomwalls.union(branchwalls));wall=wall.difference(box(-14.1,410,-13.7,414));roof=clear.buffer(.14,join_style=2).difference(oldroof.union(branchroof));parts=[]
def ceiling(z):return 15.25 if z<=418 else(15.2 if z>=419.84 else 15.25-(z-418)*.05/1.84)
def piece(name,p,bottom,top,role,category):
 vs=[];fs=[]
 for t in shapely.constrained_delaunay_triangles(p).geoms:
  xy=list(t.exterior.coords)[:3];k=len(vs);vs.extend([[x,bottom(z),z]for x,z in xy]+[[x,top(z),z]for x,z in xy]);fs.extend([[k+2,k+1,k],[k+3,k+4,k+5]])
 for ring in [list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1]for h in p.interiors]:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   k=len(vs);vs.extend([[a[0],bottom(a[1]),a[1]],[b[0],bottom(b[1]),b[1]],[b[0],top(b[1]),b[1]],[a[0],top(a[1]),a[1]]]);fs.append([k,k+1,k+2,k+3])
 parts.append({'name':name,'vertices_godot':vs,'faces':fs,'role':role,'category':category,'batch_cell':'care_dogleg','footprint_boundary':list(p.exterior.coords)[:-1],'footprint_holes':[list(h.coords)[:-1]for h in p.interiors]})
for band,(z0,z1)in enumerate([(408,418),(418,419.84),(419.84,426)]):
 for k,p in enumerate(shapely.get_parts(wall.intersection(box(-16,z0,-8,z1)))):
  if p.geom_type=='Polygon'and p.area>1e-8:
   piece(f'CareDoglegWallLow_{band}_{k}',p,lambda z:12,lambda z:13.03,'staff_bluegrey_paint','screen_wall');piece(f'CareDoglegWallHigh_{band}_{k}',p,lambda z:13.03,ceiling,'staff_white_paint','screen_wall')
 for k,p in enumerate(shapely.get_parts(roof.intersection(box(-16,z0,-8,z1)))):
  if p.geom_type=='Polygon'and p.area>1e-8:piece(f'CareDoglegRoof_{band}_{k}',p,ceiling,lambda z:ceiling(z)+.14,'staff_bluegrey_paint','overhead')
# One existing supported fixture profile is copied from the selected branch,
# at an explicit new source datum. It has no runtime identity or light binding.
housing=next(q for q in selected if q['name'].endswith('_Housing'));stem=housing['name'].rsplit('_Housing',1)[0];fixture_y=ceiling(417)
for suffix in ['Housing','Opal','Hanger0','Hanger1']:
 oldp=next(q for q in selected if q['name']==stem+'_'+suffix);a,b,lo,hi,c,d=oldp['aabb'];cx=(a+b)/2;cz=(c+d)/2
 # The reused long housing lies along X; this short dogleg has the same width.
 new=[a+(-12-((housing['aabb'][0]+housing['aabb'][1])/2)),b+(-12-((housing['aabb'][0]+housing['aabb'][1])/2)),lo+fixture_y-15.2,hi+fixture_y-15.2,c+417-422,d+417-422]
 parts.append({'name':'CareDoglegTask_'+suffix,'aabb':new,'role':oldp['role'],'category':'lighting_fixture','batch_cell':'care_dogleg','reused_fixture_profile':oldp['name']})
newlight={'name':'CareDoglegTaskDatum_SourceOnly','position':[-12,15.08,417],'native_extras':{'datum_kind':'supported_staff_task_light','world_direction_godot_xyz':[0.,-1.,0.],'source_housing':'CareDoglegTask_Housing','source_supports_json':json.dumps(['CareDoglegTask_Hanger0','CareDoglegTask_Hanger1']),'source_role_family':'Retained AST-STF-010 supported task fixture profile','lowest_fixture_y':15.065,'controller_owner':'parent existing receiving_source_lights / lighting_budget; source-only datum'}}
spec=dict(base,catalogue_id='AST-STF-G3-015',parts=parts,fixtures=[newlight],route={'points_xz':route,'clear_width_m':3.6,'existing_full_width_port_xz':[-12,422],'same_width_receiving_pocket_xz':[-12,-10.2,420.2,423.8],'quiet_pod_actual_opening':{'outer_wall_face_x':-13.9,'roof_edge_x':-14,'clear_z':[410,414],'floor_y':12,'roof_edge_underside_y':15.25},'roof_profile':'Y15.25 through Z418, linear to Y15.2 at Z419.84, then retained branch Y15.2','aft_original_inboard_entry_preserved':[-8,12,432]},original_received_pod_wall_components_reused=retained_wall_components,native_wall_boolean_mask_precision_m=.000001,original_received_opening_cut=False,original_room_or_furniture_changed=False,no_new_terminal_turn_bay_or_room=True,no_full_staff_platform_adoption=True,unfinished=['Missing floor/support is held; all original programmes and occupancy identities remain unchanged','Continuous loaded-cart turn, species, cupboard/door sweep, normal arrival, lighting and root adoption remain open','The aft arrival/conversation pod still uses its retained inboard entry; this source connects only the existing forward quiet/supply pod'])
write(HERE/'source/CARE_DOGLEG.json',spec)
compiledpath=GAME/'data/generated/structural_meshes.json';compiled=json.loads(compiledpath.read_text());addpath=GAME/'data/generated/received_structural_meshes.json';add=json.loads(addpath.read_text());assert add['source_checks']['baseline_structural_sha256']==sha(compiledpath);actual=unary_union([Polygon(t)for q in compiled['regions']+add['regions']if q['deck']=='D03'for t in q['triangles']]);crew=json.loads((FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').read_text());prior=unary_union([Polygon(q['boundary'],q['holes'])for q in crew['floor_proposal']['polygons']]);requested=box(-55.2,420.02,-11.82,423.98).union(clear.buffer(.14,join_style=2));missing=requested.difference(actual.union(prior));rows=lambda g:[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(g)if p.geom_type=='Polygon'and p.area>1e-8]
write(HERE/'source/CARE_MISSING_SUPPORT_PROPOSAL.json',{'deck':'D03','floor_y':12,'thickness':.24,'requested_area_m2':requested.area,'actual_compiled_overlap_m2':requested.intersection(actual).area,'frozen_first_street_proposed_overlap_only_m2':requested.difference(actual).intersection(prior).area,'new_missing_only_area_m2':missing.area,'polygons':rows(missing),'source_pins':pins,'general_floor_exported_or_installed':False,'adoption':'Root composes actual baseline/additive floors, previously held first-street support and only this new missing floor; structural bearing remains open.'})
layout=json.loads((GAME/'data/whole_ship_layout.json').read_text());others=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']=='D03'and q['programme_key']!='D03_directory_09']);body=json.loads((GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text());inner=Polygon(next(q for q in body['levels']if q['deck']=='D03')['inner_reservation_boundary']);spatial=json.loads((GAME/'data/spatial_layout.json').read_text());voids={q['id']:requested.intersection(Polygon(q['boundary'])).area for q in spatial['voids']if'D03'in q['decks']};crew_overlap=sum(requested.intersection(box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])).area for q in crew['instances'])
checks={'status':'PASS','new_dogleg_parts':len(parts),'reused_branch_components':len(selected),'clipped_branch_components':len(branch['exact_clipped_semantic_names']),'fully_omitted_branch_components':branch['exact_fully_omitted_selected_semantic_names'],'preserved_received_opening_width_m':4,'full_original_platform_port_preserved':True,'no_new_terminal_bay':True,'protected_200_crew_envelope_overlap_m2':crew_overlap,'other_D03_programme_overlap_m2':requested.intersection(others).area,'outside_conservative_hull_m2':requested.difference(inner).area,'protected_void_overlap_m2':voids,'new_missing_support_area_m2':missing.area,'duplicate_actual_or_prior_floor_m2':missing.intersection(actual.union(prior)).area,'new_wall_overlap_original_pod_wall_m2':wall.intersection(roomwalls).area,'new_wall_overlap_retained_branch_wall_m2':wall.intersection(branchwalls).area,'new_roof_duplicate_existing_roof_m2':roof.intersection(oldroof.union(branchroof)).area}
assert all(checks[k]<1e-7 for k in ['protected_200_crew_envelope_overlap_m2','other_D03_programme_overlap_m2','outside_conservative_hull_m2','duplicate_actual_or_prior_floor_m2','new_wall_overlap_original_pod_wall_m2','new_wall_overlap_retained_branch_wall_m2','new_roof_duplicate_existing_roof_m2'])and all(v<1e-7 for v in voids.values());write(HERE/'qa/CARE_PLAN_CHECKS.json',checks)
sections=[]
for y in [12.31,12.8,13.01,13.04,14.8,15.19]:
 for key in names:
  role,cell=key.split('|');before=unary_union([Polygon(q['boundary'],q['holes'])for q in old if q['role']==role and q['y'][0]<y<q['y'][1]]);after=unary_union([box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])for q in patchparts if q['role']==role and q['aabb'][2]<y<q['aabb'][3]]);error=after.symmetric_difference(before.difference(box(-55.2,420.2,-55.06,423.8))).area;sections.append({'world_y':y,'role':role,'cell':cell,'source_cross_section_error_m2':error,'pass':error<1e-8})
assert all(q['pass']for q in sections)
floor=actual.union(prior).union(missing);points=[[-57,12,422],[-51,12,422],[-39,12,422],[-27,12,422],[-16,12,422],[-12,12,422],[-11,12,422],[-12,12,419],[-12,12,416],[-12,12,412],[-14,12,412],[-15.5,12,412]];feet=[]
for p in points:
 f=Point(p[0],p[2]).buffer(.28);outside=f.difference(floor).area;feet.append({'floor_point':p,'actual_compiled_supported':f.difference(actual).area<1e-8,'outside_actual_or_explicit_proposed_floor_m2':outside,'pass':outside<1e-8})
assert all(q['pass']for q in feet);tri=[]
for p in shapely.get_parts(floor.intersection(box(-60,408,-8,426))):
 if p.geom_type=='Polygon':tri.extend([list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms])
write(HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json',{'status':'PASS','retained_street_cross_sections':sections,'bounded_floor_footprints':feet,'diagnostic_floor_triangles':tri,'floor_y':12,'floor_or_cutaway_exported_or_installed':False});print(json.dumps(checks))
