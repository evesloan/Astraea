"""Native binary geometry/metadata sanity; does not import or execute the model."""
from pathlib import Path
import json,struct,math,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];run=sys.argv[1] if len(sys.argv)>1 else '005'
path=ROOT/'exports'/f'D05_forward_welcome_architecture_{run}.glb';raw=path.read_bytes()
magic,version,total=struct.unpack_from('<4sII',raw,0);assert magic==b'glTF' and version==2 and total==len(raw)
offset=12;doc=None;binary=None
while offset<len(raw):
    size,kind=struct.unpack_from('<II',raw,offset);payload=raw[offset+8:offset+8+size];offset+=8+size
    if kind==0x4E4F534A:doc=json.loads(payload)
    if kind==0x004E4942:binary=payload
widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};types={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
def access(index):
    a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];fmt,size=types[a['componentType']];n=widths[a['type']];step=v.get('byteStride',n*size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*n,binary,start+i*step) for i in range(a['count'])]
triangles=0;vertex_samples=0;missing_uv=[];degenerate=0
for mi,m in enumerate(doc['meshes']):
    for pr in m['primitives']:
        positions=access(pr['attributes']['POSITION']);vertex_samples+=len(positions);assert all(math.isfinite(v) for p in positions for v in p)
        indices=[x[0] for x in access(pr['indices'])] if 'indices' in pr else list(range(len(positions)));assert len(indices)%3==0 and max(indices)<len(positions);triangles+=len(indices)//3
        for i in range(0,len(indices),3):
            a,b,c=[positions[indices[i+j]] for j in range(3)];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            if sum(x*x for x in cross)<1e-20:degenerate+=1
        if 'NORMAL' in pr['attributes']:assert all(math.isfinite(x) for n in access(pr['attributes']['NORMAL']) for x in n)
        material=doc.get('materials',[])[pr['material']] if 'material' in pr else {}
        if material.get('pbrMetallicRoughness',{}).get('baseColorTexture') and 'TEXCOORD_0' not in pr['attributes']:missing_uv.append(mi)
assert not missing_uv
report={'scope':'Native GLB finite coordinates, index ranges and textured-primitive UV presence only; no engine import, visual export equivalence, collision or body acceptance.','path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'nodes':len(doc['nodes']),'meshes':len(doc['meshes']),'triangles':triangles,'vertices_in_primitives':vertex_samples,'embedded_image_count':len(doc.get('images',[])),'missing_textured_uv':missing_uv,'zero_area_triangle_count':degenerate,'cameras_exported':len(doc.get('cameras',[])),'floor_owner':'No floor slab exported; retained component transforms remain separate assembly records.'}
(ROOT/'qa'/f'NATIVE_EXPORT_{run}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
