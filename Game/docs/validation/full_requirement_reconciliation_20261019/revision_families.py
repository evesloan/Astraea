import pathlib,json,re,hashlib,collections
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');rows=json.load(open(W/'SUCCESSOR_CONTRACT_TRACE.json'))['rows'];idx=json.load(open(W/'PROGRAMME_CHILD_INDEX.json'));actual=json.load(open(W/'ALL_CHILD_MESHES.json'))['rows'];names=collections.defaultdict(list)
for q in actual:
 for n in q['path'].split('/'):
  if len(names[n])<3:names[n].append(q['path'])
def family(s):
 s=pathlib.Path(s).stem.lower();s=re.sub(r'(^|_)r\d+[a-z]?(?=_|$)',r'\1',s);s=s.replace('_unbatched','').replace('_preview','');return re.sub('_+','_',s).strip('_')
assets=collections.defaultdict(list)
for p in (R/'Game').rglob('*.glb'):
 if any(x in p.parts for x in ['.godot','docs','tools']):continue
 rel='res://'+str(p.relative_to(R/'Game'));node=p.stem.replace('.','_');assets[family(p.name)].append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'observed_resource':rel in idx['resources'],'observed_root_name_examples':names.get(node,[])})
for q in rows:
 matches=assets[family(q['source_path'])];q['current_revision_family_candidates']=matches
 if q['source_path'].endswith('remaining_crew_bank_source_batch015/exports/AST-CRW-G3-003.glb'):
  q['triage']='INSTALLED_BOUNDED_NATIVE_SUCCESSOR';q['installation_receipt']='Game/docs/validation/remaining_crew_20261019/SUMMARY.json';q['protected_commit']='07e374a316a3e6bcd1db41f3b897b329f0bbba68'
 elif q['triage']=='RETAINED_PREDECESSOR_OR_UNRESOLVED_FAMILY' and any(m['observed_resource']or m['observed_root_name_examples']for m in matches):q['triage']='CURRENT_REVISION_FAMILY_OBSERVED_PREDECESSOR_DELTA_NOT_FULLY_AUDITED'
 elif q['triage']=='RETAINED_PREDECESSOR_OR_UNRESOLVED_FAMILY' and matches:q['triage']='CURRENT_REVISION_FAMILY_PRESENT_BINDING_REVIEW'
(W/'RETAINED_REVISION_FAMILY_REVIEW.json').write_text(json.dumps({'counts':dict(collections.Counter(q['triage']for q in rows)),'scope':'Per-file source retention and current revision-family triage. Family matching is not byte equivalence or full delta acceptance; no legacy version is installed solely because its name is unobserved.','rows':rows},indent=2)+'\n');print(collections.Counter(q['triage']for q in rows));print('unresolved',[(q['group'],q['source_path'])for q in rows if q['triage']=='RETAINED_PREDECESSOR_OR_UNRESOLVED_FAMILY'])
