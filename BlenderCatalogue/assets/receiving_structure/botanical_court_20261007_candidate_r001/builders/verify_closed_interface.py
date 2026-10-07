from pathlib import Path
import json,struct,hashlib,math
import numpy as np
from shapely.geometry import Polygon,box,LineString,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=R.parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();geo=load(R/'NATIVE_GEOMETRY.json')
compiled=load(P/'candidate/Game/data/generated/structural_meshes.json');floor=unary_union([Polygon(t) for r in compiled['regions'] if r['floor_y']==27 for t in r['triangles']]);b=(R/'AST-ATR-001_botanical_receiving_closed002.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);blob=b[28+n:]
def accessor(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];size={'VEC3':3,'SCALAR':1}[a['type']];dt=np.dtype(dtype);return np.ndarray((a['count'],size),dtype=dtype,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*dt.itemsize),dt.itemsize))
def local(o):
 if 'matrix' in o:return np.array(o['matrix']).reshape(4,4).T
 x,y,z,w=o.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(o.get('scale',[1,1,1]));m[:3,3]=o.get('translation',[0,0,0]);return m
parents={c:i for i,o in enumerate(d['nodes']) for c in o.get('children',[])}
def world(i):return (world(parents[i]) if i in parents else np.eye(4))@local(d['nodes'][i])
triangles=[];bounds=[];maxerror=0;plinths=[]
for i,node in enumerate(d['nodes']):
 if 'mesh' not in node:continue
 obj=next(o for o in geo['objects'] if o['name']==node['name']);nv=np.array(obj['vertices_world']);parts=[]
 for prim in d['meshes'][node['mesh']]['primitives']:
  vs=accessor(prim['attributes']['POSITION']).astype(float);vs=(world(i)@np.c_[vs,np.ones(len(vs))].T).T[:,:3];inds=accessor(prim['indices']).reshape(-1,3);parts.extend(vs[inds]);err=max(np.min(np.linalg.norm(nv-v,axis=1)) for v in vs);maxerror=max(maxerror,float(err));assert err<3e-5,(node['name'],err)
 ts=np.array(parts);triangles.extend(parts);v=ts.reshape(-1,3);lo=v.min(0);hi=v.max(0);bounds.append({'name':node['name'],'min':lo.tolist(),'max':hi.tolist(),'triangles':len(parts)})
 assert len(parts)==len(obj['triangles']);assert lo[1]>=27-3e-5 and hi[1]<=28.15003
 foot=MultiPoint(v[:,[0,2]]).convex_hull
 assert floor.buffer(3e-5).covers(foot),(node['name'],foot.bounds)
 assert box(-4,-238,4,-208).intersection(foot).area<1e-7,node['name']
 if 'GuardPlinth' in node['name']:assert abs(lo[1]-27)<1e-7;plinths.append(node['name'])
triangles=np.array(triangles)
def ray_hit(origin,direction,length):
 a,b,c=triangles[:,0],triangles[:,1],triangles[:,2];e1=b-a;e2=c-a;h=np.cross(np.tile(direction,(len(a),1)),e2);det=np.einsum('ij,ij->i',e1,h);valid=np.abs(det)>1e-10;f=np.zeros(len(a));f[valid]=1/det[valid];s=origin-a;u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('j,ij->i',direction,q);t=f*np.einsum('ij,ij->i',e2,q);return bool(np.any(valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=0)&(t<=length)))
hits=0
for side,x,sign in [('port',-8,1),('starboard',8,-1)]:
 for z in np.linspace(-237.70,-208.30,295):
  for y in [27.08,27.4,27.7,28.04,28.10]:
   assert ray_hit(np.array([x+sign*.6,y,z]),np.array([-float(sign),0.,0.]),.8),(side,z,y)
   hits+=1
# Fore/aft end protection remains present.
for x0,x1 in [(-8,-4),(4,8)]:
 for z,sign in [(-238,1),(-208,-1)]:
  for x in np.linspace(x0+.3 if x0<0 else x0+.075,x1-.075 if x0<0 else x1-.3,38):
   for y in [27.08,27.4,27.7,28.04,28.10]:
    assert ray_hit(np.array([x,y,z+sign*.6]),np.array([0.,0.,-float(sign)]),.8),(x,z,y)
    hits+=1
# Diagonal inside-to-outside probes close the four mitred corners.
for x,sx in [(-8,1),(8,-1)]:
 for z,sz in [(-238,1),(-208,-1)]:
  for y in [27.08,27.4,27.7,28.04,28.10]:
   direction=np.array([-sx,0.,-sz])/math.sqrt(2)
   assert ray_hit(np.array([x+sx*.6,y,z+sz*.6]),direction,1.1),(x,z,y)
   hits+=1
# Safe receiving turnaround/stance stops short of the closed future thresholds.
routes=[]
for endx in [-6.2,6.2]:
 swept=LineString([(0,-240),(0,-216),(endx,-216)]).buffer(1.2,cap_style='square',join_style='mitre');assert floor.covers(swept)
 for b in bounds:assert swept.intersection(box(b['min'][0],b['min'][2],b['max'][0],b['max'][2])).area==0,(endx,b['name'])
 routes.append({'centerline':[[0,-240],[0,-216],[endx,-216]],'swept_width_m':2.4,'floor_supported':True,'closure_clear':True,'purpose':'Arrive, read closed-destination plaque, turn back; never enter absent room'})
# Source-facing label normal must point into the axial corridor, not toward absent rooms.
label_normals=[]
for i,node in enumerate(d['nodes']):
 if 'Label' in node.get('name',''):
  normal=world(i)[:3,:3]@np.array([0,1,0]);sign=1 if '_port_' in node['name'] else -1
  assert normal[0]*sign>.99,(node['name'],normal);label_normals.append({'name':node['name'],'normal_world':normal.tolist()})
result={'status':'PASS: closed source-only receiving assembly; no room-side support dependence','guards':'Two continuous mitred U-shaped barriers; all 60m outer edge closed; both future portal sections explicitly closed','segments':len(geo['segments']),'objects':len(bounds),'triangles':len(triangles),'native_export_max_vertex_error_m':maxerror,'actual_export_barrier_rays':hits,'supported_plinths':len(plinths),'axial_intrusions':0,'routes':routes,'labels':label_normals,'future_portals':[{'id':'D06_directory_03','center':[-8,27,-216],'width_m':4.2,'state':'CLOSED receiving interface'},{'id':'D06_directory_04','center':[8,27,-216],'width_m':6,'state':'CLOSED receiving interface'}],'limits':['No Game changes or Godot jobs.','Source-defined static collision proposal, not fresh engine/import/visual acceptance.','Future opening requires separately adopted support/enclosure and removal of closure plus boundary posts as needed to recover exact clear aperture.','No structural-load or final-species certification.'],'bounds':bounds}
(R/'CLOSED_INTERFACE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='bounds'},indent=2))
