"""Actual existing-plant root contacts and conservative seat-space checks from GLBs."""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('reader',BASE/'qa/validate_glb.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def triangles(path,role=None):
 d,b=r.read(path);out=[]
 def walk(i,parent):
  n=d['nodes'][i];m=parent@r.matrix(n)
  if 'mesh'in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    if role and d['materials'][p['material']]['name']!='ASTRAEA_'+role:continue
    v=r.accessor(d,b,p['attributes']['POSITION']);v=(m@np.c_[v,np.ones(len(v))].T).T[:,:3];v=v[:,[0,2,1]];v[:,1]*=-1;ix=r.accessor(d,b,p['indices']).reshape(-1,3);out.extend(v[ix])
  for c in n.get('children',[]):walk(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return np.array(out)
def contains_xy(point,tr):
 a,b,c=tr[:,:2];p=np.array(point[:2]);mat=np.column_stack((b-a,c-a));det=np.linalg.det(mat)
 if abs(det)<1e-12:return False
 uv=np.linalg.solve(mat,p-a);return uv[0]>=-1e-7 and uv[1]>=-1e-7 and sum(uv)<=1+1e-7
soil=triangles(BASE/'exports/AST-SAL-004.glb','botanical_soil');seatvoid=next(v for v in json.loads((BASE/'AST-SAL-004.manifest.json').read_text())['receiver_voids']if v['name']=='open_above_seat');lo=np.array(seatvoid['min_source_m']);hi=np.array(seatvoid['max_source_m']);rows=[]
for ident,pos in [('AST-BOT-002',[.43,1.18,.62]),('AST-BOT-003',[-.84,1.18,.62])]:
 path=CAT/'assets/botanical_understory/exports'/f'{ident}.glb';tr=triangles(path);placed=tr+pos;root_z=float(placed[:,:,2].min());contacts=[i for i,t in enumerate(soil)if np.max(np.abs(t[:,2]-.62))<1e-6 and contains_xy(pos,t)]
 hits=np.where(np.all(placed.max(1)>lo,axis=1)&np.all(placed.min(1)<hi,axis=1))[0].tolist()
 wrong=placed+[0,-.6,0];negative=np.where(np.all(wrong.max(1)>lo,axis=1)&np.all(wrong.min(1)<hi,axis=1))[0].tolist()
 rows.append({'context_catalogue_id':ident,'existing_context_not_new_asset':True,'production_dependency':False,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'placement_source_m':pos,'root_lowest_z_m':root_z,'actual_soil_top_triangles_below_root':contacts,'seat_void_triangle_aabb_hits':hits,'forward_shift_negative_control_hit_count':len(negative),'passes':abs(root_z-.62)<1e-6 and bool(contacts)and not hits and bool(negative)})
out={'scope':'Existing actual GLBs at exact rendered QA placements. Root-lowest point on actual soil top, conservative triangle bounds stay outside finite proposed open seat volume. Deliberate0.60m forward-shift negative control is detected. Not botanical viability or actor/room acceptance.','assets':rows,'all_passed':all(r['passes']for r in rows)};(BASE/'qa/plant_context_contacts.json').write_text(json.dumps(out,indent=2)+'\n');print('PLANT_CONTEXT',out['all_passed']);assert out['all_passed']
