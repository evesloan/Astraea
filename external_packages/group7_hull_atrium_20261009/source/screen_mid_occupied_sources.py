"""Actual transformed received source census against new frame; preserve bytes."""
import json,hashlib,sys,re
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from check_retained_exports import read,acc,nodes
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_9d6f85';placements=json.loads((P/'qa/mid_occupied_source_placements.json').read_text());kind='skin' if len(sys.argv)>1 and sys.argv[1]=='skin' else 'frame';geo=json.loads((P/'qa'/('middle_skin_geometry.json' if kind=='skin' else 'middle_exterior_geometry.json')).read_text());part_min=np.array([np.array(g['vertices_world_xyz']).min(axis=0) for g in geo]);part_max=np.array([np.array(g['vertices_world_xyz']).max(axis=0) for g in geo]);rows=[];overlaps=[];potential_windows=[]
for r in placements:
 path=D/r['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['expected_sha256'],r['key'];d,b=read(path);yaw=r['yaw'];rot=np.array([[np.cos(yaw),0,np.sin(yaw)],[0,1,0],[-np.sin(yaw),0,np.cos(yaw)]]);origin=np.array(r['origin']);bounds=[];prim=[]
 for n,m in nodes(d):
  for q in d['meshes'][n['mesh']]['primitives']:
   a=acc(d,b,q['attributes']['POSITION']);a=((np.c_[a,np.ones(len(a))]@m.T)[:,:3]@rot.T)+origin;assert np.isfinite(a).all();lo=a.min(axis=0);hi=a.max(axis=0);bounds.append([lo,hi]);prim.append((n.get('name',''),q,a,lo,hi))
   if re.search(r'window|(?:^|[_\s])pane(?:s|[_\s]|$)|glaz|viewport|clerestory',n.get('name',''),re.I) and not re.search(r'guard|rail|sample|display|door|handle',n.get('name',''),re.I):
    potential_windows.append({'programme_key':r['key'],'source':r['path'],'node':n.get('name',''),'world_bounds':[lo.tolist(),hi.tolist()],'authority':'Retained candidate window-named mesh; name alone does not prove an exterior pressure window, view ray, private window ownership or adoption seam'})
 lo=np.array(bounds)[:,0].min(axis=0);hi=np.array(bounds)[:,1].max(axis=0);coarse=np.flatnonzero(np.all(np.minimum(part_max,hi)-np.maximum(part_min,lo)>1e-5,axis=1));hits=[]
 if len(coarse):
  for name,q,a,pl,ph in prim:
   part_ids=coarse[np.all(np.minimum(part_max[coarse],ph)-np.maximum(part_min[coarse],pl)>1e-5,axis=1)]
   if not len(part_ids):continue
   idx=acc(d,b,q['indices']).ravel().astype(int);tri=a[idx].reshape(-1,3,3);tl=tri.min(axis=1);th=tri.max(axis=1)
   for i in part_ids:
    n=int(np.sum(np.all(np.minimum(th,part_max[i])-np.maximum(tl,part_min[i])>1e-5,axis=1)))
    if n:hits.append({'node':name,'new_part':geo[i]['object'],'triangle_AABB_candidates':n})
 if hits:overlaps.append({'key':r['key'],'hits':hits})
 rows.append({'key':r['key'],'source_sha256':r['expected_sha256'],'mesh_primitives':len(prim),'world_bounds':[lo.tolist(),hi.tolist()],'frame_whole_model_AABB_candidates':len(coarse),'frame_triangle_AABB_candidates':hits})
out={'passed':not overlaps,'sources':rows,'source_count':len(rows),'positive_triangle_AABB_candidates':overlaps,'scope':'44 transformed middle-deck received source models with exact hashes and placements. Exclusion proves separation only for these sources; legacy procedural/static model placements, future house/luxury exports, dynamic props and optical windows still require their own census. No engine/import.'}
(P/'qa'/('mid_occupied_skin_checks.json' if kind=='skin' else 'mid_occupied_source_checks.json')).write_text(json.dumps(out,indent=2)+'\n');(P/'docs/RETAINED_WINDOW_NAMED_MESH_INVENTORY.json').write_text(json.dumps({'status':'Read-only source evidence; strict pane token excludes identity panels. Not new windows or an adopted pressure opening schedule','meshes':potential_windows},indent=2)+'\n');print('MID_OCCUPIED_SOURCES',kind,len(rows),'window-named',len(potential_windows),'overlap groups',len(overlaps));assert out['passed'],str(overlaps)[:1000]
