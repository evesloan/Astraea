"""Read actual native GLB nodes/vertices/normals and bind source physical markers in all exported states."""
from pathlib import Path
import json,math,importlib.util,hashlib
import numpy as np
from scipy.spatial import cKDTree
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native_parser',BASE/'qa/validate_glb.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
def rot(a):
 a=math.radians(a);c=math.cos(a);s=math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def closest(p,a,b,c):
 ab=b-a;ac=c-a;ap=p-a;d1=ab@ap;d2=ac@ap
 if d1<=0 and d2<=0:return a
 bp=p-b;d3=ab@bp;d4=ac@bp
 if d3>=0 and d4<=d3:return b
 vc=d1*d4-d3*d2
 if vc<=0 and d1>=0 and d3<=0:return a+(d1/(d1-d3))*ab
 cp=p-c;d5=ab@cp;d6=ac@cp
 if d6>=0 and d5<=d6:return c
 vb=d5*d2-d1*d6
 if vb<=0 and d2>=0 and d6<=0:return a+(d2/(d2-d6))*ac
 va=d3*d6-d5*d4
 if va<=0 and d4-d3>=0 and d5-d6>=0:return b+((d4-d3)/(d4-d3+d5-d6))*(c-b)
 den=1/(va+vb+vc);return a+ab*(vb*den)+ac*(vc*den)
source=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());reports=[]
for ident,data in source.items():
 rec=json.loads((BASE/f'{ident}.manifest.json').read_text());states=[{'export':rec['export'],'root':None}]+rec['state_derivatives'];motions={m['root']:m for m in rec['motion_records']}
 for st in states:
  path=BASE/st['export'];doc,blob=g.read(path);nodes={};parent_names={};surfaces={};groupverts={}
  def walk(ix,parent,parent_name):
   n=doc['nodes'][ix];m=parent@g.matrix(n);nodes[n['name']]=(n,m);parent_names[n['name']]=parent_name
   if 'mesh'in n:
    tris=[];vlist=[]
    for pr in doc['meshes'][n['mesh']]['primitives']:
     v=g.accessor(doc,blob,pr['attributes']['POSITION']);world=(m@np.column_stack((v,np.ones(len(v)))).T).T[:,:3];indices=g.accessor(doc,blob,pr['indices']).reshape(-1,3);tris.extend(world[indices]);vlist.extend(world)
    parts=json.loads(n.get('extras',{}).get('semantic_parts','[]'))
    for name in parts:surfaces[name]=np.array(tris);groupverts[name]=np.array(vlist)
   for ch in n.get('children',[]):walk(ch,m,n['name'])
  for ix in doc['scenes'][doc.get('scene',0)]['nodes']:walk(ix,np.eye(4),None)
  checks=[];vertexchecks=[]
  def transformed(p,root,normal=False):
   p=np.array(p,dtype=float)
   if root==st['root']:
    motion=motions[root]
    if motion['kind']=='rotation':p=rot(motion['travel'])@p if normal else rot(motion['travel'])@(p-motion['pivot_source_m'])+motion['pivot_source_m']
    elif not normal:p=p+[0,motion['travel'],0]
   return C@p
  for mar in rec['physical_and_proposal_markers']:
   n,m=nodes[mar['name']];actual=m[:3,3];expected=transformed(mar['source_m'],mar['parent_root']);err=float(np.linalg.norm(actual-expected));row={'name':mar['name'],'kind':mar['kind'],'actual_native_world_m':actual.tolist(),'expected_native_world_m':expected.tolist(),'position_error_m':err,'actual_parent':parent_names[mar['name']],'parent_matches':parent_names[mar['name']]==mar['parent_root'],'passes':err<2e-6 and parent_names[mar['name']]==mar['parent_root']}
   if mar['physical_part']:
    tr=surfaces[mar['physical_part']];dist=np.array([np.linalg.norm(actual-closest(actual,*t))for t in tr]);near=tr[dist<2e-6];row['actual_native_surface_distance_m']=float(dist.min());row['passes'] &= bool(dist.min()<2e-6)
    if 'direction_source'in mar:
     normal=transformed(mar['direction_source'],mar['parent_root'],True);nn=np.cross(near[:,1]-near[:,0],near[:,2]-near[:,0]);nn/=np.linalg.norm(nn,axis=1)[:,None];dot=float(np.max(nn@normal))if len(nn)else-1;row['physical_surface_normal_dot']=dot;row['passes'] &= dot>.999
   checks.append(row)
  for part in data['parts']:
   v=np.array(part['vertices'])[np.unique(np.array(part['triangles']))];expected=np.array([transformed(p,part['parent'])for p in v]);d=cKDTree(groupverts[part['name']]).query(expected)[0];vertexchecks.append({'part':part['name'],'compared_source_used_vertices':len(v),'max_nearest_native_vertex_error_m':float(d.max()),'passes':bool(d.max()<2e-6)})
  wrong=[float(np.linalg.norm(np.array(m['source_m'])-nodes[m['name']][1][:3,3]))for m in rec['physical_and_proposal_markers']if m['physical_part']]
  reports.append({'file':st['export'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'markers':checks,'source_geometry_native_vertex_binding':vertexchecks,'wrong_axis_unconverted_source_detected':max(wrong)>.1,'passes':all(x['passes']for x in checks+vertexchecks)and max(wrong)>.1})
out={'source_to_native_basis':C.tolist(),'results':reports,'all_passed':all(r['passes']for r in reports)};(BASE/'qa/native_marker_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('NATIVE_MARKERS',out['all_passed'],[(r['file'],[x['name']for x in r['markers']if not x['passes']])for r in reports])
