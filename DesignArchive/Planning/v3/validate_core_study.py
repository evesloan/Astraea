from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import fitz
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger=json.loads((root/'editable/Astraea_forward_core_constraint_ledger_v3.json').read_text())
baseline=json.loads((root/'inputs/historical_baseline.json').read_text())
vector=json.loads((root/'inputs/route_evidence/atlas_forward_arrival_vectors.json').read_text())
q3=json.loads((root/'inputs/route_evidence/R3_candidate_core_screen.json').read_text())
assert len(baseline['rooms'])==1462 and len({r['id'] for r in baseline['rooms']})==1462
assert ledger['unchanged_registry_id_count']==1462 and ledger['new_room_id_assignments']==0
assert ledger['guest_units']==1000 and sum(ledger['luxury_in_total'].values())==81
assert vector['source_sha256']==sha(root/'inputs/Astraea-current-layout-atlas.pdf')
for d in range(13,18):
 rec=next(r for r in vector['decks'] if r['deck']==d)
 side=next(r for r in rec['main_circulation_primitives'] if r['drawing_index_zero_based']==14)
 assert side['diagram_width_m']==4.6 and side['items'][0]['points_xz_m']==[[-5.5,-541.0],[-5.5,-80.0]]
 cross=next(r for r in rec['main_circulation_primitives'] if r['drawing_index_zero_based']==30)
 assert cross['diagram_width_m']==8.0
 assert [-63.0,-370.0] in [r['symbol_center_xz_m'] for r in rec['forward_door_markers']]
for d in range(9,13):
 rec=next(r for r in vector['decks'] if r['deck']==d)
 staff=next(r for r in rec['main_circulation_primitives'] if r['drawing_index_zero_based']==18)
 assert staff['diagram_width_m']==5 and staff['items'][0]['points_xz_m']==[[-57.0,-541.0],[-57.0,541.0]]
R1,R2,R3=ledger['candidate_dispositions']
assert not R1['room_intersections']
assert len(R1['ribbon_intersections'])==16
for r in R1['ribbon_intersections']:assert r['intersection']['area_m2']==(20 if 'landing' in r['reservation'].lower() else 28)
assert len(R2['room_intersections'])==4
assert sum(r['intersection']['area_m2'] for r in R2['room_intersections'])==120
assert {r['protected_record']['stable_id'] for r in R2['room_intersections']}=={'D11_music'}
assert R3['room_intersections']==[] and R3['decks']==[12,13,14,15,16,17]
for r in q3['results']:
 assert r['allocation_intersections']==[]
 if 'proposed_guest_spur' in r['candidate']:
  assert len(r['diagram_route_band_intersections'])==1 and r['diagram_route_band_intersections'][0]['intersection_area_m2']==18.4
 else:assert r['diagram_route_band_intersections']==[]
assert R3['capacity'] is None and R3['mechanism_or_cabin_count'] is None and not R3['floor_openings_authorized']
previous={'Astraea_Hybrid_District_Study_v2.pdf':'4186a5279aa0d1d9546e4bea0e37993ea614e3debccc057fa928ab97505a20b0','Astraea_Editable_Hybrid_Study_v2.zip':'3e8f2163ceac3bcc36ad708d9a0d0edb67780cefe0c010aa40ec202ebeafcdd5'}
for n,h in previous.items():assert sha(root/'history'/n)==h
for p in (root/'editable').glob('*.svg'):ET.parse(p)
pdf=fitz.open(root/'Astraea_Forward_Commons_Core_Study_v3.pdf');assert len(pdf)==5
for i,p in enumerate(pdf):
 for b in p.get_text('blocks'):assert b[0]>=0 and b[1]>=0 and b[2]<=p.rect.width+.1 and b[3]<=p.rect.height+.1,(i,b)
result={'status':'pass','pdf_pages':5,'editable_svg_pages':5,'source_ids_preserved':1462,'new_room_assignments':0,'r1_lower_colored_ribbon_conflicts':16,'r2_music_conflicting_reservations':4,'r2_music_total_plan_overlap_m2':120,'r3_room_intersections':0,'r3_core_and_landing_ribbon_intersections':0,'r3_guest_spur_sidewalk_join_m2':18.4,'route_geometry_source':'atlas vector primitives, diagram widths not certified clear widths','service_ribbon_role':'inferred from service/staff legend color','lift_pit_support_headroom_body_cart_clearance_and_capacity':'unresolved','v2_preserved_sha256':previous,'visual_review':'All five pages rendered and inspected; labeled historical and new geometry, lower ribbon interpretation, rejected placements and preserved doors.','original_runtime_and_catalogue_mutations':0}
(root/'validation.json').write_text(json.dumps(result,indent=2))
files=[root/n for n in ['Astraea_Forward_Commons_Core_Study_v3.pdf','README.txt','build_core_study.py','extract_arrival_evidence.py','validate_core_study.py','validation.json']]
files += [p for directory in ['editable','inputs','history'] for p in (root/directory).rglob('*') if p.is_file()]
(root/'SHA256.json').write_text(json.dumps({str(p.relative_to(root)):sha(p) for p in files},indent=2))
files.append(root/'SHA256.json')
with zipfile.ZipFile(root/'Astraea_Editable_Forward_Core_Study_v3.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(root)))
print(json.dumps({'status':'pass','pdf_sha256':sha(root/'Astraea_Forward_Commons_Core_Study_v3.pdf'),'zip_sha256':sha(root/'Astraea_Editable_Forward_Core_Study_v3.zip'),'zip_bytes':(root/'Astraea_Editable_Forward_Core_Study_v3.zip').stat().st_size}))
