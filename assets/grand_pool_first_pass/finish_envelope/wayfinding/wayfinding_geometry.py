"""Engine-free, dependency-free geometry shared by preparation, checks and builder."""
import hashlib, itertools, json, math
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(a,k): return [x*k for x in a]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a,a))
def unit(a):
    n=norm(a)
    if n<1e-10: raise ValueError('Undefined direction')
    return mul(a,1/n)
def bounds(vs): return [[min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]]
def corners(b): return list(itertools.product(*zip(*b)))
def overlap(a,b,tol=1e-6): return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>tol for i in range(3))
def separation(a,b): return max(max(a[0][i]-b[1][i],b[0][i]-a[1][i]) for i in range(3))
def yaw_point(p,placement):
    t=placement['yaw_radians'];c,s=math.cos(t),math.sin(t)
    return add([c*p[0]+s*p[2],p[1],-s*p[0]+c*p[2]],placement['position_xyz'])
def blender_to_world(p,placement): return yaw_point([p[0],p[2],-p[1]],placement)
def local_point(sign,p):
    return add(sign['origin_xyz'],add(mul(sign['right_xyz'],p[0]),add(mul(sign['up_xyz'],p[1]),mul(sign['normal_xyz'],p[2]))))
def local_box(sign, b): return bounds([local_point(sign,p) for p in corners(b)])
def arrow_projection(route_from, route_to, right, up, normal):
    tangent=unit(sub(route_to,route_from));u=dot(tangent,right);v=dot(tangent,up);n=dot(tangent,normal)
    planar=math.hypot(u,v)
    if planar < .25: raise ValueError('Route is nearly normal to board; no truthful in-plane arrow')
    return {'route_from_xyz':route_from,'route_to_xyz':route_to,'world_unit_tangent':tangent,
            'projected_uv':[u,v],'normal_component':n,'unit_arrow_uv':[u/planar,v/planar],
            'angle_degrees_from_sign_right':math.degrees(math.atan2(v,u))}

def ray_triangle(origin,direction,triangle,epsilon=1e-10):
    a,b,c=triangle;e1=sub(b,a);e2=sub(c,a);h=cross(direction,e2);det=dot(e1,h)
    if abs(det)<epsilon:return None
    s=sub(origin,a);u=dot(s,h)/det
    if u < -epsilon or u > 1+epsilon:return None
    q=cross(s,e1);v=dot(direction,q)/det
    if v < -epsilon or u+v>1+epsilon:return None
    t=dot(e2,q)/det
    return t if t>=-epsilon else None

def point_on_triangle(p,tri,tol=1e-5):
    a,b,c=tri;n=cross(sub(b,a),sub(c,a));ln=norm(n)
    if ln<1e-12 or abs(dot(sub(p,a),n)/ln)>tol:return False
    d0=sub(b,a);d1=sub(c,a);d2=sub(p,a)
    aa,ab,bb,ac,bc=dot(d0,d0),dot(d0,d1),dot(d1,d1),dot(d0,d2),dot(d1,d2)
    den=aa*bb-ab*ab
    if abs(den)<1e-20:return False
    u=(bb*ac-ab*bc)/den;v=(aa*bc-ab*ac)/den
    return u>=-tol and v>=-tol and u+v<=1+tol

def contact_samples(patch,steps=5):
    b=patch['bounds_xyz'];axis=patch['normal_axis'];axes=[i for i in range(3) if i!=axis]
    out=[]
    for a in range(steps):
        for bidx in range(steps):
            p=b[0].copy()
            for k,t in zip(axes,[a/(steps-1),bidx/(steps-1)]): p[k]=b[0][k]+t*(b[1][k]-b[0][k])
            out.append(p)
    return out

def glb_triangles(path,translation=(0,0,0)):
    """Decode retained GLB positions/indices and complete node transforms, without Blender."""
    import struct
    data=Path(path).read_bytes();magic,version,length=struct.unpack_from('<III',data)
    if magic!=0x46546c67 or version!=2 or length!=len(data):raise ValueError('Invalid GLB')
    offset=12;doc=buf=None
    while offset<len(data):
        n,kind=struct.unpack_from('<II',data,offset);chunk=data[offset+8:offset+8+n];offset+=8+n
        if kind==0x4e4f534a:doc=json.loads(chunk)
        elif kind==0x004e4942:buf=chunk
    def accessor(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
        if 'sparse' in a or v.get('buffer',0)!=0:raise ValueError('Unsupported external/sparse accessor')
        fmt,size={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size*n)
        return [list(struct.unpack_from('<'+fmt*n,buf,start+j*stride)) for j in range(a['count'])]
    ident=[[float(i==j) for j in range(4)] for i in range(4)]
    def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    result=[]
    def visit(index,parent):
        node=doc['nodes'][index]
        if 'matrix' in node:m=[[node['matrix'][j*4+i] for j in range(4)] for i in range(4)]
        else:
            x,y,z,w=node.get('rotation',[0,0,0,1]);sc=node.get('scale',[1,1,1]);t=node.get('translation',[0,0,0])
            r=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
            m=[[r[i][j]*sc[j] for j in range(3)]+[t[i]] for i in range(3)]+[[0,0,0,1]]
        world=mm(parent,m)
        if 'mesh' in node:
            for prim in doc['meshes'][node['mesh']]['primitives']:
                if prim.get('mode',4)!=4:raise ValueError('Only triangle primitives supported')
                vs=accessor(prim['attributes']['POSITION']);vs=[[sum(world[i][k]*([*v,1][k]) for k in range(4))+translation[i] for i in range(3)] for v in vs]
                ids=[v[0] for v in accessor(prim['indices'])] if 'indices' in prim else list(range(len(vs)))
                result.extend([[vs[ids[j+k]] for k in range(3)] for j in range(0,len(ids),3)])
        for child in node.get('children',[]):visit(child,world)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,ident)
    return result
