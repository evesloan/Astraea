"""Exact reserved starboard forward staff riser, source-only D01–D17."""
from pathlib import Path
import json,math,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2];GAME=ROOT/'Game'
plan=json.loads((GAME/'data/whole_ship_layout.json').read_text())
r=next(r for r in plan['staff_riser_reservations']if r['id']=='starboard_service_riser_1')
assert r['center_xz']==[25,-490]and r['shaft_x']==[22.8,27.2]and r['shaft_z']==[-492.2,-487.8]
contract=json.loads((GAME/'data/design_contract.json').read_text())
stops=[d for d in contract['deck_datums']if d['deck_id']!='D18']
assert len(stops)==17
parts=[];fixtures=[]
def cube(n,b,role='staff_bluegrey_paint',category='shaft_architecture'):
    parts.append({'name':n,'aabb':b,'role':role,'category':category,'batch_cell':f'y{math.floor(b[2]/8)}'})
# Mirror the retained forward port enclosure and preserve its real cabin/sill gaps.
# New source never touches the existing port lift.
for i in range(14):
    y0=i*8;y1=min((i+1)*8,105.2)
    if y1<=y0:continue
    cube(f'ShaftRear_{i}',[26.96,27.12,y0,y1,-492.2,-487.8])
    cube(f'ShaftSideFore_{i}',[22.84,26.96,y0,y1,-492.2,-492.04])
    cube(f'ShaftSideAft_{i}',[22.84,26.96,y0,y1,-487.96,-487.8])
front=box(22.84,-492.2,23.0,-487.8)
# Front wall panels retain a 3.8 m wide structural opening at each actual stop.
for i,d in enumerate(stops):
    y=float(d['floor_elevation_m']);next_y=float(stops[i+1]['floor_elevation_m']) if i+1<len(stops) else 105.2
    cube(f'ShaftFrontFore_D{i+1:02d}',[22.84,23.0,y,next_y,-492.2,-491.9])
    cube(f'ShaftFrontAft_D{i+1:02d}',[22.84,23.0,y,next_y,-488.1,-487.8])
    cube(f'ShaftFrontHeader_D{i+1:02d}',[22.84,23.0,y+2.85,next_y,-491.9,-488.1])
    # Fixed threshold overlaps the proposed lobby but clears the moving floor.
    cube(f'LandingSill_D{i+1:02d}',[23.02,23.18,y-.06,y,-491.85,-488.15],'staff_zinc','landing_threshold')
    # Economical opaque lobby, west opening for the same-side screened district link.
    cube(f'LobbyForeLeft_D{i+1:02d}',[18.8,19.2,y,y+3.2,-496,-495.86],'staff_white_paint','lobby_wall')
    cube(f'LobbyForeRight_D{i+1:02d}',[22.8,23.02,y,y+3.2,-496,-495.86],'staff_white_paint','lobby_wall')
    cube(f'LobbyForeLintel_D{i+1:02d}',[19.2,22.8,y+2.8,y+3.2,-496,-495.86],'staff_white_paint','lobby_wall')
    cube(f'LobbyAft_D{i+1:02d}',[18.8,23.02,y,y+3.2,-484.14,-484],'staff_white_paint','lobby_wall')
    cube(f'LobbyWestScreen_D{i+1:02d}',[18.8,18.94,y,y+3.2,-495.86,-484.14],'staff_white_paint','lobby_wall')
    cube(f'LobbyRoof_D{i+1:02d}',[18.8,23.18,y+3.2,y+3.34,-496,-484],'staff_bluegrey_paint','overhead')
    cube(f'LobbyLightHousing_D{i+1:02d}',[20.5,21.5,y+3.04,y+3.2,-490.16,-489.84],'staff_zinc','lighting_fixture')
    cube(f'LobbyLightDiffuser_D{i+1:02d}',[20.55,21.45,y+3.015,y+3.04,-490.12,-489.88],'staff_opal','lighting_fixture')
    cube(f'CallControlBacking_D{i+1:02d}',[22.66,22.84,y+1.08,y+1.45,-492.06,-491.96],'staff_zinc','control_fixture')
    fixtures.append({'name':f'LobbyLight_D{i+1:02d}','position':[21,y+2.995,-490],'color':[.78,.88,1],'range_m':7,'energy':.9,'budget_owner':'existing receiving_source_lights.gd / lighting_budget.gd'})
