"""Deterministic bounded byte manifest; no recursive backup or watcher."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];rows={}
for f in sorted(P.rglob('*')):
 rel=f.relative_to(P)
 if not f.is_file() or any(q in rel.parts for q in ['retention','.godot','__pycache__']) or f.suffix in ['.blend1','.pyc','.import'] or f.name in ['RESOURCE_HASHES.json','final_delivery_receipt.json']:continue
 rows[rel.as_posix()]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
manifest={'schema':1,'algorithm':'sha256','scope':'Bounded delivery files; independent Git store, generated caches, native autosave history and self manifest excluded.','files':rows}
f=P/'RESOURCE_HASHES.json';f.write_text(json.dumps(manifest,indent=2));print('Manifest SHA256 '+hashlib.sha256(f.read_bytes()).hexdigest()+'; '+str(len(rows))+' files; '+str(sum(a['bytes'] for a in rows.values()))+' bytes')
