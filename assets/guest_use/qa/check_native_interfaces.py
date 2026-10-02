"""Independent native-GLB markers, collision voids, and bounded chair approach check."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('reader',BASE/'qa/validate_glb.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def nodes(doc):
 out={}
 def walk(i,parent):
  n=doc['nodes'][i];m=parent@r.matrix(n);out[n['name']]=(n,m)
  for c in n.get('children',[]):walk(c,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return out
def geoms(doc,blob):
 out=[]
 for n,m in nodes(doc).values():
  if 'mesh'in n:
   for p in doc['meshes'][n['mesh']]['primitives']:
    v=r.accessor(doc,blob,p['attributes']['POSITION']);v=(m@np.c_[v,np.ones(len(v))].T).T[:,:3];ix=r.accessor(doc,blob,p['indices']).reshape(-1,3);out.append(v[ix])
 return np.concatenate(out)
coll=json.loads((BASE/'collision_proposals.json').read_text());rows=[]
for mp in sorted(BASE.glob('AST-GST-*.manifest.json')):
 rec=json.loads(mp.read_text());p=BASE/rec['export'];doc,blob=r.read(p);ns=nodes(doc);checks=[];vchecks=[]
 for m in rec['physical_and_proposal_markers']:
  n,t=ns[m['name']];delta=float(np.linalg.norm(t[:3,3]-m['gltf_m']));wrong=float(np.linalg.norm(t[:3,3]-m['source_m']));checks.append({'name':m['name'],'native_gltf_position_m':t[:3,3].tolist(),'expected_gltf_position_m':m['gltf_m'],'error_m':delta,'wrong_unconverted_source_error_m':wrong,'passes':delta<1e-6})
 for v in coll[rec['catalogue_id']]['preserve_voids']:
  lo=np.array(v['min_source_m'])+1e-6;hi=np.array(v['max_source_m'])-1e-6;hits=[]
  for sh in coll[rec['catalogue_id']]['shapes']:
   if sh['type']=='box':inter=np.all(np.maximum(lo,sh['min_source_m'])<np.minimum(hi,sh['max_source_m']))
   else:
    h=ConvexHull(sh['points_source_m']);sol=linprog([0,0,0],A_ub=h.equations[:,:3],b_ub=-h.equations[:,3],bounds=list(zip(lo,hi)),method='highs');inter=sol.success
   if inter:hits.append(sh['name'])
  vchecks.append({'name':v['name'],'collision_shape_intersections':hits,'passes':not hits})
 rows.append({'catalogue_id':rec['catalogue_id'],'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'marker_node_checks':checks,'collision_void_checks':vchecks,'collision_shape_count':len(coll[rec['catalogue_id']]['shapes']),'passes':all(x['passes']for x in checks+vchecks)})
# Actual GLB foot-space evidence for the labelled chair arrangement. Lamp placement
# equals render script (-.77,.14,0), yaw25deg. Convert native GLB vertices once.
lp=BASE/'exports/AST-GST-001.glb';d,b=r.read(lp);t=geoms(d,b);src=t[:,:,[0,2,1]].copy();src[:,:,1]*=-1
ang=np.radians(25);rot=np.array([[np.cos(ang),-np.sin(ang),0],[np.sin(ang),np.cos(ang),0],[0,0,1]])
placed=src@rot.T+[-.77,.14,0];low=placed[np.min(placed[:,:,2],axis=1)<.09]
# Proposed front approach volume, clearly labelled an inspection datum; no actor.
lo=np.array([-.40,-.98,.001]);hi=np.array([.40,-.34,.35]);intersect=[i for i,tr in enumerate(placed)if np.all(tr.max(0)>lo)and np.all(tr.min(0)<hi)]
cp=CAT/'assets/furniture/AST-FUR-002_day_reading_chair.glb';cd,cb=r.read(cp);ct=geoms(cd,cb);chair_min_x=float(ct[:,:,0].min());side_gap=chair_min_x-float(placed[:,:,0].max())
approach={'minimum_conservative_chair_lamp_x_gap_m':side_gap,'actual_chair_glb_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'scope':'Conservative actual imported-lamp triangle bounds against a proposed chair-front foot-space box; no actor/species certification','lamp_placement_source_m':[-.77,.14,0],'lamp_yaw_source_degrees':25,'proposed_front_approach_box_source_m':{'min':lo.tolist(),'max':hi.tolist()},'lamp_triangle_bounds_intersections':intersect,'lamp_low_base_max_x_m':float(low[:,:,0].max()),'passes':not intersect and side_gap>0}
out={'assets':rows,'chair_lamp_approach':approach,'all_passed':all(r['passes']for r in rows)and approach['passes']};(BASE/'qa/native_interfaces_and_voids.json').write_text(json.dumps(out,indent=2)+'\n');print('NATIVE_INTERFACE_PASS',out['all_passed'])
assert out['all_passed']
