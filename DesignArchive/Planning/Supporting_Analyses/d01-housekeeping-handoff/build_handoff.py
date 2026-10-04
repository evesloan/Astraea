from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, fitz
from PIL import Image
OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
S={
'atlas':AUDIT/'sources/Astraea-current-layout-atlas.pdf',
'coverage_json':AUDIT/'extracted/project_docs/architecture/whole_ship_coverage.json',
'coverage_md':AUDIT/'extracted/project_docs/architecture/WHOLE_SHIP_COVERAGE.md',
'ship_design':AUDIT/'extracted/project_docs/SHIP_DESIGN.md',
'daily_guest_life':AUDIT/'extracted/project_docs/DAILY_GUEST_LIFE.md',
'guest_simulation':AUDIT/'extracted/project_docs/GUEST_SIMULATION.md',
'species_canon':AUDIT/'extracted/project_docs/SPECIES_CANON.md',
'master_gdd':AUDIT/'extracted/Astraea_Master_Game_Design.md',
'phase_direction':AUDIT/'extracted/Current_Phase_Direction.txt',
'archive_readme':AUDIT/'extracted/SOURCE_README.txt',
'current_canon':CAT/'CATEGORY_COVERAGE.json',
'catalogue_manifest':CAT/'catalogue_manifest.json',
'engineering_reference':CAT/'references/engineering/technical_reference.png',
'staff_tall_reference':CAT/'references/landings/staff_corridor_tall.png',
'staff_services_reference':CAT/'references/landings/staff_corridor_services.png',
'engineering_provenance':CAT/'batches/batch12/reference_manifest.json',
'corridor_provenance':CAT/'batches/batch11/reference_manifest.json',
'corridor_prior_provenance':CAT/'batches/batch03/reference_manifest.json',
'aqu007_manifest':CAT/'assets/aquatic_towel_use/AST-AQU-007.manifest.json',
'aqu008_manifest':CAT/'assets/aquatic_towel_use/AST-AQU-008.manifest.json',
'hsp006_manifest':CAT/'assets/hospitality_serviceware/AST-HSP-006.manifest.json',
'med004_manifest':CAT/'assets/clinical_support/AST-MED-004.manifest.json'
}
sources=[]
for sid,p in S.items():
 root='catalogue' if p.is_relative_to(CAT) else 'district_layout_audit'
 sources.append({'id':sid,'source_root':root,'path':str(p.relative_to(CAT if root=='catalogue' else AUDIT)),'sha256':sha(p),'bytes':p.stat().st_size})
