import pathlib,json,struct,sys,math,hashlib
B=pathlib.Path(__file__).resolve().parent;S=sys.argv[1];P=B/S;r=(P/'exports/section.glb').read_bytes();pos=12;doc={};buf=b''
while pos<len(r):
 n,k=struct.unpack_from('<II',r,pos);pos+=8
 if k==0x4e4f534a:doc=json.loads(r[pos:pos+n])
 if k==0x004e4942:buf=r[pos:pos+n]
 pos+=n

def acc(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=struct.calcsize(fmt)*dims;stride=v.get('byteStride',size);offset=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*dims,buf,offset+j*stride) for j in range(a['count'])]
errors=[];triangles=0;normals=0
for m in doc['meshes']:
 for p in m['primitives']:
  attrs=p['attributes'];vs=acc(attrs['POSITION']);ns=acc(attrs['NORMAL']);normals+=len(ns)
  if 'TEXCOORD_0' not in attrs:errors.append(m['name']+' UV missing')
  if any(abs(math.sqrt(sum(x*x for x in n))-1)>.03 for n in ns):errors.append(m['name']+' nonunit normal')
  idx=[x[0] for x in acc(p['indices'])] if 'indices' in p else list(range(len(vs)))
  for i in range(0,len(idx),3):
   a,b,c=idx[i:i+3];u=[vs[b][j]-vs[a][j] for j in range(3)];v=[vs[c][j]-vs[a][j] for j in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];nn=[ns[a][j]+ns[b][j]+ns[c][j] for j in range(3)];dot=sum(cross[j]*nn[j] for j in range(3));triangles+=1
   if dot<-.00001:errors.append(m['name']+' winding/normal disagreement');break
out={'glb_sha256':hashlib.sha256(r).hexdigest(),'triangles':triangles,'normal_vectors':normals,'errors':errors,'method':'Read actual GLB binary accessors; normal lengths, texture coordinates and triangle-winding agreement'};(P/'qa/binary_normals.json').write_text(json.dumps(out,indent=2));print('Actual GLB binary normals',len(errors),'errors',errors[:10]);assert not errors
