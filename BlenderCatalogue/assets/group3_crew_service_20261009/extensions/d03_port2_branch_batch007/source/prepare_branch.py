"""D03 port2 branch into the retained spine; no longitudinal street duplicate."""
from pathlib import Path
import copy, hashlib, json, math, struct, sys
sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import LineString, Polygon, Point, box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parents[1]
ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
GAME=ROOT/'Game';CAT=ROOT/'BlenderCatalogue';FIRST=CAT/'assets/group3_crew_service_20261009'
PORT=FIRST/'extensions/port2_clinical_batch006'
LOW=CAT/'assets/lower_staff_network'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PORT/'SHA256SUMS.txt')=='61b5aa26c6d5090e5bd1e3f1c058ad02ad11e9e96a89e96a748673694acdd1ab'
for line in (PORT/'SHA256SUMS.txt').read_text().splitlines():
    h,n=line.split('  ',1);assert sha(PORT/n)==h
catalogue=json.loads((CAT/'catalogue_manifest.json').read_text())
for aid in ['AST-STF-G3-007','AST-STF-G3-008']:
    assert not any(q['catalogue_id']==aid and q.get('family')!='group3_crew_service_20261009'for q in catalogue['assets'])
lower=next(q for q in catalogue['assets']if q['catalogue_id']=='AST-STF-009')
assert sha(CAT/lower['export'])==lower['export_sha256']
assert sha(CAT/lower['source'])==lower['source_sha256']
oldparts=json.loads((LOW/'source/geometry_parts.json').read_text())['boxes']
network=json.loads((GAME/'data/architecture/LOWER_STAFF_NETWORK.json').read_text())
deck=next(q for q in network['decks']if q['deck']==3)
spine=unary_union([Polygon(q)for q in deck['floor_union_polygons_xz']])
roles=['staff_bluegrey_paint','staff_white_paint','staff_rubber','staff_zinc']
selected=[q for q in oldparts if q['deck']==3 and math.floor((q['world_aabb'][0]+q['world_aabb'][1])/40)==-3 and math.floor((q['world_aabb'][4]+q['world_aabb'][5])/40)==-15 and q['role']in roles]
assert len(selected)==23
replacement={k:f'STF_CELL_D03_X-3_Z-15_ASTRAEA_{k}'for k in roles}
raw=(CAT/lower['export']).read_bytes();native=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert all(sum(q.get('name')==name for q in native['nodes'])==1 for name in replacement.values())
changed=[];patch=[]
for q in selected:
    a,b,lo,hi,c,d=q['world_aabb']
    affected=a>=-55.345-1e-7 and b<=-55.2+1e-7 and c<-291.2 and d>-294.8 and lo<14.8
    def add(name,aa,bb,low,high,cc,dd):
        if min(bb-aa,high-low,dd-cc)<=1e-8:return
        patch.append({'name':'Port2Patch_'+name,'aabb':[aa,bb,low,high,cc,dd],'role':q['role'],'category':'retained_spine_cell','batch_cell':'-3_-15','original_semantic_name':q['name']})
    if not affected:
        add(q['name'],a,b,lo,hi,c,d);continue
    changed.append(q['name'])
    add(q['name']+'_north_retained',a,b,lo,min(hi,14.8),c,min(d,-294.8))
    add(q['name']+'_south_retained',a,b,lo,min(hi,14.8),max(c,-291.2),d)
    if hi>14.8:add(q['name']+'_upper_retained',a,b,14.8,hi,c,d)
assert len(changed)==4 and len(patch)==27
predecessor={'catalogue_id':'AST-STF-009','geometry_parts_path':str((LOW/'source/geometry_parts.json').relative_to(ROOT)),'geometry_parts_sha256':sha(LOW/'source/geometry_parts.json'),'editable_blend_path':lower['source'],'editable_blend_sha256':lower['source_sha256'],'runtime_export_path':lower['export'],'runtime_export_sha256':lower['export_sha256'],'all_other_runtime_meshes_preserved':len([q for q in native['nodes']if 'mesh'in q])-4}
patchspec={'schema':1,'catalogue_id':'AST-STF-G3-008','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; exact four-cell-role D03 lower staff spine successor','parts':patch,'fixtures':[],'predecessor':predecessor,'material_contract':'retained_lower_staff_network','runtime_batch_name_by_role':replacement,'retained_runtime_node_extras':{'catalogue_id':'AST-STF-009','deck':3,'collision_contract':'concave_static_surface','cell_x':-3,'cell_z':-15},'native_mesh_batches_to_omit_only_during_root_adoption':list(replacement.values()),'original_semantic_parts_in_these_batches':[q['name']for q in selected],'original_semantic_parts_changed':changed,'opening_clear_xz_y':{'wall_and_trim_x':[-55.345,-55.2],'z':[-294.8,-291.2],'clear_y':[12,14.8],'lintel_top_y':15.2},'original_source_or_registered_identities_modified':False,'full_lower_staff_network_export':False,'automatic_runtime_adoption':False,'adoption_rule':'Root omits exactly four named original native wall/ceiling/trim/bumper cell-role meshes and substitutes these four compact successor meshes. The twenty-three original semantic components are retained except four bounded mouth changes. All other cells, lights, doors, stops and save identities stay unchanged.'}
(HERE/'source/D03_SPINE_RECEIVER_PATCH.json').write_text(json.dumps(patchspec,indent=2)+'\n')

