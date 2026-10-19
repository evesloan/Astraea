import json,pathlib,hashlib,collections,struct
R=pathlib.Path('/workspace/Astraea');W=pathlib.Path('/workspace/full-requirement-reconciliation-20261019');p=W/'PROGRAMME_CHILD_INDEX.json';d=json.loads(p.read_text());old=json.load(open('/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json'))['rows'];actual=json.load(open(W/'ALL_CHILD_MESHES.json'))['rows'];byname=collections.defaultdict(list)
for r in actual:byname[r['path'].split('/')[-1]].append(r['path'])
# A deferred current source is inspected as source bytes, never credited as loaded geometry.
for s in json.load(open(R/'Game/data/architecture/REMAINING_BATCH_SECTIONS.json'))['sections']:
 k=s['key']
 if k not in d['programmes'] or d['programmes'][k]['actual_child_mesh_nodes']:continue
 f=R/('Game/'+s['runtime'][6:]);b=f.read_bytes();h=hashlib.sha256(b).hexdigest();assert h==s['hash'];n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);nodes=[x for x in g['nodes'] if 'mesh' in x];counts=collections.Counter(x['name'] for x in nodes)
 d['programmes'][k]['deferred_source']={'path':str(f.relative_to(R)),'sha256':h,'registered_source_receipt':'Game/data/architecture/REMAINING_BATCH_SECTIONS.json','source_mesh_nodes':len(nodes),'source_node_names':list(counts),'loaded_in_current_survey':False,'configured_translation':s['position']}
# Exact current Group8 batch names connect authored children to the installed batch model.
contracts=[]
for f in (R/'Game/data/architecture/group8').glob('*.json'):
 c=json.loads(f.read_text())
 if not isinstance(c,dict):continue
 bs=c.get('runtime_batches');model=c.get('model_file');expected=c.get('model_sha256')
 if not isinstance(bs,list) or not model or not expected:continue
 modelpath=R/'Game/assets/models'/model
 if not modelpath.exists():continue
 h=hashlib.sha256(modelpath.read_bytes()).hexdigest();assert h==expected,(f,model)
 instances=[r['path'].lstrip('/') for r in old if r['scene_source']=='res://assets/models/'+model]
 if not instances:continue
 bykey=collections.defaultdict(list)
 for b in bs:
  names=[path for path in byname[b['name']] if any(path.lstrip('/').startswith(i+'/') for i in instances)]
  if not names:continue
  k=b.get('programme_key')
  if k in d['programmes']:bykey[k].append({'batch_name':b['name'],'observed_paths':names,'authored_members':b.get('source_members',[]),'triangles_in_source_batch':b.get('triangles')})
 rec={'contract':str(f.relative_to(R)),'contract_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'model':str(modelpath.relative_to(R)),'model_sha256':h,'unbatched_export':c.get('unbatched_export'),'observed_model_instances':instances,'programme_batch_counts':{k:len(v) for k,v in bykey.items()}}
 contracts.append(rec)
 for k,items in bykey.items():d['programmes'][k].setdefault('authored_batch_children',[]).append({'contract':rec['contract'],'model':rec['model'],'model_sha256':h,'batches':items})
d['batch_contracts']=contracts;p.write_text(json.dumps(d,indent=2)+'\n');print('deferred source inventories',sum('deferred_source' in p for p in d['programmes'].values()),'exact installed batch contracts',len(contracts),'programmes with authored batch joins',sum('authored_batch_children' in p for p in d['programmes'].values()))
