"""Verify embedded interface texture bytes against the retained original catalogue files."""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];p=R/'qa/texture_byte_equality.json';report=json.loads(p.read_text());raw=(R/'exports/AST-RES-005.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);data=raw[28+n:];expected={}
for entry in report['assets']['AST-RES-005']:
 for name in entry['exact_original_material_files']:expected.setdefault(hashlib.sha256((C/name).read_bytes()).hexdigest(),[]).append(name)
rows=[]
for image in g['images']:
 view=g['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);h=hashlib.sha256(data[start:start+view['byteLength']]).hexdigest();assert h in expected
 rows.append({'image':image.get('name'),'sha256':h,'exact_original_material_files':expected[h]})
assert len(rows)==len(expected)==2
assert {r['image'] for r in rows}=={'champagne_metal','ivory_enamel'}
report['assets']['AST-RES-005']=rows;p.write_text(json.dumps(report,indent=2)+'\n');print('Both embedded RES005 textures exactly match retained catalogue bytes')
