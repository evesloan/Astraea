"""Port upper shaft successor and screened Tidal edge; no house interior edits."""
from pathlib import Path
import json,math,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import box,Polygon,LineString,shape
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2];GAME=ROOT/'Game'
retained=json.loads((GAME/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text())['staff']
assert retained['existing_persistent_lift_id']=='forward_staff_lift_001'
assert retained['proposed_all_stops_y']==[0,6,12,46.2,52.5]
stops=[('D13',84),('D14',88.5),('D15',93),('D16',97.5),('D17',102)]
parts=[];fixtures=[]
def cube(n,b,role='staff_bluegrey_paint',category='upper_shaft'):
    parts.append({'name':n,'aabb':b,'role':role,'category':category,'batch_cell':f'y{math.floor(b[2]/8)}'})
start=55.6
for i in range(7):
    y0=start if i==0 else 56+i*8;y1=min(64+i*8,105.2)
    if y1<=y0:continue
    cube(f'PortUpperRear_{i}',[-27.12,-26.96,y0,y1,-492.2,-487.8])
    cube(f'PortUpperFore_{i}',[-26.96,-22.84,y0,y1,-492.2,-492.04])
    cube(f'PortUpperAft_{i}',[-26.96,-22.84,y0,y1,-487.96,-487.8])
cube('PortUpperBlankFront_D10_D12',[-23,-22.84,start,84,-492.2,-487.8])
for i,(deck,y)in enumerate(stops):
    next_y=stops[i+1][1] if i+1<len(stops) else 105.2
    cube('PortFrontFore_'+deck,[-23,-22.84,y,next_y,-492.2,-491.9])
    cube('PortFrontAft_'+deck,[-23,-22.84,y,next_y,-488.1,-487.8])
    cube('PortFrontHeader_'+deck,[-23,-22.84,y+2.85,next_y,-491.9,-488.1])
    cube('PortSill_'+deck,[-23.18,-23.02,y-.06,y,-491.85,-488.15],'staff_zinc','landing_threshold')
cube('PortUpperTopCap',[-27.12,-22.84,105.2,105.34,-492.2,-487.8],'staff_bluegrey_paint','overhead')
route=unary_union([LineString([(-21,-490),(-21,-500),(-61,-500),(-61,-484)]).buffer(1.8,cap_style=2,join_style=2),box(-23.18,-496,-18.8,-484)])
walls=route.buffer(.14,join_style=2).difference(route)
# Five true shaft mouths and two separated root-owned house receiver boundaries.
mouths=unary_union([box(-23.4,-491.9,-22.5,-488.1),box(-63.1,-494.8,-62.6,-491.2),box(-63.1,-488.8,-62.6,-485.2)])
walls=walls.difference(mouths)
walls=walls.difference(box(-27.2,-492.2,-23.18,-487.8))
def prisms(prefix,shape,y0,y1,role,category,deck):
    a,b,c,d=shape.bounds
    for ix in range(math.floor(a/8),math.floor(c/8)+1):
        for iz in range(math.floor(b/8),math.floor(d/8)+1):
            for k,p in enumerate(shapely.get_parts(shape.intersection(box(ix*8,iz*8,(ix+1)*8,(iz+1)*8)))):
                if p.geom_type!='Polygon'or p.area<1e-8:continue
                parts.append({'name':f'{prefix}_{deck}_{ix}_{iz}_{k}','boundary':list(p.exterior.coords)[:-1],'holes':[list(r.coords)[:-1]for r in p.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],'y':[y0,y1],'role':role,'category':category,'batch_cell':f'{deck}_{ix}_{iz}'})
compiled=json.loads((GAME/'data/generated/structural_meshes.json').read_text())
guest=json.loads((GAME/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
body=json.loads((GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
tidal=json.loads((GAME/'data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json').read_text())
private_verges=[shape(r['geometry']) for r in tidal['floor_regions'] if 'PrivateWindowVerge' in r['name']]
assert private_verges,'Actual retained private window verge must be inspected, not inferred from guest envelopes'
verge=unary_union(private_verges)
floors=[];checks=[];interfaces=[];receiver_supports=[];floor_region_checks=[]
additional_streets=[]
for family in ['tidal_aquatic_singles_20261009','tidal_aquatic_double_20261009']:
    p=ROOT/'BlenderCatalogue/assets'/family/'STREET_EXTENSION.json'
    q=json.loads(p.read_text());additional_streets.append((str(p.relative_to(ROOT)),q['floor_y'],box(*q['floor_xz_bounds'])))
for deck,y in stops:
    prisms('TidalStaffWallLow',walls,y,y+1.02,'staff_bluegrey_paint','screen_wall',deck)
    prisms('TidalStaffWallHigh',walls,y+1.02,y+3.2,'staff_white_paint','screen_wall',deck)
    prisms('TidalStaffRoof',route,y+3.2,y+3.34,'staff_bluegrey_paint','overhead',deck)
    for role,z in [('clean_linen_supply',-493),('sealed_soiled_waste',-487)]:
        cube('TidalReceiverLintel_'+deck+'_'+role,[-62.94,-62.8,y+2.8,y+3.2,z-1.8,z+1.8],'staff_white_paint','receiver_header')
        interfaces.append({'deck':deck,'floor_y':y,'role':role,'group3_end_plane_x':-62.8,'center_z':z,'clear_opening_xz':[[-62.8,z-1.8],[-62.8,z+1.8]],'width_m':3.6,'height_m':2.8,'root_owned_receiver_edge':'Actual Tidal house edge near X-63; root owns collar, local stock/returns and all guest-space work','installed':False})
    for i,(x,z)in enumerate([(-21,-490),(-21,-498),(-33,-500),(-45,-500),(-58,-500),(-61,-493),(-61,-487)]):
        cube(f'TidalStaffLightHousing_{deck}_{i}',[x-.4,x+.4,y+3.04,y+3.2,z-.13,z+.13],'staff_zinc','lighting_fixture')
        cube(f'TidalStaffLightDiffuser_{deck}_{i}',[x-.35,x+.35,y+3.015,y+3.04,z-.1,z+.1],'staff_opal','lighting_fixture')
        fixtures.append({'name':f'TidalStaffLight_{deck}_{i}','position':[x,y+2.995,z],'color':[.78,.88,1],'range_m':7.5,'energy':.9,'budget_owner':'existing receiving_source_lights.gd / lighting_budget.gd'})
    old=unary_union([Polygon(t)for p in compiled['regions']if p['deck']==deck for t in p['triangles']])
    shaft=box(-27.2,-492.2,-23.18,-487.8)
    requested=route.buffer(.14,join_style=2).difference(shaft);missing=requested.difference(old)
    floors.append({'deck':deck,'floor_y':y,'thickness':.24,'missing_only_area_m2':missing.area,'polygons':[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(missing)if p.geom_type=='Polygon'and p.area>1e-7],'existing_floor_cut_m2':old.intersection(shaft).area,'shaft_exclusion':list(shaft.exterior.coords)[:-1]})
    for r in tidal['floor_regions']:
        floor_region_checks.append({'deck':deck,'retained_region':r['name'],'retained_floor_y':r['floor_y'],'same_datum':abs(r['floor_y']-y)<1e-6,'same_datum_overlap_m2':requested.intersection(shape(r['geometry'])).area if abs(r['floor_y']-y)<1e-6 else 0.0})
    for name,fy,poly in additional_streets:
        floor_region_checks.append({'deck':deck,'retained_region':name,'retained_floor_y':fy,'same_datum':abs(fy-y)<1e-6,'same_datum_overlap_m2':requested.intersection(poly).area if abs(fy-y)<1e-6 else 0.0})
    for role,z in [('clean_linen_supply',-493),('sealed_soiled_waste',-487)]:
        # Parent owns exact collar/receiver geometry beyond the Group 3 end plane.
        collar=box(-63.3,z-1.8,-62.8,z+1.8)
        unsupported=collar.difference(old.union(missing))
        receiver_supports.append({'deck':deck,'floor_y':y,'role':role,'root_owned_full_width_collar_bounds_xz':list(collar.bounds),'proposed_external_floor_overlap_m2':collar.intersection(requested).area,'existing_compiled_floor_overlap_m2':collar.intersection(old).area,'root_owned_missing_support_area_m2':unsupported.area,'root_owned_missing_support_polygons':[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(unsupported)if p.geom_type=='Polygon'and p.area>1e-7],'local_commons_route_confirmed':False})
    guest_overlap=sum(requested.intersection(box(p['x'][0],p['z'][0],p['x'][1],p['z'][1])).area for p in guest if int(p['deck'])==int(deck[1:]))
    inner=Polygon(next(p for p in body['levels']if p['deck']==deck)['inner_reservation_boundary'])
    checks.append({'deck':deck,'guest_envelope_overlap_m2':guest_overlap,'actual_private_window_verge_overlap_m2':requested.intersection(verge).area,'root_house_allocation_overlap_m2':requested.intersection(Polygon(next(p for p in json.loads((GAME/'data/whole_ship_layout.json').read_text())['residential_court_reservations']if p['id']=='port_forward_residential_court')['boundary'])).area,'outside_conservative_hull_m2':requested.difference(inner).area,'floor_duplicate_area_m2':missing.intersection(old).area,'wall_foot_supported_m2':walls.difference(old.union(missing)).area})
pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [GAME/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',GAME/'scripts/lower_staff_network.gd',GAME/'assets/models/AST-STF-009_pool_market_home_equipment.glb',GAME/'data/whole_ship_layout.json',GAME/'data/reference/historical_guest_census.json',GAME/'data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json',GAME/'data/generated/structural_meshes.json']+[ROOT/name for name,fy,poly in additional_streets]}
spec={'schema':1,'catalogue_id':'AST-STF-G3-003','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; bounded port upper successor and outside-house service edge','parts':parts,'fixtures':fixtures,'source_pins':pins,'interfaces':interfaces,'floor_proposals':floors,'root_owned_receiver_support_proposals':receiver_supports,'actual_house_floor_region_checks':floor_region_checks,'retained_existing_stops_y':[0,6,12,46.2,52.5],'added_stop_y':[y for deck,y in stops],'controller_binding':'Preserve forward_staff_lift_001 and existing commons_lift.gd, cabin AST-CIR-003_five_stop.glb, retained stop IDs and wet Y46.2. Root binds the extra five stops.','required_retained_source_derivative':{'source_file':'AST-STF-009_pool_market_home_equipment.glb','remove_only_existing_cap_y':[55.6,55.74],'keep_all_other_source_geometry':True,'status':'Not modified by helper; root must author/verify the reversible source successor before runtime operation'},'D18_connection_created':False,'root_house_geometry_modified':False,'unfinished':['Root-owned retained cap derivative and actual continuous cabin sweep','Exact existing source-volume survey at outside-house receivers','Root floor and lift/door integration','Root local linen/supply/soiled-waste cupboards and cart parking','No simultaneous segregated-flow or full service operation is certified','Other residential houses and broader staff district links']}
(HERE/'source/TIDAL_STAFF_INTERFACE.json').write_text(json.dumps(spec,indent=2)+'\n')
report={'status':'PASS'if all(not any(v>1e-7 for k,v in q.items()if k!='deck')for q in checks)and all(q['same_datum_overlap_m2']<1e-7 for q in floor_region_checks)else'FAIL','checks':checks,'actual_house_floor_region_checks':floor_region_checks,'root_owned_receiver_support_proposals':receiver_supports,'source_parts':len(parts),'retained_five_stops_preserved':True,'root_house_geometry_modified':False,'previous_rejected_trunk':{'center_x':-57,'D14_guest_envelope_overlap_m2':38.16,'decision':'Rejected. Earlier X-61/Z-480 extension also rejected after actual private window verge discovery. Current front-only route ends Z-484, with receivers Z-493 and Z-487'},'scope':'Source construction, conservative hull, guest/court allocation, and actual authored house floor-region separation. Source roof/wall outlook, full-width native receiver survey, root-owned upper receiver supports and commons routes remain explicit integration gates.'}
(HERE/'qa/TIDAL_STAFF_PLAN_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['status']=='PASS'
