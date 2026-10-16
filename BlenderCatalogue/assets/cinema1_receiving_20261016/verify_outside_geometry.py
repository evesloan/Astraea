from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
D=Path(__file__).resolve().parent;G=Path('/workspace/Astraea/Game');receipt=json.loads((D/'NATIVE_VERIFICATION.json').read_text())
def load(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def accessor(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];t={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dt=np.dtype(t);return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def faces(j,b,name):
 node=next(n for n in j['nodes']if n.get('name')==name);out=[]
 x,y,z,w=node.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 transform=np.eye(4);transform[:3,:3]=rot@np.diag(node.get('scale',[1,1,1]));transform[:3,3]=node.get('translation',[0,0,0])
 if 'matrix'in node:transform=np.array(node['matrix']).reshape(4,4).T
 for p in j['meshes'][node['mesh']]['primitives']:
  vs=accessor(j,b,p['attributes']['POSITION']);uv=accessor(j,b,p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else np.zeros((len(vs),2));ix=accessor(j,b,p['indices']).reshape(-1)if'indices'in p else np.arange(len(vs))
  out += [[{'p':(transform@np.r_[vs[i].astype(float),1])[:3]+np.array([11,69.5,-468]),'uv':uv[i].astype(float)}for i in tri]for tri in ix.reshape(-1,3)]
 return out

def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k]+(e[k]-s[k])*t for k in ['p','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out

def cut(poly,z,tolerance=0.):
 pieces=[];inside=poly
 for axis,plane,less in[(1,69.5-tolerance,False),(1,72.7+tolerance,True),(2,-403.5-tolerance,False),(2,-401.1+tolerance,True)]:
  p=clip(inside,axis,plane,not less)
  if len(p)>=3:pieces.append(p)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
def subtract(tri,tolerance=0.):
 polys=[tri]
 for z in [0.]:polys=[part for poly in polys for part in cut(poly,z,tolerance)]
 return [[poly[0],poly[i],poly[i+1]]for poly in polys for i in range(1,len(poly)-1)]
def key(tri):return tuple(sorted(tuple(round(float(x),4)for x in np.r_[v['p'],v['uv']])for v in tri))
from shapely.geometry import Polygon
from shapely.ops import unary_union
a,ab=load(G/'assets/models/WP13_cinema1.glb');n,nb=load(D/'exports/CINEMA1_SERVICE_RECEIVER_r001.glb');results=[]
for row in receipt['walls']:
 source=faces(a,ab,row['source_name']);new=faces(n,nb,row['replacement_name'])
 def reveal(t):
  xlo,xhi=row['reveal_x']
  if all(-403.5001<=v['p'][2]<=-401.0999 and xlo-.0001<=v['p'][0]<=xhi+.0001 and 69.4999<=v['p'][1]<=72.7001 for v in t):
   return all(abs(v['p'][1]-72.7)<.0001 for v in t)or any(all(abs(v['p'][2]-zz)<.0001 for v in t)for zz in[-403.5,-401.1])
  return False
 skin=[t for t in new if not reveal(t)];maxerr=0.;maxuv=0.;missing=0.;excess=0.;missing_outside_tolerance=0.;excess_outside_tolerance=0.
 # Every non-reveal vertex and centroid must lie on the immutable source skin with the same interpolated UV.
 for t in skin:
  samples=list(t)+[{'p':sum(v['p']for v in t)/3,'uv':sum(v['uv']for v in t)/3}]
  for q in samples:
   matches=[]
   for old in source:
    v0,v1,v2=[v['p']for v in old];mat=np.column_stack((v1-v0,v2-v0));w=np.linalg.lstsq(mat,q['p']-v0,rcond=None)[0];err=np.linalg.norm(v0+mat@w-q['p']);uv=old[0]['uv']+w[0]*(old[1]['uv']-old[0]['uv'])+w[1]*(old[2]['uv']-old[0]['uv']);ue=np.linalg.norm(uv-q['uv'])
    candidates=[]
    if min(w)>=0 and sum(w)<=1:candidates.append((v0+mat@w,old[0]['uv']+w[0]*(old[1]['uv']-old[0]['uv'])+w[1]*(old[2]['uv']-old[0]['uv'])))
    for k in range(3):
     va,vb=old[k],old[(k+1)%3];edge=vb['p']-va['p'];length2=np.dot(edge,edge);t=np.clip(np.dot(q['p']-va['p'],edge)/length2,0,1)if length2>1e-20 else 0;candidates.append((va['p']+edge*t,va['uv']+(vb['uv']-va['uv'])*t))
    closest,uv=min(candidates,key=lambda pair:np.linalg.norm(pair[0]-q['p']));err=np.linalg.norm(closest-q['p']);ue=np.linalg.norm(uv-q['uv'])
    if err<.0001 and ue<.0001:matches.append((err,ue))
   assert matches,('source skin/UV',q)
   e,u=min(matches);maxerr=max(maxerr,e);maxuv=max(maxuv,u)
 # Independent polygon coverage for every original triangle, including bevels; clipped triangulation may differ.
 for old in source:
  ps=[v['p']for v in old];normal=np.cross(ps[1]-ps[0],ps[2]-ps[0]);norm=np.linalg.norm(normal)
  if norm<1e-10:continue
  normal/=norm;axis=int(np.argmax(abs(normal)));axes=[i for i in range(3)if i!=axis]
  original=Polygon([v[axes]for v in ps]);expected=unary_union([Polygon([v['p'][axes]for v in t])for t in subtract(old)]).intersection(original)
  coplanar=[t for t in skin if max(abs(np.dot(v['p']-ps[0],normal))for v in t)<.0001]
  got_raw=unary_union([Polygon([v['p'][axes]for v in t])for t in coplanar]);got=got_raw.intersection(original)
  expected_strict=unary_union([Polygon([v['p'][axes]for v in t])for t in subtract(old,.0001)]).intersection(original);expected_loose=unary_union([Polygon([v['p'][axes]for v in t])for t in subtract(old,-.0001)]).intersection(original)
  missing+=expected.difference(got).area/max(abs(normal[axis]),1e-8);excess+=got.difference(expected).area/max(abs(normal[axis]),1e-8)
  missing_outside_tolerance+=expected_strict.difference(got_raw.buffer(.0001)).area/max(abs(normal[axis]),1e-8);excess_outside_tolerance+=got.difference(expected_loose.buffer(.0001)).area/max(abs(normal[axis]),1e-8)
 assert missing_outside_tolerance<1e-9 and excess_outside_tolerance<1e-9,(missing_outside_tolerance,excess_outside_tolerance)
 results.append({'node':row['source_name'],'original_triangles':len(source),'retained_skin_triangles':len(skin),'new_reveal_triangles':len(new)-len(skin),'max_position_error_m':maxerr,'max_uv_error':maxuv,'missing_skin_area_m2':missing,'excess_skin_area_m2':excess,'missing_outside_fixed_100um_tolerance_m2':missing_outside_tolerance,'excess_outside_fixed_100um_tolerance_m2':excess_outside_tolerance})
report={'status':'PASS_SOURCE_SKIN_POLYGON_COVERAGE_AND_INTERPOLATED_UV','fixed_position_tolerance_m':.0001,'fixed_uv_tolerance':.0001,'walls':results,'source_sha256':receipt['source_pins']['assets/models/WP13_cinema1.glb'],'new_model_sha256':receipt['model_sha256']};(D/'OUTSIDE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
