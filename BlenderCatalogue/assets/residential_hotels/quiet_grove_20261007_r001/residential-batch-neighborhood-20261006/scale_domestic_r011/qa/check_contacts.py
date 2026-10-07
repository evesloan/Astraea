"""Supplementary export-based furniture/shell surface penetration probe.
Not an engine collider, route or clearance test; intentionally excludes floor contact.
"""
import runpy,json,math
from pathlib import Path
import numpy as np
R=Path('/workspace/scratch/375c2e438292/residential-batch-neighborhood-20261006/scale_domestic_r011');CAT=next(q for q in Path(__file__).resolve().parents if (q/'catalogue_manifest.json').is_file());REV='production_r011'
js=lambda p:json.loads(Path(p).read_text())
A={'protos':js(R/'PROTOTYPE_PLAN.json')};cache={};cache_names={}
decode=runpy.run_path(str('/workspace/scratch/375c2e438292/residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py'))['decode']
def to_blender(t):return t[:,:,[0,2,1]]*np.array([1,-1,1])
def model_path(component):
 if component.get("candidate_export"):return R/component["candidate_export"]
 p=Path(component["catalogue_source"])
 if 'source'in p.parts:return CAT/p.parent.parent/'exports'/(p.stem+'.glb')
 return CAT/p.with_suffix('.glb')
def hits(segment_start,segment_end,t):
 direction=segment_end-segment_start;e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];pv=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.sum(e1*pv,axis=1);safe=np.abs(det)>1e-9;inv=np.where(safe,1/np.where(safe,det,1),0);tv=segment_start-t[:,0];u=np.sum(tv*pv,axis=1)*inv;qv=np.cross(tv,e1);v=np.sum(direction*qv,axis=1)*inv;s=np.sum(e2*qv,axis=1)*inv
 mask=safe&(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)&(s>1e-5)&(s<1-1e-5)
 return segment_start+s[mask,None]*direction,np.flatnonzero(mask)
rows=[]
for p in A['protos']['rooms']:
 shell=to_blender(decode(R/'outputs'/REV/p['address']/'shell.glb')[1]);slo=shell.min(1);shi=shell.max(1);rc=js(R/'outputs'/REV/p['address']/'SOURCE_RECEIPT.json')
 for c in rc['placements']:
  f=model_path(c)
  if f not in cache:
   dd=decode(f);cache[f]=to_blender(dd[1]);cache_names[f]=dd[3]
  ang=c['source_yaw'];M=np.array([[math.cos(ang),-math.sin(ang),0],[math.sin(ang),math.cos(ang),0],[0,0,1]]);t=cache[f]@M.T+np.array(c['source_xyz']);lo=t.min((0,1));hi=t.max((0,1));ix=np.where(np.all(shi>=lo,1)&np.all(slo<=hi,1)&(shi[:,2]>.025))[0];st=shell[ix];sl=slo[ix];sh=shi[ix];found=[];seen=set()
  for ti,tt in enumerate(t):
   owner=cache_names[f][ti]
   if owner in seen:continue
   for a,b in ((tt[0],tt[1]),(tt[1],tt[2]),(tt[2],tt[0])):
    mi=np.minimum(a,b);ma=np.maximum(a,b);ix=np.where(np.all(sh>=mi,1)&np.all(sl<=ma,1))[0]
    if not len(ix):continue
    pts,_=hits(a,b,st[ix]);pts=[x.tolist()for x in pts if x[2]>.03]
    if pts:found.append({'node_material':owner,'point':pts[0]});seen.add(owner);break
  # Reverse direction catches shell edges passing through a large furniture face.
  tl=t.min(1);th=t.max(1)
  for tt in st:
   for a,b in ((tt[0],tt[1]),(tt[1],tt[2]),(tt[2],tt[0])):
    mi=np.minimum(a,b);ma=np.maximum(a,b);ix=np.where(np.all(th>=mi,1)&np.all(tl<=ma,1))[0]
    if not len(ix):continue
    pts,idx=hits(a,b,t[ix])
    for point,i in zip(pts,idx):
     owner=cache_names[f][ix[i]]
     if point[2]>.03 and owner not in seen:found.append({'node_material':owner,'point':point.tolist(),'direction':'shell_edge_through_furniture'});seen.add(owner)
  rows.append({'prototype':p['address'],'component':c['label'],'export_path':str(f),'furniture_aabb':(lo.tolist(),hi.tolist()),'surface_crossing_points':found})
out={'scope':'Supplementary exact GLB triangle-edge probe. Furniture exports represent catalogue source shapes; excludes floor contact and cannot certify complete contact/clearance. Crossings require source inspection.','results':rows,'crossing_pairs':sum(bool(r['surface_crossing_points'])for r in rows)}
(Path(__file__).parent/'BROAD_ALL_FURNITURE_SHELL_CONTACTS.json').write_text(json.dumps(out,indent=2)+'\n');print('CROSSING_PAIRS',out['crossing_pairs']);print(json.dumps({r['component']:r['surface_crossing_points']for r in rows if r['surface_crossing_points']},indent=2))

from collections import Counter
print('PAIR COUNTS',dict(Counter(r['component']for r in rows if r['surface_crossing_points'])))
