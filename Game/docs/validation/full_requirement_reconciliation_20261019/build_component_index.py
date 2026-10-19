import json,pathlib,collections,re,hashlib,bisect
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');survey=json.load(open('/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json'));rows=survey['rows'];by_path={r['path'].lstrip('/'):r for r in rows};
for r in json.load(open(W/'ALL_CHILD_MESHES.json'))['rows']:
 key=r['path'].lstrip('/')
 if key not in by_path:rows.append(dict(r,metadata={},scene_source=r.get('scene_source','')))
programmes=json.load(open(R/'Game/docs/validation/ship_scope_20261019/PROGRAMME_MATRIX.json'))['programmes']
# Index actual child geometry only. Normalize detached residency paths, retaining attachment status.
indexed=sorted((r['path'].lstrip('/'),i) for i,r in enumerate(rows));paths=[p for p,i in indexed];parts={};assets={}
for p in programmes:
 found=set()
 for root in p['runtime_named_roots']:
  prefix=root['path'].lstrip('/')+'/';start=bisect.bisect_left(paths,prefix)
  for path,i in indexed[start:]:
   if not path.startswith(prefix):break
   found.add(i)
 children=[rows[i] for i in sorted(found)];meshes=[r for r in children if r['class'] in ['MeshInstance3D','MultiMeshInstance3D']];groups=collections.defaultdict(list)
 for r in meshes:
  name=r['path'].split('/')[-1];kind=re.sub(r'\d+','N',name);groups[kind].append(r['path'])
 refs=sorted(set(r['scene_source'] for r in children if r['scene_source'].startswith('res://') and r['scene_source'].endswith('.glb')))
 for ref in refs:
  if ref not in assets:
   f=R/('Game/'+ref[6:]);assets[ref]={'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
 parts[p['key']]={'programme_name':p['name'],'runtime_roots':p['runtime_named_roots'],'actual_child_mesh_nodes':len(meshes),'source_resources':refs,'component_families':[{'name_pattern':k,'mesh_nodes':len(v),'example_paths':v[:3]} for k,v in sorted(groups.items())],'retained_delivery_receipts':p['retained_source_receipts'],'current_source_references':p['current_source_references'],'scope':'Observed child geometry, not equipment function, complete room/species fit, contact or visual acceptance.'}
(W/'PROGRAMME_CHILD_INDEX.json').write_text(json.dumps({'survey_sha256':hashlib.sha256(pathlib.Path('/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json').read_bytes()).hexdigest(),'programmes':parts,'resources':assets},indent=2)+'\n')
print('161 programmes:',len(parts),'with actual child meshes:',sum(bool(p['actual_child_mesh_nodes']) for p in parts.values()),'resources:',len(assets))
print('no child meshes:',[(k,p['programme_name']) for k,p in parts.items() if not p['actual_child_mesh_nodes']])
