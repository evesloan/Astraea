"""Actual evaluated source geometry and witnesses. Not a production input."""
import bpy,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
M=json.loads((BASE/'manifest.json').read_text());out={'scope':'Actual source markers/normals/contact witnesses and reusable geometry snapshot; no host or physical acceptance','assets':{}};geo={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nearest(part,query):
 q=np.array(query,dtype=float);d=ge[part];best=None
 for face in d['triangles']:
  a,b,c=np.array([d['vertices'][i]for i in face],dtype=float);ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.linalg.norm(n)
  if nn<1e-14:continue
  n/=nn;proj=q-n*np.dot(q-a,n);v=proj-a
  u11=np.dot(ab,ab);u12=np.dot(ab,ac);u22=np.dot(ac,ac);det=u11*u22-u12*u12
  v1=(np.dot(v,ab)*u22-np.dot(v,ac)*u12)/det;v2=(np.dot(v,ac)*u11-np.dot(v,ab)*u12)/det
  points=[]
  if v1>=-1e-12 and v2>=-1e-12 and v1+v2<=1+1e-12:points.append(proj)
  for st,en in((a,b),(b,c),(c,a)):
   e=en-st;points.append(st+max(0,min(1,np.dot(q-st,e)/np.dot(e,e)))*e)
  for pp in points:
   dist=np.linalg.norm(q-pp)
   if best is None or dist<best[3]:best=(Vector(pp),Vector(n),0,float(dist))
 return best

for r in M['assets']:
 ident=r['catalogue_id'];p=BASE/r['source'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();ge={};trees={};parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];checks=[];joins=[]
 for o in parts:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vs=[o.matrix_world@v.co for v in me.vertices];fs=[list(tr.vertices)for tr in me.loop_triangles];trees[o.name]=BVHTree.FromPolygons(vs,fs,all_triangles=True)
  ge[o.name]={'vertices':[list(v)for v in vs],'triangles':fs,'owner':o.parent.name,'role':o['material_role']};ev.to_mesh_clear()
 for m in r['physical_and_proposal_markers']:
  if not m.get('physical_part'):continue
  pos=Vector(m['source_m']);tree=trees[m['physical_part']];pt,n,idx,dist=nearest(m['physical_part'],pos);dot=n.dot(Vector(m['direction_source']))if m.get('direction_source')else None
  checks.append({'name':m['name'],'part':m['physical_part'],'actual_marker_node_position_m':list(bpy.data.objects[m['name']].matrix_world.translation),'distance_m':dist,'normal_dot':dot,'passed':dist<2e-6 and (dot is None or dot>.999)})
 for j in r['joins']:
  ps=Vector(j['probe_source_m']);hits=[]
  for side,part in zip(('a','b'),j['parts']):
   pt,n,idx,dist=nearest(part,ps);wanted=j.get('normal_'+side+'_source');inside=(ps-pt).dot(n)<=2e-6
   hits.append({'part':part,'distance_m':dist,'signed_nearest_m':(ps-pt).dot(n),'normal_dot':n.dot(Vector(wanted))if wanted else None,'passed':(dist<2e-6 and n.dot(Vector(wanted))>.999)if wanted else inside})
  joins.append({'name':j['name'],'parts':hits,'passed':all(x['passed']for x in hits)})
 row={'source_sha256':sha(p),'markers':checks,'joins':joins,'mesh_count':len(parts),'finite_vertices':all(math.isfinite(c)for a in ge.values()for v in a['vertices']for c in v)};row['passed']=all(q['passed']for q in checks+joins)and row['finite_vertices'];out['assets'][ident]=row;geo[ident]={'source_sha256':sha(p),'parts':ge}
out['all_passed']=all(r['passed']for r in out['assets'].values());(BASE/'qa/source_checks.json').write_text(json.dumps(out,indent=2));(BASE/'qa/source_geometry.json').write_text(json.dumps(geo));print(json.dumps(out,indent=2))
