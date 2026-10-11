from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
from glb_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2]
F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
T=R/'Game/source_derivatives/group4_completion_20261011';T.mkdir(parents=True,exist_ok=True)
P=R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json';P.parent.mkdir(parents=True,exist_ok=True)
plan=json.loads((W/'RECEIVING_PLAN.json').read_text()); sources=[]
def add(p,role):
    assert p.exists(),p
    shutil.copy2(p,T/p.name)
    policies={name:extras.get('collision_policy','static_trimesh_candidate') for name,t,extras in triangles(p)}
    sources.append(dict(file=p.name,role=role,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),policies=policies,original=str(p.relative_to(R))))
for q in plan['stations']:add(F/q['station_source']/q['asset'],'station_'+q['label'])
for rel,role in [
    ('port_successor_002/AST-TRM-G4-016_continuous_guideway.glb','guideway'),
    ('receiving_module_003/AST-TRM-G4-017_receiving_module.glb','guideway_receivers'),
    ('central_stair_receiving_004/AST-TRM-G4-018_central_stair_receiving.glb','central_stair_receivers'),
    ('north_receiving_006/AST-TRM-G4-021_north_missing_only_receiving.glb','north_floor_receivers'),
    ('north_access_protection_007/AST-TRM-G4-022_north_access_protection.glb','north_access_guards'),
    ('boarding_north_005/AST-TRM-G4-019_boarding_bridge.glb','bridge_component'),
    ('port_successor_002/AST-TRM-G4-011_cart_tram_component.glb','vehicle_component')]:add(F/rel,role)
add(W/'AST-TRM-G4-023_station_receiving_r002.glb','station_annex_receivers')
# Candidate-only exact retained D09 floor triangles after the four proposed pit subtractions.
# This is an isolated local scene fixture, never a replacement compiler or shared production floor.
test_floor=[]
for source in ['structural_meshes.json','received_structural_meshes.json']:
    data=json.loads((R/'Game/data/generated'/source).read_text())
    for q in data['regions']:
        if q['floor_y']!=52.5:continue
        keep=[]
        for t in q['triangles']:
            poly=Polygon(t)
            for cut in plan['required_shared_floor_cuts']:
                if q['id'] in cut['owners']:poly=poly.difference(box(*cut['bounds_xz']))
            polys=list(poly.geoms) if hasattr(poly,'geoms') else [poly]
            for p in polys:
                if p.is_empty:continue
                for tr in triangulate(p):
                    if p.covers(tr.representative_point()):
                        assert tr.difference(p).area<1e-7
                        keep.append([list(v) for v in list(tr.exterior.coords)[:3]])
        test_floor.append(dict(id=q['id'],floor_y=q['floor_y'],thickness=q['thickness'],triangles=keep))
(T/'CANDIDATE_FLOOR_FIXTURE.json').write_text(json.dumps(test_floor,separators=(',',':'))+'\n')
lights=[]
for source in sources:
    if not source['role'].startswith('station_'):continue
    for name,t,extras in triangles(T/source['file']):
        if 'Opal' not in name:continue
        lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));pos=(lo+hi)/2
        # Exit beyond the actual lens front; source geometry still owns the fixture.
        toward=-1 if source['role']=='station_AFT_MIDSHIP' else 1
        if source['role']=='station_annex_receivers':toward=-1 if name.startswith(('FORWARD','AFT')) else 1
        pos[0]=(lo[0]-.01) if toward<0 else (hi[0]+.01)
        lights.append(dict(name=name,xyz=pos.tolist(),source=source['file'],range=8,energy=.55,color=[1,.89,.72]))
candidate=dict(schema='astraea.group4.inactive.integration.v1',active=False,whole_group_complete=False,
    stations=plan['stations'],models=sources,lights=lights,shared_floor_cuts=plan['required_shared_floor_cuts'],
    new_floor_area_m2=plan['new_floor_area_m2'],retained_north_floor_area_m2=356.38,
    protected_polyline_xz=plan['protected_polyline_xz'],baseline=plan['baseline'],
    operating_scope='existing five two-stop commons_lift bindings; physical bridge pose adapter; stationary vehicle preview only',
    activation_requires=['shared floor compiler cuts','explicit north physical docking adoption','actual-main source/collision/route audit'],
    limits=['No tram travel, new cart, stock, guest transport, capacity, structural or whole-species acceptance','Not active in main; no shared registry or ship root edits'])
P.write_text(json.dumps(candidate,indent=2)+'\n')
print('RUNTIME_PREPARED',len(sources),'pinned models;',len(lights),'source-positioned lights;',len(test_floor),'candidate floor owners')
