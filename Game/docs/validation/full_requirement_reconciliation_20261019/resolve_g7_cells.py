from pathlib import Path
import json,hashlib,re
R=Path('/workspace/Astraea');W=Path('/workspace/full-requirement-reconciliation-20261019');actual=json.load(open(W/'ALL_CHILD_MESHES.json'))['rows'];contracts=['Game/data/architecture/GROUP7_COMPLETION.json','Game/data/consolidated_all_eight_20261013/G7_ADDITIONAL.json'];rows=[]
for contract in contracts:
 d=json.load(open(R/contract))
 for q in d['models']:
  path=R/'Game/assets/models'/q['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==q['sha256'];root='/ShipSpace/Districts/Group7CompletionCandidate/'+q['cell'];children=[a['path']for a in actual if a['path'].startswith(root+'/')];assert children,(q['file'],root)
  rows.append({'contract':contract,'contract_sha256':hashlib.sha256((R/contract).read_bytes()).hexdigest(),'model':str(path.relative_to(R)),'sha256':q['sha256'],'cell':q['cell'],'source':q.get('source'),'observed_child_mesh_nodes':len(children),'examples':children[:3]})
(W/'GROUP7_EXACT_CELL_BINDINGS.json').write_text(json.dumps({'models':rows,'count':len(rows),'scope':'Exact active contract/model hashes joined to actual cell child paths. No new geometry or duplicate source installation.'},indent=2)+'\n');print('exact current Group7 model/cell joins',len(rows))
