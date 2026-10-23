from pathlib import Path
import json,hashlib,re,collections
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'recovery/release_operations_fix_20261023';O=P/'payload';B=R/'recovery/quiet_d14_chain_fix/payload';sha=lambda b:hashlib.sha256(b).hexdigest()
def base(rel):return(B/rel).read_bytes()if(B/rel).exists()else(R/rel).read_bytes()
def historical(rel):
 parts=Path(rel).parts
 return any(x in ['docs','tests','source_derivatives','.godot','dependency_preimages','dependency_graph_preimages','predecessors300']or x.startswith('retained')for x in parts) or ('/evidence/'in rel and Path(rel).name not in ['INPUT_PINS.json','GUARD_PLAN.json']) or '/d04_surface_cells_20261023/'in rel
files={str(p.relative_to(R))for p in(R/'Game').rglob('*')if p.is_file()and p.suffix in ['.gd','.json','.tscn','.cfg']}
files.update(str(p.relative_to(Path('/tmp/release_operations_base/payload')))for p in Path('/tmp/release_operations_base/payload').rglob('*')if p.is_file())
manifest='Game/scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';files.discard(manifest)
original={};hashes={};reverse=collections.defaultdict(set)
for rel in files:
 if historical(rel):continue
 try:b=base(rel)
 except FileNotFoundError:b=None
 hashes[rel]=sha(b)if b is not None else None
 op=Path('/tmp/release_operations_base/payload')/rel
 source=op.read_bytes()if op.exists()else b
 if source is None:continue
 text=source.decode();original[rel]=text
 for h in set(re.findall(r'\b[0-9a-f]{64}\b',text)):reverse[h].add(rel)

def normalize(s):
 if not isinstance(s,str):return None
 if s.startswith('res://'):return'Game/'+s[6:]
 if s.startswith(('Game/','BlenderCatalogue/')):return s
 if s.startswith(('scripts/','data/','assets/','scenes/')):return'Game/'+s
 return None
current={rel:sha(text.encode())for rel,text in original.items()};edges=set();unresolved=[]
for iteration in range(80):
 changed={rel:(hashes.get(rel),h)for rel,h in current.items()if h!=hashes.get(rel)}
 byold=collections.defaultdict(list)
 for target,(old,new)in changed.items():
  if old:byold[old].append((target,new))
 candidates=set().union(*(reverse.get(old,set())for old in byold))if byold else set()
 updated=False;unresolved=[]
 for rel in sorted(candidates):
  text=original[rel];used=[]
  if rel.endswith('.json'):
   data=json.loads(text)
   def visit(v,trail=()):
    if isinstance(v,list):return[visit(x,trail+(i,))for i,x in enumerate(v)]
    if not isinstance(v,dict):return v
    out={}
    paths={normalize(x)for x in v.values()if isinstance(x,str)}
    for k,value in v.items():
     if isinstance(value,str)and value in byold:
      choices=[(t,n)for t,n in byold[value]if normalize(k)==t or t in paths]
      if rel.endswith('/delivery_quiet_d14_20261023/COMPOSITION.json')and k=='receipt_sha256':choices=[(t,n)for t,n in byold[value]if t=='Game/data/quiet_d14_receiving_20261016/RECEIPT.json']
      if len(choices)==1:
       t,n=choices[0];out[k]=n;used.append((rel,t,value,n,str(trail+(k,))));continue
     out[k]=visit(value,trail+(k,))
    return out
   result=visit(data)
   # Do not rewrite an untouched historical-like JSON merely for serialization.
   nexttext=json.dumps(result,indent=2)+'\n'if used else text
  else:
   nexttext=text
   for old,targets in byold.items():
    if old not in text:continue
    choices=[(t,n)for t,n in targets if t in text or ('res://'+t.removeprefix('Game/'))in text]
    if len(choices)==1:
     t,n=choices[0];nexttext=nexttext.replace(old,n);used.append((rel,t,old,n,'literal'))
  h=sha(nexttext.encode())
  if h!=current[rel]:
   target=O/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(nexttext);current[rel]=h;updated=True
  edges.update(used)
  for old,targets in byold.items():
   if old in nexttext:unresolved.append({'consumer':rel,'targets':[t for t,n in targets],'old':old})
 if not updated:break
else:raise RuntimeError('Hash dependency cycle or nonconvergence')
changed={r:(hashes.get(r),h)for r,h in current.items()if h!=hashes.get(r)}
(P/'PIN_CLOSURE_DRAFT.json').write_text(json.dumps({'iterations':iteration+1,'changed':changed,'edges':[list(e)for e in sorted(edges)],'unresolved':unresolved},indent=2)+'\n')
print('iterations',iteration+1,'changed',len(changed),'unresolved',len(unresolved))
for row in unresolved:print(row['consumer'],'<-',row['targets'])
