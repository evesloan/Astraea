"""Prepare four-row extension preserving exact old61 row bytes; never promote."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';BASE='d1bd76caf5ef2a10992514b312f9e3464de47fb4'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
base_text=subprocess.check_output(['git','show',BASE+':standards/catalogue_interfaces.json'],cwd=ROOT,text=True);proposal=json.loads(base_text);old=proposal['assets'];assert len(old)==61
rebuild=json.loads((OUT/'independent_rebuild_receipts.json').read_text());assert rebuild['passed'];rb={x['family']:x for x in rebuild['families']}
profile=json.loads((OUT/'independent_collision_profile_review.json').read_text());pr={x['catalogue_id']:x for x in profile['assets']};new=[];inventory=[]
meanings={
 'AST-MED-001':'Supported original opaque privacy/arrival return with rigid screen on exposed sleeves/rod, true physical grip and declared finite privacy field. Source retains an editable linear prismatic action; closed/open GLBs are static state derivatives of one design. No host door or whole-room confidentiality.',
 'AST-MED-002':'Shaped wash basin and dry work surface with separate clean-supply shelves and front service cover. Real capped water/drain/control contacts remain unimplemented; no fluid, chemistry or treatment behavior.',
 'AST-MED-003':'Fixed neutral modular support platform with three equal removable pad forms, actual contact plateaux and optional under-edge attachment faces. No species posture, body/load/transfer suitability, powered lift/tilt or bed allocation.',
 'AST-MED-004':'Dedicated clinical supply trolley with protected staging surface, two closed original cases, open lower retrieval region and supported fixed wheel/fork/axle assemblies. Contents unspecified; no cleaning-cart, dynamics or medicine claim.'}
for family in ['clinical_architecture','clinical_support']:
 ap=OUT/('independent_'+family+'_interfaces.json');a=json.loads(ap.read_text());assert a['passed'];ar={x['id']:x for x in a['assets']}
 for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];r=ar[ident];sp=mp.parent/m['source'];gp=mp.parent/m['export'];s=json.loads((OUT/f'independent_source_{ident}.json').read_text());e=json.loads((OUT/f'independent_export_{ident}.json').read_text());assert s['sha256']==sha(sp) and e['sha256']==sha(gp) and not e['issues'];g=Native(gp);roles=sorted(x['name'].removeprefix('ASTRAEA_')for x in e['materials']);assert roles==sorted(m['material_roles'])
  for b in r['bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
  assert pr[ident]['source_sha256']==sha(sp) and pr[ident]['collision_sha256']==sha(mp.parent/m['collision_proposal_file'])
  roots=[{'index':i,'name':g.g.doc['nodes'][i].get('name'),'world_matrix_gltf_yup':g.world[i].tolist()}for i in g.g.doc['scenes'][g.g.doc.get('scene',0)]['nodes']]
  uri=[x['uri']for x in g.g.doc.get('buffers',[])+g.g.doc.get('images',[])if 'uri'in x];assert not uri
  bindings={k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp)]};marker_source=str((mp.parent/m['interface_api']).relative_to(ROOT))if m.get('interface_api')else str(mp.relative_to(ROOT))+'#/physical_and_proposal_markers'
  inventory.append({'catalogue_id':ident,'source_export_manifest_bindings':bindings,'interface_record_source':marker_source,'actual_marker_checks':r['markers'],'source_join_checks':r['joins'],'collision_proposal':bind(mp.parent/m['collision_proposal_file']),'empty_volume_checks':r['empty_volume_checks'],'source_dependency_closure':rb[family]['production_inputs']})
  new.append({'catalogue_id':ident,'family':family,'source_export_manifest_bindings':bindings,
   'units':{'status':'explicit_existing_file_or_catalogue_contract','value':'metres','evidence':['standards/COORDINATE_CONTRACT.md',str(mp.relative_to(ROOT))]},
   'datum_and_pivot':{'status':'identified_existing_datum','meaning':'Floor/contact datum at source origin; it can lie in intentional empty space. Host floor/support remains unknown.','actual_native_root_nodes':roots,'evidence':[str(mp.relative_to(ROOT)),str(ap.relative_to(ROOT))]},
   'source_and_native_frames':{'status':'identified_and_actual_native_hierarchy_read','source':'Blender Z-up, +X right, front -Y','exchange':'Native GLB Y-up, front +Z','conversion':'(x,y,z) -> (x,z,-y)','rule':'Resolve actual native parent hierarchy before placement; do not convert native geometry a second time.','evidence':['standards/COORDINATE_CONTRACT.md',str(ap.relative_to(ROOT))]},
   'connections_and_normals':{'status':'existing_physical_interfaces_and_proposed_placements','meaning':'Actual named source surfaces and native geometry carry physical contacts and supported joins. Proposed eye/approach/interaction positions are separate; capped ports are unimplemented.','evidence':[marker_source,str(ap.relative_to(ROOT))]+(['qa/batch12/independent_privacy_motion_review.json']if ident=='AST-MED-001'else[]),'omission_assessment':'Original host absent. Room polygons, doors, pockets, ceilings, floor/support and service reservations remain unknown.'},
   'physical_contact_pose_and_origin':{'status':'existing_records_classified','meaning':meanings[ident],'evidence':[marker_source,str(ap.relative_to(ROOT))],'native_physical_surface_witness_count':sum(x.get('physical_contact_on_named_surface',False)for x in r['markers']),'physical_surface_normals_independently_checked':True,'limit':'Component geometric witnesses only; no structural load, universal species fit or installed room acceptance.'},
   'motion_and_hierarchy':{'status':'source_linear_prismatic_action_and_native_static_state_derivatives'if ident=='AST-MED-001'else'not_applicable_static_part','native_animation_clips':len(g.g.doc.get('animations',[])),'native_skin_count':len(g.g.doc.get('skins',[])),'meaning':'Source SCREEN_TRANSLATION action moves left1.16m; actual closed/open native states and continuous own-support clearance independently checked. Both derivatives are one design; no game action, locking, damping or external-body sweep.'if ident=='AST-MED-001'else'Fixed component with no lift, shelf travel, fluid, wheel dynamics or operational behavior.','evidence':[marker_source,str(ap.relative_to(ROOT))]},
   'dependencies_and_material_roles':{'status':'actual_generator_read_closure_and_native_roles_inspected','actual_material_roles':roles,'material_match':True,'runtime_external_uris':uri,'local_generator_files':[bind(mp.parent/m['generator'])],'full_generator_input_closure':rb[family]['production_inputs'],'evidence':['qa/batch12/independent_rebuild_receipts.json'],'limit':'Every helper-loaded image role is included even when unused. State derivatives and QA arrangements are not new designs or host placements.'},
   'collision_proposal_screen':{'status':'component_geometry_not_runtime_adoption','shape_count':r['collision_shape_count'],'finite_clear_and_blocked_controls':len(r['void_and_blocked_tests']),'empty_box_volume_checks':len(r['empty_volume_checks']),'sampled_max_external_inflation_m':pr[ident]['sampled_max_external_inflation_m'],'evidence':[str(ap.relative_to(ROOT)),'qa/batch12/independent_collision_profile_review.json'],'limits':'Empty boxes use triangle/box and convex feasibility with0.2mm surface inset. Profile inflation is sampled, not a certified continuous upper bound. No actor/cart sweep or runtime physics.'},
   'existing_independent_evidence':[str(ap.relative_to(ROOT)),str((OUT/f'independent_source_{ident}.json').relative_to(ROOT)),str((OUT/f'independent_export_{ident}.json').relative_to(ROOT))],
   'findings':[],'exact_record_inventory_pointer':'qa/batch12/independent_interface_coverage_map.json#/assets/'+str(len(inventory)-1),'engine_adopted_instances':0})
assert len(new)==4 and len({x['catalogue_id']for x in new})==4
proposal['assets']=old+new;proposal['unique_assets']=65;proposal['revision']='astraea-catalogue-interfaces-05-proposed';proposal['status']='proposed_component_consumer_index_not_engine_acceptance';proposal['audit_source']={'path':'qa/batch12/independent_interface_coverage_map.json','report':'qa/batch12/independent_review.md'}
proposal['binding_validation']={'exact_asset_id_set':True,'current_bound_files_checked':195,'all_files_current':all(sha(ROOT/b['path'])==b['sha256']for r in proposal['assets']for b in r['source_export_manifest_bindings'].values())};assert proposal['binding_validation']['all_files_current']
def raw_records(text):
 decoder=json.JSONDecoder();pos=text.index('[',text.index('"assets"'))+1;rows=[]
 while True:
  while text[pos].isspace()or text[pos]==',':pos+=1
  if text[pos]==']':return rows
  start=pos;_,pos=decoder.raw_decode(text,pos);rows.append(text[start:pos].encode())
text=json.dumps(proposal,indent=2,ensure_ascii=False)+'\n'
# Preserve historical mixed Unicode escaping and every intra-row byte, not only decoded JSON values.
decoder=json.JSONDecoder();pos=text.index('[',text.index('"assets"'))+1;spans=[]
for _ in range(61):
 while text[pos].isspace()or text[pos]==',':pos+=1
 start=pos;_,pos=decoder.raw_decode(text,pos);spans.append((start,pos))
for (a,b),raw in reversed(list(zip(spans,raw_records(base_text)))):text=text[:a]+raw.decode()+text[b:]
assert raw_records(base_text)==raw_records(text)[:61]
assert json.loads(text)==proposal
(OUT/'independent_interface_normalized_index_proposed.json').write_text(text)
(OUT/'independent_interface_coverage_map.json').write_text(json.dumps({'executed_script_sha256':sha(Path(__file__)),'assets':inventory,'baseline_commit':BASE,'preserved_original_record_count':61,'old_records_raw_json_bytes_identical':True,'new_records':4,'proposed_total':65,'promoted':False},indent=2)+'\n')
print('Prepared65-row proposal; old61 raw row bytes preserved and195 current source/export/manifest bindings verified. Canonical index untouched.')
