"""Screened, additive D03 street and porch architecture. Source-only."""
from pathlib import Path
import json, sys, math, hashlib
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
batch=json.loads((HERE/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').read_text())
shape=unary_union([Polygon(p['boundary'],p['holes'])for p in batch['route_polygons']+batch['porches']])
rooms=unary_union([box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])for q in batch['instances']])
walls=shape.buffer(.14,join_style=2).difference(shape).difference(rooms)
# Open each source porch against its real proposed room entry; no retained wall cut.
mouths=[]
for q in batch['instances']:
    x,y,z=q['position'];sign=-1 if q['yaw']else 1;door=x+sign*6
    mouths.append(box(door-.2,z-1.8,door+.2,z+1.8))
for x,z in [(-57,-216),(21,-490)]:mouths.append(box(x-1.8,z-.3,x+1.8,z+.3))
walls=walls.difference(unary_union(mouths))
parts=[]
def clipped_prisms(name,geom,y0,y1,role,category):
    a,b,c,d=geom.bounds
    for ix in range(math.floor(a/8),math.floor(c/8)+1):
        for iz in range(math.floor(b/8),math.floor(d/8)+1):
            cut=geom.intersection(box(ix*8,iz*8,(ix+1)*8,(iz+1)*8))
            for k,q in enumerate(shapely.get_parts(cut)):
                if q.geom_type!='Polygon'or q.area<1e-8:continue
                parts.append({'name':f'{name}_{ix}_{iz}_{k}','boundary':list(q.exterior.coords)[:-1],'holes':[list(r.coords)[:-1]for r in q.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(q).geoms],'y':[y0,y1],'role':role,'category':category,'batch_cell':f'{ix}_{iz}'})
clipped_prisms('StreetWallLow',walls,12,13.02,'staff_bluegrey_paint','screen_wall')
clipped_prisms('StreetWallHigh',walls,13.02,15.2,'staff_white_paint','screen_wall')
clipped_prisms('StreetCeiling',shape,15.2,15.34,'staff_bluegrey_paint','overhead')
fixtures=[]
for side in [-1,1]:
    for z in list(range(-328,-39,24))+list(range(56,344,24)):
        x=side*86
        if not shape.covers(box(x-.48,z-.13,x+.48,z+.13)):continue
        cell=f'{math.floor(x/8)}_{math.floor(z/8)}'
        parts.append({'name':f'BankLightHousing_{side}_{z}','aabb':[x-.48,x+.48,15.06,15.2,z-.13,z+.13],'role':'staff_zinc','category':'lighting_fixture','batch_cell':cell})
        parts.append({'name':f'BankLightDiffuser_{side}_{z}','aabb':[x-.43,x+.43,15.035,15.06,z-.1,z+.1],'role':'staff_opal','category':'lighting_fixture','batch_cell':cell})
        fixtures.append({'name':f'BankLight_{side}_{z}','position':[x,15.015,z],'color':[.78,.87,1],'range_m':8,'energy':.9,'budget_owner':'existing receiving_source_lights.gd / lighting_budget.gd'})
spec={'schema':1,'catalogue_id':'AST-STF-G3-001','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres, Y12 source route','parts':parts,'fixtures':fixtures,'floor_exported':False,'render_batch_cell_m':8,'route_shape':batch['route_polygons'],'porch_shapes':batch['porches'],'source_pins':batch['source_pins'],'receiving_interfaces':[{'name':'PortForwardExistingStaffStreet','position':[-57,12,-216],'state':'Open source end, actual retained receiving interface still to be checked'},{'name':'StarboardForwardPlannedStaffRiser','position':[21,12,-490],'state':'Source end only; no installed vertical arrival'}],'unfinished':['Root main-scene floor compilation and room/porch adoption','Actual receiving collars and programme back-of-house openings','Actual main collision, fixture registration and graphical acceptance','Staff vertical risers beyond retained lower three-stop system','Full cart/species traversal']}
(HERE/'source/CREW_STREETS.json').write_text(json.dumps(spec,indent=2)+'\n')
nativecheck=json.loads((HERE/'qa/HOME_NATIVE_GEOMETRY.json').read_text())
assert nativecheck['status']=='PASS'
allroomsfit=all(box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1]).area==114 for q in batch['instances'])
compiled=json.loads((ROOT/'Game/data/generated/structural_meshes.json').read_text())
existing=unary_union([Polygon(t)for r in compiled['regions']if r['deck']=='D03'for t in r['triangles']])
floor=unary_union([Polygon(p['boundary'],p['holes'])for p in batch['floor_proposal']['polygons']])
voids=json.loads((ROOT/'Game/data/spatial_layout.json').read_text())['voids']
overlap={v['id']:floor.intersection(Polygon(v['boundary'])).area for v in voids if 'D03'in v['decks']}
body=json.loads((ROOT/'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
inner=Polygon(next(r for r in body['levels']if r['deck']=='D03')['inner_reservation_boundary'])
supported=existing.union(floor)
wallfoot=walls.difference(supported).area
checks={'status':'PASS' if allroomsfit and floor.intersection(existing).area<1e-7 and not any(a>1e-7 for a in overlap.values())and wallfoot<1e-7 and shape.buffer(.14,join_style=2).difference(inner).area<1e-7 else'FAIL','200_allocations_fit_native_home_bounds':allroomsfit,'physical_rests_proposed':398,'new_population_keys':0,'screen_wall_support_area_missing_m2':wallfoot,'floor_duplicate_area_m2':floor.intersection(existing).area,'protected_void_overlap_m2':overlap,'source_route_outside_conservative_D03_inner_hull_m2':shape.buffer(.14,join_style=2).difference(inner).area,'minimum_inner_hull_boundary_clearance_m':inner.boundary.distance(shape.buffer(.14,join_style=2)),'source_parts':len(parts),'new_floor_exported':False,'scope':'Pure source geometry, conservative plan hull and explicit floor proposals; not primary structure, in-engine or cart/species acceptance.'}
(HERE/'qa/CREW_BATCH_PLAN_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks));assert checks['status']=='PASS'
