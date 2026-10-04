"""Raw native GLB transforms + triangle binding, no Blender imports."""
from pathlib import Path
import json,numpy as np,hashlib
B=Path(__file__).resolve().parents[1]
ns={};exec((B/'qa/validate_glb.py').read_text().split('records=[validate(')[0].replace('ROOT=Path(__file__).resolve().parents[1]',f'ROOT=Path({str(B)!r})'),ns)
read,accessor,matrix=ns['read'],ns['accessor'],ns['matrix']
M=json.loads((B/'manifest.json').read_text());S=json.loads((B/'qa/source_geometry.json').read_text());results=[]
C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
def nearest(tris,q):
 best=None
 for a,b,c in tris:
  ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.linalg.norm(n)
  if nn<1e-12:continue
  n/=nn;proj=q-n*np.dot(q-a,n);v=proj-a;u11=np.dot(ab,ab);u12=np.dot(ab,ac);u22=np.dot(ac,ac);det=u11*u22-u12*u12
  v1=(np.dot(v,ab)*u22-np.dot(v,ac)*u12)/det;v2=(np.dot(v,ac)*u11-np.dot(v,ab)*u12)/det
  points=[]
  if v1>=-1e-11 and v2>=-1e-11 and v1+v2<=1+1e-11:points.append(proj)
  for st,en in((a,b),(b,c),(c,a)):
   e=en-st;points.append(st+np.clip(np.dot(q-st,e)/np.dot(e,e),0,1)*e)
  for p in points:
   d=np.linalg.norm(q-p)
   if best is None or d<best[0]-1e-10:best=(float(d),n)
 return best

def tris_sig(tris):return sorted(tuple(sorted(tuple(np.round(v,5))for v in tri))for tri in tris if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-12)
for r in M['assets']:
 ident=r['catalogue_id']
 for state,path in [('closed',r['export'])]+[(a['name'],a['export'])for a in r['state_derivatives']]:
  doc,blob=read(B/path);nodes={};groups={}
  def walk(i,parent):
   n=doc['nodes'][i];w=parent@matrix(n);nodes[n.get('name','')]=w
   if 'mesh'in n:
    owner=None;names=json.loads(n.get('extras',{}).get('semantic_parts','[]'))
    for part in names:
     if part in S[ident]['parts']:owner=S[ident]['parts'][part]['owner'];break
    role=n.get('extras',{}).get('material_role');ts=[]
    for p in doc['meshes'][n['mesh']]['primitives']:
     vs=accessor(doc,blob,p['attributes']['POSITION']);vs=(w@np.c_[vs,np.ones(len(vs))].T).T[:,:3];fs=accessor(doc,blob,p['indices']).reshape(-1,3);ts.extend(vs[fs])
    groups[(owner,role)]=np.array(ts)
   for ch in n.get('children',[]):walk(ch,w)
  for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
  travel={v['root']:v['access_m'] if state=='access'else 0 for v in r['motions']}
  srcgroups={}
  for name,p in S[ident]['parts'].items():
   vs=np.array(p['vertices']);vs[:,1]+=travel.get(p['owner'],0);vs=vs@C.T;srcgroups.setdefault((p['owner'],p['role']),[]).extend(vs[np.array(p['triangles'])])
  geom=[]
  for key,tris in srcgroups.items():geom.append({'owner':key[0],'role':key[1],'source_triangles':len(tris),'native_triangles':len(groups[key]),'rounded_10um_triangle_signature_match':tris_sig(tris)==tris_sig(groups[key])})
  checks=[]
  for m in r['physical_and_proposal_markers']:
   p=np.array(m['source_m'],float);p[1]+=travel.get(m['owner'],0);p=C@p;actual=nodes[m['name']][:3,3];row={'name':m['name'],'native_m':actual.tolist(),'expected_native_m':p.tolist(),'node_error_m':float(np.linalg.norm(p-actual))}
   if m['physical_part']:
    sp=S[ident]['parts'][m['physical_part']];d,n=nearest(groups[(sp['owner'],sp['role'])],p);row['physical_surface_distance_m']=d;row['normal_dot']=float(n@(C@np.array(m['direction_source'])))
   row['passed']=row['node_error_m']<2e-6 and row.get('physical_surface_distance_m',0)<2e-6 and row.get('normal_dot',1)>.999;checks.append(row)
  results.append({'asset':ident,'state':state,'export':path,'export_sha256':hashlib.sha256((B/path).read_bytes()).hexdigest(),'source_sha256':S[ident]['source_sha256'],'triangles':geom,'markers':checks,'wrong_axis_negative_control':float(np.linalg.norm(np.array([0,0,1])-C@np.array([0,0,1])))>1,'passed':all(x['rounded_10um_triangle_signature_match']for x in geom)and all(x['passed']for x in checks)})
out={'scope':'Actual native GLB node hierarchy and triangles; coordinates/normals separately converted from source; precision-bound tests, no runtime integration','results':results,'all_passed':all(x['passed']for x in results)};(B/'qa/native_marker_checks.json').write_text(json.dumps(out,indent=2));print('NATIVE',out['all_passed'])
