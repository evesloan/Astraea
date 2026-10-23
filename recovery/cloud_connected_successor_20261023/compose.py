"""Read-only source composition; writes only a compact verified source map to /tmp."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;R=S.parents[1]
layers=['recovery/contact_packed_successor_20261023/payload','recovery/route_activation_fix_20261023/payload','recovery/texture_lifetime_fix_20261023/payload','recovery/release_operations_fix_20261023/payload','recovery/quiet_d14_chain_fix/payload','.']
sha=lambda b:hashlib.sha256(b).hexdigest()
def resolve(rel):
 return next(R/l/rel for l in layers if (R/l/rel).is_file())
manifest=resolve('Game/scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json');rows=json.loads(manifest.read_text());verified=0;size=0
for row in rows:
 p=resolve('Game/'+row['path'][6:]);b=p.read_bytes()
 if len(b)!=row['bytes'] or sha(b)!=row['sha256']:raise RuntimeError('Contract differs: '+row['path'])
 verified+=1;size+=len(b)
# Mount the immutable successor payloads and local scripts over the retained import pack.
# This is a focused cloud test resource layer, not a standalone full-ship export.
paths=set()
for layer in layers[:-1]:
 paths.update(str(p.relative_to(R/layer)) for p in (R/layer/'Game').rglob('*') if p.is_file())
paths.update(str(p.relative_to(R)) for p in (R/'Game/scripts').rglob('*.gd'))
index=[{'path':'res://'+rel[5:],'source':str(resolve(rel)),'sha256':sha(resolve(rel).read_bytes())} for rel in sorted(paths)]
receipt={'base_source':'f94cc1c8fde5e310bfae3ebd045272f67de66089','layer_checkpoint':'f15084ff4b78217eee673f550b439ae1114c5061','precedence':layers,'manifest_sha256':sha(manifest.read_bytes()),'source_contract_entries':verified,'source_contract_bytes':size,'mount_files':len(index),'mount_bytes':sum(Path(r['source']).stat().st_size for r in index),'composition_sha256':sha(json.dumps(index,sort_keys=True,separators=(',',':')).encode()),'standalone_export':False}
lock=S/'COMPOSITION.json'
if lock.exists():
 expected=json.loads(lock.read_text())
 for key in ['manifest_sha256','composition_sha256','source_contract_entries','source_contract_bytes','mount_files','mount_bytes']:
  if receipt[key]!=expected[key]:raise RuntimeError('Immutable composition differs: '+key)
Path('/tmp/astraea-connected-source-map.json').write_text(json.dumps(index));Path('/tmp/astraea-connected-composition.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
