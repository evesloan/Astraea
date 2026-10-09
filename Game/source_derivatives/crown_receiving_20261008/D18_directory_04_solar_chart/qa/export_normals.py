import pathlib,json,hashlib,struct,math,sys
p=pathlib.Path(sys.argv[1]);key=json.loads((p/'contract.json').read_text())['programme_key'];f=p/'exports'/(key+'.glb');raw=f.read_bytes();pos=12;doc=None;binary=None
while pos<len(raw):
 n,kind=struct.unpack_from('<II',raw,pos);pos+=8
 if kind==0x4e4f534a:doc=json.loads(raw[pos:pos+n])
 if kind==0x004e4942:binary=raw[pos:pos+n]
 pos+=n
bad=[];count=0;lengths=[]
for mi,mesh in enumerate(doc['meshes']):
 for pi,primitive in enumerate(mesh['primitives']):
  idx=primitive['attributes'].get('NORMAL')
  if idx is None:bad.append([mi,pi,'missing NORMAL']);continue
  accessor=doc['accessors'][idx];view=doc['bufferViews'][accessor['bufferView']]
  assert accessor['componentType']==5126 and accessor['type']=='VEC3'
  offset=view.get('byteOffset',0)+accessor.get('byteOffset',0);stride=view.get('byteStride',12)
  for j in range(accessor['count']):
   v=struct.unpack_from('<3f',binary,offset+j*stride);length=math.sqrt(sum(q*q for q in v));count+=1;lengths.append(length)
   if not all(math.isfinite(q) for q in v) or abs(length-1)>.002:bad.append([mi,pi,j,v,length])
negative=[node.get('name',n) for n,node in enumerate(doc['nodes']) if math.prod(node.get('scale',[1,1,1]))<0]
report={'status':'PASS' if not bad and not negative else 'FAIL','scope':'Actual GLB binary NORMAL accessor vectors and node scale orientation; no engine acceptance.','sha256':hashlib.sha256(raw).hexdigest(),'normal_vectors':count,'unit_length_range':[min(lengths),max(lengths)],'bad_normals':bad,'negative_scale_nodes':negative}
(p/'qa/export_normals.json').write_text(json.dumps(report,indent=2));print(report)
assert report['status']=='PASS'