points=[[-21,-289],[-21,-293],[-57,-293]]
clear=LineString(points).buffer(1.8,cap_style=2,join_style=2)
requested=clear.buffer(.14,join_style=2)
wall=requested.difference(clear).difference(spine)
# The start cap extends toward the lobby (positive Z), not only into the
# branch. Clear both sides of the exact receiver plane while retaining jambs.
wall=wall.difference(box(-22.8,-289.3,-19.2,-288.7))
oldroof=unary_union([box(q['world_aabb'][0],q['world_aabb'][4],q['world_aabb'][1],q['world_aabb'][5])for q in oldparts if q['deck']==3 and q['name'].startswith('STF_D03_Ceiling_')])
roof=clear.difference(oldroof)
parts=[]
def rows(shape):
    return [{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(shape)if p.geom_type=='Polygon'and p.area>1e-8]
def prism(name,p,y,role,category,cell):
    return {'name':name,'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],'y':y,'role':role,'category':category,'batch_cell':cell}
def pieces(name,shape,y,role,category):
    a,b,c,d=shape.bounds
    for ix in range(math.floor(a/12),math.floor(c/12)+1):
        for iz in range(math.floor(b/12),math.floor(d/12)+1):
            for k,p in enumerate(shapely.get_parts(shape.intersection(box(ix*12,iz*12,(ix+1)*12,(iz+1)*12)))):
                if p.geom_type=='Polygon'and p.area>1e-8:parts.append(prism(f'{name}_{ix}_{iz}_{k}',p,y,role,category,f'{ix}_{iz}'))
def cube(name,bounds,role,category):
    parts.append({'name':name,'aabb':bounds,'role':role,'category':category,'batch_cell':'receiver'})
pieces('D03Port2BranchWallLow',wall,[12,13.03],'staff_bluegrey_paint','screen_wall')
pieces('D03Port2BranchWallHigh',wall,[13.03,15.2],'staff_white_paint','screen_wall')
pieces('D03Port2BranchRoof',roof,[15.2,15.34],'staff_bluegrey_paint','overhead')
cube('D03Port2LobbyReceiverStep',[-22.8,-19.2,14.8,15.2,-289.14,-289],'staff_white_paint','receiver_header')
fixtures=[]
for i,(x,z)in enumerate([(-21,-291),(-31,-293),(-41,-293),(-51,-293)]):
    cube(f'D03Port2TaskHousing_{i}',[x-.55,x+.55,15.04,15.2,z-.12,z+.12],'staff_zinc','lighting_fixture')
    cube(f'D03Port2TaskDiffuser_{i}',[x-.505,x+.505,15.015,15.04,z-.085,z+.085],'staff_opal','lighting_fixture')
    fixtures.append({'name':f'D03Port2TaskLight_{i}','position':[x,15.005,z],'color':[.8,.9,1],'range_m':7.5,'energy':.8,'budget_owner':'Existing receiving_source_lights.gd / lighting_budget.gd'})
compiledpath=GAME/'data/generated/structural_meshes.json'
compiled=json.loads(compiledpath.read_text());actual=unary_union([Polygon(t)for q in compiled['regions']if q['deck']=='D03'for t in q['triangles']])
riserpath=PORT/'source/PORT_SECOND_STAFF_RISER.json';riser=json.loads(riserpath.read_text());landing=next(q for q in riser['floor_proposals']if q['deck']=='D03')
assert landing['district_link_center']==[-21,12.0,-289]
lobby=unary_union([Polygon(q['boundary'],q['holes'])for q in landing['missing_floor_polygons']])
missing=requested.difference(actual.union(lobby))
crewpath=FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json';crew=json.loads(crewpath.read_text())
crew_overlap=sum(requested.intersection(box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])).area for q in crew['instances'])
layoutpath=GAME/'data/whole_ship_layout.json';layout=json.loads(layoutpath.read_text())
programmes=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']=='D03'])
bodypath=GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json';body=json.loads(bodypath.read_text());inner=Polygon(next(q for q in body['levels']if q['deck']=='D03')['inner_reservation_boundary'])
spatialpath=GAME/'data/spatial_layout.json';spatial=json.loads(spatialpath.read_text());voids={q['id']:requested.intersection(Polygon(q['boundary'])).area for q in spatial['voids']if 'D03'in q['decks']}
dep=FIRST/'extensions/depot_receiving_batch005/source/DEPOT_RECEIVING.json';depot=json.loads(dep.read_text());assert depot['receiver']['position']==[-54,12,-216]
pins={str(p.relative_to(ROOT)):sha(p)for p in [LOW/'source/geometry_parts.json',LOW/'source/build_lower_staff_network.py',LOW/'source/section_contract.json',CAT/lower['export'],CAT/lower['source'],CAT/lower['manifest'],GAME/'data/architecture/LOWER_STAFF_NETWORK.json',riserpath,PORT/'exports/AST-STF-G3-006.glb',dep,crewpath,compiledpath,layoutpath,bodypath,spatialpath,CAT/'catalogue_manifest.json',CAT/'materials/staff/manifest.json',GAME/'docs/master_source/MASTER_FULL_CONTENT_INDEX.json',GAME/'docs/master_source/MASTER_CURRENT_APPLICATION.json']}
floor={'deck':'D03','floor_y':12,'thickness':.24,'additional_missing_only_area_m2':missing.area,'polygons':rows(missing),'general_floor_exported_or_installed':False,'dependency':'Root composes existing D03 compiled support, frozen port2 missing lobby floor and this missing-only branch proposal. No duplicate longitudinal street or floor owner.'}
spec={'schema':1,'catalogue_id':'AST-STF-G3-007','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres; D03 port2 screened branch into retained lower staff spine','parts':parts,'fixtures':fixtures,'route':{'points_xz':points,'gross_clear_width_m':3.6,'existing_supported_spine_leg_used_only':[[-57,-293],[-57,-216]],'existing_depot_receiver':[-54,12,-216]},'floor_proposal':floor,'source_pins':pins,'receiving_interfaces':[{'role':'frozen_port2_D03_lobby_fore','position':[-21,12,-289],'gross_clear_width_height_m':[3.6,2.8],'installed':False},{'role':'retained_lower_spine_east_wall','position':[-55.2,12,-293],'gross_clear_width_height_m':[3.6,2.8],'installed':False,'wall_and_bumper_depth_m':.145,'exact_patch':'D03_SPINE_RECEIVER_PATCH.json'}],'protected_fore_blank_D04_D07_rule_preserved':True,'existing_depot_east_closure_preserved':True,'new_stops_stock_cart_people_or_berth_keys_registered':0,'new_controller_or_longitudinal_street':False,'automatic_runtime_adoption':False,'unfinished':['Root adopts exact four-cell-role receiver successor and composes held branch/lobby floors','Actual gate/cabin boarding, loaded cart/species/structural and ordinary route acceptance','Full depot, crew district, other port2 receivers and remaining Group3 network']}
(HERE/'source/D03_PORT2_BRANCH.json').write_text(json.dumps(spec,indent=2)+'\n')
checks={'status':'PASS','new_branch_parts':len(parts),'tiny_spine_patch_parts':len(patch),'original_semantic_parts_changed':len(changed),'exact_native_cell_role_replacements':list(replacement.values()),'unmodified_other_original_native_meshes':predecessor['all_other_runtime_meshes_preserved'],'protected_200_crew_envelope_overlap_m2':crew_overlap,'D03_programme_intrusion_m2':requested.intersection(programmes).area,'protected_void_overlap_m2':voids,'outside_conservative_hull_m2':requested.difference(inner).area,'missing_floor_duplicate_m2':missing.intersection(actual.union(lobby)).area,'additional_missing_branch_floor_m2':missing.area,'existing_branch_floor_support_m2':requested.intersection(actual).area,'new_header_roof_duplicate_m2':roof.intersection(oldroof).area,'new_header_walls_inside_retained_spine_m2':wall.intersection(spine).area,'wall_feet_outside_actual_or_explicit_proposed_floor_m2':wall.difference(actual.union(lobby).union(missing)).area,'duplicate_existing_longitudinal_street_authored':False,'scope':'Bounded D03 source branch and exact four native cell-role successor proposal. Existing spine and depot are used, never reauthored.'}
zeros=['protected_200_crew_envelope_overlap_m2','D03_programme_intrusion_m2','outside_conservative_hull_m2','missing_floor_duplicate_m2','new_header_roof_duplicate_m2','new_header_walls_inside_retained_spine_m2','wall_feet_outside_actual_or_explicit_proposed_floor_m2']
assert all(checks[k]<1e-7 for k in zeros) and all(v<1e-7 for v in voids.values())
(HERE/'qa/D03_BRANCH_PLAN_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks))
