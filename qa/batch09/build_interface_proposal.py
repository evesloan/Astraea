"""Build only a proposed index under Batch09; never mutate canonical standards/catalogue."""
from pathlib import Path
import json,hashlib,sys,subprocess,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09';BASE='620908833951216425172c95dfdb337ec33afc4c'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def binding(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
base=json.loads(subprocess.check_output(['git','show',BASE+':standards/catalogue_interfaces.json'],cwd=ROOT));proposal=json.loads(json.dumps(base));oldrows=json.loads(json.dumps(base['assets']));new=[];inventory=[]
meanings={
'AST-GST-001':('Floor origin at source Z0; the split runners retain their open front.','Floor-pad, switch and diffuser points are physical surfaces. Reading aim is a nonphysical direction target; clips and power-entry datums are static service proposals.'),
'AST-GST-002':('Wall plane source Y0, local mounting centre source Z0; not a floor origin.','Rear mount, rocker and diffuser points are physical surfaces. Reading aim is a nonphysical direction target. Service fasteners do not supply a removal trajectory.'),
'AST-GST-003':('Floor origin at source Z0.','Luggage slat, tray and shelf contacts are physical surfaces; open-landing and shelf-mouth centres are nonphysical receiver volumes. Three distinct open regions are preserved.'),
'AST-LIB-008':('Receiver contact plane source Z0; not a floor datum. Existing study receiver transforms are separate placements.','Shoe underside and diffuser are physical contact surfaces. Source centre is inside the represented housing, while service workspace and cable feed are proposals. No working illumination is supplied.'),
'AST-LIB-009':('Floor origin at source Z0.','Six static face-out title centres are proposed selection targets, not removable-book motion. Lower/upper stock is about 0.69/1.05 m; this is not universal reach approval. Lower storage has two real dividers.'),
'AST-LIB-010':('Floor origin at source Z0.','Display and separate search/index/back/select control points lie on their represented surfaces. Standing/seated points are pose proposals; the central void is not actor-fit or accessibility certification.')}
for family in ['guest_use','library_use']:
 auditpath=OUT/('independent_guest_interfaces.json' if family=='guest_use' else 'independent_library_interfaces.json');audit=json.loads(auditpath.read_text());assert audit['passed'];audits={a['id']:a for a in audit['assets']}
 for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];a=audits[ident]
  for b in a['bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
  sp=mp.parent/m['source'];gp=mp.parent/m['export'];g=Native(gp);j=g.g.doc;sr=json.loads((OUT/f'independent_source_{ident}.json').read_text());assert sr['sha256']==sha(sp)
  er=json.loads((OUT/f'independent_export_{ident}.json').read_text());assert er['sha256']==sha(gp) and not er['issues']
  roles=sorted(x['name'].removeprefix('ASTRAEA_') for x in er['materials']);assert roles==sorted(m['material_roles'])
  mr='physical_and_proposal_markers' if family=='guest_use'else'positions_and_normals';mref=str(mp.relative_to(ROOT));ev=lambda key:mref+'#/'+key
  rootnodes=[{'name':j['nodes'][i].get('name'),'index':i,'world_matrix_gltf_yup':g.world[i].tolist()}for i in j['scenes'][j.get('scene',0)]['nodes']]
  deps=mp.parent/'dependency_manifest.json';assert deps.exists()
  localgens=[mp.parent/m[k] for k in ['generator','texture_generator']if k in m]
  physicalcount=sum(bool(x.get('physical_contact_on_named_surface',x.get('physical_contact_on_native_surface',False)))for x in a['markers'])
  inv={'catalogue_id':ident,'source_export_manifest_bindings':{k:binding(p)for k,p in [('source',sp),('export',gp),('manifest',mp)]},'actual_marker_checks':a['markers'],'original_marker_records':m[mr],'collision_evidence':{'path':str(auditpath.relative_to(ROOT)),'sha256':sha(auditpath),'collision_shape_count':a['collision_shape_count'],'finite_segment_tests':len(a['void_and_blocked_tests'])},'actual_source_objects':len(sr['objects']),'runtime_external_uris':[b['uri']for b in j.get('buffers',[])+j.get('images',[])if 'uri'in b]}
  inventory.append(inv)
  row={'catalogue_id':ident,'family':family,'source_export_manifest_bindings':inv['source_export_manifest_bindings'],
  'units':{'status':'explicit_existing_file_or_catalogue_contract','value':'metres','evidence':[ev('source_frame' if family=='guest_use'else'units'),'standards/COORDINATE_CONTRACT.md#Axes-and-units']},
  'datum_and_pivot':{'status':'identified_existing_datum','meaning':meanings[ident][0],'evidence':[ev('pivot' if family=='guest_use'else'datum')],'actual_native_root_nodes':rootnodes},
  'source_and_native_frames':{'status':'identified_and_actual_native_hierarchy_read','source':'Blender source Z-up','exchange':'Native glTF Y-up','conversion':'(x,y,z) -> (x,z,-y)','rule':'Resolve actual native node parents. Do not convert native GLB transforms twice. Metadata points describe the neutral asset pose.','evidence':[ev('exchange_frame' if family=='guest_use'else'coordinate_contract'),str(auditpath.relative_to(ROOT))]},
  'connections_and_normals':{'status':'existing_interface' if ident in ['AST-GST-002','AST-LIB-008']else'no_modular_connector_claimed','meaning':'Existing wall/study support mounting datums and explicit outward directions.'if ident in ['AST-GST-002','AST-LIB-008']else'No modular seam connector is claimed; use the individual support/contact and approach proposals.','evidence':[ev(mr)]+([ev('compatible_mounts')]if ident=='AST-LIB-008'else[]),'omission_assessment':'No connector, reach guarantee, moving trajectory or runtime light is invented.'},
  'physical_contact_pose_and_origin':{'status':'existing_records_classified','meaning':meanings[ident][1],'evidence':[ev(mr),str(auditpath.relative_to(ROOT))],'native_physical_surface_witness_count':physicalcount,'limit':'Contact surfaces, housing source centres, opening/pose datums and service workspace have distinct semantics. No universal actor fit.'},
  'motion_and_hierarchy':{'status':'not_applicable_static_part','evidence':[ev('interaction_status' if family=='guest_use'else'runtime_status')],'native_animation_clips':len(j.get('animations',[])),'native_skin_count':len(j.get('skins',[])),'meaning':'Fixed represented controls, covers and stock. No moving descendant, operating control, removable trajectory, animation, physics or electrical behavior is supplied. Static marker hierarchy is preserved.'},
  'dependencies_and_material_roles':{'status':'existing_paths_and_role_mapping_inspected','evidence':[ev('generator'),ev('material_roles'),str(deps.relative_to(ROOT))],'actual_material_roles':roles,'material_match':True,'local_generator_files':[binding(p)for p in localgens],'runtime_external_uris':inv['runtime_external_uris'],'limit':'Self-contained GLBs do not alone prove generator restoration. Source-only execution is separately bound in the Batch09 review.'},
  'existing_independent_evidence':[str(auditpath.relative_to(ROOT)),f'qa/batch09/independent_export_{ident}.json',f'qa/batch09/independent_source_{ident}.json'],
  'findings':[],'exact_record_inventory_pointer':'qa/batch09/interface_coverage_map.json#/assets/'+str(len(inventory)-1),'engine_adopted_instances':0}
  new.append(row)
assert len(new)==6 and len({r['catalogue_id']for r in new})==6
proposal['assets']=oldrows+new;proposal['unique_assets']=51;proposal['revision']='astraea-catalogue-interfaces-02-proposed';proposal['status']='proposed_component_consumer_index_not_engine_acceptance'
proposal['audit_source']={'path':'qa/batch09/interface_coverage_map.json','report':'qa/batch09/interface_audit_report.md','correction_map':'qa/batch09/interface_proposed_corrections.json'}
proposal['binding_validation']={'exact_asset_id_set':True,'current_bound_files_checked':153,'all_files_current':all(sha(ROOT/b['path'])==b['sha256']for r in proposal['assets']for b in r['source_export_manifest_bindings'].values())}
assert proposal['binding_validation']['all_files_current'];assert proposal['assets'][:45]==base['assets']
canonical=lambda r:json.dumps(r,indent=2,ensure_ascii=False).encode()
assert all(canonical(a)==canonical(b)for a,b in zip(base['assets'],proposal['assets'][:45]))
(OUT/'interface_coverage_map.json').write_text(json.dumps({'assets':inventory,'baseline_commit':BASE,'preserved_original_record_count':45,'old_records_canonical_bytes_identical':True},indent=2)+'\n')
(OUT/'interface_normalized_index_proposed.json').write_text(json.dumps(proposal,indent=2)+'\n')
def raw_asset_records(text):
 decoder=json.JSONDecoder();pos=text.index('[',text.index('\"assets\"'))+1;result=[]
 while True:
  while text[pos].isspace()or text[pos]==',':pos+=1
  if text[pos]==']':break
  start=pos;_,pos=decoder.raw_decode(text,pos);result.append(text[start:pos].encode())
 return result
oldtext=subprocess.check_output(['git','show',BASE+':standards/catalogue_interfaces.json'],cwd=ROOT,text=True)
newtext=(OUT/'interface_normalized_index_proposed.json').read_text();assert raw_asset_records(oldtext)==raw_asset_records(newtext)[:45]
coverage=json.loads((OUT/'interface_coverage_map.json').read_text());coverage['old_records_raw_json_bytes_identical']=True
(OUT/'interface_coverage_map.json').write_text(json.dumps(coverage,indent=2)+'\n')
print('Proposed 51-row index written; original 45 raw JSON record bytes unchanged, six current native-hierarchy additions')
