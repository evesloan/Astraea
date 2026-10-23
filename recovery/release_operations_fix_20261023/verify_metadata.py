from pathlib import Path
import json,re,hashlib
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'recovery/release_operations_fix_20261023';O=P/'payload';B=R/'recovery/quiet_d14_chain_fix/payload';changes=[]
def walk(a,b,t=()):
 if a==b:return
 if isinstance(a,dict)and isinstance(b,dict):
  assert a.keys()==b.keys(),t
  for k in a:walk(a[k],b[k],t+(k,))
 elif isinstance(a,list)and isinstance(b,list):
  assert len(a)==len(b),t
  for i,(x,y)in enumerate(zip(a,b)):walk(x,y,t+(i,))
 else:
  assert isinstance(a,str)and isinstance(b,str)and re.fullmatch('[a-f0-9]{64}',a)and re.fullmatch('[a-f0-9]{64}',b),(t,a,b)
  assert 'inverse_edits'not in t,t
  changes.append(t)
count=0
for f in O.rglob('*.json'):
 rel=f.relative_to(O)
 if f.name=='SOURCE_CONTRACTS.json':continue
 old=B/rel if(B/rel).exists()else R/rel
 if not old.exists():continue
 walk(json.loads(old.read_text()),json.loads(f.read_text()),(str(rel),));count+=1
receipt={'status':'PASS','json_files_compared':count,'hash_leaf_changes':len(changes),'geometry_identity_and_nonhash_values':'UNCHANGED','historical_inverse_edits':'UNCHANGED'}
(P/'METADATA_VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
