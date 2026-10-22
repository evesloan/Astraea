from pathlib import Path
import json,struct,hashlib,numpy as np,collections
P=Path(__file__).resolve().parent;G=P.parent;R=G.parent;d=json.loads((P/'PACKAGE.json').read_text());checks=[];bounds=[]
def check(ok,label):checks.append({'pass':bool(ok),'label':label})
def matrix(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1.]])
 m[:3,:3]=m[:3,:3]@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
for r in d['rooms']:
 i=r['allocation']['source_envelope_index'];a=r['allocation'];b=(G/'assets/models'/r['model_file']).read_bytes();check(hashlib.sha256(b).hexdigest()==r['model_sha256'],f'{i} export hash');j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);world={};children={};roots=j['scenes'][j.get('scene',0)]['nodes']
 def visit(k,m):
  n=j['nodes'][k];world[k]=m@matrix(n);children[k]=n.get('children',[])
  for c in children[k]:visit(c,world[k])
 for k in roots:visit(k,np.eye(4))
 def points(k):
  n=j['nodes'][k];out=[]
  if 'mesh'in n:
   for primitive in j['meshes'][n['mesh']]['primitives']:
    access=j['accessors'][primitive['attributes']['POSITION']];lo,hi=access['min'],access['max'];v=np.array([[x,y,z,1]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]);out.extend((world[k]@v.T).T[:,:3])
  for c in children[k]:out.extend(points(c))
  return out
 for c in r['components']:
  candidates=[k for k,n in enumerate(j['nodes'])if n.get('extras',{}).get('role')==c['name']];check(len(candidates)==1,f'{i} unique native component {c["name"]}')
  if len(candidates)!=1:continue
  pts=np.array(points(candidates[0]));lo,hi=pts.min(axis=0),pts.max(axis=0);record={'allocation':i,'component':c['name'],'catalogue_id':c['catalogue_id'],'min':lo.tolist(),'max':hi.tolist()};bounds.append(record)
  check(lo[0]>=a['allocation_x'][0]-.03 and hi[0]<=a['allocation_x'][1]+.03 and lo[2]>=a['allocation_z'][0]-.03 and hi[2]<=a['allocation_z'][1]+.03,f'{i} component inside exact allocation {c["name"]}')
  if c['catalogue_id']=='AST-RST-QC-001':
   rear=a['allocation_x'][1]if a['allocation_x'][0]>45 else a['allocation_x'][0];clear=rear-hi[0]if a['allocation_x'][0]>45 else lo[0]-rear;record['full_width_lounge_clear_depth']=clear;check(clear>=2.8,f'{i} cocoon leaves2.8m minimum full-width view lounge')
 check(len([c for c in r['components']if 'rest_slot_id'in c])==a['proposed_rest_place_count'],f'{i} original reserved rest count')
for path,h in d['preimage_pins'].items():check(hashlib.sha256((R/path).read_bytes()).hexdigest()==h,'retained preimage '+path)
failed=[x for x in checks if not x['pass']];out={'status':'FAIL'if failed else'PASS','checks':checks,'component_bounds':bounds,'failed':failed,'scope':'Exact allocation containment and native-export viewing-lounge clearance; not body/species or final visual acceptance'};(P/'evidence/GEOMETRY_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('GEOMETRY',len(checks),'failed',len(failed));print('\n'.join(x['label']for x in failed[:25]))
