"""Compare exported native input arrays and retained assembly records, without an engine."""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parents[1]
BASE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/medical_forward_welcome_candidate_20261006/finish008')
old=json.loads((BASE/'qa/SOURCE_MANIFEST_008.json').read_text());new=json.loads((R/'qa/SOURCE_MANIFEST_010.json').read_text())
def load(p):
 raw=p.read_bytes();o=12;d=b=None
 while o<len(raw):
  size,kind=struct.unpack_from('<II',raw,o);v=raw[o+8:o+8+size];o+=8+size
  if kind==0x4E4F534A:d=json.loads(v)
  if kind==0x004E4942:b=v
 return d,b
width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};sizes={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
def native(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];size=width[a['type']]*sizes[a['componentType']];stride=v.get('byteStride',size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
 raw=b''.join(b[start+j*stride:start+j*stride+size]for j in range(a['count']))
 return [a['count'],a['componentType'],a['type'],hashlib.sha256(raw).hexdigest()]
def records(path):
 d,b=load(path);rows={}
 for n in d['nodes']:
  if 'mesh'not in n:continue
  chunks=[]
  for p in d['meshes'][n['mesh']]['primitives']:
   mat=d['materials'][p['material']]['name']if'material'in p else None
   chunks.append({'attributes':{k:native(d,b,v)for k,v in p['attributes'].items()},'indices':native(d,b,p['indices'])if'indices'in p else None,'material':mat,'mode':p.get('mode',4)})
  rows[n['name']]={'native':chunks,'transform':{k:n.get(k)for k in['matrix','translation','rotation','scale']}}
 return rows
A=records(BASE/'exports/D05_forward_welcome_architecture_008.glb');B=records(Path(new['architecture_export']));changes=set(new['explicit_existing_source_changes']);preserved={k:v for k,v in A.items()if k not in changes}
assert all(k in B and B[k]==v for k,v in preserved.items())
assert all(x in new['retained_component_instances']for x in old['retained_component_instances'])
assert old['fixture_sources']==new['fixture_sources'][:len(old['fixture_sources'])]
result={'status':'EXACT_NATIVE_PREDECESSOR_PRESERVATION_PASS','predecessor_source_sha256':old['source_sha256'],'candidate_source_sha256':new['source_sha256'],'predecessor_export_sha256':old['export_sha256'],'candidate_export_sha256':new['export_sha256'],'preserved_old_architecture_meshes':len(preserved),'preserved_old_architecture_names':sorted(preserved),'allowed_five_changed_source_objects':sorted(changes),'old_retained_assembly_records_exact':len(old['retained_component_instances']),'old_fixture_records_exact':len(old['fixture_sources']),'candidate_total_architecture_meshes':len(B),'candidate_new_named_meshes':len(set(B)-set(A)),'note':'SOURCE_MANIFEST.new_editable_parts is the total candidate architecture census, inherited field naming; it does not mean all782 meshes are new.'}
(R/'qa/PREDECESSOR_PRESERVATION_010.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(preserved),len(B),result['candidate_new_named_meshes'])
