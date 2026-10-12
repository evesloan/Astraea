from pathlib import Path
import json,hashlib
import numpy as np
from shapely.geometry import box,LineString,Polygon
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'));context=json.load(open(W/'SYNTHESIS_ACTUAL_CONTEXT.json'));scope=json.load(open(W/'SCOPE_AND_BOUNDARIES.json'))
EPS=.001;target=box(-95.111,-30.111,-55.889,30.111);bay=Polygon(scope['protected_original_bay_keepout_xz']);route=LineString([(-60,0),(-44,0)]).buffer(.85);holds=[];checks=0;tested=0
def positive_triangle_box(triangle,bounds):
    centre=np.array([(bounds[i]+bounds[i+1])/2 for i in[0,2,4]]);half=np.array([(bounds[i+1]-bounds[i])/2 for i in[0,2,4]]);v=triangle-centre;edges=[v[1]-v[0],v[2]-v[1],v[0]-v[2]];axes=[*np.eye(3),np.cross(edges[0],edges[1])]
    axes.extend(np.cross(edge,axis)for edge in edges for axis in np.eye(3))
    for axis in axes:
        length=np.linalg.norm(axis)
        if length<1e-10:continue
        axis/=length;values=v@axis;r=half@np.abs(axis)
        if values.min()>=r-EPS or values.max()<=-r+EPS:return False
    return True
old=[]
for row in context['old_meshes']:
    t=np.array(row['triangles']);old.append((row['path'],t,t.min(axis=1),t.max(axis=1)))
for row in p['meshes']:
    a=row['world_aabb'];plan=box(a[0],a[4],a[1],a[5]);checks+=3
    assert target.covers(plan)and a[2]>=-1e-7 and a[3]<=5.450001,('Source containment/cap',row['name'],a)
    if a[2]<4.35:assert plan.intersection(bay).area<1e-8,('Original retained bay keepout',row['name'])
    if a[2]<2.2:assert plan.intersection(route).area<1e-8,('Original service approach',row['name'])
    lower=np.array([a[0],a[2],a[4]]);upper=np.array([a[1],a[3],a[5]])
    for path,triangles,lo,hi in old:
        mask=((lo<upper-EPS)&(hi>lower+EPS)).all(axis=1);indices=np.flatnonzero(mask);checks+=1
        for i in indices:
            tested+=1
            if positive_triangle_box(triangles[i],a):holds.append({'new_source':row['name'],'original_source':path,'old_triangle':int(i)})
assert not holds,holds[:20]
floor=json.load(open(W/'MISSING_ONLY_FLOOR_PROPOSAL.json'));pieces=[Polygon(r['rings'][0],r['rings'][1:])for r in floor['regions']];original=json.load(open(R/'Game/data/generated/structural_meshes.json'));kept=[Polygon(r['rings'][0],r['rings'][1:])for r in original['regions']if r['id']in floor['retained_floor_owners']]
for part in pieces:
    for old_part in kept:checks+=1;assert part.intersection(old_part).area<1e-8
report={'status':'PASS','new_source_meshes':len(p['meshes']),'actual_nearby_original_meshes':len(old),'actual_original_context_triangles':sum(len(r[1])for r in old),'containment_protected_bay_route_and_original_context_checks':checks,'broadphase_candidates_exact_triangle_AABB_SAT':tested,'positive_original_contact_holds':holds,'tolerance_m':EPS,'missing_only_floor_proposal_m2':floor['proposed_missing_floor_area_m2'],'original_floor_positive_area_overlap_m2':0,'current_shared_floor_or_primary_engineering_acceptance':False}
(W/'SOURCE_CONTEXT_SCREEN001.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
