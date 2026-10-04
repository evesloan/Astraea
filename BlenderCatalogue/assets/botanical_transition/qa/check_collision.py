"""Exact convex-vs-box feasibility, whole finite cavity checks, and collision samples."""
from pathlib import Path
import numpy as np,json,itertools,hashlib
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1];spec=json.loads((ROOT/'collision_proposals.json').read_text());solids=[]
for c in spec['solids']:
 p=np.unique(np.array(c['points_source_m']),axis=0);h=ConvexHull(p);solids.append({'name':c['name'],'planes':h.equations.tolist(),'vertices':p[h.vertices].tolist(),'triangles':p[h.simplices].tolist(),'min':p.min(0).tolist(),'max':p.max(0).tolist()})
boxes=[('seated_above_ribbon',[.010,-.485,.471],[1.790,-.025,1.350]),('lower_structural_soil_cavity',[.010,.160,.110],[.550,.870,.380]),('upper_structural_soil_cavity',[.690,.160,.370],[1.670,.870,.780]),('underseat_bay_1',[.280,-.420,.090],[.840,-.120,.340]),('underseat_bay_2',[.960,-.420,.090],[1.520,-.120,.340]),('under_upper_cell',[.850,.240,.115],[1.500,.790,.320]),('front_approach',[.010,-1.690,.005],[1.790,-.500,1.90]),('rear_maintenance_unplanted',[.010,1.080,.005],[1.790,1.880,1.90])]
voids=[]
for name,lo,hi in boxes:
 hits=[]
 for c in solids:
  if any(c['min'][i]>hi[i]or c['max'][i]<lo[i]for i in range(3)):continue
  eq=np.array(c['planes']);r=linprog([0,0,0],A_ub=eq[:,:3],b_ub=-eq[:,3],bounds=list(zip(lo,hi)),method='highs')
  if r.success:hits.append({'solid':c['name'],'actual_intersection_point_m':r.x.tolist()})
 voids.append({'name':name,'min_source_m':lo,'max_source_m':hi,'method':'Full convex half-space intersection with entire axis-aligned box using linear-program feasibility','hits':hits,'passed':not hits})
controls=[]
for name,p in [('seat',[.9,-.25,.45]),('bracket',[.9,-.1,.2]),('upper_floor',[1.1,.5,.35]),('closed_end',[1.74,.5,.6]),('front_wall',[1.1,.10,.6]),('rear_wall',[1.1,.94,.6])]:
 occupants=[c['name']for c in solids if np.all(np.array(c['planes'])[:,:3]@p+np.array(c['planes'])[:,3]<=1e-7)];controls.append({'name':name,'source_m':p,'occupants':occupants,'passed':bool(occupants)})
result={'collision_sha256':hashlib.sha256((ROOT/'collision_proposals.json').read_bytes()).hexdigest(),'compound_count':len(solids),'finite_void_checks':voids,'positive_solid_controls':controls,'passed':all(c['passed']for c in voids+controls)}
(ROOT/'qa/collision_volume_checks.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'qa/collision_hulls_for_source_check.json').write_text(json.dumps(solids,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
