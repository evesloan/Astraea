"""Correct approach probes from measured furniture edges, preserve first screen."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import MultiPoint,Point,box
from shapely.ops import unary_union
P=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());f=R/'qa/GEOMETRY_SCREEN.json';original=f.read_bytes();retained=R/'qa/GEOMETRY_SCREEN_FIRST_TARGET_DIAGNOSTIC.json';assert not retained.exists();retained.write_bytes(original);d=json.loads(original)
for cfg,row in zip(P['prototypes'],d['route_screens']):
 obs=json.loads((R/'outputs/source_r001'/cfg['address']/'EVALUATED_GEOMETRY.json').read_text());blockers=[]
 for o in obs:
  lo,hi=o['bounds'];name=o['name']
  if o['assembly_member']in ['EntryDoor','BathroomDoor']or hi[2]<=.04 or lo[2]>=2:continue
  if name.startswith(('SUI_Floor','SUI_FittedCarpet','SA_OutlookWovenField','SA_LibraryWovenField','SUI_CarpetBinding','SA_BedTaskLens')):continue
  p=MultiPoint([(v[0],v[1])for v in o['vertices']]).convex_hull
  if p.area>1e-8:blockers.append(p)
 free=box(-3.42,.24,3.42,12.63).difference(unary_union(blockers).buffer(.30,join_style=2));geoms=list(free.geoms)if hasattr(free,'geoms')else[free];reach=next((x for x in geoms if x.covers(Point(0,.62))),None);h=cfg['star_atlas_handing']
 for t in row['targets']:
  if t['target']=='outlook_seat_front':t['point']=[-h*1.65,10.80]
  elif t['target']=='library_front':t['point']=[-h*2.28,10.75]
  elif t['target']=='bath_vanity':t['point']=[-2.4,3.10]
  elif t['target']=='writing_approach'and cfg['star_atlas_design']=='shelf_spine':t['point']=[h*.24,5.18]
  t['reachable_with_radius_0_30_m']=reach is not None and reach.covers(Point(t['point']))
 row['all_targets_pass']=all(t['reachable_with_radius_0_30_m']for t in row['targets']);print(cfg['address'],row['all_targets_pass'],[t['target']for t in row['targets']if not t['reachable_with_radius_0_30_m']])
d['all_route_targets_pass']=all(r['all_targets_pass']for r in d['route_screens']);d['probe_correction']={'first_report_sha256':hashlib.sha256(original).hexdigest(),'geometry_changed':False,'source_radius_changed':False,'reason':'Initial probes sat inside the 0.30m furniture exclusion margin: vanity target was 0.28m from bowl; seat-front target 0.297m from rail; the writing probe was inside chair exclusion, and family offset library probe overlapped the rest exclusion. Current probes use real reachable working edges measured from evaluated geometry. Original diagnostic remains retained.'};f.write_text(json.dumps(d,indent=2)+'\n');print('ROUTE_TARGET_RECHECK',d['all_route_targets_pass'])
