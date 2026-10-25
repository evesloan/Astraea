"""Source geometry gate against retained structural-floor triangles and route air."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=Path(__file__).resolve().parents[4]
plan=json.loads((ROOT/'PLAN.json').read_text(encoding='utf-8'))
for path,sha in plan['source_pins'].items():
    assert hashlib.sha256((REPO/path).read_bytes()).hexdigest()==sha,path
floors=json.loads((REPO/'Game/data/generated/structural_meshes.json').read_text(encoding='utf-8'))
triangles={r['id']:r['triangles'] for r in floors['regions'] if r['id'] in ['D18_fore_route','D18_aft_route']}


def contains(point,triangle):
    signs=[(triangle[(i+1)%3][0]-triangle[i][0])*(point[1]-triangle[i][1])-
           (triangle[(i+1)%3][1]-triangle[i][1])*(point[0]-triangle[i][0]) for i in range(3)]
    return min(signs)>=-1e-7 or max(signs)<=1e-7


def obstructs(part):
    v=part['vertices'];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
    return lo[0]<4 and hi[0]>-4 and lo[1]<110.5 and hi[1]>106.50001


contact_samples=0
for part in plan['parts']:
    assert not obstructs(part),part['name']+' enters full protected route'
    assert all(-541<=v[2]<=541 and v[1]<=114.5 for v in part['vertices'])
    if part['name'].endswith('_EdgeSole'):
        z0=min(v[2] for v in part['vertices']);z1=max(v[2] for v in part['vertices'])
        owner='D18_fore_route' if z0<0 else 'D18_aft_route'
        x=-3.9 if '_Port_' in part['name'] else 3.9
        for fraction in [0,.25,.5,.75,1]:
            z=z0+(z1-z0)*fraction
            assert any(contains((x,z),t) for t in triangles[owner]),(part['name'],x,z,'unsupported sole')
            contact_samples+=1
    v=part['vertices'];assert len(v)==8 and len(part['faces'])==6
    assert all(v[i+4][1]>v[i][1] for i in range(4)),part['name']+' zero thickness'
# Demonstrate that the route guard rejects a real low roof and an inward pier.
for bad in [dict(vertices=[[-1,110.4,200],[1,110.6,201]]),
            dict(vertices=[[3.8,106.5,200],[4.2,111,201]])]:
    assert obstructs(bad),'negative route guard did not reject obstruction'
assert not plan['new_room_ids'] and plan['capacity_delta']==0
report=dict(status='SOURCE_GEOMETRY_PASS',parts=len(plan['parts']),sole_contact_samples=contact_samples,
            retained_floor_owners=list(triangles),route_width_m=8,route_air_m=4,
            negative_guards=2,source_sha256=hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),
            limitations=['AABB route clearance is conservative; installed-world queries still required',
                         'Sampled sole/floor contacts are geometry evidence, not capacity engineering',
                         'Roof receiving joins, collision, native reopen and graphical inspection pending'])
(ROOT/'SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
