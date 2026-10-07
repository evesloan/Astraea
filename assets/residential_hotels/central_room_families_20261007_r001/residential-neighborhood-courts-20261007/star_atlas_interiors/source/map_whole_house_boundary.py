"""Read-only derivation of the complete 148-member Star Atlas construction boundary."""
from pathlib import Path
import json,math,hashlib,sys
from collections import Counter
R=Path(__file__).resolve().parents[1];W=R.parents[1];G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());A=G/'data/architecture/D12_D14_star_atlas.json';arc=json.loads(A.read_text());SP=G/'data/generated/structural_meshes.json';struct=json.loads(SP.read_text())['regions'];DP=G/'data/reference/directory_allocations.json';dirs=json.loads(DP.read_text())['records'];CW=W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';cross=json.loads(CW.read_text())['records'];members=[r for r in cross if r['house']==P['house_id']];instance={r['census_source_index']:r for r in P['units']}
# Existing public owners retain their own state. These static source transforms
# reconstruct their geometry only and do not replace lift/controllers/floor owners.
assets={a['catalogue_id']:a for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']};placements=[]
def add(aid,name,origin,yaw=0,source_override=None,owner='star_atlas.gd'):
 a=assets.get(aid,{});source=C/(source_override or a['source']);assert source.is_file(),source
 placements.append({'asset_id':aid,'name':name,'source':str(source),'source_sha256':sha(source),'godot_origin_xyz':origin,'godot_yaw':yaw,'blender_world_origin_xyz':[origin[0],-origin[2],origin[1]],'blender_yaw_z':yaw,'source_owner':str(G/'scripts'/owner),'geometry_only_no_new_controller':True})
add('AST-LIB-011','StarAtlasAuthoredArchitecture',[-80,78,0])
add('AST-CIR-003','StarAtlasThreeStopCabinAtRest',[-68.2,78,-10.2],-math.pi/2,'assets/commons_lift_cabin/source/AST-CIR-003_three_stop.blend','commons_lift.gd')
for aid,name,pos,yaw in [('AST-LIB-STR-003','CollectionStartCap',[-88,78,-26.5],0),('AST-LIB-STR-001','CollectionProfile_0',[-88,78,-26.5],0),('AST-LIB-STR-001','CollectionProfile_1',[-85.6,78,-26.5],0),('AST-LIB-STR-002','CollectionProfile_2',[-83.2,78,-26.5],0),('AST-LIB-STR-003','CollectionTurnCap',[-81.4,78,-28.3],math.pi/2),('AST-LIB-STUDY-01','CollectionSharedStudy',[-86,78,-21.5],0),('AST-LIB-007','CollectionReadingFolio',[-85.45,78.75,-21.23],0),('AST-LIB-008','CollectionTaskFixture',[-86,78.754,-21.5],0)]:add(aid,name,pos,yaw,'assets/library_structure/source/AST-LIB-STR-003_start.blend'if name=='CollectionStartCap'else None,'star_atlas_collections.gd')
for x in [-.55,.55]:
 for z in [-1.035,1.035]:add('AST-FUR-002','CollectionStudyChair_'+str((x,z)),[-86+x,78,-21.5+z],math.pi if z>0 else 0,owner='star_atlas_collections.gd')
for aid,name,pos,yaw in [('AST-LIB-012','LibraryReferenceCounter',[-63,78,5],math.pi),('AST-LIB-010','LibraryCatalogue_StaticOnly',[-55.7,78,7.4],2.65),('AST-LIB-009','PeriodicalBrowseEdge',[-59,78,12],math.pi),('AST-FUR-002','AtriumReadingChairNorth',[-55.2,78,16],0),('AST-FUR-002','AtriumReadingChairSouth',[-55.2,78,18.5],math.pi),('AST-FUR-003','AtriumReadingTable',[-55.2,78,17.25],0),('AST-GST-001','AtriumReadingFloorLamp',[-56.1,78,16.1],math.pi/3)]:add(aid,name,pos,yaw,owner='star_atlas_arrival.gd')
add('AST-LIB-STUDY-02','D13WindowStudy',[-64.7,84,-4.8],-math.pi/2,owner='star_atlas_commons.gd')
def rotated(v,yaw):x,y,z=v;return[x*math.cos(yaw)+z*math.sin(yaw),y,-x*math.sin(yaw)+z*math.cos(yaw)]
def at13(v):return[a+b for a,b in zip([-64.7,84,-4.8],rotated(v,-math.pi/2))]
add('AST-FUR-002','D13WindowStudyChair',at13([.105,0,.99]),math.pi/2,owner='star_atlas_commons.gd')
for h in [.42,.83]:add('AST-LIB-006','D13StudyStock_'+str(h),at13([-.711,h,-.075]),0,owner='star_atlas_commons.gd')
add('AST-LIB-008','D13WindowStudyFixture',at13([-.433,.756,-.286]),-math.pi/2,owner='star_atlas_commons.gd')
for aid,name,pos,yaw in [('AST-FUR-003','D14ConversationTable',[-88.5,88.5,9],0),('AST-FUR-002','D14ConversationChairWest',[-89.7,88.5,9],math.pi/2),('AST-FUR-002','D14ConversationChairEast',[-87.3,88.5,9],-math.pi/2)]:add(aid,name,pos,yaw,owner='star_atlas_commons.gd')
# Probe two candidate cross-links without silently claiming a supported floor.
routes=[]
for deck,y in [('D13',84),('D14',88.5),('D15',93),('D16',97.5)]:
 rs=[r for r in members if r['deck']==deck];z0=min(r['allocation_z'][0]for r in rs);z1=max(r['allocation_z'][1]for r in rs)
 candidates=[('north_existing_entry_gap',box(-86.05,z0,-81.95,-34.6)),('south_existing_entry_gap',box(-86.05,34.6,-81.95,z1)),('north_roof_bypass_crosslink',box(-86.05,-37.8,-48,-34.6)),('south_roof_bypass_crosslink',box(-86.05,34.6,-48,37.8)),('existing_atrium_edge_join',box(-51,-34.6,-48,34.6))]
 for name,q in candidates:
  guestrooms=[];programmes=[];owners=[]
  for u in cross:
   if u['deck']!=deck:continue
   x,z=u['allocation_x'],u['allocation_z'];a=q.intersection(box(x[0],z[0],x[1],z[1])).area
   if a>1e-6:guestrooms.append({'source_index':u['source_envelope_index'],'area_m2':a})
  for d in dirs:
   if d['deck']!=int(deck[1:]):continue
   x,z=d['x'],d['z'];a=q.intersection(box(x[0],z[0],x[1],z[1])).area
   if a>1e-6:programmes.append({'programme':d['programme_key'],'name':d['name'],'area_m2':a})
  existing=[]
  for o in struct:
   if abs(o['floor_y']-y)>1e-6:continue
   geom=unary_union([Polygon(t)for t in o['triangles']]);a=q.intersection(geom).area
   if a>1e-6:owners.append({'owner':o['id'],'area_m2':a,'not_public_roof':o['id']=='D13_star_atlas_lower_roof_0'});existing.append(geom)
  gap=q.difference(unary_union(existing)).area
  routes.append({'deck':deck,'floor_y':y,'proposal':name,'boundary_xz':list(q.exterior.coords)[:-1],'width_m':4.1 if'entry_gap'in name else 3.2 if'crosslink'in name else 3,'guest_intersections':guestrooms,'programme_intersections':programmes,'current_compiled_floor_overlaps':owners,'unsupported_plan_area_m2':gap,'status':'Candidate source route only; add only missing floor after bearing/roof/service/guard and runtime route review','keeps_closed_StarAtlas_north_south_walls':True})
# Every assigned unit, including unbuilt specialty/VIP, remains an explicit member.
member_rows=[]
for r in members:
 i=r['source_envelope_index'];supported=i in instance
 member_rows.append({'source_index':i,'proposed_runtime_id':r['proposed_runtime_id'],'historical_persistent_id':r['historical_persistent_id'],'deck':r['deck'],'family':r['proposed_family'],'source_allocation_x':r['allocation_x'],'source_allocation_z':r['allocation_z'],'scope_status':'r002 room source checked; receiving/access/runtime gates open'if supported else'D17 standard held at separate fit gate'if r['production_lane']=='D17_retained_standard_replan'else'Unbuilt specialty/VIP reservation; not a finished room','current_room_source':instance[i]['source_recipe_key']if supported else None})
views=[]
for family in sorted(set(r['view_target_family']for r in P['units'])):
 rs=[r for r in P['units']if r['view_target_family']==family]
 views.append({'view_class':family,'units':len(rs),'source_indices':[r['census_source_index']for r in rs],'view_target_ids':sorted(set(r['view_target_id']for r in rs)),'by_deck':dict(Counter(r['deck']for r in rs)),'actual_source_action':rs[0]['view_source_action'],'receiving_status':'Existing main atrium is retained; room-to-atrium interface and privacy still need construction/review'if family=='existing_main_atrium'else'Genuinely unbuilt receiving architecture; no real outlook acceptance','window_planes_x':sorted(set(r['aperture_contract']['plane_origin_world'][0]for r in rs)),'window_center_z_by_deck':{d:sorted(r['aperture_contract']['plane_origin_world'][2]for r in rs if r['deck']==d)for d in sorted(set(r['deck']for r in rs))}})
paths=[A,SP,DP,CW,G/'scripts/commons_lift.gd',G/'data/architecture/library_stock_anchors.json',C/'assets/star_atlas_architecture/source/section_contract.json',C/'assets/library_structure/source/AST-LIB-STR-003_start.blend',G/'data/architecture/packages/upper_hull/HOUSE_CROWN_BOUNDARY_CONTRACT.json']
out={'schema':'astraea.star_atlas_whole_house_continuation.v1','status':'Explicit source composition boundary; no new full-house assembly launched','house_id':P['house_id'],'total_units':148,'family_counts':dict(Counter(r['proposed_family']for r in members)),'deck_counts':dict(Counter(r['deck']for r in members)),'members':member_rows,'input_hashes':{str(p):sha(p)for p in paths},'protected_owner_files':json.loads((R/'qa/REFERENCE_INSPECTION.json').read_text())['owners_read_and_protected'],'retained_public_static_source_placements':placements,'retained_dynamic_owner':{'script':'scripts/commons_lift.gd','identity':'star_atlas_lift_001','floors_y':[78,84,88.5],'deck_numbers':[12,13,14],'shaft_top_y':91.85,'gate_origins':'World(-68.32, floor_y, -10.2), yaw PI/2, per exact owner','cabin_at_rest':'World(-68.2,78,-10.2), yaw -PI/2','no_D15_D17_extension_authorized':True},'datum_bound_public_contents':[{'owner':'scripts/star_atlas_collections.gd','source':'data/architecture/library_stock_anchors.json','binding':'Each exact source shelf/cell anchor transformed through the three retained collection placements; same three deterministic stock variants; preserve source loop.'},{'owner':'scripts/star_atlas_arrival.gd','asset':'AST-LIB-012','binding':'CounterReferenceFolio and CounterTaskFixture stay bound to DATUM_west/east_work_surface and DATUM_west/east_fixture_receiver; yaw PI plus -0.515 west / +0.515 east. Read evaluated datum matrices before placement.'},{'owner':'All four existing scripts','binding':'Retain actual source lens/aim markers for all public fixtures; no source-origin fallback.'}],'retained_floor_owners':[r for r in arc['floor_regions']],'critical_interface_findings':['D13 and D14 north/south Star Atlas perimeter walls at Z +/-13.85 are closed. Existing six-metre arrivals are east-facing at Z0; do not cut new doors in protected owner scripts.','D13_star_atlas_lower_roof_0 is explicitly non-public: do not credit it as a residential street just because compiled data calls its material guest_floor.','The D15 protected cover remains continuous; D15-D17 commons and vertical links are new distinct programme work, not an extension of the D12-D14 opening.','Ordinary source doors face the real 4.1m gap X -86.05..-81.95; view edges are on the opposite faces.','Candidate roof-bypass crosslinks at Z +/-34.6..37.8 reach the existing atrium edge X -51..-48, then the real Z0 Star Atlas connector. Their plan checks do not establish structure or runtime traversal.'],'candidate_floor_ownership_rule':'Union adjoining street/crosslink strips, then subtract every current compiled owner; never emit each overlapping proposal as a separate coincident slab. Streets extend to Z +/-34.6 so they overlap their crosslinks without a gap.','candidate_guest_route_boundaries':routes,'receiving_view_groups':views,'unbuilt_central_programmes':[d for d in dirs if d['deck']in[15,16,17]and d['x']==[-97.0,-63.0]and d['z']==[-14.0,14.0]],'D17_policy':'Use exact separate retained polygons and fit report; all10 standards held. The7 VIP footprints including Supreme upper level stay explicit; no scaled ordinary source. Do not reuse obsolete historical D18 positions instead of current Crown ownership.','next_construction_sequence':['Compose and source-check missing D13/D14 street and roof-bypass arrivals around retained floor owners and closed commons; preserve the actual public source libraries above.','Author actual bounded flanking courts and D13/D14 outer wintergarden receiving geometry, including windows, private setbacks, structure and light.','Resolve D15 specialty-only streets/environmental interfaces and D16 outer wintergarden hull shoulder/loggia with current upper-hull owner; no species population invented.','Resolve D17 entry easements, 18m central court intent and new distinct commons/access; then fit ten standards and seven VIP programmes to their actual separate footprints.','Adopt only after exact structure/interfaces, operating source doors, loaded cart/species paths, current whole-room/vertical privacy and normal-play visual gates pass.'],'Game_or_Catalogue_writes':False,'runtime_acceptance':False}
(R/'WHOLE_148_CONTINUATION_BOUNDARY.json').write_text(json.dumps(out,indent=2)+'\n')
print('WHOLE_HOUSE_BOUNDARY',len(members),len(placements),'routes',len(routes),'route_guest_conflicts',sum(len(r['guest_intersections'])for r in routes),'program_conflicts',sum(len(r['programme_intersections'])for r in routes),'roof_overlap',sum(o['area_m2']for r in routes for o in r['current_compiled_floor_overlaps']if o['not_public_roof']))
for r in routes:
 if r['guest_intersections']or r['programme_intersections']:print('CONFLICT',r['deck'],r['proposal'],r['guest_intersections'],r['programme_intersections'])