cube('NewRiserPitPan',[23.2,26.8,-.24,-.2,-492,-488],'staff_zinc','pit_pan')
cube('NewRiserTopCap',[22.84,27.12,105.2,105.34,-492.2,-487.8],'staff_bluegrey_paint','overhead')
compiled=json.loads((GAME/'data/generated/structural_meshes.json').read_text())
floor_rows=[];checks=[]
body=json.loads((GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
for i,d in enumerate(stops):
    deck=d['deck_id'];y=d['floor_elevation_m']
    old=unary_union([Polygon(t)for q in compiled['regions']if q['deck']==deck for t in q['triangles']])
    requested=box(18.8,-496,23.18,-484);missing=requested.difference(old)
    shaft=box(23.18,-492.2,27.2,-487.8)
    cuts=old.intersection(shaft)
    # Roof clears the fixed sill and all moving cabin/gate bounds.
    inner=Polygon(next(q for q in body['levels']if q['deck']==deck)['inner_reservation_boundary'])
    floor_rows.append({'deck':deck,'floor_y':y,'missing_floor_polygons':[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(missing)if p.geom_type=='Polygon'and p.area>1e-7],'missing_area_m2':missing.area,'existing_floor_overlap_retained_m2':requested.intersection(old).area,'existing_floor_cut_required_m2':cuts.area,'shaft_exclusion':list(shaft.exterior.coords)[:-1],'gate_center':[23.08,y,-490],'district_link_center':[21,y,-496],'state':'Source-only receiving; no working stop installed'})
    checks.append({'deck':deck,'reserved_lobby_inside_conservative_hull':inner.covers(box(18.8,-496,27.2,-484)),'no_new_floor_in_shaft':missing.intersection(shaft).area<1e-7,'missing_floor_duplicate_area_m2':missing.intersection(old).area,'next_canonical_datum_roof_clearance_m':(float(contract['deck_datums'][i+1]['floor_elevation_m'])-.24)-(float(y)+3.34)})
pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [GAME/'data/whole_ship_layout.json',GAME/'data/architecture/LOWER_STAFF_NETWORK.json',GAME/'scripts/commons_lift.gd',GAME/'data/generated/structural_meshes.json']}
spec={'schema':1,'catalogue_id':'AST-STF-G3-002','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; mirror of retained lower staff cabin/shaft interface','parts':parts,'fixtures':fixtures,'source_pins':pins,'controller_binding_proposal':{'controller':'Existing commons_lift.gd only','center':[25,0,-490],'yaw':0,'stop_y':[float(d['floor_elevation_m'])for d in stops],'cabin_file':'AST-CIR-003_three_stop.glb','gate_file':'AST-DOR-003.glb','moving_cabin_floor_x':[23.2,26.8],'moving_cabin_floor_z':[-492,-488],'moving_gate_x':23.32,'landing_gate_x':23.08,'gate_width_m':2.4,'gate_height_m':2.65,'existing_dynamic_source_reused':True,'controller_or_dynamic_assets_created':False},'floor_proposals':floor_rows,'roof_limit_y':105.34,'D18_connection_created':False,'existing_port_lift_modified':False,'population_or_registered_berths_added':0,'unfinished':['Root floor/aperture adoption and existing-controller stop binding','All17 same-side screened district route receivers','Actual main cabin sweep, gate, boarding and contact evidence','Roof/crown interface and D18 connection are separately held','Body/cart/species and final in-engine visual acceptance']}
(HERE/'source/STARBOARD_FORWARD_STAFF_RISER.json').write_text(json.dumps(spec,indent=2)+'\n')
report={'status':'PASS'if all(q['reserved_lobby_inside_conservative_hull']and q['no_new_floor_in_shaft']and q['missing_floor_duplicate_area_m2']<1e-7 and q['next_canonical_datum_roof_clearance_m']>0 for q in checks)else'FAIL','checks':checks,'parts':len(parts),'source_floor_proposals':17,'D18_connection_created':False,'existing_port_lift_modified':False,'scope':'Conservative plan and source-datum construction screen, not actual moving lift or structure acceptance.'}
(HERE/'qa/STAFF_RISER_PLAN_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['status']=='PASS'
