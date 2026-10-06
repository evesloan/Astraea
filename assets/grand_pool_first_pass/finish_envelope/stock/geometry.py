"""Standard-library retained GLB geometry reader and conservative predicates."""
import json, math, struct, itertools
EPS=1e-6

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length(a):return math.sqrt(dot(a,a))
def unit(a):return mul(a,1/length(a))
def bounds(v):return [list(map(min,zip(*v))),list(map(max,zip(*v)))]
def overlap(a,b,eps=EPS):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>eps for i in range(3))
def corners(b):return list(itertools.product(*zip(*b)))
def rotate(v,yaw):c,s=math.cos(yaw),math.sin(yaw);return(c*v[0]+s*v[2],v[1],-s*v[0]+c*v[2])
def transform(v,position,yaw):return add(rotate(v,yaw),position)
def eye():return[[float(i==j)for j in range(4)]for i in range(4)]
def mm(a,b):return[[sum(a[i][k]*b[k][j]for k in range(4))for j in range(4)]for i in range(4)]
def mv(m,v):v=(*v,1);return tuple(sum(m[i][j]*v[j]for j in range(4))for i in range(3))
def read_glb(path):
 b=path.read_bytes();magic,version,size=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and size==len(b)
 off=12;doc=buf=None
 while off<len(b):
  size,typ=struct.unpack_from('<II',b,off);chunk=b[off+8:off+8+size];off+=8+size
  if typ==0x4e4f534a:doc=json.loads(chunk)
  elif typ==0x004e4942:buf=chunk
 assert doc is not None and buf is not None
 def accessor(i):
  a=doc['accessors'][i];assert 'sparse' not in a;v=doc['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0
  kind={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+kind*n;size=struct.calcsize(fmt);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
  return[struct.unpack_from(fmt,buf,start+k*stride)for k in range(a['count'])]
 meshes=[];markers={}
 def visit(i,parent):
  node=doc['nodes'][i]
  if 'matrix'in node:m=[node['matrix'][j::4]for j in range(4)]
  else:
   x,y,z,w=node.get('rotation',[0,0,0,1]);m=eye();r=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
   for row in range(3):
    for col in range(3):m[row][col]=r[row][col]*node.get('scale',[1,1,1])[col]
    m[row][3]=node.get('translation',[0,0,0])[row]
  world=mm(parent,m);markers[node.get('name',str(i))]=mv(world,(0,0,0))
  if'mesh'in node:
   mesh=doc['meshes'][node['mesh']]
   for pi,p in enumerate(mesh['primitives']):
    assert p.get('mode',4)==4;v=[mv(world,q)for q in accessor(p['attributes']['POSITION'])];ix=[t[0]for t in accessor(p['indices'])]if'indices'in p else list(range(len(v)));assert len(ix)%3==0
    tri=[tuple(v[j]for j in ix[k:k+3])for k in range(0,len(ix),3)];meshes.append({'name':node.get('name',mesh.get('name','mesh')),'primitive':pi,'vertices':v,'triangles':tri,'bounds':bounds(v)})
  for j in node.get('children',[]):visit(j,world)
 for n in doc['scenes'][doc.get('scene',0)]['nodes']:visit(n,eye())
 return{'meshes':meshes,'markers':markers,'vertices':[v for m in meshes for v in m['vertices']],'triangles':[t for m in meshes for t in m['triangles']]}

def bary_xz(p,t,tol=EPS):
 a,b,c=t;u=(b[0]-a[0],b[2]-a[2]);v=(c[0]-a[0],c[2]-a[2]);w=(p[0]-a[0],p[2]-a[2]);d=u[0]*v[1]-v[0]*u[1]
 if abs(d)<1e-12:return None
 q=(w[0]*v[1]-v[0]*w[1])/d;r=(u[0]*w[1]-w[0]*u[1])/d
 return(1-q-r,q,r)if min(q,r,1-q-r)>=-tol else None

def horizontal_hits(p,triangles,up=True):
 out=[]
 for idx,t in enumerate(triangles):
  n=cross(sub(t[1],t[0]),sub(t[2],t[0]));ln=length(n)
  if ln<1e-12 or (n[1]/ln<(0.99 if up else -1.01)if up else n[1]/ln>-.99):continue
  bc=bary_xz(p,t)
  if bc is not None:out.append((sum(t[k][1]*bc[k]for k in range(3)),idx,t))
 return out

def convex_box_overlap(part,box):
 """Full SAT: convex source polyhedron vs complete axis-aligned item envelope. Contact allowed."""
 if not overlap(part['bounds'],box):return False
 v=part['vertices'];bv=corners(box);axes=[(1,0,0),(0,1,0),(0,0,1)]
 for t in part['triangles']:
  e=[sub(t[(k+1)%3],t[k])for k in range(3)];axes.append(cross(e[0],e[1]))
  for x in e:
   axes.extend(cross(x,a)for a in ((1,0,0),(0,1,0),(0,0,1)))
 for axis in axes:
  ln=length(axis)
  if ln<1e-10:continue
  a=[dot(p,axis)for p in v];b=[dot(p,axis)for p in bv]
  if min(max(a),max(b))-max(min(a),min(b))<=EPS*ln:return False
 return True

def check_convex(part):
 center=tuple(sum(p[i]for p in part['vertices'])/len(part['vertices'])for i in range(3))
 for t in part['triangles']:
  n=cross(sub(t[1],t[0]),sub(t[2],t[0]));ln=length(n)
  if ln<1e-10:continue
  if dot(n,sub(center,t[0]))>0:n=mul(n,-1)
  if max(dot(n,sub(v,t[0]))for v in part['vertices'])>EPS*ln:return False
 return True

def segment_triangle(a,b,t):
 d=sub(b,a);e1=sub(t[1],t[0]);e2=sub(t[2],t[0]);h=cross(d,e2);det=dot(e1,h)
 if abs(det)<1e-12:return None
 inv=1/det;s=sub(a,t[0]);u=dot(s,h)*inv
 if u<-EPS or u>1+EPS:return None
 q=cross(s,e1);v=dot(d,q)*inv
 if v<-EPS or u+v>1+EPS:return None
 f=dot(e2,q)*inv
 return f if -EPS<=f<=1+EPS else None

def triangle_intersects(a,b):
 if not overlap(bounds(a),bounds(b),-EPS):return False
 # SAT for triangles, including coplanar in-plane separating axes.
 ea=[sub(a[(i+1)%3],a[i])for i in range(3)];eb=[sub(b[(i+1)%3],b[i])for i in range(3)];na=cross(ea[0],ea[1]);nb=cross(eb[0],eb[1]);axes=[na,nb]+[cross(x,y)for x in ea for y in eb]+[cross(na,x)for x in ea]+[cross(nb,x)for x in eb]
 for axis in axes:
  ln=length(axis)
  if ln<1e-12:continue
  pa=[dot(p,axis)for p in a];pb=[dot(p,axis)for p in b]
  if max(min(pa),min(pb))-min(max(pa),max(pb))>EPS*ln:return False
 return True
