"""Actual source geometry screen across every shared Tidal Garden family."""
from pathlib import Path
import json,sys,math,runpy,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,MultiPoint,Point,box
from shapely.ops import unary_union
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');P=json.loads((R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json').read_text())
decode=runpy.run_path(str(W/'residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py'))['decode'];cache={}
rows=[];transforms=[];contacts=[];pairs=[]
def triangles(o):
 v=np.array(o['vertices']);return v[np.array(o['triangles'])]
def hits(a,b,t):
 d=b-a;e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*p,1);safe=np.abs(det)>1e-9;inv=np.where(safe,1/np.where(safe,det,1),0);tv=a-t[:,0];u=np.sum(tv*p,1)*inv;q=np.cross(tv,e1);v=np.sum(d*q,1)*inv;s=np.sum(e2*q,1)*inv;m=safe&(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)&(s>1e-5)&(s<1-1e-5);return a+s[m,None]*d
for cfg in P['prototypes']:
 key=cfg['address'];D=R/'outputs/interiors_r003'/key;obs=json.loads((D/'EVALUATED_GEOMETRY.json').read_text());by={}
 for o in obs:
  if o['assembly_member']:by.setdefault(o['assembly_member'],[]).append(o)
 for c in cfg['component_placements']:
  if c.get('candidate_source'):path=Path(c['candidate_source']).with_suffix('.glb')
  else:
   path=Path(c['catalogue_source']);path=CAT/path.parent.parent/'exports'/(path.stem+'.glb') if 'source'in path.parts else CAT/path.with_suffix('.glb')
  if path not in cache:cache[path]=decode(path)[1].reshape(-1,3)[:,[0,2,1]]*np.array([1,-1,1])
  a=c['source_yaw'];M=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);exp=cache[path]@M.T+np.array(c['source_xyz']);got=np.concatenate([o['vertices'] for o in by[c['label']]])
  err=max(float(np.abs(exp.min(0)-got.min(0)).max()),float(np.abs(exp.max(0)-got.max(0)).max()));transforms.append({'prototype':key,'component':c['label'],'bounds_error_m':err,'pass':err<.0001})
 # Conservative actual low-body projected obstruction polygons. Open-state door
 # leaves are excluded; this is no replacement for runtime moving-door collision.
 blockers=[]
 for o in obs:
  lo,hi=o['bounds'];name=o['name']
  if o['assembly_member'] in ['EntryDoor','BathroomDoor']:continue
  if hi[2]<=.04 or lo[2]>=2.0:continue
  if name.startswith(('SUI_Floor','SUI_FittedCarpet','FT_LivingWovenField','SUI_CarpetBinding','FT_BedTaskLens')):continue
  poly=MultiPoint([(v[0],v[1]) for v in o['vertices']]).convex_hull
  if poly.area>1e-8:blockers.append(poly)
 occupied=unary_union(blockers);free=box(-3.42,.24,3.42,12.63).difference(occupied.buffer(.30,join_style=2));entry=Point(0,.62)
 components=list(free.geoms) if hasattr(free,'geoms') else[free];reach=next((x for x in components if x.covers(entry)),None)
 h=cfg['family_terrace_handing'];shared=cfg['family_terrace_design']=='shared_table';targets=[('shared_window_surface',(0,11.75)),('group_bench_end',(-h*2.26 if shared else h*2.13,7.30)),('group_table_end',(cfg['group_surface_xyz'][0],6.82)),('kitchen_work',(1.80,1.60)),('bath_door_exterior',(-.18,2.90))]
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];yaw=a['source_yaw']
  if abs(yaw)>.1:pt=(x+h*1.60,y)
  else:pt=(x-math.copysign(1.015,x),y)
  targets.append(('rest_'+str(i),pt))
 outcomes=[{'target':n,'point':xy,'reachable_with_radius_0_30_m':reach is not None and reach.covers(Point(xy))} for n,xy in targets]
 rows.append({'prototype':key,'targets':outcomes,'all_targets_pass':all(x['reachable_with_radius_0_30_m'] for x in outcomes),'scope':'Conservative actual evaluated geometry planar route screen, 0.30m radius, door leaves omitted for open-state aperture. Not actual cart or species-body runtime test.'})
 # Exact triangle-edge crossing screen; keep shell-owner names for honest
 # classification of intended bathroom/service mounting and fixed door contacts.
 shells=[o for o in obs if not o['assembly_member'] and o['bounds'][1][2]>.04 and not o['name'].startswith(('SUI_Floor','SUI_FittedCarpet','SUI_CarpetBinding','FT_LivingWovenField'))]
 for member,parts in by.items():
  found=[]
  for ob in parts:
   t=triangles(ob);lo=t.min((0,1));hi=t.max((0,1));tl=t.min(1);th=t.max(1)
   for so in shells:
    sl,sh=np.array(so['bounds']);
    if not np.all(sh>=lo) or not np.all(sl<=hi):continue
    st=triangles(so);slo=st.min(1);shi=st.max(1);hit=None
    for tt in t:
     for a,b in zip(tt,np.roll(tt,-1,axis=0)):
      mi=np.minimum(a,b);ma=np.maximum(a,b);ix=np.where(np.all(shi>=mi,1)&np.all(slo<=ma,1))[0]
      if len(ix):
       pts=hits(a,b,st[ix]);pts=pts[pts[:,2]>.04]
       if len(pts):hit=pts[0].tolist();break
     if hit:break
    if hit:found.append({'furniture_part':ob['name'],'shell_part':so['name'],'point':hit})
  if found:contacts.append({'prototype':key,'component':member,'surface_crossings':found})
 # Furniture pairs: per-part convex footprint/height overlap is a conservative
 # broad screen and is reported separately from exact surface penetrations.
 names=list(by)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   if set([a,b])<=set(['bath_vanity','bath_wc','bath_shower','BathroomDoor']):continue
   overlaps=[]
   for oa in by[a]:
    la,ha=np.array(oa['bounds']);pa=MultiPoint(np.array(oa['vertices'])[:,:2]).convex_hull
    for ob in by[b]:
     lb,hb=np.array(ob['bounds']);
     if min(ha[2],hb[2])-max(la[2],lb[2])<.03:continue
     pb=MultiPoint(np.array(ob['vertices'])[:,:2]).convex_hull;ar=pa.intersection(pb).area
     if ar>.002:overlaps.append({'a':oa['name'],'b':ob['name'],'plan_overlap_m2':ar})
   if overlaps:pairs.append({'prototype':key,'a':a,'b':b,'overlaps':overlaps})
 print(key,'routes',rows[-1]['all_targets_pass'],'contacts',len(contacts),flush=True)
report={'all_component_transforms_pass':all(t['pass']for t in transforms),'all_route_targets_pass':all(r['all_targets_pass']for r in rows),'prototype_count':len(rows),'component_count':len(transforms),'transform_checks':transforms,'route_screens':rows,'shell_surface_contacts':contacts,'furniture_pair_broad_overlaps':pairs,'unit_count':82,'rest_slots':214,'adjacency_edges':len(P['adjacency_edges']),'runtime_acceptance':False}
(R/'qa/GEOMETRY_SCREEN.json').write_text(json.dumps(report,indent=2)+'\n');print('SUMMARY',report['all_component_transforms_pass'],report['all_route_targets_pass'],len(contacts),len(pairs))
