from pathlib import Path
import json,hashlib,subprocess
S=Path(__file__).resolve().parent;R=S.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
subprocess.run(['python',str(R/'recovery/cloud_connected_successor_20261023/compose.py')],check=True)
rows=json.loads(Path('/tmp/astraea-connected-source-map.json').read_text());mapping={r['path']:r for r in rows}
for p in (S/'payload/Game').rglob('*'):
 if p.is_file():
  uri='res://'+str(p.relative_to(S/'payload/Game'));mapping[uri]={'path':uri,'source':str(p),'sha256':sha(p.read_bytes())}
rows=sorted(mapping.values(),key=lambda r:r['path']);Path('/tmp/astraea-connected-source-map.json').write_text(json.dumps(rows))
manifest=S/'payload/Game/scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json';contract=json.loads(manifest.read_text());layers=[S/'payload',R/'recovery/contact_packed_successor_20261023/payload',R/'recovery/route_activation_fix_20261023/payload',R/'recovery/texture_lifetime_fix_20261023/payload',R/'recovery/release_operations_fix_20261023/payload',R/'recovery/quiet_d14_chain_fix/payload',R]
for row in contract:
 p=next(l/('Game/'+row['path'][6:]) for l in layers if (l/('Game/'+row['path'][6:])).is_file());b=p.read_bytes()
 if sha(b)!=row['sha256'] or len(b)!=row['bytes']:raise RuntimeError(row['path'])
receipt={'source_contract_entries':len(contract),'manifest_sha256':sha(manifest.read_bytes()),'composition_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),'layer_parent':'3079b99757b00ac1036af8a15d4d75b156782a94'}
lock=S/'COMPOSITION.json'
if lock.exists() and json.loads(lock.read_text())!=receipt:raise RuntimeError('Composition changed')
Path('/tmp/staged-composition.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
