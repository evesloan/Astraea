import json,pathlib,hashlib,collections,re
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');p=W/'PROGRAMME_CHILD_INDEX.json';d=json.load(open(p));actual=json.load(open(W/'ALL_CHILD_MESHES.json'))['rows'];by=collections.defaultdict(list)
for row in actual:by[row['path'].split('/')[-1]].append(row['path'])
manifest=json.load(open(R/'Game/data/architecture/crew_batch/runtime_manifest.json'))['sections'];joined=[]
for file in (R/'Game/data/architecture').rglob('*NODE_NAME_MAP.json'):
 rows=json.load(open(file));assert isinstance(rows,list);k=next((x for x in d['programmes']if any(x in q.get('runtime_name','') for q in rows)),None)
 if not k:
  k={'night_table':'D10_directory_07','laundry':'D01_directory_03'}.get(file.parent.name)
 if not k:continue
 programme=d['programmes'][k];roots=[q['path']for q in programme['runtime_roots']];links=[]
 for q in rows:
  if not q.get('runtime_name'):continue
  paths=[s for s in by[q['runtime_name']] if any(s.startswith(root+'/')for root in roots)]
  if paths:links.append({'source_name':q['source_name'],'runtime_name':q['runtime_name'],'observed_paths':paths})
 rec={'name_map':str(file.relative_to(R)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'mapped_rows':len(rows),'observed_child_joins':len(links),'children':links}
 programme['authored_name_map']=rec;joined.append({'key':k,**{a:b for a,b in rec.items()if a!='children'}})
p.write_text(json.dumps(d,indent=2)+'\n');(W/'NAME_MAP_JOINS.json').write_text(json.dumps(joined,indent=2)+'\n');print(joined)
