"""Closed-parameter-box coverage of the lower shelves' previously lost depth.
The small 3mm-radius proxy describes depth clearance, not an actor or hand fit.
"""
from pathlib import Path
import ast,json,hashlib,math,itertools,sys
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'qa/batch07'))
from independent_geometry import Native,C
source=ast.parse((OUT/'validate_collision_revision.py').read_text())
selected=[x for x in source.body if isinstance(x,ast.FunctionDef) and x.name in ['hulls','segment_hull','point_tri_distance','segment_tri_distance']]
exec(compile(ast.Module(body=selected,type_ignores=[]),'shared_geometry_functions','exec'))
current=json.loads((ROOT/'assets/hospitality_counters/collision_proposals.json').read_text());old=json.loads((OUT/'original_inputs/assets/hospitality_counters/collision_proposals.json').read_text())
records=[]
for i in [1,2]:
 ident=f'AST-HSP-00{i}';hs=hulls(current[ident]);oh=hulls(old[ident]);native=Native(ROOT/f'assets/hospitality_counters/exports/{ident}.glb');tris=native.tris@C
 regions=([('left',.12,.66),('middle',.94,1.46),('right',1.74,2.28)] if i==1 else [('entry',.18,.35),('middle',.63,.94),('exit',1.22,1.40)])
 for label,lo,hi in regions:
  grid=np.linspace(lo,hi,math.ceil((hi-lo)/(.010 if i==1 else .005))+1);zs=np.linspace(.23,.40,35);inflation=((1. if i==1 else .924)*(grid[1]-grid[0])+(zs[1]-zs[0]))/2;radius=.003+inflation
  starts=[];ends=[]
  for x,z in itertools.product(grid,zs):
   if i==1:starts.append([x,.60,z]);ends.append([x,-.304,z])
   else:starts.append([.10*math.sin(x),.62-.10*math.cos(x),z]);ends.append([.924*math.sin(x),.62-.924*math.cos(x),z])
  starts=np.array(starts);ends=np.array(ends);blocked=np.zeros(len(starts),bool);old_blocked=np.zeros(len(starts),bool)
  for h in hs:blocked|=segment_hull(starts,ends,h,radius)
  for h in oh:old_blocked|=segment_hull(starts,ends,h)
  mind=.060;bad=[]
  for j,(a,b) in enumerate(zip(starts,ends)):
   low=np.minimum(a,b)-.06;high=np.maximum(a,b)+.06;near=tris[(tris.min(axis=1)<=high).all(axis=1)&(tris.max(axis=1)>=low).all(axis=1)]
   d=segment_tri_distance(a,b,near) if len(near) else .06;mind=min(mind,d)
   if d<radius-1e-7:bad.append(j)
  rec={'id':ident,'region':label,'coordinate':'source_x' if i==1 else 'angle_radians','closed_interval':[lo,hi],'source_z_closed_interval_m':[.23,.40],'path':'source y+.600 to y-.304' if i==1 else 'radius.100 to radius.924 about source(0,.620)','nominal_sphere_radius_m':.003,'covering_inflation_m':float(inflation),'tested_radius_m':float(radius),'sample_count':len(starts),'current_compound_blocked_count':int(blocked.sum()),'actual_visual_blocked_count':len(bad),'minimum_actual_visual_clearance_m':mind,'old_fascia_negative_control_blocked_centreline_count':int(old_blocked.sum()),'pass':not blocked.any() and not bad and bool(old_blocked.any())}
  records.append(rec);print(json.dumps(rec),flush=True)
report={'pass':all(r['pass'] for r in records),'checks':records,'current_collision_sha256':hashlib.sha256((ROOT/'assets/hospitality_counters/collision_proposals.json').read_bytes()).hexdigest(),'method':'Every point of each closed coordinate/height rectangle is within the inflated radius of a sampled segment. Expanded hull plane tests conservatively prove compound clearance; exact segment-to-triangle distances check actual visual clearance. Baseline whole-fascia hulls deliberately fail source-clear centrelines.','limits':['3mm sphere is a storage-depth geometric probe, not a body/hand fit claim.','Continuous regional coverage is bounded to the stated rectangles. No engine or mechanical certification.']}
(OUT/'deep_corridor_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS',report['pass'])
