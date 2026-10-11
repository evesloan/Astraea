from pathlib import Path
import json,struct
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));f=R/'Game/assets/models'/P['source_models']['central']['model'];b=f.read_bytes();assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);pos=20+n;size,kind=struct.unpack_from('<II',b,pos);assert kind==0x004e4942;buf=b[pos+8:pos+8+size];out={}
for row in P['moves']:
 node=next(q for q in g['nodes']if q.get('name')==row['name']);assert not any(k in node for k in ['matrix','translation','rotation','scale']);mesh=g['meshes'][node['mesh']];vs=[]
 for prim in mesh['primitives']:
  a=g['accessors'][prim['attributes']['POSITION']];assert a['componentType']==5126 and a['type']=='VEC3';v=g['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);vs += [list(struct.unpack_from('<fff',buf,offset+i*stride))for i in range(a['count'])]
 out[row['name']]=vs
(W/'RAW_SOURCE_VERTICES.json').write_text(json.dumps(out,indent=2)+'\n');print('Exact raw source vertices retained for',len(out),'rigid moves')
