from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, zipfile
import fitz
from PIL import Image

OUT = Path(__file__).resolve().parent
AUDIT = OUT.parent
CAT = Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
save = lambda name, value: (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
S = {
    'atlas': AUDIT/'sources/Astraea-current-layout-atlas.pdf',
    'source_archive': AUDIT/'sources/Astraea_Master_Design_Source.zip',
    'coverage_json': AUDIT/'extracted/project_docs/architecture/whole_ship_coverage.json',
    'coverage_md': AUDIT/'extracted/project_docs/architecture/WHOLE_SHIP_COVERAGE.md',
    'ship_design': AUDIT/'extracted/project_docs/SHIP_DESIGN.md',
    'daily_guest_life': AUDIT/'extracted/project_docs/DAILY_GUEST_LIFE.md',
    'species_canon': AUDIT/'extracted/project_docs/SPECIES_CANON.md',
    'master_gdd': AUDIT/'extracted/Astraea_Master_Game_Design.md',
    'connected_salon': AUDIT/'extracted/project_docs/architecture/D09_CONNECTED_SALON.md',
    'composition_contract': AUDIT/'extracted/project_docs/architecture/D09_COMPOSITION_CONTRACT.md',
    'current_canon': CAT/'CATEGORY_COVERAGE.json',
    'promenade_reference': CAT/'references/retail/promenade_reference.png',
    'promenade_identity': CAT/'references/retail/promenade_library_identity.json',
    'public_blueprint': AUDIT/'sources/2.png',
    'copied_public_blueprint': CAT/'references/retail/public_blueprint.png',
    'prior_atlas_extraction': AUDIT/'planning-package-v3/inputs/atlas_allocations.json',
    'batch18_contract': CAT/'batches/batch18/CONTRACT.md',
}
cov = load(S['coverage_json'])
rooms = [r for r in cov['rooms'] if r['deck']==9]
byid = {r['id']:r for r in rooms}
assert len(rooms)==len(byid)==110
assert {r['id'] for r in rooms if r['family_id']=='small_retail'} == {f'R{i:03}' for i in range(1,101)}
assert byid['R070']['name']=='Kind Curios / 070'
assert sha(S['promenade_reference'])=='f80a4f58ec2c53679c20b990acc663dec270ebfabc1626e84c3eeb861d109d6d'
assert sha(S['public_blueprint'])==sha(S['copied_public_blueprint'])

sources=[]
with zipfile.ZipFile(S['source_archive']) as archive:
    for key,path in S.items():
        root = 'catalogue' if path.is_relative_to(CAT) else 'district_layout_audit'
        row={'id':key,'source_root':root,'path':str(path.relative_to(CAT if root=='catalogue' else AUDIT)),
             'bytes':path.stat().st_size,'sha256':sha(path)}
        if path.is_relative_to(AUDIT/'extracted'):
            member=str(path.relative_to(AUDIT/'extracted'))
            row['archive_member']=member
            row['archive_member_hash_matches']=hashlib.sha256(archive.read(member)).hexdigest()==sha(path)
            assert row['archive_member_hash_matches']
        sources.append(row)

pdf=fitz.open(S['atlas']); page=pdf[10]; ds=page.get_drawings()
hull=ds[13]['rect']; scale=hull.width/1082; cy=(hull.y0+hull.y1)/2
inset_hull=ds[306]['rect']; inset_scale=inset_hull.width/1082; inset_cy=(inset_hull.y0+inset_hull.y1)/2
def pt(q,inset=False):
    h,s,c=(inset_hull,inset_scale,inset_cy) if inset else (hull,scale,cy)
    return [round((q.y-c)/s,3),round((q.x-h.x0)/s-541,3)]
def bounds(r,inset=False):
    a,b=pt(r.tl,inset),pt(r.br,inset)
    return {'x':[a[0],b[0]],'z':[a[1],b[1]]}
def rec(i,inset=False):
    d=ds[i]
    return {'drawing_index_zero_based':i,'pdf_sequence_number':d['seqno'],
            'bounds_xz_m':bounds(d['rect'],inset),'pdf_bounds_points':list(d['rect']),
            'center_xz_m':pt((d['rect'].tl+d['rect'].br)/2,inset),
            'stroke_rgb':d['color'],'fill_rgb':d['fill'],
            'graphical_stroke_width_in_model_m':round(d['width']/(inset_scale if inset else scale),3) if d['width'] else None,
            'items':[{'operator':it[0], 'points_xz_m':[pt(q,inset) for q in it[1:] if isinstance(q,fitz.Point)]} for it in d['items']]}

label_rect={}
for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
        for span in line['spans']:
            t=span['text']; bb=fitz.Rect(span['bbox']); center=(bb.tl+bb.br)/2
            if t.isdigit() and 1<=int(t)<=10 and hull.contains(center):
                candidates=[i for i in range(40,70,3) if ds[i]['rect'].contains(center)]
                assert len(candidates)==1
                label_rect[int(t)]=candidates[0]
assert len(label_rect)==10
larger=[]
for number,row in enumerate(rooms[:10],1):
    i=label_rect[number]
    larger.append({'id':row['id'],'name':row['name'],'kind':row['kind'],'family_id':row['family_id'],
      'staff_only':row['staff_only'],'atlas_directory_number':number,'page_one_based':11,
      'historical_allocation':rec(i),'historical_door_symbol':rec(i+1),
      'allocation_dimensions_xz_m':[46,68],'allocation_area_m2':3128,
      'registered_capacity':row['registered_capacity'],
      'whole_room_simultaneous_occupancy_limit':row['whole_room_simultaneous_occupancy_limit'],
      'limits':'Allocation is historical and rectangular. Door symbol center is evidence; symbol extent is not aperture, swing, pocket, threshold landing or opening head.'})

small=[]
for i in range(70,270,2):
    a,b=ds[i]['rect'],ds[i+1]['rect']
    extent=bounds(a)
    assert abs(extent['x'][1]-extent['x'][0]-12)<0.002 and abs(extent['z'][1]-extent['z'][0]-12)<0.002
    small.append({'evidence_key':f'atlas_p11_drawing_{i:03}','stable_id':None,
                  'allocation':rec(i),'door_symbol':rec(i+1),
                  'identity_status':'Unlabelled in the main plan; no ID inferred from drawing order.'})
labelled=[]
for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
        for span in line['spans']:
            if not re.fullmatch(r'R\d{3}',span['text']): continue
            sid=span['text']; bb=fitz.Rect(span['bbox']); c=(bb.tl+bb.br)/2
            candidate=[i for i in range(333,369,2) if ds[i]['rect'].contains(c)]
            assert len(candidate)==1
            i=candidate[0]; b=bounds(ds[i]['rect'],True)
            matching=[v for v in small if v['allocation']['bounds_xz_m']==b]
            assert len(matching)==1
            matching[0]['stable_id']=sid
            matching[0]['identity_status']='Confirmed by explicit address label in the inset and identical calibrated main-plan bounds.'
            labelled.append({'stable_id':sid,'name':byid[sid]['name'],'inset_allocation':rec(i,True),
                             'inset_door_symbol':rec(i+1,True),'main_plan_evidence_key':matching[0]['evidence_key']})
assert len(small)==100 and len(labelled)==16
selected=next(v for v in labelled if v['stable_id']=='R070')
assert selected['inset_allocation']['bounds_xz_m']=={'x':[66.0,78.0],'z':[230.0,242.0]}
assert selected['inset_door_symbol']['center_xz_m']==[78.0,236.0]

# Cross-check independently extracted geometry against the surviving previous extraction; it is not our source of geometry.
prior=[r for r in load(S['prior_atlas_extraction']) if r['deck']==9]
prior_shapes=sorted((tuple(r['x']),tuple(r['z'])) for r in prior)
new_shapes=sorted((tuple(r['historical_allocation']['bounds_xz_m']['x']),tuple(r['historical_allocation']['bounds_xz_m']['z'])) for r in larger)+[]
new_shapes=sorted(new_shapes+[(tuple(r['allocation']['bounds_xz_m']['x']),tuple(r['allocation']['bounds_xz_m']['z'])) for r in small])
assert len(prior_shapes)==110
assert all(max(abs(a-b) for tup1,tup2 in zip(p,n) for a,b in zip(tup1,tup2))<0.002 for p,n in zip(prior_shapes,new_shapes))

vectors={
 'schema':'astraea.d09_historical_atlas_vectors.v1',
 'source_sha256':sha(S['atlas']),'page_one_based':11,
 'method':'Direct PDF vector extraction; ten large rooms joined by numbered labels and directory order. Sixteen small IDs explicitly labelled in the inset joined to identical calibrated main-plan bounds. Other 84 address-to-footprint assignments are left unknown.',
 'calibration':{'ship_axes':'X port negative/starboard positive; Z bow negative/aft positive; Y up',
                'hull_z_limits_m':[-541,541],'main_hull_pdf_bounds':list(hull),'main_scale_points_per_m':scale,'main_x_zero_pdf_y':cy,
                'inset_hull_pdf_bounds':list(inset_hull),'inset_scale_points_per_m':inset_scale,'inset_x_zero_pdf_y':inset_cy},
 'precision_note':'0.001 m rounding reports PDF extraction precision, not architectural surveying accuracy. Source-level coordinates rounded to the evident integer grid are used in the handoff; full extracted values are retained here.',
 'larger_destinations':larger,'small_shop_footprints':small,'explicitly_labelled_small_shops':labelled,
 'circulation_primitives':[rec(i) for i in range(14,40)],
 'atrium_primitives':[rec(i) for i in range(270,285)],
 'tram_primitive':rec(285),'tram_stops':[rec(i) for i in [286,289,292,295,298]],
 'unlabelled_service_colored_objects':[rec(i) for i in [287,288,290,291,293,294,296,297,299,300]],
 'limits':['Atlas simplifies/omits actual walls, furniture, ceilings and minor objects.','Graphical route stroke widths are not as-built clear widths.','R072/R097 appear beyond the fully visible labeled inset crop; they are not included in the sixteen direct label joins.','No inferred identity, stock function or access permission is assigned to unlabelled service-colored objects.']}
save('D09_atlas_vector_evidence.json',vectors)

exact_rows={
 'schema':'astraea.d09_exact_coverage_rows.v1','source_sha256':sha(S['coverage_json']),
 'source_registry_snapshot_utc':cov['scope']['inventory_snapshot_utc'],
 'rows_are_verbatim_json_objects':True,
 'deck_row':next(d for d in cov['decks'] if d['deck']==9),
 'retail_family_rows':[f for f in cov['families'] if f['family_id'] in ['retail_destinations','small_retail']],
 'rooms':rooms,
 'spatial_system_rows':[r for r in cov['unregistered_spatial_systems'] if r['system_id'] in ['circulation_D09','atrium_level_D09','panoramic_lift_towers']],
 'relevant_evidence':{k:cov['evidence'][k] for k in ['REGISTRY_NOW','SPATIAL_ALL','D09_SPATIAL','CHANGE_SCOPE','PROFILE_PERSISTENCE']},
 'authority_limits':'Historical status strings are preserved, including dated rejections. Later source direction approves Composition04 propagation/refinement, not final D09 acceptance. Exact rows do not certify current host or grant replacement slot ownership.'}
save('D09_exact_coverage_rows.json',exact_rows)

def excerpt(sid,start,end):
    return {'source_id':sid,'line_start_one_based':start,'line_end_one_based':end,
            'text':'\n'.join(S[sid].read_text().splitlines()[start-1:end])}
excerpts=[excerpt('master_gdd',613,620),excerpt('master_gdd',771,773),
          excerpt('daily_guest_life',35,47),excerpt('connected_salon',11,15),
          excerpt('composition_contract',44,46),excerpt('coverage_md',75,78)]

proposals=[
 {'id':'stepped_display_island','counts_as_designs':1,
  'role':'A low freestanding stepped display for inspectable goods/container silhouettes, with an obvious supported base and browsing face.',
  'catalogue_id':'AST-RTL-002',
  'sample_nominal_local_dimensions_xyz_m':[1.9,1.4,1.05],
  'sample_source_placement_xyz_m':[3.2,4.2,0],'sample_yaw_degrees':0,
  'sample_source_bounds_xyz_m':{'x':[2.25,4.15],'y':[3.5,4.9],'z':[0,1.05]},
  'sample_approach_xy_m':{'x':[2.25,4.15],'y':[2.0,3.5]},
  'profile_direction':'Two or three broad usable levels with a restrained orange inset/reveal under pale display surfaces; curved or chamfered ends related to the wall profile. Do not make stairs or a climbable promenade obstruction.',
  'adjustable_sample_tier_heights_m':None,
  'acceptance_checks':['All goods rest on actual display surfaces, not only marker origins.','Read a stepped merchandise display rather than seating or a generic table.','Approach is visible and separate from the central through path; verify actual reaching later.','Low geometry must remain legible at ordinary player height and the target retro resolution.']},
 {'id':'fitted_wall_display_storage_bay','counts_as_designs':1,
  'role':'An architectural display/storage edge with a single coherent wall-to-plinth-to-canopy profile and a visible relationship to the existing entry.',
  'catalogue_id':'AST-RTL-001',
  'sample_nominal_local_dimensions_xyz_m':[3.4,0.9,2.9],
  'sample_source_placement_xyz_m':[-4.85,3.5,0],'sample_yaw_degrees':90,'placed_facing':'+sourceX',
  'sample_source_bounds_xyz_m':{'x':[-5.3,-4.4],'y':[1.8,5.2],'z':[0,2.9]},
  'sample_approach_xy_m':{'x':[-4.4,-2.9],'y':[1.8,5.2]},
  'profile_direction':'A thick pale textured outer cheek, a deep orange recessed return, a dark inner display/storage plane and a stepped overhead soffit. Build real depth and joining edges. The forward return at sourceY=1.8 is the local left/sourceX-negative end before rotation; shape it to face the threshold obliquely and reveal goods beyond it. The same profile terminates into a backed storage plinth and a shielded display-light reveal.',
  'threshold_relationship':'Set the fitted bay back from the entry datum. Its forward cheek and canopy belong to the interior side-wall profile, never a replacement door frame. The outward-looking display face can be seen from the existing threshold while the actual moving door, pocket and header zones remain unresolved and separately reserved by the host.',
  'wall_support_condition':'SourceX=-6 is the historical allocation edge in the test frame, not a proven finished support surface. The nominal bay back at -5.3 is 0.7 m inside that edge. This is a diagram gap, not a discovered wall/service recess or proof of wall attachment. Verify actual wall depth/fixings and adjust before host fit.',
  'section_proposal':'Keep display shelves/use surfaces low enough to inspect; reserve the upper nested profile for visual framing and shielded light. Sample overall 2.9 m profile is a new adjustable design choice below the documented 8.25 m deck allowance. Neither number proves actual local headroom.',
  'acceptance_checks':['Neutral-material cutaway shows a real recess and wall/ceiling/storage relationship.','Orange surface is within a pale structural profile; a colored flat panel on a generic cabinet does not pass.','Keep entry approach, true portal clearance and storage retrieval distinct.','No door pocket/head or fixed mounting interface is inferred from the reference image.']},
 {'id':'compact_wrapping_checkout_bench','counts_as_designs':1,
  'role':'A compact flat wrapping/handling surface with tidy packaging storage and distinguishable public and staff faces.',
  'catalogue_id':'AST-RTL-003',
  'sample_nominal_local_dimensions_xyz_m':[1.8,0.9,1.15],
  'sample_source_placement_xyz_m':[3.2,8.9,0],'sample_yaw_degrees':0,'public_face':'-sourceY','staff_face':'+sourceY',
  'sample_source_bounds_xyz_m':{'x':[2.3,4.1],'y':[8.45,9.35],'z':[0,1.15]},
  'sample_public_approach_xy_m':{'x':[2.1,4.3],'y':[7.05,8.45]},
  'sample_staff_approach_xy_m':{'x':[2.1,4.3],'y':[9.35,10.85]},
  'profile_direction':'An uninterrupted supported working top, controlled orange/pale end profile, accessible storage intent and a packing-material recess. Keep the task surface useful; do not fill it with decorative controls.',
  'checkout_limit':'Checkout is a visual programme label. No cash register, scanner/payment protocol, prices, currency, stock deduction, player wallet action, merchant labor or assigned operator is implemented or authorized here.',
  'acceptance_checks':['Public and staff sides are visually intelligible.','Container transfer and wrapping occur on a supported plane.','Sample standing pads do not become capacity slots or staff ownership.','Actual body/reach/knee contact, storage opening travel and support must be checked later.']},
 {'id':'reusable_goods_container_set','counts_as_designs':1,
  'role':'One coordinated reusable goods container with nested carrier/tray and supported lid or explicitly detached handling state, suited to displaying, staging and carrying ordinary fictional goods.',
  'sample_source_bounds_xyz_m':None,
  'catalogue_id':'AST-RTL-004','sample_maximum_outer_dimensions_xyz_m':[0.5,0.38,0.35],
  'placement_rule':'No separate floor allocation. Place sample variants on the island, wall shelf or bench, wholly inside their verified support polygons; contained goods remain illustrative.',
  'profile_direction':'Shared rim, grip, latch/lid and stacking language; clear empty interiors and credible contact surfaces. Material variants and packaging states remain within one catalogue design, not extra asset-count credits.',
  'acceptance_checks':['Container rests/stack interfaces are physically legible.','Use only supported positions; no floating props or blocked wrapping surface.','No actual inventory, contents quantity, food-safe/chemical-safe grade, cleaning method or species compatibility claim.','Future movable instances must retain stable identity, owner, transform/state across stream-out, but no persistence implementation is claimed now.']}
]

main={
 'schema':'astraea.d09_retail_programme_reference_handoff.v1',
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'conclusion':'Use R070 / Kind Curios / 070 as the proven source-level 12 x 12 m test context for a partial threshold/display/wrapping sequence. Orchard market remains its separate large destination. Four useful designs are identified; no installation, new destination, capacity or payment behavior is created.',
 'scope':{'audit_only':True,'owned_output_directory':'d09-retail-handoff','parent_gate':'Parent reports Batch17 durably delivered and next retail family approved.',
          'catalogue_or_runtime_modified':False,'assets_created':False,'new_masterplan':False,
          'runtime_expected_path':'/workspace/shared/space-hotel-full','runtime_path_exists':Path('/workspace/shared/space-hotel-full').exists(),
          'host_integration':'pending','portable':'Source facts, exact rows, vector geometry and source hashes are embedded in this directory. Provenance paths identify inputs; they are not runtime dependencies.'},
 'current_governing_canon':load(S['current_canon'])['governing_canon'],
 'sources':sources,
 'source_identity':{
   'atlas':{'library_file_id':'libfile_b9125cc753a481919b12ded74d590b04','identity_provenance':'Surviving d01/d11 source handoffs; local content freshly rehashed, not a new Library query.','source_snapshot_date':'2026-10-01','page_one_based':11},
   'source_archive':{'library_file_id':'libfile_362451ac969c8191afbf823122078feb','version':2,'identity_provenance':'Surviving handoffs; extracted relevant documents independently verified against archive members.'},
   'promenade':load(S['promenade_identity']),
   'public_blueprint':{'library_file_id':'libfile_45f3a99c597c8191b5974a9e725331cd','sheet':'3 of 6 / ASW-GV-03 / Public Amenities + Entertainment + Retail','identity_provenance':'Surviving d11/reference inventory provenance; original and lead copy hashes freshly matched.'}},
 'historical_programme':{
   'D09_registered_spaces':110,'addressed_small_shops':100,'small_shop_addresses':[f'R{i:03}' for i in range(1,101)],
   'separate_larger_destinations':10,'larger_retail_destinations':7,'shopping_destinations_count':107,
   'count_explanation':'Seven large retail destinations plus 100 small shops = 107 shopping destinations; the three remaining larger places are two social/tea destinations and one culture/recreation destination. 110 is all registered D09 spaces, not retail capacity.',
   'large_retail_ids':next(f for f in cov['families'] if f['family_id']=='retail_destinations')['room_ids'],
   'other_large_destinations':[{'id':sid,'name':byid[sid]['name'],'family_id':byid[sid]['family_id']} for sid in ['D09_tea1','D09_salon5','D09_arcade9']],
   'orchard_market':next(r for r in larger if r['id']=='D09_market0'),
   'all_larger_destinations':larger,
   'all_D09_rooms_staff_only_false':all(r['staff_only'] is False for r in rooms),
   'occupancy_capacity':'No simultaneous occupancy limit is assigned by the coverage rows. Null is unknown, not zero or permission to derive capacity from area.',
   'bakery_is_not_dining_capacity':'Starlight bakery is an existing retail destination; do not add it to the separate D10 meal-place ledger.',
   'address_ownership':'Preserve R001–R100 unique IDs, repeated brand names, existing destination assignment and all actual slot/instance owners. This audit does not assign merchants or change ownership.'},
 'selected_candidate':{
   'stable_id':'R070','name':byid['R070']['name'],'kind':'shop','family_id':'small_retail','staff_only':False,
   'historical_allocation_bounds_ship_xz_m':{'x':[66,78],'z':[230,242]},'dimensions_xz_m':[12,12],'allocation_area_m2':144,
   'allocation_center_ship_xz_m':[72,236],'historical_door_symbol_ship_xz_m':[78,236],
   'entrance_edge':'+X allocation edge; inward direction is -shipX',
   'direct_identity_proof':selected,'matching_main_plan_drawing_index':208,'matching_main_plan_door_drawing_index':209,
   'source_eligibility':'Named and geometrically mapped in the surviving atlas, and separately present in coverage; suitable only as a bounded source-level test envelope.',
   'actual_finished_interior_polygon':None,'actual_door_aperture_width_height':None,'moving_leaf_pockets_and_travel':None,'header_and_threshold_support':None,
   'actual_facility_slot_ids_positions_facing_owners':None,'actual_approach_and_turn_envelopes':None,
   'proof_door_is_symbolic':'Main-plan door symbol is about 3.2 m wide at its calibrated scale; inset symbol is about 1.318 m wide. Centers agree but extents change with drawing scale, so neither is a door aperture.'},
 'historical_section':{
   'deck_floor_world_y_m':52.5,'next_D10_floor_world_y_m':61,'deck_available_clear_height_m':8.25,
   'allowance_ceiling_world_y_m':60.75,
   'source_ids':['coverage_json','connected_salon','ship_design'],
   'limit':'8.25 m is a deck-level usable-height allowance. It does not prove R070/market local ceiling profile, door head, beam/service intrusions, fixtures or attachment heights. No new mezzanine or floor opening.'},
 'neighboring_and_protected_relationships':[
   {'relation':'R070 nearest explicitly mapped same-bank neighbors','ids':['R069','R071'],'bounds':{'R069':{'x':[66,78],'z':[204,216]},'R071':{'x':[66,78],'z':[256,268]}},'interpretation':'14 m between allocation ends; this is a geometric gap, not free space or a certified route.'},
   {'relation':'R095 faces R070 across the local retail-bank interval','ids':['R070','R095'],'bounds_R095':{'x':[94,106],'z':[230,242]},'door_R095_xz_m':[94,236],'face_to_face_interval_x_m':[78,94],'interpretation':'16 m between allocation faces; do not adopt that whole interval as empty promenade, queue area or cart clearance.'},
   {'relation':'Nearest drawn transverse bank connection','source':'atlas drawing38','line_x_m':[55,95],'line_z_m':216,'interpretation':'Historical public-colored connection. Graphical stroke is 5 m but does not establish as-finished width. Its 14 m longitudinal separation from R070 boundary is not route length.'},
   {'relation':'Separate axial routes','source':'atlas drawings14–19,285','guest_ribbon_x_m':[-5.5,5.5],'outer_service_colored_line_x_m':[-57,57],'tram_centerline_x_m_outside_atrium':0,'interpretation':'Preserve distinct public/service/transit purposes. Route strokes and colors do not grant service access or clearance.'},
   {'relation':'Orchard market and Copper kettle face across axial street','ids':['D09_market0','D09_tea1'],'longitudinal_band_z_m':[-466,-398],'market_front_door_xz_m':[-8,-432],'tea_front_door_xz_m':[8,-432],'interpretation':'Historical fronts face one another; no verified direct service/rear connection.'},
   {'relation':'Orchard market is remote from R070 and the atrium sample','market_z_m':[-466,-398],'R070_z_m':[230,242],'atrium_slab_opening_z_m':[-64,64],'interpretation':'Do not portray the market as the atrium frontage or assume all 100 shops are on one atrium ring.'},
   {'relation':'Protected central atrium and salon context','source_ids':['connected_salon','atlas'],'slab_opening_xz_m':{'x':[-48,48],'z':[-64,64]},'salon_allocation_xz_m':{'x':[52,98],'z':[-34,34]},'salon_terrace_sample_z_m':[-14,14],'protected_tram_strip_x_m':[35,45],'salon_transverse_route_z_m':0,'existing_atrium_portal_x_m':48,'salon_front_door_x_m':52,'panoramic_lift_landmark_xz_m':[31.2,5],'interpretation':'These exact source reservations belong to the existing central salon/atrium checkpoint, not to R070 or Orchard. Preserve them globally; do not import them as a shop layout or new shop frontage.'}
 ],
 'coordinate_frame_for_optional_source_check':{
   'units':'metres','source_axes':'Blender/source X lateral, Y inward, Z up; front is source -Y',
   'source_origin':'Existing R070 symbolic threshold center, only as a QA datum',
   'planning_coordinates':'u = shipZ - 236; v = 78 - shipX',
   'proper_source_coordinates':'sourceX = -u; sourceY = v; sourceZ = shipY - 52.5',
   'source_to_ship_formula':'ship(x,y,z) = (78 - sourceY, 52.5 + sourceZ, 236 - sourceX)',
   'source_to_ship_rotation_matrix':[[0,-1,0],[0,0,1],[-1,0,0]],'rotation_determinant':1,
   'native_GLTF_GLB_note':'After normal Blender Z-up to glTF Y-up export, native GLB yaw +90 degrees and translation (78,52.5,236) give the same proper placement. This records a transform for inspection, not runtime placement.',
   'historical_allocation_in_source_xy_m':{'x':[-6,6],'y':[0,12]},
   'avoid_reflection':'Do not use sourceX=u with the same inward axis; it silently mirrors the placement and reverses orientation.'},
 'bounded_relative_plan_section_proposal':{
   'status':'Adjustable new proposal for source inspection only; not measured from either reference, not actual host placement, no new reserved use slots.',
   'source_backed_envelope_only':{'x':[-6,6],'y':[0,12],'z_deck_allowance':[0,8.25]},
   'partial_scope':'One existing 12 x 12 m allocation is an outer inspection boundary. Three nominal fixture boxes and proposed approach pads demonstrate only a partial threshold/display/work sequence. All remaining space is unexamined existing host space, not newly available storage or a new room.',
   'proposal_source':'Parent placement direction and batch18_contract, freshly read and hashed. Bounding boxes assume nominal dimensions are centered laterally/depthwise on each stated placement and floor-based at sourceZ=0. Replace them with evaluated asset extents after authors produce geometry.',
   'all_new_dimensions_are_adjustable':True,
   'proposed_keep_clear_test_regions':[
      {'name':'entire arrival band','x':[-6,6],'y':[0,1.5],'basis':'new adjustable proposal, not actual opening, turning proof or mandatory clearance'},
      {'name':'uninterrupted inspection through path','x':[-1.2,1.2],'y':[1.5,11.5],'basis':'new adjustable 2.4 m test strip, not a certified cart/species route'}],
   'actual_host_approach_reservations':None,
   'separately_required_host_reservations':['actual opening/closed and open leaf geometry','complete leaf travel and door pockets','true door head/jamb/support volume','existing authored arrival/browse/work slot approaches and facing','cart/body turns, swept appendages and stopping/retrieval areas','fixed wall/ceiling/services support','cleaning access and interaction rays'],
   'sequence':'Existing threshold datum leads beside a fitted orange-recess wall profile and a low island on the opposite side; the central path stays visually legible. A compact wrapping bench sits farther inside at an edge with distinct public/staff task faces. Goods containers sit on supported display/work surfaces.',
   'nominal_box_screen':{
      'method':'Axis-aligned bounds after source placement, using full nominal fixture dimensions and exact 90-degree wall rotation. No geometry/physics engine, actual authored mesh, actor or door motion has been tested.',
      'all_three_boxes_inside_historical_outer_boundary':True,
      'all_three_boxes_clear_both_proposed_empty_regions':True,
      'wall_box_to_arrival_band_gap_m':0.3,
      'wall_box_to_negative_lateral_allocation_edge_gap_m':0.7,
      'wall_box_to_central_strip_gap_m':3.2,
      'island_box_to_central_strip_gap_m':1.05,
      'bench_box_to_central_strip_gap_m':1.1,
      'staff_pad_to_rear_allocation_edge_gap_m':1.15,
      'interpretation':'Arithmetic separation only. These are not required safe margins, door pockets, actor clearances or extra usable floor area. Any evaluated mesh, fixture overhang, goods or movement extending beyond nominal bounds triggers a fresh local screen.'},
   'components':proposals,
   'critical_limit':'Because actual host reservations are absent, a clean diagram/inter-object separation cannot be reported as door clearance, installed six-species fit or an operational retail room.'},
 'reference_pixel_audit':{
   'atlas_page11_inspected':True,'public_blueprint_inspected':True,'original_promenade_inspected':True,
   'promenade_pixels':list(Image.open(S['promenade_reference']).size),
   'promenade_observations':['Monumental pale textured columns and curved solid balcony/soffit edges establish structure.','Warm orange is concentrated in deep, rounded shopfront recesses behind a pale outer frame.','Dark inner fascia/display framing, layered reveals and warm concealed light give the shop entry thickness.','Actual objects on shelves/platforms and inhabited thresholds reveal use behind the frontage.','Planting, seating and slim golden/glazed guard edges belong to coherent public pockets; they do not justify adding these wholesale to a 12 m shop.','Coarse surface/dither texture supports broad readable silhouettes and material hierarchy.'],
   'required_translation':'Author a small fitted profile with real wall/display/storage/canopy depth and a threshold-facing return. Use the reference architectural hierarchy; do not merely recolor freestanding generic cabinets orange.',
   'public_blueprint_observations':['Printed retail promenade is on illustrative Deck10 with 100+ shops; current reconciled programme assigns retail to D09.','The plate separates public primary/secondary, staff and retail-supply routes in its legend.','Promenade inset and isometric public-core view show layered inhabited retail edges.'],
   'reference_conflicts_not_adopted':['Illustrative Deck10 retail and Deck9 aquatic labels are not current deck assignments.','Printed 38 m width, deck elevations, 420 m promenade length, 2,500 retail visitors, 18 dining outlets and 12 lounge zones are not current geometry/capacity authority.','Illustrated bridges, atrium monument, shop names, alien silhouettes and apparent dimensions do not create new current destinations, species, floor openings or body sizes.'],
   'not_measurable_from_images':['finished door width/pocket/head','wall or canopy section dimensions','goods/container counts or performance','safe reach/body/appendage envelopes','material chemistry, food contact, fire rating or species compatibility','photometric lighting performance']},
 'ownership_behavior_and_material_boundaries':[
   'Preserve 100 unique R addresses and all ten larger IDs; no shop relocations, new merchants, extra destination or capacity.',
   'DAILY_GUEST_LIFE describes unique physical slot ownership across browse/work users, reservations during travel, release/reuse and save rebuild. The exact R070 slot transforms/IDs/owners are not in surviving coverage and must be recovered from the host.',
   'No capacity is inferred from 144 m2, 3,128 m2, an approach pad, furniture count or a visual empty space. No existing authored browse/work slot is replaced by a prototype marker.',
   'Historical ambient nominal purchases/parcels/restock do not authorize player retail checkout, inventory, wallet deductions, pricing, merchant labor, food service or economic balancing.',
   'Keep goods generic and non-operational; a label or apparent material does not certify species-safe, food-safe, chemical-safe, washable or load-rated use.',
   'Koblin stature, Mantelid appendages/privacy, Baelin soft-cartilage/contact and special-cleaner needs, Munko four-arm clearance and Mindo personhood remain canonical concerns; body dimensions, actual reaching/support, goods compatibility and hardware interfaces are unresolved.',
   'No Mindo charging/food system, universal food or cleaning product, species sales policy, transaction protocol or biological simulation is invented.',
   'One container set is one prop design despite variants or supporting sample placements. Instance counts in a render never create inventory, admission or ownership records.',
   'Future actual movable props must preserve stable instance ID, owner, transform and state through streaming/reload; this audit and four unplaced designs do not implement that persistence.'
 ],
 'historical_evidence_limits':{
   'coverage_snapshot':cov['scope']['inventory_snapshot_utc'],'D09_focused_evidence':cov['evidence']['D09_SPATIAL'],
   'selected_R070_exact_physical_evidence':byid['R070']['physical_evidence'],
   'later_facility_document':'DAILY_GUEST_LIFE contains later model and slot evidence than some coverage remaining-gap text. Respect its ownership contract without inventing absent per-shop slot geometry.',
   'current_component_acceptance':False,
   'limits':'Historical 0.65 m broad/static screens, portal tests and one salon cart crossing do not certify new profiles, every retail bay, dynamic crowd throughput, moving doors, all six canonical bodies, real wrapping/stock handling or final art.'},
 'actionable_acceptance_sequence':[
   'Inspect the four distinct source silhouettes together inside the declared relative R070 outer boundary; label new dimensions and all unmeasured host reservations.',
   'Render a threshold-height view, plan, section and neutral-material cutaway. The wall profile must visibly join recess, return, storage and soffit; distinguish each function without relying on labels.',
   'Verify authored solids and prop supports against the proposed diagram only; report those results as source geometry checks, never installed route acceptance.',
   'Recover the real R070 host polygon, support surfaces, door states/pockets/head and existing facility slots/ownership before any host fit or registry write.',
   'After approved host fitting, check affected actual arrival, browse/work, body/appendage, storage, cleaning, cart and persistence interfaces; preserve unrelated destinations/transit/voids and obtain visual acceptance.'
 ],
 'exact_document_excerpts':excerpts,
 'derivatives':[
   {'file':'D09_atlas_vector_evidence.json','sha256':sha(OUT/'D09_atlas_vector_evidence.json')},
   {'file':'D09_exact_coverage_rows.json','sha256':sha(OUT/'D09_exact_coverage_rows.json')},
   {'file':'atlas-page-11.png','sha256':sha(OUT/'atlas-page-11.png'),'role':'Read-only source-page render used for visual inspection'}]
}
save('D09_retail_programme_reference_handoff.json',main)

# These assertions validate evidence joins and proposed inter-object boxes only, never host clearance.
def intersects(a,b):
    return all(min(a[k][1],b[k][1])-max(a[k][0],b[k][0])>1e-8 for k in ['x','y'])
boxes=[p['sample_source_bounds_xyz_m'] for p in proposals if p['sample_source_bounds_xyz_m']]
regions=main['bounded_relative_plan_section_proposal']['proposed_keep_clear_test_regions']
approaches=[p[k] for p in proposals for k in ['sample_approach_xy_m','sample_public_approach_xy_m','sample_staff_approach_xy_m'] if k in p]
assert all(-6<=b['x'][0]<b['x'][1]<=6 and 0<=b['y'][0]<b['y'][1]<=12 and 0<=b['z'][0]<b['z'][1]<=8.25 for b in boxes)
assert not any(intersects(a,b) for i,a in enumerate(boxes) for b in boxes[i+1:])
assert not any(intersects(a,b) for a in boxes for b in regions)
assert all(-6<=a['x'][0]<a['x'][1]<=6 and 0<=a['y'][0]<a['y'][1]<=12 for a in approaches)
assert not any(intersects(a,b) for a in approaches for b in boxes+regions)
assert not any(intersects(a,b) for i,a in enumerate(approaches) for b in approaches[i+1:])
validation={
 'source_documents_hashed':len(sources),'all_relevant_extracted_archive_members_match':True,
 'source_images_pixel_inspected':True,'source_atlas_page_pixel_inspected':True,
 'atlas_larger_destinations':len(larger),'atlas_small_footprints':len(small),'explicit_small_ID_to_footprint_joins':len(labelled),
 'unmapped_small_ID_to_footprint_joins':100-len(labelled),'all110_footprints_match_prior_independent_extraction_within_0_002m':True,
 'all110_unique_coverage_rows_preserved_verbatim':len(exact_rows['rooms'])==110,'all100_unique_R_addresses_preserved':True,
 'R070_exact_label_main_plan_inset_and_coverage_agree':True,'R070_door_symbol_centers_match':True,
 'four_design_count':sum(p['counts_as_designs'] for p in proposals),
 'proposal_boxes_within_historical_outer_envelope':True,'proposal_boxes_do_not_intersect_one_another_or_proposed_central_bands':True,
 'four_proposed_approach_pads_inside_outer_envelope_and_clear_of_boxes_bands_each_other':True,
 'geometry_screen_is_host_fit':False,'unknown_actual_host_reservations_remain_null':True,
 'catalogue_runtime_source_edits_by_this_audit':False,'new_room_capacity_goods_compatibility_or_payment_behavior':False,
 'source_to_ship_transform_determinant':1,'new_dimensions_adjustable_proposals_only':True,
 'final_handoff_sha256':sha(OUT/'D09_retail_programme_reference_handoff.json')}
save('D09_audit_validation.json',validation)
save('SHA256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256.json'})
print(json.dumps(validation,indent=2))
