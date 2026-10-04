"""Compare preserved baseline GLB byte geometry and hierarchy to metadata-only revision."""
from pathlib import Path
import subprocess,json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';BASE='11936f59ff9a9c31392105ff81bf8feef8688496';REL='assets/staff_workbay/AST-STF-007_supply_work_cabinet.glb'
def unpack(data):
 magic,version,length=struct.unpack_from('<4sII',data);assert magic==b'glTF' and version==2 and length==len(data);chunks={};off=12
 while off<len(data):
  n,k=struct.unpack_from('<I4s',data,off);off+=8;chunks[k]=data[off:off+n];off+=n
 return json.loads(chunks[b'JSON']),chunks[b'BIN\0']
before=subprocess.check_output(['git','show',BASE+':'+REL],cwd=ROOT);after=(ROOT/REL).read_bytes();a,ab=unpack(before);b,bb=unpack(after)
def without_node_extras(doc):
 d=json.loads(json.dumps(doc))
 for n in d.get('nodes',[]):n.pop('extras',None)
 return d
r={'baseline_commit':BASE,'path':REL,'baseline_file_sha256':hashlib.sha256(before).hexdigest(),'current_file_sha256':hashlib.sha256(after).hexdigest(),'baseline_BIN_sha256':hashlib.sha256(ab).hexdigest(),'current_BIN_sha256':hashlib.sha256(bb).hexdigest(),'binary_payload_identical':ab==bb,'all_JSON_outside_node_extras_identical':without_node_extras(a)==without_node_extras(b),'before_pivot_metadata':[n for n in a['nodes'] if 'pivot' in n.get('name','')],'current_pivot_metadata':[n for n in b['nodes'] if 'pivot' in n.get('name','')],'scope':'Actual GLB payload and JSON comparison. Identical BIN includes vertex/index/normal/UV/image bytes; JSON equality outside node extras includes hierarchy, transforms, materials and accessor interpretation. Source Blender invariants are separately supplied by the metadata-edit worker.'}
r['geometry_material_hierarchy_unchanged']=r['binary_payload_identical'] and r['all_JSON_outside_node_extras_identical'];(OUT/'independent_coordinate_cabinet_diff.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['before_pivot_metadata','current_pivot_metadata']},indent=2))
