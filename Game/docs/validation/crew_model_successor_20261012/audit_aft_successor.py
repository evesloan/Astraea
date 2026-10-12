import collections, hashlib, json, pathlib, struct
root=pathlib.Path('/workspace/astraea-protected-integration-20261012/Game/assets/models')
out=pathlib.Path(__file__).parent
def read(name):
 data=(root/name).read_bytes();length=struct.unpack_from('<I',data,12)[0]
 doc=json.loads(data[20:20+length]);binary=data[28+length:]
 def accessor(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
  fmt,size={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}[a['componentType']]
  width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width*size)
  return [struct.unpack_from('<'+fmt*width,binary,start+i*stride) for i in range(a['count'])]
 nodes={n['name']:n for n in doc['nodes'] if 'mesh' in n}
 def triangles(node):
  result=collections.Counter()
  for p in doc['meshes'][node['mesh']]['primitives']:
   attrs={k:accessor(v) for k,v in p['attributes'].items()}
   ids=[x[0] for x in accessor(p['indices'])]
   material=json.dumps(doc['materials'][p['material']],sort_keys=True)
   for i in range(0,len(ids),3):
    vertices=tuple(tuple((k,attrs[k][v]) for k in sorted(attrs)) for v in ids[i:i+3])
    oriented=min(vertices,vertices[1:]+vertices[:1],vertices[2:]+vertices[:2])
    result[(material,oriented)]+=1
  return result
 images=[]
 for im in doc.get('images',[]):
  v=doc['bufferViews'][im['bufferView']];start=v.get('byteOffset',0)
  images.append(hashlib.sha256(binary[start:start+v['byteLength']]).hexdigest())
 return data,doc,nodes,triangles,images
old_file='AST-CIR-005_aft_uniforms_d03.glb';new_file='AST-CIR-005_aft_crewcare_d03.glb'
a,ad,an,at,ai=read(old_file);b,bd,bn,bt,bi=read(new_file)
assert ad['materials']==bd['materials'] and ai==bi
assert len(an)==9 and len(bn)==29 and set(an)<=set(bn)
removed=collections.Counter();added_in_old=collections.Counter();unchanged=[]
for name,node in an.items():
 assert {k:v for k,v in node.items() if k!='mesh'}=={k:v for k,v in bn[name].items() if k!='mesh'},name
 before=at(node);after=bt(bn[name]);removed+=before-after;added_in_old+=after-before
 if before==after:unchanged.append(name)
boxes={}
slots=[(0,-1),(6,-1),(6,1),(12,-1),(21,-1),(21,1),(35.5,-1),(44,-1),(44,1),(52.5,-1),(52.5,1),(61,1),(69.5,-1),(69.5,1),(78,-1),(78,1)]
datums=[0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5]
for floor,side in slots:
 top=datums[datums.index(floor)+1]-.24
 for kind,xlo,xhi,ylo,yhi in [('wall',7.72,7.88,floor,top),('dado',7.635,7.685,floor+.12,floor+.78)]:
  xs=sorted([side*xlo,side*xhi]);boxes[f'{floor}_{side}_{kind}']=[xs[0],ylo,-13.0,xs[1],yhi,20.0]
counts=collections.Counter();corners=collections.defaultdict(set)
for key,count in removed.items():
 points=[dict(v)['POSITION'] for v in key[1]]
 matches=[]
 for name,bounds in boxes.items():
  if all(all(abs(p[i]-bounds[i])<1e-5 or abs(p[i]-bounds[i+3])<1e-5 for i in range(3)) for p in points):matches.append(name)
 assert len(matches)==1,(points,matches)
 counts[matches[0]]+=count
 for point in points:corners[matches[0]].add(tuple(round(v,5) for v in point))
assert len(counts)==32 and all(v in [8,12] for v in counts.values()) and all(len(v)==8 for v in corners.values())
assert sum(removed.values())==288
added_counts=collections.Counter()
for key,count in added_in_old.items():
 points=[dict(v)['POSITION'] for v in key[1]]
 matches=[name for name,bounds in boxes.items() if all(all(bounds[i]-1e-5<=p[i]<=bounds[i+3]+1e-5 for i in range(3)) for p in points)]
 assert len(matches)==1,(points,matches)
 name=matches[0];floor=float(name.split('_')[0])
 assert max(p[2] for p in points)<=-2+1e-5 or min(p[2] for p in points)>=2-1e-5 or min(p[1] for p in points)>=floor+2.65-1e-5
 added_counts[name]+=count
assert len(added_counts)==24 and sum(added_in_old.values())==624
assert all(v==(32 if k.endswith('wall') else 20) for k,v in added_counts.items())
new_names=sorted(set(bn)-set(an));new_triangles=sum(sum(bt(bn[n]).values()) for n in new_names)
assert new_triangles==240
report={'status':'PASS_EXACT_BOUNDED_IMMUTABLE_SOURCE_SUCCESSOR_DELTA',
 'original_file':old_file,'original_sha256':hashlib.sha256(a).hexdigest(),
 'successor_file':new_file,'successor_sha256':hashlib.sha256(b).hexdigest(),
 'original_meshes':9,'successor_meshes':29,'retained_node_metadata_transform_exact':True,
 'unchanged_entire_mesh_geometry_attributes':unchanged,'original_uniforms_aperture_five_meshes_exact':all('Uniforms' in n for n in unchanged if not n.startswith('CORE_BATCH')),
 'all_remaining_original_oriented_triangle_attributes_exact':True,
 'materials_and_embedded_image_bytes_exact':True,'removed_triangles':sum(removed.values()),
 'removed_exact_closed_source_prisms':dict(counts),'removed_source_bounds':boxes,
 'added_bounded_profile_triangles':dict(added_counts),'changed_source_aperture_slots':slots,
 'new_profile_meshes':new_names,'new_profile_triangles':new_triangles,
 'scope':'Exactly16 retained sidewall/dado aperture replacements;all other original oriented geometry/normal/UV/material/transform data preserved, including five original Uniforms pieces. Current source already retained at8664ac1;no new geometry or portal/primary capacity/route adoption.'}
(out/'AFT_SUCCESSOR_SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
