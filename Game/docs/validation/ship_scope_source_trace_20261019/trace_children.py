import json,pathlib,hashlib,re,collections
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/ship-scope-reconciliation-20261019');O=R/'Game/docs/validation/ship_scope_source_trace_20261019'
rows=json.loads((W/'RUNTIME_SURVEY.json').read_text())['rows'];theater=[r for r in rows if 'GrandLanternTheater_ConnectedStaticStage_WIP' in r['path']];sem=collections.defaultdict(list)
for r in theater:
 m=r['metadata'];a=m.get('extras',{}).get('source_semantic_ids',[])
 if isinstance(a,str):a=json.loads(a)
 a=list(a)+([m['source_instance_id']] if 'source_instance_id' in m else [])+list(m.get('source_instance_ids',[]))+([m['source_motion_group']] if 'source_motion_group' in m else [])
 for s in a:sem[s].append(r['path'])
T={122:(r'^stalls_', 'Stalls chair instances observed; capacity/access acceptance separate.'),123:(r'^first_gallery_', 'First gallery chairs observed; upper receiving installed separately.'),124:(r'^crown_gallery_', 'Crown gallery chairs observed; upper receiving installed separately.'),125:(r'_royal_(port|starboard)_', 'Royal box chair instances observed; private access and complete enclosure require separate reconciliation.'),126:(r'^(stage_36x14|proscenium_)','Stage and proscenium source geometry observed.'),127:(r'theater_foyer_landings|THEATER_D1[123]_MAIN_LEAF', 'Foyer and entry geometry observed; only D11 main entry operation enabled in current runtime metadata.'),128:(r'balcony_lounge', 'No exact balcony-lounge semantic join found in this venue; source/design reconciliation remains open.'),129:(r'^THEATER_(LIFT_CABIN|D1[123]_LANDING_GATE)', 'Cabin and three landing-gate groups observed. Their operation_enabled metadata remains false; not an operating gallery lift.'),130:(r'^D1[12]_D1[23]_(F[1-4]_tread|turn_)','Native treads/turns observed; eight walking-contact successors also installed.'),131:(r'theater_(stalls_rake|gallery_seating|rear_public_returns)', 'Rake/gallery geometry observed; full named aisle/side-gallery reconciliation remains open.'),132:(r'^stage_access_ramp_1_in_12$', 'Authored stage ramp observed; no new accessibility acceptance inferred.'),133:(r'(viewing|transfer)_bay','No exact viewing/transfer bay semantic join located; presence cannot establish accessible viewing bays.'),134:(r'FP_.*stage|FP_FIXTURE_stage', 'Stage fixture geometry exists; original light performance is not established by fixture presence.')}
result=[]
for i,(pat,note) in T.items():
 matched={s:sorted(set(paths)) for s,paths in sem.items() if re.search(pat,s)}
 result.append({'requirement_id':f'AME-{i:03}','evidence_kind':'EXACT_RUNTIME_SOURCE_SEMANTIC_JOIN' if matched else 'NO_EXACT_CHILD_JOIN_LOCATED','selector':pat,'matched_semantic_count':len(matched),'source_semantics':matched,'interpretation':note,'status':'PARTIAL_PHYSICAL_EVIDENCE_OPERATION_UNFINISHED' if i in [125,127,129,131,134] and matched else 'CHILD_PHYSICAL_EVIDENCE_OBSERVED' if matched else 'CHILD_RECONCILIATION_OPEN','accepted_complete':False})
for cinema in range(1,7):
 key=f'D11_directory_{cinema+1:02}';scope=[r for r in rows if (key+'/' in r['path'] or (cinema==5 and 'Cinema5Receiving_WIP/' in r['path'])) and r['class']=='MeshInstance3D']
 patterns=[r'E_foyer_|E_outer_(west|east)_opening',r'E_booth_|E_projector_',r'E_aisle_step|E_return_ramp|E_rear_crossing',r'E_screen$|E_original_still_|E_screen_speaker|E_speaker_grille',r'E_transfer_place_marker']
 for j,pat in enumerate(patterns):
  matched=[r['path'] for r in scope if re.search(pat,r['path'].split('/')[-1])]
  status='CHILD_PHYSICAL_EVIDENCE_OBSERVED' if matched else 'CHILD_RECONCILIATION_OPEN'
  note=['Foyer furnishings and opening geometry observed; circulation acceptance separate.','Booth enclosure and projector geometry observed.','Raked aisle, return ramp and rear crossing geometry observed.','Screen and static original stills observed; animated abstract-short playback and audio not established.','Transfer-place marker is observed; usable viewing/transfer space requires dimensional reconciliation.'][j]
  if j in [3,4] and matched:status='PARTIAL_PHYSICAL_EVIDENCE_REQUIREMENT_OPEN'
  if cinema==1:status='SOURCE_LOCATED_RUNTIME_DEFERRED';note='Main survey has Cinema1Receiving_WIP stream_loaded=false. Existing received source and installation receipts are located; child geometry not loaded by this survey. Not classified as absent.'
  result.append({'requirement_id':f'AME-{135+(cinema-1)*5+j:03}','programme_key':key,'selector':pat,'evidence_kind':'EXACT_RUNTIME_MESH_NAME_JOIN' if matched else 'DEFERRED_OR_UNRESOLVED','matching_nodes':matched,'interpretation':note,'status':status,'accepted_complete':False})
pins={}
for p in [R/'Game/data/architecture/THEATER_RUNTIME_STAGE001.json',R/'Game/data/architecture/packages/theater/SOURCE_GEOMETRY_003.json',*[R/'Game/assets/models'/f for f in ['AST-CUL-005_static_003.glb','AST-CUL-005_moving_003.glb','AST-CUL-005_prototype_003.glb']]]:pins[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
out={'base_commit':'a101873cdd8df17eb9e49e7d810e16c0c5cefa76','survey_base_commit':'3833e6897e66420814a51f7b2c0c3a425f9967a1','survey_reuse':'No runtime or native changes between survey and this trace. Reuses actual attached/cached survey; never treats deferred visuals as absent.','non_additive':True,'pins':pins,'requirements':result,'counts':dict(collections.Counter(x['status'] for x in result)),'limits':'43 specific child rows examined. Other271 rows remain in existing matrix for continued reconciliation; no whole-programme acceptance.'}
(O/'CULTURAL_CHILD_EVIDENCE.json').write_text(json.dumps(out,indent=2)+'\n')
p=R/'Game/docs/validation/ship_scope_20261019/REQUIREMENT_MATRIX.json';d=json.loads(p.read_text());lookup={x['requirement_id']:x for x in result}
for r in d['requirements']:
 if r['id'] in lookup:
  x=lookup[r['id']];r.update(status=x['status'],child_evidence_receipt='Game/docs/validation/ship_scope_source_trace_20261019/CULTURAL_CHILD_EVIDENCE.json',interpretation=x['interpretation'])
p.write_text(json.dumps(d,indent=2)+'\n');print(out['counts'])
