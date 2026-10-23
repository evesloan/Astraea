from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'recovery/quiet_d14_chain_fix';P.mkdir(exist_ok=False);payload=P/'payload';prior=R/'recovery/quiet_d14_composed_fix/payload';shutil.copytree(prior,payload)
sha=lambda b:hashlib.sha256(b).hexdigest();changes={};edges=[]
script='Game/scripts/quiet_d14_receiving_20261016/package.gd';changes[script]=(sha((R/script).read_bytes()),sha((payload/script).read_bytes()))
receipts=[f'Game/data/{fam}_d{d}_receiving_20261016/RECEIPT.json'for fam,decks in [('quiet',[13,16]),('family',[13,14,15,16])]for d in decks]
for rel in receipts:
 original=(R/rel).read_bytes();d=json.loads(original);before=json.loads(original)
 for target,(old,new)in changes.items():
  if target in d['source_pins']:
   assert d['source_pins'][target]==old;d['source_pins'][target]=new;edges.append({'consumer':rel,'target':target,'old':old,'new':new})
 assert {k:v for k,v in d.items()if k!='source_pins'}=={k:v for k,v in before.items()if k!='source_pins'}
 # Preserve original serialized bytes except exact pin tokens.
 out=original.decode()
 for e in edges:
  if e['consumer']==rel:out=out.replace(e['old'],e['new'])
 assert json.loads(out)==d
 p=payload/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(out);changes[rel]=(sha(original),sha(p.read_bytes()))
rel='Game/family_specialty_bank_20261022/evidence/GUARD_PLAN.json';b=(R/rel).read_bytes();old,new=changes['Game/data/family_d14_receiving_20261016/RECEIPT.json'];assert old in b.decode();out=b.decode().replace(old,new);p=payload/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(out);changes[rel]=(sha(b),sha(p.read_bytes()));edges.append({'consumer':rel,'target':'Game/data/family_d14_receiving_20261016/RECEIPT.json','old':old,'new':new})
# Entire reverse-hash closure of affected runtime inputs, including all .gd/.json consumers; historical docs classified separately.
remaining=[];history=[]
for target,(old,new)in list(changes.items()):
 result=subprocess.run(['rg','-l','-F',old,'Game','--glob','*.json','--glob','*.gd','--glob','*.tscn','--glob','*.cfg'],cwd=R,capture_output=True,text=True)
 for rel in result.stdout.splitlines():
  actual=(payload/rel)if(payload/rel).exists()else(R/rel)
  if old not in actual.read_text():continue
  record={'consumer':rel,'target':target,'old_sha256':old}
  if rel.startswith('Game/docs/'):history.append(record)
  else:remaining.append(record)
print('UNRESOLVED_RUNTIME',remaining)
assert not remaining
# Source manifest: retain all old entries, update only affected listed paths; explicitly include newly changed receipts for export exactness.
m='Game/scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';rows=json.loads((payload/m).read_text());by={r['path']:r for r in rows};delta=[]
for rel in receipts+['Game/family_specialty_bank_20261022/evidence/GUARD_PLAN.json']:
 name='res://'+rel[5:];p=payload/rel;record={'path':name,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size};delta.append({'path':name,'before':by.get(name),'after':record});by[name]=record
(payload/m).write_text(json.dumps(sorted(by.values(),key=lambda r:r['path']),indent=2)+'\n')
(P/'DEPENDENCY_GRAPH.json').write_text(json.dumps({'status':'CLOSED_RUNTIME_HASH_GRAPH','edges':edges,'changed':changes,'unresolved_runtime':remaining,'immutable_historical_consumers_preserved':history,'manifest_delta':delta,'manifest_total':len(by)},indent=2)+'\n')
print('edges',len(edges),'historical_refs',len(history),'contracts',len(by))
