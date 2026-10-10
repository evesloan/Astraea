import json,struct,hashlib,math

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def matmul(a,b):return [[sum(a[x][k]*b[k][y] for k in range(4)) for y in range(4)] for x in range(4)]
def node_matrix(node):
 if 'matrix' in node:return [[node['matrix'][c*4+r] for c in range(4)] for r in range(4)]
 x,y,z,w=node.get('rotation',[0,0,0,1]);s=node.get('scale',[1,1,1]);t=node.get('translation',[0,0,0]);a=[[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w,t[0]],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w,t[1]],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y,t[2]],[0,0,0,1]]
 for r in range(3):
  for c in range(3):a[r][c]*=s[c]
 return a

def read_glb(path):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw);n,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a;g=json.loads(raw[20:20+n]);p=20+n;ln,kind=struct.unpack_from('<II',raw,p);assert kind==0x004e4942;blob=raw[p+8:p+8+ln]
 def accessor(index):
  a=g['accessors'][index];assert 'sparse' not in a;v=g['bufferViews'][a['bufferView']];dim={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];size=struct.calcsize(fmt);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size*dim);return [struct.unpack_from('<'+fmt*dim,blob,off+i*stride) for i in range(a['count'])]
 identity=[[int(a==b) for b in range(4)] for a in range(4)];nodes=[]
 def visit(k,parent):
  node=g['nodes'][k];matrix=matmul(parent,node_matrix(node));vertices=[];triangles=[];normal_count=0;uv_count=0;max_normal_error=0;materials=[]
  if 'mesh' in node:
   for primitive in g['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4;local=accessor(primitive['attributes']['POSITION']);offset=len(vertices)
    vertices.extend(tuple(sum(matrix[r][c]*v[c] for c in range(3))+matrix[r][3] for r in range(3)) for v in local)
    indices=[a[0] for a in accessor(primitive['indices'])] if 'indices' in primitive else list(range(len(local)));assert len(indices)%3==0;triangles.extend(tuple(offset+indices[j+c] for c in range(3)) for j in range(0,len(indices),3))
    assert 'NORMAL' in primitive['attributes'] and 'TEXCOORD_0' in primitive['attributes'];normals=accessor(primitive['attributes']['NORMAL']);uvs=accessor(primitive['attributes']['TEXCOORD_0']);normal_count+=len(normals);uv_count+=len(uvs)
    assert all(math.isfinite(x) for v in vertices for x in v) and all(math.isfinite(x) for v in normals+uvs for x in v);max_normal_error=max(max_normal_error,max(abs(math.sqrt(sum(x*x for x in a))-1) for a in normals));materials.append(primitive.get('material'))
   bounds=[[min(v[c] for v in vertices) for c in range(3)],[max(v[c] for v in vertices) for c in range(3)]];nodes.append(dict(name=node['name'],extras=node.get('extras',{}),matrix=matrix,vertices=vertices,triangles=triangles,bounds=bounds,normals=normal_count,uvs=uv_count,normal_error=max_normal_error,materials=materials))
  for child in node.get('children',[]):visit(child,matrix)
 for k in g['scenes'][g.get('scene',0)]['nodes']:visit(k,identity)
 return g,nodes

def hull(points):
 p=sorted(set(tuple(round(x,6) for x in a) for a in points))
 if len(p)<3:return p
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 low=[];high=[]
 for a in p:
  while len(low)>1 and cross(low[-2],low[-1],a)<=0:low.pop()
  low.append(a)
 for a in reversed(p):
  while len(high)>1 and cross(high[-2],high[-1],a)<=0:high.pop()
  high.append(a)
 return low[:-1]+high[:-1]

def clip(poly,h,lower):
 if not poly:return []
 result=[];prev=poly[-1];inside=prev[1]>=h if lower else prev[1]<=h
 for curr in poly:
  current=curr[1]>=h if lower else curr[1]<=h
  if current!=inside:
   t=(h-prev[1])/(curr[1]-prev[1]);result.append(tuple(prev[k]+t*(curr[k]-prev[k]) for k in range(3)))
  if current:result.append(curr)
  prev=curr;inside=current
 return result

def projected_grid(nodes,floor,height):
 polygons=[];grid={};cell=3
 for node in nodes:
  if node['bounds'][1][1]<floor or node['bounds'][0][1]>floor+height:continue
  for tri in node['triangles']:
   p=clip(clip([node['vertices'][k] for k in tri],floor-.00001,True),floor+height,False)
   if not p:continue
   poly=[(v[0],v[2]) for v in p];index=len(polygons);polygons.append((node['name'],poly))
   for x in range(math.floor(min(a[0] for a in poly)/cell),math.floor(max(a[0] for a in poly)/cell)+1):
    for z in range(math.floor(min(a[1] for a in poly)/cell),math.floor(max(a[1] for a in poly)/cell)+1):grid.setdefault((x,z),[]).append(index)
 return polygons,grid

def poly_dist(p,poly):
 crosses=[];minimum=999
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1];crosses.append(dx*(p[1]-a[1])-dz*(p[0]-a[0]));den=dx*dx+dz*dz;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/den)) if den else 0;minimum=min(minimum,math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz))
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))
 if abs(area)>1e-9 and (all(x>=-1e-8 for x in crosses) or all(x<=1e-8 for x in crosses)):return 0
 return minimum

def route_check(polygons,grid,points,radius):
 blocked=[];poses=[];minimum=999
 for a,b in zip(points,points[1:]):
  steps=max(1,math.ceil(math.dist(a,b)/.1))
  for q in range(steps+1):
   t=q/steps;p=(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]));candidates=set()
   for x in range(math.floor((p[0]-radius)/3),math.floor((p[0]+radius)/3)+1):
    for z in range(math.floor((p[1]-radius)/3),math.floor((p[1]+radius)/3)+1):candidates.update(grid.get((x,z),[]))
   distance,name=min(((poly_dist(p,polygons[k][1]),polygons[k][0]) for k in candidates),default=(999,None));minimum=min(minimum,distance);poses.append(p)
   if distance<radius-.001:blocked.append(dict(point=p,node=name,distance=distance))
 return dict(passed=not blocked,poses=len(poses),sample_step_m=.1,radius_m=radius,min_actual_source_surface_distance_m=minimum,blocked=blocked[:30])
