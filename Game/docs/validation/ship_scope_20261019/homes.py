import json,pathlib,collections
R=pathlib.Path('/workspace/Astraea'); rows=json.load(open('/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json'))['rows']
sha_index={}; identities={}; citations=collections.defaultdict(list)
def walk(x,path):
 if isinstance(x,dict):
  index=x.get('source_envelope_index',x.get('census_source_index'))
  if isinstance(index,int):
   if x.get('allocation_sha256'):sha_index[x['allocation_sha256']]=index
   for k in ['existing_rebuild_identity','rebuild_identity']:
    if x.get(k):identities[x[k]]=index
   citations[index].append(path)
  for v in x.values():walk(v,path)
 elif isinstance(x,list):
  for v in x:walk(v,path)
for folder in ['Game/data','BlenderCatalogue/assets/residential_production_batch']:
 for p in (R/folder).rglob('*.json'):
  if '/packages/' in str(p) or p.stat().st_size>8_000_000:continue
  try:walk(json.loads(p.read_text()),str(p.relative_to(R)))
  except (ValueError,UnicodeError):pass
found=collections.defaultdict(list);unmatched=[]
for r in rows:
 m=r['metadata'];i=m.get('census_source_index')
 if i is None and m.get('allocation_sha256'):i=sha_index.get(m['allocation_sha256'])
 if i is None and m.get('rebuild_identity'):i=identities.get(m['rebuild_identity'])
 if i is None and m.get('retained_group2_home') and str(m.get('group2_source_key','')).isdigit():i=int(m['group2_source_key'])
 if i is not None:found[int(i)].append(r['path'])
 elif 'allocation_sha256'in m or 'rebuild_identity'in m:unmatched.append({'path':r['path'],'metadata':m})
census=json.load(open(R/'Game/data/reference/historical_guest_census.json'))['guest_envelopes']
missing=[{'index':i,'envelope':census[i],'matching_current_data_references':sorted(set(citations[i]))}for i in range(1000)if i not in found]
result={'scope':'Existing allocation index joins to observed current home roots. Not finished-unit, berth, persistent-identity or capacity acceptance. Missing means no matching home root in this survey, not proof that all possible source archives lack a source.','observed_unique_indices':len(found),'unmatched_home_roots':unmatched,'absent_indices':missing,'observed':dict(found)}
(R/'Game/docs/validation/ship_scope_20261019/ACCOMMODATION_MATRIX.json').write_text(json.dumps(result,indent=2)+'\n')
print('observed',len(found),'unmatched',len(unmatched),'absent',len(missing));print('absent by deck',collections.Counter(x['envelope']['deck']for x in missing));print('unmatched',[(x['path'],x['metadata'].get('rebuild_identity'))for x in unmatched]);print('D17 missing',[x['index']for x in missing if x['envelope']['deck']==17])