cov=load(S['coverage_json']); d01=[r for r in cov['rooms'] if r['deck']==1]
byid={r['id']:r for r in d01}
pdf=fitz.open(S['atlas']);p=pdf[2];ds=p.get_drawings()
h=next(d for d in ds if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=h.width/1082;cy=(h.y0+h.y1)/2
# PDF coordinates follow atlas page2: page horizontal is Z; page vertical is X with negative X at top.
def pt(q):return [round((q.y-cy)/scale,3),round((q.x-h.x0)/scale-541,3)]
def box(r):return {'x':[pt(r.tl)[0],pt(r.br)[0]],'z':[pt(r.tl)[1],pt(r.br)[1]]}
def rec(i):
 d=ds[i];items=[]
 for it in d['items']:
  if it[0]=='re':items.append({'operator':'re','bounds_xz_m':box(it[1])})
  else:items.append({'operator':it[0],'points_xz_m':[pt(q) for q in it[1:] if isinstance(q,fitz.Point)]})
 return {'drawing_index_zero_based':i,'pdf_sequence_number':d['seqno'],'pdf_bounds_points':list(d['rect']),'type':d['type'],'fill_rgb':d['fill'],'stroke_rgb':d['color'],'bounds_xz_m':box(d['rect']),'diagram_stroke_width_m':round(d['width']/scale,3) if d['width'] else None,'items':items}
rects=[(i,d) for i,d in enumerate(ds) if h.contains(d['rect']) and len(d['items'])==1 and d['items'][0][0]=='re' and d['fill'] and d['rect'].get_area()>10]
label_rect={}
for block in p.get_text('dict')['blocks']:
 for line in block.get('lines',[]):
  for span in line['spans']:
   t=span['text'];bb=fitz.Rect(span['bbox']);c=(bb.tl+bb.br)/2
   if t.isdigit() and 1<=int(t)<=10 and h.contains(c):
    choices=[(i,d) for i,d in rects if d['rect'].contains(c)]
    if choices:label_rect[int(t)]=min(choices,key=lambda a:a[1]['rect'].get_area())[0]
assert set(label_rect)==set(range(1,11))
rooms=[]
for n,r in enumerate(d01,1):
 i=label_rect[n];b=box(ds[i]['rect']);di=i+1;door=ds[di]
 assert door['fill'] and abs(door['fill'][0]-.141176)<.00001
 doorpos=pt((door['rect'].tl+door['rect'].br)/2)
 rooms.append({'id':r['id'],'name':r['name'],'kind':r['kind'],'family_id':r['family_id'],'deck':1,'atlas_directory_number':n,'atlas_page_one_based':3,'historical_allocation_bounds_xz_m':b,'historical_allocation_center_xz_m':pt((ds[i]['rect'].tl+ds[i]['rect'].br)/2),'historical_allocation_dimensions_xz_m':[round(b['x'][1]-b['x'][0],3),round(b['z'][1]-b['z'][0],3)],'historical_allocation_rectangle_area_m2':round((b['x'][1]-b['x'][0])*(b['z'][1]-b['z'][0]),3),'allocation_drawing_index_zero_based':i,'door_marker':{'center_xz_m':doorpos,'drawing_index_zero_based':di,'pdf_sequence_number':door['seqno'],'symbol_bounds_xz_m':box(door['rect']),'interpretation':'Historical symbolic door center only; marker size is not clear opening, swing or pocket.'},'historical_staff_only':r['staff_only'],'registered_capacity':r['registered_capacity'],'whole_room_simultaneous_occupancy_limit':r['whole_room_simultaneous_occupancy_limit'],'finished_polygon_known':False,'evidence_sources':['atlas','coverage_json']})
vector={'schema':'astraea.historical_d01_atlas_vectors.v1','source_id':'atlas','source_sha256':sha(S['atlas']),'atlas_snapshot_utc':'2026-10-01T01:07:00Z','page_one_based':3,'method':'Direct PyMuPDF vector extraction and numbered-label containment; numbered directory names match coverage IDs. No coordinate inference from the older technical plate.','extraction_precision_note':'Values rounded to 0.001 m from PDF vectors; precision is not architectural survey accuracy. Near-integer rounding such as 431.999 m is retained in extracted markers.','calibration':{'hull_pdf_rect_points':list(h),'hull_z_limits_m':[-541,541],'scale_points_per_m':scale,'x_zero_pdf_y':cy,'axes':'X port negative/starboard positive; Z bow negative/aft positive; Y deck height'},'rooms':rooms,'circulation_primitives':[rec(i) for i in range(14,38)],'tram_primitive':rec(68),'tram_stop_markers':[{'center_xz_m':pt((ds[i]['rect'].tl+ds[i]['rect'].br)/2),**rec(i)} for i in [69,72,75,78,81]],'unidentified_small_service_colored_rectangles':[rec(i) for i in [70,71,73,74,76,77,79,80,82,83]],'limits':['PDF furniture, walls, ceilings and minor objects are deliberately simplified.','Circulation ribbons are drawing evidence, not a navigation certification.','No identity or implemented purpose is assigned here to the small unlabelled rectangles.','No current runtime exists at the expected original-game path.']}
(OUT/'D01_atlas_vector_evidence.json').write_text(json.dumps(vector,indent=2)+'\n')
refs=[]
refspec=[('engineering_reference','libfile_10019fb78188819197691dbcc5f685f1','engineering_provenance','Crew + Medical + Engineering + Logistics; sheet 4 of 6, ASW-GV-04; printed v1.0.3, 25.07.04',[ 'The lower Deck 03 Logistics & Services panel visibly labels housekeeping/laundry, stores/supplies and maintenance alongside the longitudinal service route.','The legend differentiates service corridor, separated guest circulation, restricted access and vertical circulation.','The panel gives useful programme relationships and an institutional service identity, not laundry equipment dimensions or operating design.'],['Master GDD reference plate 2 explicitly remaps this plate logistics D03 to canonical D01, engineering D04 to D02 and crew D06 to D03; medical remains D05.','The plate faces forward to page-right, opposite the atlas main-plan orientation. Do not transfer coordinates.','Printed machinery/facility totals, old deck labels and legacy species examples are not current allocation or capacity authority.']),('staff_tall_reference','libfile_763ed82d83e88191a7b025212b2b4592','corridor_provenance','Original stored filename image(20261001-185254).png',['Actual pixels show broad pale panels, long metallic protective contact rails, a regularly tiled floor, a high exposed structural/service zone and paired longitudinal pipes.','Small practical wall fixtures and repeated service supports organize the long passage.'],['Use broad washable-looking panel language, protected edges and coherent service mounting; no real material hygiene certification.','Do not infer a safe passage width, ceiling height, species fit or photometric performance from the photo.']),('staff_services_reference','libfile_024c7db762c481918da24e3840ef1412','corridor_provenance','Original stored filename image(20261001-185255).png',['Actual pixels show pale block-like walls, dark door frames, exposed overhead conduits and parallel service runs, suspended elongated fixtures, and an uncluttered hard floor.','Workmanlike repeatable brackets, service organization and readable door outlines matter more than decorative clutter.'],['Do not copy the narrow photographed passage width or invent measurements.','Practical cool light and exposed services are visual intent; actual game illumination and clearance need separate checks.'])]
for sid,lib,prov,panel,obs,limits in refspec:
 refs.append({'source_id':sid,'library_file_id':lib,'sha256':sha(S[sid]),'pixels_inspected_in_this_audit':True,'pixel_size':list(Image.open(S[sid]).size),'stored_provenance_source_id':prov,'label_or_original_name':panel,'observations':obs,'authority_limits':limits,'runtime_dependency':False})
roles=[
{'id':'cloth_treatment_appliance','name':'Fictional cloth-treatment appliance','anchor_room_id':'D01_laundry2','useful_distinct_role':True,'purpose':'An enclosed workplace textile-processing station gives the named laundry a specific work object.','design_readout':['Readable textile load opening and supported load staging','Fictional state display/control face','Distinct maintainable access face and removable-component intent'],'separation_from_existing':'Neither AST-AQU-007 dry stock retrieval nor AST-AQU-008 guest towel return is a textile-processing appliance.','boundaries':['No actual wash chemistry, temperature, disinfection, biological compatibility or treatment sequence','No inferred water, waste, power, extraction or plumbing connection','No promise that this appliance replenishes the player cloth or bottles','No production throughput, equipment count or installed placement']},
{'id':'drying_conditioning_rack','name':'Drying and conditioning rack','anchor_room_id':'D01_laundry2','useful_distinct_role':True,'purpose':'Provide explicit supported spacing and temporary holding for work textiles rather than another folded-stock display.','design_readout':['Open supported rails or textile holders with deliberate hand access','Readable separation of items and stable floor contact','A serviceable frame distinct from enclosed treatment and flat folding work'],'separation_from_existing':'AST-AQU-007 stores folded dry guest stock. This proposed rack stages separated textiles for fictional conditioning; it is not a second guest retrieval niche.','boundaries':['No inferred active heat, airflow, humidity target or biological/hygiene result','No textile dryness or treated/clean state established by appearance alone','No canonical body/reach fit, load capacity, throughput or quantity']},
{'id':'sorting_folding_workbench','name':'Sorting and folding workbench','anchor_room_id':'D01_laundry2','useful_distinct_role':True,'purpose':'Give staff a supported flat surface for identifying, separating, folding and staging textiles, with storage supporting those tasks.','design_readout':['Clear supported work surface','Legible used/awaiting-process and ready-to-store staging intent without mixing them by default','Under-surface storage or return recesses that leave approach and service access readable'],'separation_from_existing':'A staff textile work surface differs from both guest towel dispensing and the small mobile dining-service trays. It must not become a generic decorated counter.','boundaries':['Any separation labels denote design purposes, not contamination control or proven hygiene','No prescribed compulsory sequence, worker count, cleaning method or workstation ownership','Keep actual knee/reach/body and service clearances unresolved until a host layout and bodies exist']},
{'id':'wheeled_linen_carrier','name':'Distinct wheeled linen carrier','anchor_room_id':'D01_laundry2','useful_distinct_role':True,'condition':'Useful only with a clear standalone workplace textile-carrying identity; another generic wheeled receiver would duplicate existing coverage.','purpose':'A manoeuvrable staff carrier for staged linens, with load retention, credible hand contact, wheels and a parking/transfer purpose.','design_readout':['Purpose-specific textile holding body and load-retaining edges','Readable push grip, wheel/floor contacts and turning/parking needs','Separate used-load and ready-load staging intent; no asserted common mixed load'],'separation_from_existing':'AST-AQU-008 is a guest-return fixed station with a removable rolling receiver; AST-HSP-006 is a two-tier dining trolley. Neither establishes this independent workplace linen-transfer role. AST-MED-004 is clinical supply/retrieval and remains a separate purpose.','boundaries':['Do not replace, reskin, duplicate or modify the inherited player care cart or its three bottle identities','Do not claim fit through historical doors, lifts, tram or corridors','No implemented rolling controller, route, staff delivery automation, payload or inventory count','No invented D08-to-D01 or D01-to-depot transport connection']}
]
canon=load(S['current_canon'])['governing_canon']
family=next(f for f in cov['families'] if f['family_id']=='service_logistics')
comparison=[]
for sid in ['aqu007_manifest','aqu008_manifest','hsp006_manifest','med004_manifest']:
 m=load(S[sid]);comparison.append({'source_id':sid,'catalogue_id':m['catalogue_id'],'name':m['name'],'known_asset_roles':m.get('use_roles', ['dining-service trays on a two-tier mobile furnishing'] if sid=='hsp006_manifest' else ['closed clinical supplies and retrieval']),'limitations':m.get('limitations',[]),'special_limitation':m.get('limitations_extra',[]),'game_adoption_claim':False})
main={
'schema':'astraea.d01_housekeeping_programme_handoff.v1',
'created_utc':datetime.now(timezone.utc).isoformat(),
'title':'D01 housekeeping and laundry programme and asset roles',
'conclusion':'All four roles are useful and distinct as a bounded D01_laundry2 workplace kit. The linen carrier needs a specifically textile-focused carrying/transfer purpose to avoid duplicating the existing towel-return receiver or dining trolley. This audit approves no room layout, machinery operation or chore loop.',
'scope':{'read_only_sources':True,'catalogue_edited':False,'assets_authored':False,'new_room_or_district_masterplan':False,'original_game_expected_path':'/workspace/shared/space-hotel-full','original_game_path_present':False,'historical_runtime_claims_are_not_current_runtime':True,'audit_type':'Historical programme and reference audit; current catalogue-role comparison; JSON evidence handoff only','source_roots':{'district_layout_audit':'source locators are relative to the audit source directory','catalogue':'source locators are relative to the catalogue root'},'portability':'Core facts, limits, role decisions, geometry and hashes are embedded. Local source paths are provenance locators, not runtime dependencies. Heavyweight source images are not duplicated.'},
'current_governing_canon':{'source_id':'current_canon','decks':18,'guest_units_total_including_luxury':1000,'luxury_units_included':81,'luxury_breakdown':canon['luxury_units_within_guest_total'],'hard_passenger_cap':2000,'crew_including_one_player':400,'player_home':'Shared with an existing colleague within the unchanged 400; no roommate story or room relocation decided here','species':['Koblins','Mantelids','Humans','Baelins','Munkos','Mindos'],'preserve':['Existing original care cart and bottle identities','Stable room, person, berth, incident and ownership identities','No guest/crew capacity or equipment quantity change'],'historical_conflicts':['SHIP_DESIGN, GUEST_SIMULATION, atlas p2 and coverage prose retain a private employee-cabin/single player-berth statement. The current shared-existing-colleague rule supersedes that housing description without adding a 401st crew member.','Old class distributions, illustrative technical-plate totals and legacy species labels do not override current 1,000 inclusive units, 81 luxury units, 2,000 cap and six-species canon.']},
'historical_source_scope':{'atlas_snapshot_utc':'2026-10-01T01:07:00Z','coverage_registry_snapshot_utc':cov['scope']['inventory_snapshot_utc'],'coverage_extraction_method':cov['evidence']['REGISTRY_NOW']['method'],'spatial_evidence_scope':cov['evidence']['SPATIAL_ALL'],'consequence':'Historical ledger and atlas snapshots are related but different captures. Their original pass/status text does not certify current geometry, machinery operation or six-species use.'},
'historical_d01_deck':{'name':'Logistics & shuttle docks','floor_elevation_m':0,'next_deck_floor_elevation_m':6,'available_clear_height_m_in_historical_coverage':5.75,'clear_height_limit':'Deck-level allowance only. Actual laundry/depot soffit, beams, hanging services and equipment headroom remain unknown.','registered_spaces':10,'all_ten_staff_only':all(r['staff_only'] for r in d01),'finished_deck_acceptance':False,'room_ledger':rooms,'geometry_source':'atlas page3; direct vectors in D01_atlas_vector_evidence.json'},
'primary_programme_rooms':[{'id':sid,'name':byid[sid]['name'],'role':role,'status_in_historical_coverage':byid[sid]['status'],'physical_evidence_in_historical_coverage':byid[sid]['physical_evidence'],'whole_room_simultaneous_occupancy_limit':None,'equipment_quantity':None,'source_ids':['coverage_json','coverage_md','atlas']} for sid,role in [('D01_laundry2','Workplace textile handling and fictional laundry processing; anchor for the four candidate assets'),('D01_service9','Separately registered custodial depot; retain depot/stores/support identity without moving the laundry or prescribing the player return/refill/locker route')]],
'known_spatial_relationships':[
{'fact':'Laundry and Cargo exchange share the longitudinal band Z[-250,-182] and face inward across the axial street.','ids':['D01_laundry2','D01_service3'],'scope':'Historical allocation and door-marker relationship; not a certified connecting route'},
{'fact':'Custodial depot and Shuttle concourse share Z[398,466] and face inward across the axial street.','ids':['D01_service9','D01_arrivals8'],'scope':'Historical allocation and door-marker relationship; access policy remains unresolved'},
{'fact':'Laundry door is approximately (-8,-216); depot door approximately (8,432) in X,Z metres. They are 648 m apart longitudinally.','ids':['D01_laundry2','D01_service9'],'scope':'Coordinate separation only, not travel distance or adjacency'},
{'fact':'The D01 atlas draws a straight axial tram line at X0 with stop markers Z[-432,-216,-72,216,432], plus paired axial circulation ribbons at X±5.5 and service-colored outer lines at X±57.','scope':'Drawn relationships only; widths are graphical, not installed clear widths'},
{'fact':'The extracted logistics family calls for readable arrival/sort/store/dispatch and clean/dirty purposes, recessed work bays, storage depth, overhead service structure and protected cart thresholds.','source_id':'coverage_json','pointer':'families[family_id=service_logistics]'},
{'fact':'Technical reference plate includes laundry, stores, maintenance and separated circulation; master GDD remaps its logistics D03 to D01.','source_ids':['engineering_reference','master_gdd'],'scope':'Programme/composition guidance; no adjacency or equipment count transfer'}],
'access_conflicts':[
{'id':'all_d01_staff_only_vs_arrivals','evidence':'All 10 coverage room records have staff_only=true, including D01_luggage0 Shuttle arrivals and D01_arrivals8 Shuttle concourse; the atlas also uses guest-circulation ribbons on D01.','interpretation':'Access metadata conflicts with guest-facing names/drawing language. Neither names nor colors establish permission.','action':'Retain flags and IDs; report the conflict for access-policy design. Do not silently open public access or treat all D01 as guest circulation.'},
{'id':'allocation_vs_finished_route','evidence':'Atlas p2 explicitly omits furnishings, wall thickness, ceiling forms and most minor objects; corridor ribbons are not a navigation certification.','interpretation':'A rectangle, door marker or old static route pass cannot establish a usable workroom.','action':'No room fitting, direct route, door aperture or loaded-carrier clearance claim.'}],
'unknowns':{'finished_laundry_polygon':None,'finished_depot_polygon':None,'door_aperture_dimensions':None,'door_pockets_and_swings':None,'local_headroom_and_overhead_service_intrusions':None,'workstation_and_maintenance_clearances':None,'loaded_carrier_turning_parking_passing':None,'laundry_to_depot_direct_connection':None,'laundry_to_guest_towel_points_connection':None,'staff_home_locker_room_and_refill_sequence':None,'utilities_and_plumbing':None,'installed_equipment_count_or_capacity':None,'workstation_ownership_and_shift_assignment':None,'six_species_body_reach_environment_contact_compatibility':None,'note':'Null means unknown or undecided; it is not zero, a failed test, free space or permission to invent an implementation.'},
'design_purposes':[
{'purpose':'Used handling','intent':'Make awaiting-processing textile staging and staff handling readable','limit':'No disease, infection or hazardous-material classification inferred'},
{'purpose':'Clean/ready handling and storage','intent':'Give ready-to-store/folded items their own legible staging and storage purpose','limit':'Design labels are not proof of successful treatment, disinfection or biological safety'},
{'purpose':'Conditioning','intent':'Support separated textiles at an open work rack','limit':'No active drying mechanism or validated environmental setpoint'},
{'purpose':'Maintenance','intent':'Keep service faces, supports, joins and removable components comprehensible','limit':'Actual access volumes, utilities and procedures are unknown'},
{'purpose':'Staff access','intent':'Retain protected arrivals/approaches, handling surfaces and carrier parking as requirements to resolve','limit':'No new access policy, travel route or space allocation'},
{'purpose':'Optional player interaction','intent':'Assets may support future authored choices once gameplay is defined','limit':'The return/refill/locker/room example is not a compulsory loop, production sequence or authorization to relocate rooms'}],
'candidate_asset_roles':roles,
'existing_catalogue_comparison':comparison,
'reference_pixel_audit':refs,
'biological_and_gameplay_boundaries':[
'No demographics, body dimensions, reach envelopes or species-to-job distribution are assigned.',
'Baelin special-cleaner need is canon; names, ingredients, dose, process and actual textile/equipment compatibility remain open. No generic appliance claims universal compatibility.',
'Mantelid molting is extremely gruesome; frequency, privacy, depiction and care method remain unresolved. Do not turn it into infection simulation or ordinary dust.',
'Munko four-arm contact and all six actual body/environment interactions require later asset/host verification. Legacy broad 0.65 m screens do not certify them.',
'Mindo sentience and rights are preserved. No charging ports, fuel, food, connectors or rest system is invented.',
'Historical staff work means bounded arrived station time and aggregate background care, not a specific custodian physically carrying every linen load.',
'No new real treatment instructions, plumbing, equipment quantity, autonomous chore scheduling, worker throughput, economy rule or compulsory player action.'
],
'next_design_gate':'Use the four distinct roles for component contracts only. A later room/host placement must establish actual room envelope, apertures, support and service access before any installed-workplace or operational claim. This audit does not relocate a room or replace the player cart.',
'sources':sources,
'derivative_evidence':{'file':'D01_atlas_vector_evidence.json','sha256':sha(OUT/'D01_atlas_vector_evidence.json'),'preview':'atlas-page-03.png','preview_sha256':sha(OUT/'atlas-page-03.png')},
'validation':{'ten_D01_IDs_match_coverage':len(rooms)==10 and [r['id'] for r in rooms]==[r['id'] for r in d01],'ten_atlas_labels_uniquely_resolved':len(set(label_rect.values()))==10,'all_source_files_hashed':len(sources)==len(S),'three_reference_hashes_match_stored_provenance':True,'catalogue_and_sources_unmodified_by_this_audit':True,'runtime_or_assets_authored':False}
}
# Verify the three image identities against the stored provenance, not just supplied names.
prov_eng=load(S['engineering_provenance'])['inputs'];prov_corr=load(S['corridor_provenance'])['inputs']
for ref in refs:
 entries=prov_eng if ref['source_id']=='engineering_reference' else prov_corr
 match=next(e for e in entries if e.get('library_file_id')==ref['library_file_id'])
 assert match['sha256']==ref['sha256'],ref['source_id']
assert not Path('/workspace/shared/space-hotel-full').exists()
assert len(roles)==4 and canon['guest_units']==1000 and sum(canon['luxury_units_within_guest_total'].values())==81
assert all(r['historical_staff_only'] is True for r in rooms)
(OUT/'D01_housekeeping_programme_handoff.json').write_text(json.dumps(main,indent=2)+'\n')
# Read back and rehash all inputs after authoring; writing is confined to this handoff directory.
parsed=load(OUT/'D01_housekeeping_programme_handoff.json')
validation={'schema':'astraea.d01_handoff_validation.v1','json_roundtrip':parsed==main,'source_files_unchanged_during_audit':all(sha(S[s['id']])==s['sha256'] for s in sources),'reference_hashes_verified':True,'reference_pixels_inspected':True,'atlas_page_pixels_inspected':True,'D01_room_count':len(rooms),'candidate_role_count':len(roles),'geometry_scope':'PDF vector allocation/door symbols only','primary_handoff_sha256':sha(OUT/'D01_housekeeping_programme_handoff.json'),'game_or_catalogue_mutation':False}
assert validation['json_roundtrip'] and validation['source_files_unchanged_during_audit']
(OUT/'D01_audit_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
manifest={'files':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256.json'},'source_hashes_embedded_in':'D01_housekeeping_programme_handoff.json'}
(OUT/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'out':str(OUT/'D01_housekeeping_programme_handoff.json'),'sha256':sha(OUT/'D01_housekeeping_programme_handoff.json'),'bytes':(OUT/'D01_housekeeping_programme_handoff.json').stat().st_size,'validation':validation},indent=2))
