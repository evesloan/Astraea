from pathlib import Path
import json,hashlib,gzip,shutil,collections,csv,datetime
R=Path('/workspace/Astraea');W=Path('/workspace/full-requirement-reconciliation-20261019');D=R/'Game/docs/validation/full_requirement_reconciliation_20261019';D.mkdir(exist_ok=True)
idx=json.load(open(W/'PROGRAMME_CHILD_INDEX.json'));review=json.load(open(W/'REVIEWED_SUPPORTING_PROGRAMMES.json'));raw=json.load(open(W/'REMAINING_271_EVIDENCE.json'))
review['ENGS-027']['review']=review['ENGS-027']['review'].replace('default-main installed verification is pending this reconciliation','default-main installed verification also passes6233 checks; independently protected commit07e374a3')
for q in raw['requirements']:
 q['review_status']='SOURCE_AND_CURRENT_CHILD_EVIDENCE_RECONCILED_REQUIREMENT_UNFINISHED';q['construction_complete']=False
 if q['id']in review:
  note=review[q['id']];q['specific_review']=note;q['supporting_programme_evidence']=[]
  for k in note['supporting_programme_keys']:
   p=idx['programmes'][k];q['supporting_programme_evidence'].append({'programme_key':k,'name':p['programme_name'],'observed_mesh_children':p['actual_child_mesh_nodes'],'source_resources':[idx['resources'][s]for s in p['source_resources']],'registered_deferred_source':{a:b for a,b in p.get('deferred_source',{}).items()if a!='source_node_names'},'example_components':p['component_families'][:8],'authored_name_map':{a:b for a,b in p.get('authored_name_map',{}).items()if a!='children'}})
 else:
  q['specific_review']={'review':'Source-backed children or exact registered deferred source identified under the authoritative programme. Full interior equipment, interfaces, intended quantity and final visual acceptance are not implied. Existing construction must be retained; next work must target a demonstrated missing child or physical defect.','authoritative_allocation_changed':False}
raw.update(snapshot_geometry_commit='042c4bb2f2d0e6ac11ac0eee8ac6738e48d163b6',subsequent_verified_installation_commit='07e374a316a3e6bcd1db41f3b897b329f0bbba68',reviewed_rows=len(raw['requirements']),all_requirements_accepted_complete=False)
(D/'REMAINING_271_RECONCILIATION.json').write_text(json.dumps(raw,indent=2)+'\n')
for f in ['NAME_MAP_JOINS.json','special_selectors.json','build_component_index.py','extend_component_index.py','extend_name_maps.py','reconcile_all.py','finish_review_notes.py','trace_successor_contracts.py','revision_families.py','finalize_records.py']:
 shutil.copyfile(W/f,D/f)
(D/'REVIEWED_SUPPORTING_PROGRAMMES.json').write_text(json.dumps(review,indent=2)+'\n')
# Compact selective evidence, not another workspace archive.
compressed=[]
for f in ['ALL_CHILD_MESHES.json','PROGRAMME_CHILD_INDEX.json']:
 b=(W/f).read_bytes();out=gzip.compress(b,compresslevel=6,mtime=0);(D/(f+'.gz')).write_bytes(out);assert gzip.decompress(out)==b;compressed.append({'path':f+'.gz','compressed_sha256':hashlib.sha256(out).hexdigest(),'uncompressed_sha256':hashlib.sha256(b).hexdigest(),'uncompressed_bytes':len(b)})
(D/'COMPRESSED_EVIDENCE.json').write_text(json.dumps(compressed,indent=2)+'\n')
with (D/'REVIEW_271.csv').open('w')as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['id','requirement','source_child_disposition','review','complete'])
 for q in raw['requirements']:w.writerow([q['id'],q['name'],q['reconciliation'],q['specific_review']['review'],False])
shutil.copyfile('/workspace/ship-scope-reconciliation-20261019/REMOTE_VERIFICATION.json',D/'CREW_INSTALLATION_REMOTE_VERIFICATION.json')
summary={'status':'ALL_314_REQUIREMENT_ROWS_HAVE_SOURCE_CHILD_RECONCILIATION_FULL_SHIP_UNFINISHED','current_working_revision':'07e374a316a3e6bcd1db41f3b897b329f0bbba68','previous_cultural_rows':43,'additional_reviewed_rows':271,'total_nonadditive_requirement_rows':314,'canonical_programme_headings':161,'headings_with_actual_child_geometry_at_survey':147,'registered_deferred_programme_sources_verified_without_force_loading':14,'full_survey_mesh_or_multimesh_nodes':229027,'explicit_noncanonical_requirement_review_notes':77,'retained_name_maps':7,'name_map_observed_child_joins':sum(q['observed_child_joins']for q in json.load(open(W/'NAME_MAP_JOINS.json'))),'authored_batch_contract_programme_joins':sum(bool(p.get('authored_batch_children'))for p in idx['programmes'].values()),'installed_new_completed_source_assembly':'Group3 remaining crew bank batch015:183 source allocations,366 physical rests; bounded native receiving successor;6233 candidate and installed checks;4 pixel-reviewed local views.','no_duplicate_Group4_bindings_installed':True,'home_source_state':{'recorded_unfinished':186,'exact_pilot_exports_unlocated':2,'royalty790_lower_only_upper_design_gap':1},'final_ship_art_gameplay_species_capacity_acceptance':False,'remaining_scope':'Specific child completeness, unresolved exact source bindings and required new physical construction remain open. This is source/child reconciliation, not a completed-ship declaration.','geometry_snapshot':'Current-child survey is from042c4bb; exact additional crew installation verified separately at07e374a3.'}
(D/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
