import json,pathlib,re,collections,hashlib,csv
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');index=json.load(open(W/'PROGRAMME_CHILD_INDEX.json'));ps=index['programmes'];matrix=json.load(open(R/'Game/docs/validation/ship_scope_20261019/REQUIREMENT_MATRIX.json'));selectors=json.load(open(W/'special_selectors.json'));actual=json.load(open(W/'ALL_CHILD_MESHES.json'))['rows']
# Global search candidates remain explicitly unbound to programme/quantity unless a canonical key exists.
search=[(r['path'],r['path'].split('/')[-1]) for r in actual]
for p in ps.values():
 for contract in p.get('authored_batch_children',[]):
  for b in contract['batches']:
   for member in b['authored_members']:search.append((b['observed_paths'][0],member))
for key,p in ps.items():
 for child in p.get('authored_name_map',{}).get('children',[]):
  for path in child['observed_paths']:search.append((path,child['source_name']))
source_maps=json.load(open(R/'Game/docs/validation/ship_scope_20261019/HELPER_MODEL_CROSSWALK.json'))['models'];hash_refs=collections.defaultdict(list)
for m in source_maps:hash_refs[m['source_sha256']].append({'group':m['group'],'source_commit':m['source_commit'],'source_path':m['source_path'],'retention_path':m['retention_path']})
stop={'the','and','for','with','full','original','public','private','rooms','room','areas','area','center','centre','system','systems','of','in','on','or','inside','set'}
result=[]
for r in matrix['requirements']:
 if r['status']!='REQUIREMENT_SPECIFIC_RECONCILIATION_REQUIRED':continue
 a=r['authoritative_requirement'];keys=a.get('parent_programme_keys',a.get('programme_keys',[]));kind=a.get('kind',a.get('classification','unspecified'));rec={'id':r['id'],'name':r['name'],'authoritative_kind':kind,'canonical_programme_keys':keys,'accepted_complete':False,'evidence_scope':'Current installed children plus exact registered deferred sources and retained delivery hashes. Physical presence never certifies complete fit, operation, capacity or visual quality.'}
 linked=[]
 for key in keys:
  if key not in ps:continue
  p=ps[key];families=p['component_families'];resources=[index['resources'][s] for s in p['source_resources']];extra=p.get('deferred_source');batches=p.get('authored_batch_children',[])
  terms=[t for t in re.findall(r'[a-z]{4,}',r['name'].lower()) if t not in stop];matching=[f for f in families if any(t in f['name_pattern'].lower() for t in terms)]
  members=[{'name':n,'batch':b['batch_name'],'path':b['observed_paths'][0]} for c in batches for b in c['batches'] for n in b['authored_members'] if any(t in n.lower() for t in terms)]
  selected=matching if matching else sorted(families,key=lambda f:-f['mesh_nodes'])[:12]
  linked.append({'programme_key':key,'observed_child_mesh_nodes':p['actual_child_mesh_nodes'],'component_family_count':len(families),'representative_child_components':selected[:20],'name_specific_matches':len(matching),'authored_batch_member_matches':members[:20],'authored_batch_member_match_count':len(members),'installed_source_resources':resources,'deferred_source':{k:v for k,v in extra.items() if k!='source_node_names'} if extra else None,'deferred_child_examples':extra['source_node_names'][:15] if extra else [],'authored_name_map':({**{k:v for k,v in p['authored_name_map'].items() if k!='children'},'child_examples':p['authored_name_map']['children'][:15]} if p.get('authored_name_map') else None), 'retained_delivery_receipts':p['retained_delivery_receipts'],'helper_source_hash_joins':[{'sha256':res['sha256'],'retained_sources':hash_refs[res['sha256']]} for res in resources if hash_refs[res['sha256']]],'runtime_scope_metadata':[q['metadata'] for q in p['runtime_roots']]})
 rec['programme_child_evidence']=linked
 if linked:
  has_actual=any(p['observed_child_mesh_nodes'] for p in linked);has_deferred=any(p['deferred_source'] for p in linked)
  rec['reconciliation']='INSTALLED_CHILD_GEOMETRY_PARTIAL_REQUIREMENT' if has_actual else 'REGISTERED_DEFERRED_SOURCE_CHILDREN_VERIFIED' if has_deferred else 'PROGRAMME_ASSOCIATION_WITHOUT_VERIFIED_CHILD_GEOMETRY'
  rec['remaining_work']='Reconcile the named requirement against fitted dimensions, required subspaces/equipment and current interfaces; these child examples establish existing construction, not full completion.'
  if kind=='parent_programme':rec['remaining_work']='Existing source-backed construction is identified; detailed interior completeness and final visual review remain unaccepted. See separately enumerated child requirements where present.'
 else:
  domain,part=selectors[r['id']];dr=re.compile(domain,re.I);pr=re.compile(part,re.I);hits=[{'path':p,'child_name_or_authored_member':n} for p,n in search if dr.search(p) and pr.search(n)]
  # Keep exact matches and compact families, without converting names into completeness claims.
  unique={(h['path'],h['child_name_or_authored_member']):h for h in hits};hits=list(unique.values());rec['bounded_selector']={'path_domain':domain,'child_or_authored_member':part};rec['matching_child_count']=len(hits);rec['matching_child_examples']=hits[:20];rec['reconciliation']='INSTALLED_COMPONENT_CANDIDATES_REQUIRE_EXACT_SCOPE_BINDING' if hits else 'NO_MATCHING_CHILD_IDENTIFIED_IN_CURRENT_SEARCH'
  rec['remaining_work']='Candidate children need exact allocation/programme, dimensions and complete source-family binding; generic matching components do not prove the required room/system exists.' if hits else 'No matching child was identified by this bounded semantic search. Inspect retained native/delivery contracts before classifying as unbuilt or constructing a replacement.'
 rec['source_search_exhaustive']=False
 result.append(rec)
(W/'REMAINING_271_EVIDENCE.json').write_text(json.dumps({'base_commit':'042c4bb2f2d0e6ac11ac0eee8ac6738e48d163b6','requirements':result,'counts':dict(collections.Counter(x['reconciliation'] for x in result))},indent=2)+'\n')
with (W/'REVIEW_271.csv').open('w') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['id','name','reconciliation','keys','matching_children_or_families','examples'])
 for x in result:
  ev=x['programme_child_evidence'];names=[m['name_pattern'] for p in ev for m in p['representative_child_components'][:3]] if ev else [h['child_name_or_authored_member'] for h in x.get('matching_child_examples',[])[:3]]
  w.writerow([x['id'],x['name'],x['reconciliation'],';'.join(x['canonical_programme_keys']),sum(p['component_family_count'] for p in ev) if ev else x.get('matching_child_count',0),';'.join(names)])
print(collections.Counter(x['reconciliation'] for x in result));print('examined',len(result));print('no exact children',[(x['id'],x['name']) for x in result if x['reconciliation']=='NO_MATCHING_CHILD_IDENTIFIED_IN_CURRENT_SEARCH'])
