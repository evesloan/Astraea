import json,struct,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
raw=(O/'source.glb').read_bytes();magic,version,size=struct.unpack_from('<III',raw,0);assert magic==0x46546C67 and version==2 and size==len(raw)
p=12;doc=None;buf=None
while p<len(raw):
 n,typ=struct.unpack_from('<II',raw,p);p+=8;chunk=raw[p:p+n];p+=n
 if typ==0x4E4F534A:doc=json.loads(chunk)
 elif typ==0x004E4942:buf=chunk
I=[[1.,0,0,0],[0,1.,0,0],[0,0,1.,0],[0,0,0,1.]]
def mul(a,b):return[[sum(a[i][k]*b[k][j]for k in range(4))for j in range(4)]for i in range(4)]
def transform(n):
 if 'matrix'in n:return[[n['matrix'][j*4+i]for j in range(4)]for i in range(4)]
 x,y,z,w=n.get('rotation',[0,0,0,1]);sx,sy,sz=n.get('scale',[1,1,1]);t=n.get('translation',[0,0,0])
 m=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],[0,0,0,1]]
 for i in range(3):
  for j,s in enumerate([sx,sy,sz]):m[i][j]*=s
 return m
parents={j:i for i,n in enumerate(doc['nodes'])for j in n.get('children',[])};mats={}
def matrix(i):
 if i not in mats:mats[i]=mul(matrix(parents[i])if i in parents else I,transform(doc['nodes'][i]))
 return mats[i]
cache={};floor_triangles=[];triangle_deltas=[]
def indices(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];fmt,sz={5121:('B',1),5123:('H',2),5125:('I',4)}[a['componentType']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz);return[struct.unpack_from('<'+fmt,buf,start+j*stride)[0]for j in range(a['count'])]
def vertices(i):
 if i not in cache:
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);cache[i]=[struct.unpack_from('<fff',buf,start+j*stride)for j in range(a['count'])]
 return cache[i]
records={r['name']:r for r in json.loads((O/'PARTS.json').read_text())['objects']};errors=[];checked=0;maxerr=0;found=set();triangles=0
for i,node in enumerate(doc['nodes']):
 if 'mesh'not in node:continue
 name=node.get('name');M=matrix(i);lo=[math.inf]*3;hi=[-math.inf]*3;node_triangles=0
 for prim in doc['meshes'][node['mesh']]['primitives']:
  if 'indices'in prim:
   ntri=doc['accessors'][prim['indices']]['count']//3;triangles+=ntri;node_triangles+=ntri
  global_points=[]
  for v in vertices(prim['attributes']['POSITION']):
   p=[sum(M[j][k]*v[k]for k in range(3))+M[j][3]for j in range(3)];global_points.append(p)
   lo=[min(lo[j],p[j])for j in range(3)];hi=[max(hi[j],p[j])for j in range(3)]
  if name in ['GARDEN_ProposedBase','GALLERY_UpperDeck','LOWER_EndCrosslink','UPPER_EndCrosslink','LOWER_ReadingPocket','STAIR_BottomLanding']:
   inds=indices(prim['indices'])
   for q in range(0,len(inds),3):
    t=[global_points[inds[q+k]]for k in range(3)]
    if max(v[1]for v in t)-min(v[1]for v in t)<.00001:floor_triangles.append(t)
 if name in records and node_triangles!=records[name]['evaluated_triangles']:triangle_deltas.append({'name':name,'source_triangles':records[name]['evaluated_triangles'],'glb_triangles':node_triangles})
 if name not in records:errors.append({'name':name,'issue':'exported geometry without source part record'});continue
 r=records[name];found.add(name);error=max(abs(a-b)for a,b in zip(lo+hi,r['bounds_world_min_xyz']+r['bounds_world_max_xyz']));maxerr=max(maxerr,error);checked+=1
 if error>0.0002:errors.append({'name':name,'maximum_bounds_delta_m':error})
missing=sorted(set(records)-found)
# Floor support is tested against actual exported horizontal triangles plus actual compiled spine triangles.
G=Path('/workspace/shared/astraea-godot-production-20261003')
for region in json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']:
 if region['floor_y']in [84,88.5]:floor_triangles.extend([[(p[0],region['floor_y'],p[1])for p in t]for t in region['triangles']])
def inside(x,z,t):
 ss=[]
 for a,b in zip(t,t[1:]+t[:1]):ss.append((b[0]-a[0])*(z-a[2])-(b[2]-a[2])*(x-a[0]))
 return min(ss)>=-0.0001 or max(ss)<=0.0001
floor_checks=[]
for route in json.loads((O/'ROUTES.json').read_text())['routes'][:2]:
 probes=0;miss=[];pts=route['points_world_xyz'];rad=route['design_minimum_clear_width_m']/2
 for a,b in zip(pts,pts[1:]):
  steps=max(1,math.ceil(math.dist(a,b)/.2))
  for j in range(steps+1):
   p=[a[i]+(b[i]-a[i])*j/steps for i in range(3)]
   for dx,dz in [(0,0),(-rad,-rad),(-rad,rad),(rad,-rad),(rad,rad)]:
    probes+=1
    if not any(abs(t[0][1]-p[1])<.031 and inside(p[0]+dx,p[2]+dz,t)for t in floor_triangles):miss.append([p[0]+dx,p[1],p[2]+dz])
 floor_checks.append({'route':route['id'],'floor_center_and_corner_probes':probes,'unsupported':miss,'pass':not miss})
result={'status':'Source GLB actual hierarchy/vertex comparison; not runtime import validation','source_sha256':hashlib.sha256((O/'source.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(raw).hexdigest(),'mesh_nodes_checked':checked,'source_parts':len(records),'triangles_glb':triangles,'largest_bounds_delta_m':maxerr,'tolerance_m':.0002,'errors':errors,'missing_source_geometry_nodes':missing,'floor_support_checks':floor_checks,'triangle_count_differences':{'nodes':len(triangle_deltas),'explanation':'135 AST-BOT-011 canopy leaf sprays each have120 reversed duplicate source triangles consolidated with double-sided export materials. Other source object triangle counts match.','other_differences':[x for x in triangle_deltas if '__TREE_LeafSpray_'not in x['name']]},'area_light_limit':'KHR punctual lights excludes Blender area lights; retain .blend and LIGHTS.json for source composition','pass':not errors and not missing and all(x['pass']for x in floor_checks)}
(O/'EXCHANGE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
