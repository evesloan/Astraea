exec(open('/workspace/ship-scope-reconciliation-20261019/reconcile.py').read().split('matrix=[]')[0])
asset_hashes=collections.defaultdict(list)
for p in (ROOT/'Game/assets').rglob('*.glb'):asset_hashes[digest(p)].append(str(p.relative_to(ROOT)))
observed=collections.defaultdict(list)
for r in rows:
 refs=[r['scene_source']]
 for k in ['catalogue_file','source_prototype_file']:
  value=r['metadata'].get(k)
  if isinstance(value,str):refs.append(value if value.startswith('res://') else 'res://assets/models/'+value)
 for ref in refs:
  if not ref.endswith('.glb'):continue
  p=ROOT/ref.replace('res://','Game/')
  if p.is_file():observed[str(p.relative_to(ROOT))].append(r['path'])
result=[]
for m in sorted((ROOT/'RetainedConstruction').glob('*/SOURCE_MAP.json')):
 d=json.loads(m.read_text())
 for f in d['files']:
  if not f['source_path'].endswith('.glb'):continue
  matches=asset_hashes.get(f['sha256'],[])
  live=[{'asset':p,'instances':len(observed[p]),'example':observed[p][0]}for p in matches if observed[p]]
  stored=ROOT/f['storage_path']
  result.append({'group':d['group'],'source_commit':d['source_commit'],'source_path':f['source_path'],'source_sha256':f['sha256'],'retention_path':f['storage_path'],'retention_exact':digest(stored)==f['sha256'] if stored.exists() else None,'current_exact_assets':matches,'observed_exact_instances':live,'status':'EXACT_SOURCE_OBSERVED'if live else 'CURRENT_FILE_BINDING_OR_DEFERRED_INSTANCE_REVIEW'if matches else 'SUCCESSOR_OR_INACTIVE_SOURCE_REVIEW'})
out=ROOT/'Game/docs/validation/ship_scope_20261019/HELPER_MODEL_CROSSWALK.json';out.write_text(json.dumps({'base_commit':base,'scope':'All runtime GLBs in seven initial helper source maps. Historical variants are included; unmatched rows are review candidates, never automatically missing sections. Later successors and deferred rooms require separate current bindings.','models':result},indent=2)+'\n')
print(collections.Counter(r['status']for r in result))
for g in range(2,9):print(g,dict(collections.Counter(r['status']for r in result if r['group']==g)))
for r in result:
 if r['status']=='CURRENT_FILE_BINDING_OR_DEFERRED_INSTANCE_REVIEW':print(r['group'],r['source_path'])
