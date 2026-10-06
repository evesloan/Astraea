"""Pure-plan checks only. No Blender, Godot, imports or source/render acceptance."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/geometry_plan.json').read_text());K=json.loads((R/'source/section_contract.json').read_text())
checks=[]
def check(n,ok,detail=None):
    checks.append(dict(check=n,pass_check=bool(ok),detail=detail));assert ok,(n,detail)
def bounds(p):
    v=p['vertices_xyz'];return [min(q[i] for q in v) for i in range(3)]+[max(q[i] for q in v) for i in range(3)]
def overlap(b,r):return all(min(b[i+3],r[i+3])-max(b[i],r[i])>1e-6 for i in range(3))
export=[p for p in D['parts'] if p['export']]
check('all names unique',len({p['name'] for p in D['parts']})==len(D['parts']))
check('no preview floor/cap export',not any('PREVIEW' in p['name'] for p in export))
check('no walkable source slabs',not any('floor' in p['name'].lower() for p in export))
check('contained within programme and protected vertical storey',all(b[0]>=8-1e-6 and b[3]<=54+1e-6 and b[1]>=6-1e-6 and b[4]<=11.52+1e-6 and b[2]>=-466-1e-6 and b[5]<=-398+1e-6 for b in map(bounds,export)))
# Boxes represent protected true-clear prisms. Door headers above them do not count.
prisms={'north_cart_strip':[20,6,-454.6,53.7,8.7,-451],'south_cart_strip':[20,6,-413,53.7,8.7,-409.4],'east_continuous_cart_strip':[48.3,6,-465.7,53.7,9.6,-398.3],'control_turn':[28.2,6,-460.8,31.8,8.7,-457.2],'workbay_turn':[28.2,6,-406.8,31.8,8.7,-403.2],'control_operating_face':[21.9,6,-462.4,30.1,8.4,-460.9]}
for name,r in prisms.items():
    hits=[p['name'] for p in export if overlap(bounds(p),r)]
    check(name+' true clear geometry prism',not hits,hits)
for p in export:
    check('finite mesh '+p['name'],all(math.isfinite(c) for v in p['vertices_xyz'] for c in v))
    check('valid face indices '+p['name'],all(len(f)>=3 and len(set(f))==len(f) and all(0<=i<len(p['vertices_xyz']) for i in f) for f in p['faces']))
check('fixture source housings and supports exist',all(any(p['name']==m['housing'] for p in export) and any(p['name']==m['support'] for p in export) for m in D['markers']))
check('nine supported fixture markers',len(D['markers'])==9)
for m in D['markers']:
    if m['name'].startswith('DATUM_plant_inspection'):
        stem=next(p for p in export if p['name']==m['ceiling_stem']);cap=next(p for p in export if p['name']=='containment_cap');sb=bounds(stem);cb=bounds(cap);check(m['name']+' exact stem-cap support contact',abs(sb[4]-cb[1])<1e-6 and m['support_owner']=='containment_cap')
check('all door openings minimum width and height',all(d['range'][1]-d['range'][0]>=2.4-1e-6 and d['clear_height']>=2.7 for d in K['doors']))
check('segmented module door margins',K['clearance']['loaded_height']<=2.7 and max(K['clearance']['module_xyz'][0],K['clearance']['module_xyz'][2])<=2.4)
report=dict(stage='pure geometry plan check; not source/export/runtime traversal',pass_check=True,parts=len(D['parts']),export_parts=len(export),preview_parts=len(D['parts'])-len(export),fixtures=len(D['markers']),checks=checks,inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'source/generate_section.py',R/'source/geometry_plan.json',R/'source/section_contract.json']},not_tested=['triangulation/manifold in Blender','dynamic doors/pockets','exact capsule or loaded-cart motion','fixture visual acceptance','physical machine operation','hull per-height or external routes'])
(R/'qa/pure_geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['stage','pass_check','parts','export_parts','preview_parts','fixtures']}))
