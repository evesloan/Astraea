from pathlib import Path
import hashlib
import json
import zipfile
from datetime import datetime, timezone

ROOT = Path('/workspace/scratch/375c2e438292')
AUDIT = ROOT / 'district-layout-audit'
OUT = AUDIT / 'd11-kit-handoff'
DOCS = AUDIT / 'extracted/project_docs'
COVERAGE = json.loads((DOCS / 'architecture/whole_ship_coverage.json').read_text())
ROOMS = {r['id']: r for r in COVERAGE['rooms']}
ARCHIVE = AUDIT / 'sources/Astraea_Master_Design_Source.zip'
ARCHIVE_ID = 'libfile_362451ac969c8191afbf823122078feb'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source(key, path, **extra):
    path = Path(path)
    return dict(key=key, absolute_path=str(path), workspace_relative_path=str(path.relative_to(ROOT)),
                filename=path.name, size_bytes=path.stat().st_size, sha256=sha(path), **extra)

sources = [
    source('theatre_image', ROOT / 'theater-catalogue-input/image(20261001-035518).png',
           library_file_id='libfile_cea1fdbbc9f88191b79316fc34b74282',
           file_id='file_00000000a5b481f6896ddc2f7fc82b25', library_version=0,
           dimensions_px=[1448,1086], pixel_inspected=True,
           supplied_sha256_matched=True, authority='Visual character and functional composition only; no measured seat, passage, tier or structural dimensions.'),
    source('theatre_image_identity', ROOT / 'theater-catalogue-input/reference_identity.json'),
    source('public_blueprint', AUDIT / 'sources/2.png',
           library_file_id='libfile_45f3a99c597c8191b5974a9e725331cd',
           dimensions_px=[1491,1055], pixel_inspected=True,
           identity_provenance='astraea-recovery-evidence/reference-inventory-check-20261002.json, recorded 2026-10-02T16:21:47Z; not a new Library metadata query',
           sheet='3 of 6 / ASW-GV-03 / Public Amenities + Entertainment + Retail',
           authority='Historical illustration; conflicting deck assignments, elevations, beam and other capacity figures do not override current canon.'),
    source('atlas', AUDIT / 'sources/Astraea-current-layout-atlas.pdf',
           library_file_id='libfile_b9125cc753a481919b12ded74d590b04',
           identity_provenance='district-layout-audit/d05-kit-handoff/D05_programme_reference_handoff.json; local hash freshly rechecked, no new Library metadata query',
           source_date='2026-10-01', page_one_based=13, pixel_inspected=True,
           authority='Historical allocation rectangles, door symbols and programme. Not final room interiors, door-pocket geometry or navigation certification.'),
    source('source_archive', ARCHIVE, library_file_id=ARCHIVE_ID,
           library_version=2,
           identity_provenance='district-layout-audit/d05-kit-handoff/D05_programme_reference_handoff.json and planning-package-v2/README.txt; archive hash freshly measured'),
]
with zipfile.ZipFile(ARCHIVE) as z:
    for key, member in [('auditoriums','project_docs/AUDITORIUMS.md'),
                        ('coverage','project_docs/architecture/whole_ship_coverage.json'),
                        ('ship_design','project_docs/SHIP_DESIGN.md'),
                        ('species','project_docs/SPECIES_CANON.md')]:
        path = AUDIT / 'extracted' / member
        assert hashlib.sha256(z.read(member)).hexdigest() == sha(path)
        sources.append(source(key, path, container_library_file_id=ARCHIVE_ID,
                              archive_member=member, archive_member_hash_matches=True,
                              authority='Dated documentary evidence; no restored runtime or current acceptance implied.'))

