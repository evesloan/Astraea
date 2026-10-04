"""Independent binary glTF accessor/role/normal/transform checks; no Blender imports."""
import json,struct,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def read_glb(path):
 data=path.read_bytes();magic,ver,length=struct.unpack_from('<III',data)
 assert magic==0x46546C67 and ver==2 and length==len(data)
 off=12;j=None;binary=None
 while off<len(data):
  n,tag=struct.unpack_from('<II',data,off);off+=8;block=data[off:off+n];off+=n
  if tag==0x4E4F534A:j=json.loads(block)
  elif tag==0x004E4942:binary=block
 return j,binary

def accessor(j,binary,idx):
 a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];fmt={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']]
 n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=struct.calcsize(fmt)*n;stride=v.get('byteStride',size)
 start=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt*n,binary,start+i*stride) for i in range(a['count'])]

def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))

reports=[]
for path in sorted(ROOT.glob('*.glb')):
 j,binary=read_glb(path);issues=[];tri=0;positions=[];uv_count=0;degenerate=0;opposed=0;collapsed_uv_surface=0.0
 for mesh in j.get('meshes',[]):
  for p in mesh['primitives']:
   assert p.get('mode',4)==4
   ps=accessor(j,binary,p['attributes']['POSITION']);ns=accessor(j,binary,p['attributes']['NORMAL']);ix=[i[0] for i in accessor(j,binary,p['indices'])]
   positions.extend(ps);tri+=len(ix)//3
   uvs=None
   if any(k.startswith('TEXCOORD_') and k!='TEXCOORD_0' for k in p['attributes']):issues.append('Redundant UV set after consolidation')
   if 'TEXCOORD_0' in p['attributes']:
    uvs=accessor(j,binary,p['attributes']['TEXCOORD_0']);uv_count+=len(uvs)
    if not all(math.isfinite(c) for uv in uvs for c in uv):issues.append('Nonfinite UV')
   else:issues.append('Missing TEXCOORD_0')
   if not all(math.isfinite(c) for v in ps+ns for c in v):issues.append('Nonfinite positions/normals')
   for n in range(0,len(ix),3):
    ia,ib,ic=ix[n:n+3];face=cross(minus(ps[ib],ps[ia]),minus(ps[ic],ps[ia]));normal=tuple(sum(ns[k][axis] for k in (ia,ib,ic))/3 for axis in range(3))
    if dot(face,face)<1e-18:degenerate+=1
    elif dot(face,normal)<-1e-10:opposed+=1
    if uvs:
     ua,ub,uc=uvs[ia],uvs[ib],uvs[ic]
     uvarea=abs((ub[0]-ua[0])*(uc[1]-ua[1])-(ub[1]-ua[1])*(uc[0]-ua[0]))*.5
     if uvarea<1e-12:collapsed_uv_surface+=math.sqrt(dot(face,face))*.5
 lo=[min(v[i] for v in positions) for i in range(3)];hi=[max(v[i] for v in positions) for i in range(3)]
 mats=[];texture_hashes=[]
 for im in j.get('images',[]):
  bv=j['bufferViews'][im['bufferView']];offset=bv.get('byteOffset',0);embedded=binary[offset:offset+bv['byteLength']]
  digest=hashlib.sha256(embedded).hexdigest();source=ROOT.parent.parent/'materials'/(im['name']+'.png')
  if not source.exists():source=ROOT/'textures'/(im['name']+'.png')
  matching=source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()==digest
  texture_hashes.append({'name':im['name'],'embedded_sha256':digest,'matches_exact_shared_or_original_local_texture':matching})
  if not matching:issues.append('Texture bytes mismatch: '+im['name'])
 for m in j.get('materials',[]):
  pbr=m.get('pbrMetallicRoughness',{});ti=pbr.get('baseColorTexture',{}).get('index')
  valid=ti is not None and 'bufferView' in j['images'][j['textures'][ti]['source']]
  mats.append({'name':m['name'],'ordinary_pbr_base_color_texture_embedded':valid,'metallic':pbr.get('metallicFactor',1),'roughness':pbr.get('roughnessFactor',1)})
  if not valid:issues.append('Missing embedded ordinary base color for '+m['name'])
 if opposed:issues.append('Face/vertex normals opposed')
 if degenerate:issues.append('Degenerate triangles')
 if collapsed_uv_surface>1e-9:issues.append('Collapsed UV surface area')
 manifest=json.loads(path.with_suffix('.manifest.json').read_text());expected=manifest['dimensions_m'];actual=[hi[i]-lo[i] for i in range(3)]
 expected_gltf=[expected[0],expected[2],expected[1]]
 if max(abs(x-y) for x,y in zip(actual,expected_gltf))>1e-5:issues.append('Source/export dimension mismatch')
 if tri!=manifest['triangles_evaluated']:issues.append('Triangle mismatch')
 for node in j.get('nodes',[]):
  if any(abs(x-1)>1e-6 for x in node.get('scale',[1,1,1])):issues.append('Unapplied scale')
 report={'file':path.name,'valid_glb_header':True,'mesh_count':len(j.get('meshes',[])),'node_count':len(j.get('nodes',[])),'material_primitive_count':sum(len(m['primitives']) for m in j['meshes']),'triangles':tri,'dimensions_gltf_Yup_m':actual,'source_dimension_match':not any('dimension' in x for x in issues),'uv_vertex_count':uv_count,'collapsed_uv_surface_m2':collapsed_uv_surface,'materials':mats,'texture_hashes':texture_hashes,'degenerate_triangles':degenerate,'opposed_normal_triangles':opposed,'issues':issues,'status':'PASS' if not issues else 'FAIL'}
 reports.append(report)
(ROOT/'qa'/'glb_independent_validation.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
assert all(r['status']=='PASS' for r in reports)
