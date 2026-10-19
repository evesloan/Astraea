import pathlib,json,re,collections,hashlib
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');rows=json.load(open(R/'Game/docs/validation/ship_scope_20261019/HELPER_MODEL_CROSSWALK.json'))['models'];pending=[q for q in rows if q['status']=='SUCCESSOR_OR_INACTIVE_SOURCE_REVIEW'];hashes={q['source_sha256']for q in pending};pat=re.compile('|'.join(sorted(hashes)));mentions=collections.defaultdict(list)
for folder in ['Game/scripts','Game/data']:
 for f in (R/folder).rglob('*'):
  if f.suffix not in ['.json','.gd'] or any(x in str(f).lower()for x in ['dependency_preimages','retained_current','runtime_proof','scope_audit','scope_index']):continue
  s=f.read_text(errors='replace')
  for m in pat.finditer(s):mentions[m.group()].append({'path':str(f.relative_to(R)),'contract_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'context':s[max(0,m.start()-100):m.end()+100]})
out=[]
for q in pending:
 refs=mentions[q['source_sha256']];out.append({**q,'current_contract_mentions':refs,'triage':'REJECTED_OR_FAILED_RETAINED_CANDIDATE'if any(s in q['source_path'].lower()for s in ['/qa/','reject','failed'])else 'CURRENT_CONTRACT_REFERENCES_RETAINED_SOURCE'if refs else 'RETAINED_PREDECESSOR_OR_UNRESOLVED_FAMILY','acceptance':'References are provenance/receiving clues, not automatic runtime adoption proof. No missing geometry is inferred from a filename.'})
(W/'SUCCESSOR_CONTRACT_TRACE.json').write_text(json.dumps({'rows':out,'counts':dict(collections.Counter(q['triage']for q in out))},indent=2)+'\n');print(collections.Counter(q['triage']for q in out))