theatre = dict(
    stable_id='D11_grand_theater', name=ROOMS['D11_grand_theater']['name'],
    registered_capacity=2200, capacity_key='entertainment_capacity', seat_key='entertainment_seats',
    center_xyz_deck_local_m=[-76,0,-190], registered_size_width_depth_height_m=[84,150,22],
    registered_x_m=[-118,-34], registered_z_m=[-265,-115],
    main_entry_xyz_d11_local_m=[-34,0,-126],
    upper_entries_xyz_d11_local_m=[[-34,8.5,-126],[-34,14.5,-126]],
    nominal_aperture_m=5.2, aperture_note='Source says jambs reduce nominal aperture by about 0.22 m; no finished door pocket or mechanism drawing survives in these sources.',
    stage_width_m=36, clear_proscenium_height_m=16,
    tier_counts=[{'name':'Lantern Stalls','places':740,'floor_y_d11_local_m':0},
                 {'name':'First Gallery','places':740,'floor_y_d11_local_m':8.5},
                 {'name':'Crown Gallery','places':720,'floor_y_d11_local_m':14.5}],
    row_structure='Each full row has four blocks of ten chairs. Each of the two lower tiers also has a twenty-chair central row.',
    highest_seat_floor_y_d11_local_m=16.54,
    aliases=[{'id':'D12_theater_gallery','name':'Grand theater / First gallery','additional_places':0},
             {'id':'D13_theater_gallery','name':'Grand theater / Crown gallery','additional_places':0}],
    live_programme='A Thousand Small Worlds',
    live_programme_facts=['Mechanical orrery','Twelve suspended light-worlds','Proscenium curtains','Practical stage fixtures','Procedural moving constellation backdrop'],
    sources=['auditoriums:Capacity and geometry; Entry, care and circulation; Original performance and film program',
             'coverage:rooms[id=D11_grand_theater]; families[family_id=theater_access]', 'atlas:p13'])

titles = ['The Tide Remembers','A Map of Small Suns','The Patient Orchard','Letters from the Quiet Moon','The Last Lantern Home','Clouds Borrow the Sea']
programmes = ['Layered moving ocean-light ribbons','Slowly evolving stars and small luminous worlds','Growing stems and glowing canopies','A shaded moon and drifting paper forms','A breathing city of lit windows','Drifting, layered cloud currents']
cinemas = []
for n,(cz,title,programme) in enumerate(zip([-432,-280,-128,128,280,432],titles,programmes),1):
    cinemas.append(dict(stable_id=f'D11_cinema_{n}', name=ROOMS[f'D11_cinema_{n}']['name'],
                        registered_capacity=200, capacity_key='entertainment_capacity', seat_key='entertainment_seats',
                        center_xyz_deck_local_m=[36,0,cz], registered_size_width_depth_height_m=[50,72,8.25],
                        registered_x_m=[11,61], registered_z_m=[cz-36,cz+36],
                        main_entry_xyz_d11_local_m=[11,0,cz+25], nominal_aperture_m=4.8,
                        row_structure='Ten rows of twenty chairs, split into two ten-chair blocks.',
                        programme_title=title, programme_visual=programme,
                        programme_medium='Original locally generated real-time abstract shader short; not a licensed feature film.',
                        source='auditoriums:Capacity and geometry; Entry, care and circulation; Original performance and film program; coverage:rooms; atlas:p13',
                        bounds_derivation='X/Z bounds = documented center plus or minus half documented width/depth; independently agree with atlas p13 rectangle vectors.'))

ancillary_data = [
 ('D11_music',[-54,-8],[-384,-316],[-8,-350],2002,2003),
 ('D11_greenroom',[-98,-52],[-34,34],[-52,0],2005,2006),
 ('D11_arcade',[-54,-8],[182,250],[-8,216],2008,2009),
 ('D11_gallery',[-103,-57],[290,358],[-57,324],2011,2012),
 ('D11_listening',[-54,-8],[398,466],[-8,432],2014,2015),
 ('D11_service',[-98,-52],[46,114],[-52,80],2017,2018),
]
ancillary = []
for rid,x,z,door,rect_ix,door_ix in ancillary_data:
    r=ROOMS[rid]
    ancillary.append(dict(stable_id=rid,name=r['name'],historical_staff_only=r['staff_only'],
                          registered_entertainment_capacity=r['registered_capacity']['entertainment_capacity'],
                          historical_allocation_x_m=x,historical_allocation_z_m=z,
                          historical_door_symbol_xz_m=door,atlas_page_one_based=13,
                          atlas_rectangle_drawing_index_zero_based=rect_ix,
                          atlas_door_drawing_index_zero_based=door_ix,
                          source='coverage:rooms; atlas:p13, main-plan vectors and numbered directory',
                          limits='Allocation only; symbolic door center does not establish aperture width, pocket, swing or actual service connection.'))

