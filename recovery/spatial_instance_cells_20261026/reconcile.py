from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();G=R/'Game';out=R/'recovery/spatial_instance_cells_20261026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tracked=subprocess.check_output(['git','ls-files','Game/*CONTRACT*.json'],text=True).splitlines()
changed=set(json.loads((out/'CHANGED_PATHS.json').read_text()))-{'res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json'}
pre={}
for _ in range(12):
 progress=False
 for rel in tracked:
  if rel.endswith('SOURCE_CONTRACTS.json'):continue
  p=R/rel;raw=p.read_bytes();d=json.loads(raw)
  def visit(v):
   if isinstance(v,dict):
    for k,x in v.items():
     if k in changed and isinstance(x,str) and len(x)==64:
      expected=sha(G/k.removeprefix('res://'))
      if x!=expected:v[k]=expected
     else:visit(x)
   elif isinstance(v,list):
    for x in v:visit(x)
  before=json.dumps(d);visit(d)
  if json.dumps(d)!=before:
   if rel not in pre:pre[rel]=raw
   p.write_bytes((json.dumps(d,indent=2)+'\n').encode());changed.add('res://'+p.relative_to(G).as_posix());progress=True
 if not progress:break
else:raise RuntimeError('cycle')
for rel,raw in pre.items():
 p=out/'preimages'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
p=G/'scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';d=json.loads(p.read_bytes());seen=set()
for row in d:
 if row['path'] in changed:
  q=G/row['path'].removeprefix('res://');row.update(sha256=sha(q),bytes=q.stat().st_size);seen.add(row['path'])
for path in sorted(changed-seen):
 q=G/path.removeprefix('res://');d.append(dict(path=path,sha256=sha(q),bytes=q.stat().st_size))
p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
(out/'CHANGED_PATHS.json').write_text(json.dumps(sorted(changed|{'res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json'}),indent=2))
print(json.dumps({'contracts':len(d),'changed':sorted(changed),'preimages':len(pre)}))