data = {
 'schema':'astraea_d11_component_programme_reference_handoff_v1',
 'generated_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Bounded research handoff for four proposed theatre/cinema components after Batch15 durable gate. No catalogue edits, asset creation, placement assignment or new district plan.',
 'authority':'Latest explicit user canon and parent task direction override historical text and illustrative labels. Verified below means source content or source pixels checked, not current runtime validation.',
 'current_gate':{'batch15_status_from_parent':'Frozen and being backed up','this_audit_changes_gate':False,
                 'next_asset_work':'Only after the parent confirms the existing durable gate; this file is research readiness only.'},
 'current_runtime':{'expected_path':'/workspace/shared/space-hotel-full','path_exists_at_audit':False,
                    'historical_sources_are_restored_runtime':False,'integration_status':'pending'},
 'current_canon':{'decks':18,'guest_units':1000,'luxury_units_included_in_guest_total':81,
                  'passenger_hard_cap':2000,'crew_including_player_and_colleagues':400,
                  'player_home':'Shares an existing crew room; historical separate private-player-room text is superseded.',
                  'species':['Koblins','Mantelids','Humans','Baelins','Munkos','Mindos'],
                  'species_population_split':None,'new_accommodation_or_seat_counts_created':False,
                  'canon_source':'Parent task direction; SPECIES_CANON.md confirms current six identities and qualitative traits.'},
 'sources':sources,
 'historical_registry_and_capacity':{'registry_capture_utc':COVERAGE['scope']['inventory_snapshot_utc'],
     'theatre_places':2200,'cinema_count':6,'places_per_cinema':200,'total_entertainment_places':3400,
     'count_check':2200+6*200==3400,'theatre_tier_count_check':740+740+720==2200,
     'capacity_not_population':'Venue seat supply does not add passengers or crew and does not certify 3,400 simultaneous spectator agents or admissions.',
     'd10_meal_places_are_separate':True,'viewing_transfer_bays':'Use substitutes for a numbered place; never adds to admission limit.',
     'theatre':theatre,'cinemas':cinemas,'related_existing_d11_spaces':ancillary},
 'historical_section_and_routes':{
     'coordinate_system':'Metres, Y up. Documented room and anchor coordinates are deck-local. D11 world floor elevation is +69.5 m.',
     'world_floor_elevations_m':{'D11':69.5,'D12':78,'D13':84,'D14':88.5},
     'protected_void':'Existing theatre footprint crosses intermediate D12-D14 slabs/ceilings. Preserve the registered 84 x 150 m volume and upper entry dependencies; do not add new cuts.',
     'cinema_headroom':'8.25 m shell terminates below D12 floor at D11-local +8.5 m; screen, cornice, title and fixtures stay in that budget.',
     'boundary_notes':['Theatre walls/trim extend slightly outside the registration box.','Port service threshold reaches X -120 m and is clamped to the 240 m beam.','Upper east exterior threshold projects only 1.4 m past theatre wall; actual exterior landings/dependencies or deck transition belong to host.'],
     'cart_clearance_contract_m':3.4,
     'level_routes':['Theatre side aisles and upper side galleries provide documented cart clearance.','Lower foyer connects both sides ahead of stair enclosure.','Cinemas have rear foyers, level side circulation, raked middle/outer aisles and rear return ramps.','Cinema far-side crossing is behind the audience return ramps and ahead of projector booth.'],
     'theatre_gangway_rise_ratio':'Approximately 1:12.08; collision surfaces, not visual-only rotation.',
     'transverse_aisle_m':3,
     'stage_access_ramp_ratio':'1:12',
     'guards':'Outer rake guards protect drops onto adjacent level side galleries.',
     'stair':{'clear_flight_width_m':3.2,'half_flight_run_m':8,'maximum_riser_m':0.15,'form':'Separate switchback through all three levels; cutouts in upper rear gallery floors.'},
     'lift':{'landing_xyz_d11_local_m':[[-41.5,0,-126],[-41.5,8.5,-126],[-41.5,14.5,-126]],
             'car_base_center_xyz_d11_local_m':[-41.5,0,-121],'platform_size_xz_m':[5,5],
             'source_claim_speed_m_s':0.72,'source_claim_dwell_seconds':8,
             'source_claim_gate_behavior':'Fixed landing gates open only while stopped at that level.',
             'limits':'Historical implementation description. Current lift operation, load carrying, gate geometry, support and rider clearance remain unverified.'},
     'anchors':'Small sets of level foyer/side-aisle anchors; preserve height and room.center transforms. Do not route flat-floor generic crowds directly into elevated seats.',
     'routing_history':'AUDITORIUMS.md describes circulation_route(room,target) as an amenity helper, not a complete reserved-chair scheduler. Later coverage records actual-seat watching model evidence. Neither proves all-seat live physical routes.',
     'backstage_connection_unknown':'D11_service is a separate historical allocation at X -98..-52, Z +46..+114; it is not evidence of a contiguous stage-wing passage from the theatre at Z -265..-115.',
     'source':['auditoriums:Capacity and geometry; Entry, care and circulation; Integration contract','ship_design:Scale, elevations and circulation','coverage:families; unregistered_spatial_systems[system_id=theater_void_D11_D14]','atlas:p13']},
 'reference_visual_read':{
     'inspection_status':'Both supplied PNGs and rendered atlas page 13 were visually inspected by this audit.',
     'theatre_image_observations':[
         'Warm cream/ivory textured stone columns and broad arch/soffit surfaces; restrained gold/brass edge details.',
         'Saturated rust/orange curtains, recessed wall fields and upholstered curved audience rows.',
         'Stacked curved balcony fronts with slim transparent/open rail sections, shaped solid ends, planting and visible circulation behind.',
         'Tall, framed proscenium with layered curtains; planetary scenic composition and suspended warm light elements.',
         'Warm linear reveals at balcony/soffit edges, wall sconces and illuminated steps establish a hierarchy that leads to the stage.',
         'Foyer approach and balcony-lounge insets show usable public edges, seating, planting and staff/guest scale cues.',
         'Presentation uses visibly stylized pixel/dither-like texture; component silhouette, trim and lights need to remain readable at game scale.'
     ],
     'requirements_inferred_for_the_four_components':[
         'Carry a restrained shared theatre palette and readable curved/recessed architectural rhythm into public components.',
         'Keep useful light on route edges and at the working surface while preserving stage/screen emphasis.',
         'Give acoustic/display and backstage fixtures unmistakably different working forms; colour changes to generic care panels are insufficient.',
         'Treat the reference as a visual target to interpret within existing geometry, not as authority to rebuild the seating plan.'
     ],
     'illustrative_plan_traps':[
         'Reference legend names stage, orchestra, lower balcony, upper balcony, royal boxes and foyer access. These are image annotations, not extra registered rooms, tiers or numbered places.',
         'Do not replace the documented four-block numbered rows with an unverified radial layout merely because the illustration curves.',
         'Do not import reference columns, balcony depths, arches or decorative braces into clear aisles or structural voids without real support/sightline checks.',
         'No seat width/pitch, door mechanism, acoustic coefficient, material fire rating or species body dimensions can be measured reliably from this perspective illustration.'
     ],
     'public_blueprint_relevant_pixels':{'D11_panel':'Cinema Complex (6 theaters / 1,200 seats) and Grand Theater (2,200 seats).',
         'grand_theater_inset':'2,200 capacity, 3 levels, stage width 36 m and printed stage height 16 m; corroborates programme scale, not construction geometry.',
         'do_not_adopt':'Printed D11 +38.5 m elevation, 38 m width, adjacent public-deck assignments and other occupancy totals conflict with reconciled current ship canon.',
         'motifs':'Separated public/service route legend, multi-level performance volume, legible destinations and cultural/public adjacency.'},
     'atlas_visual_role':'Historical p13 shows a rectangular allocated theatre with lower-tier seat dots only; upper galleries are explicitly omitted. It is a location/capacity diagram, not the finished visual target.'},
 'four_proposed_component_roles':[
     {'component':'acoustic_programme_display_return','status':'Proposed role, not a placed or acoustically certified object',
      'function':'A shallow architectural return that presents venue/programme information toward the foyer and a ribbed or baffled acoustic-facing surface toward the auditorium.',
      'candidate_context':'Inside an existing theatre/cinema foyer or side-wall allocation after host geometry inspection; no assigned coordinate.',
      'form_direction':'A thickened return with separated recessed programme face, visible acoustic ribs/baffles, restrained brass edging and a low-glare warm reveal. Express two functional faces and a real wall/foot connection.',
      'critical_traps':['Must not thicken the 5.2/4.8 m nominal portal inward, occupy the door pocket or block a turn.','Keep display glow out of audience sightlines and avoid per-instance real lights.','Do not advertise unapproved showtimes or call visual baffles measured acoustic treatment.','A return does not create a new room, door, service access or capacity.'],
      'reference_basis':['theatre_image:layered stone/orange recesses and warm edge lighting','coverage:auditoriums threshold and original fixtures','auditoriums:original programme titles']},
     {'component':'usher_service_station','status':'Proposed public-facing station; no ticketing implementation claim',
      'function':'A compact identifiable staff point for wayfinding, programme handling and queue guidance at an existing foyer edge.',
      'candidate_context':'A supported level foyer/side-aisle edge outside protected arrival, turning, lift, stair and cinema crossover paths.',
      'form_direction':'A small counter/lectern with a clear working surface, integrated programme rack, modest task source, reachable public face and tidy staff storage; public finish rather than medical-cabinet language.',
      'critical_traps':['Queue footprint and staff approach are part of placement, not spare space inside a cart lane.','Reach heights and knees/limbs are unverified for all six species.','No assumed paid ticket transaction, new crew count, new room ID or extra spectator place.','D11_greenroom is historically public-tagged; a station does not silently make it staff-only.']},
     {'component':'adjustable_audience_seat_end_module','status':'Proposed reusable seat/end asset; actual adjustment mechanism and body acceptance pending',
      'function':'A low-complexity seat and row-end system that can be configured around existing numbered seat anchors and expose a readable aisle end.',
      'candidate_context':'Exactly one existing numbered place per seat. End pieces are attached furniture, not added admissions or reserve places.',
      'form_direction':'Economical contoured pad/back, explicit base/fixing support, restrained arm/end parts and configurable support clearances. Limit hidden geometry and repeated high-frequency details.',
      'critical_traps':['Do not move, merge, duplicate or renumber entertainment_seats; never write the meal-only seats key.','Keep rows, aisles, transfer substitutions, anchors, sightlines and rake floor contact; pitch/width and final collisions remain unknown.','No default Human fit can certify Munko four-arm clearance, Baelin cartilage support, Mantelid appendages, Koblin stature or Mindo hardware.','Do not add a scripted mechanism, light, high-poly text label or unique material for every one of 3,400 possible instances.','No trial fit in an isolated asset scene proves host crowd or rendering performance.']},
     {'component':'backstage_cue_work_light_stand','status':'Proposed distinct backstage working fixture; exact placement, wiring and cue integration pending',
      'function':'A shielded aimable work light with a small cue/work surface and controlled cable route for staff stage preparation.',
      'candidate_context':'A verified supported backstage/workshop position; named D11_service can host workshop intent but does not establish a direct stage-wing link.',
      'form_direction':'A stable base, slender post, visible hinge/yoke, hooded lamp, compact cue shelf and contained cable path. Practical cooler structure with a warm task pool distinguishes it from public carved returns and care panels.',
      'critical_traps':['Base, adjustment sweep and cable slack may not enter egress, curtain, prop, stage-ramp or cart paths.','Prevent audience glare; emissive appearance alone is not proven work illumination.','Support, stability and anchors are unverified; do not claim pressure-vessel or professional stage certification.','No inferred power outlet, wiring port, rigging load, cue protocol or new Mindo charging interface.']}
 ],
 'economical_seat_geometry_contract':{
     'population_of_potential_instances':3400,
     'proposal':['Author reusable linked meshes with a small shared material palette.','Separate stable seat body from optional row-end/marker parts; simplify unseen undersides and repeated trim.','Capture mesh triangles, vertices, material slots, mesh instances, bounds and export size for the prototype and configurable states.','Once counts exist, any 3,400-instance totals are arithmetic estimates only; measure in the restored main host before performance acceptance.','Use bounded host lighting and established static batching/streaming policies after owner inspection; avoid per-seat scripts and real lights by default.'],
     'numeric_triangle_budget':None,'engine_performance_result':None,'current_source_basis':'AUDITORIUMS.md historical shared meshes/static batching; SHIP_DESIGN.md bounded rendering and light budget. Not verification of the absent host.'},
 'known_unknowns':[
     'Current finished wall, floor, ceiling and balcony polygons; actual revision and host scene ownership.',
     'Door leaf, pocket, swing/slide travel, jamb construction, portal screens and as-finished clear width after component installation.',
     'Actual support and fixing surfaces, fasteners, attachment loads, stability, cable channels and electrical interfaces.',
     'Every numbered seat transform, row pitch, available width, visible-stage sightline and seated animation envelope in current host.',
     'Six canonical body dimensions, support needs and interactions; Baelin cartilage support and Munko four-arm clearance are explicit unresolved requirements.',
     'Finished six-species rigs, Mantelid cocoon/molt contact states and cleaning presentation; no legacy eight-rig test accepts them.',
     'All-seat route traversal, real audience arrival/exit waves, interrupted journeys, reservations/release in current host and live crowd performance.',
     'Actual upper-gallery exterior landings/dependencies, loaded-cart lift riding, moving gate contact and cross-deck rendering.',
     'The real backstage-to-stage service journey and individual staff task animation; a room name is not a verified connection.',
     'Acoustic performance, show schedules, lamp photometry, glare, actual light-budget use and user visual acceptance.'
 ],
 'historical_test_evidence_boundaries':{
     'source_claims':['AUDITORIUMS.md reports Godot 4.6.3 focused compilation, seven venues, 3,400 unique anchors, tier counts and 28 door-to-amenity paths.','AUDITORIUMS.md reports integrated D11 static player/cart query-shape entrance/turning and 28 care-route sweeps, not live cart driving/lift riding.','Coverage adds bounded audience model evidence, actual-seat watching/release and D12/D13 alias sharing; 40 visible actors is expressly not a full audience.'],
     'cart_query_shape_historical_m':[1.14,1.4,0.77],
     'not_reproduced_now':True,
     'new_component_acceptance':False,
     'current_host_integration':'pending','current_six_species_fit':'pending','current_crowd_performance':'pending'},
 'next_bounded_acceptance':[
     'Parent confirms Batch15 durable backup gate before any asset production.',
     'Review the four distinct unplaced component silhouettes and labelled intended working/support faces against these actual supplied pixels.',
     'Measure prototype mesh/export counts and adjustable bounds; preserve no-new-capacity and no-host-fit claims.',
     'When current host is available, inspect ownership, stable anchors, finished geometry, door pockets, support and paths before assigning positions.',
     'Then run only affected host route/turn, rake contact, sightline, six-species contact, lighting and repeat-instance performance checks; obtain user visual acceptance.'
 ],
 'audit_validation':{
     'source_documents_read':True,'both_reference_images_pixel_inspected':True,'atlas_page13_pixel_inspected':True,
     'archive_members_match_extracted_documents':True,'theatre_sha_matches_parent':True,
     'ids_exist_in_historical_coverage':True,'seat_arithmetic_preserved':True,
     'catalogue_modified':False,'assets_created':False,'new_layout_proposed':False,
     'inspection_png_is_source_render_only':'historical-atlas-page13-inspection.png'
 }
}

assert sha(ROOT/'theater-catalogue-input/image(20261001-035518).png') == '4f1d548bc85cd48e73a2375a6badccc5810d10021713e86212ea6127595e56f4'
assert sum(r['registered_capacity'] for r in cinemas)+theatre['registered_capacity'] == 3400
assert all(r['stable_id'] in ROOMS for r in [theatre,*cinemas,*ancillary])
assert all(ROOMS[r['stable_id']]['registered_capacity']['entertainment_capacity']==r['registered_capacity'] for r in [theatre,*cinemas])
assert len(data['four_proposed_component_roles'])==4
OUT.mkdir(exist_ok=True)
result=OUT/'D11_programme_reference_handoff.json'
result.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
json.loads(result.read_text())
(OUT/'SHA256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='SHA256.json'},indent=2)+'\n')
print(json.dumps({'handoff':str(result),'sha256':sha(result),'bytes':result.stat().st_size,'venues':7,'entertainment_places':3400,'components':4,'runtime_path_exists':False},indent=2))
