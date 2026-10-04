from pathlib import Path
import json, hashlib, zipfile, xml.etree.ElementTree as ET
import fitz
root=Path(__file__).parent
base=json.loads((root/'inputs/historical_baseline.json').read_text())
ledger=json.loads((root/'editable/Astraea_allocation_constraint_ledger.json').read_text())
cross=json.loads((root/'editable/Astraea_1462_ID_program_crosswalk.json').read_text())
ids={r['id']:r for r in base['rooms']};assert len(ids)==1462
for r in cross['rooms']:
 q=ids[r['existing_id']];assert r['historical_name']==q['name'] and r['deck']==q['deck'] and r['historical_capacity']==q['registered_capacity'];assert r['proposed_hotel_id'] is None
hull=base['hull_plan_zx_m']
def inside(z,x):
 on=False
 for a,b in zip(hull,hull[1:]+hull[:1]):
  if (a[1]>x)!=(b[1]>x) and z<(b[0]-a[0])*(x-a[1])/(b[1]-a[1])+a[0]:on=not on
 return on
def overlap(a,b):return all(a[k][0]<b[k][1] and b[k][0]<a[k][1] for k in ['x','y','z'])
volumes={'atrium':{'x':[-48,48],'z':[-64,64],'y':[6,106.5]},'theater':{'x':[-118,-34],'z':[-265,-115],'y':[69.5,91.5]}}
checks=[]
for alt in ledger['hotel_alternatives']:
 for m in alt['masses']:
  assert all(inside(z,x) for z in m['z'] for x in m['x'])
  assert 0<=m['y'][0]<m['y'][1]<=118
  assert all(not overlap(m,v) for v in volumes.values())
  assert m['x'][1]<=-12 or m['x'][0]>=12
  checks.append({'hotel':m['id'],'inside_atlas_plan_footprint':True,'within_reference_height':True,'avoids_known_atrium_and_theater':True,'local_upper_hull_fit':'unverified','other_room_conflicts':'unresolved'})
for p in sorted((root/'editable').glob('*.svg')):ET.parse(p)
pdf=fitz.open(root/'Astraea_District_Planning_Study.pdf');assert len(pdf)==8
outbounds=[]
for i,p in enumerate(pdf):
 for b in p.get_text('blocks'):
  if b[0]<0 or b[1]<0 or b[2]>p.rect.width+.1 or b[3]>p.rect.height+.1:outbounds.append((i+1,b[:4],b[4]))
assert not outbounds,outbounds
ledger['salon_assembly_proposal']['unknown_door_parameters']={'public_aperture_width_m':None,'public_clear_height_m':None,'service_aperture_width_m':None,'service_clear_height_m':None,'leaf_stroke_m':None,'cassette_depth_m':None,'head_reservation_m':None}
(root/'editable/Astraea_allocation_constraint_ledger.json').write_text(json.dumps(ledger,indent=2))
result={'date':'2026-10-02','pdf_pages':8,'svg_pages':8,'source_records_retained':1462,'all_original_ids_names_decks_and_capacities_preserved':True,'proposed_hotel_assignments':0,'new_runtime_scenes':0,'visual_review':'All eight rendered pages inspected. After independent review, sheets 1-5 were revised and visually rechecked: caption clear of routes; simplified tram/support omission explicit; theater floor openings/gallery interfaces named; paired court locations unresolved. Latest sheets clean.','hotel_envelope_screen':checks,'known_limitations':['No current-runtime or final upper hull verification','No physical route, door mechanism, body-envelope or occupancy certification','Massing boxes are proposals, not assignments or approved floor openings','A 4m assembly study strip is not a verified clearance standard','No public/service salon door aperture, head, leaf or cassette dimensions survive in the inspected sources']}
(root/'validation.json').write_text(json.dumps(result,indent=2))
files=[root/'Astraea_District_Planning_Study.pdf',root/'README.txt',root/'build_planning_package.py',root/'validate_planning_package.py',root/'validation.json']+list((root/'editable').glob('*'))+list((root/'inputs').rglob('*'))
files=[p for p in files if p.is_file()]
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(root/'SHA256.json').write_text(json.dumps(manifest,indent=2));files.append(root/'SHA256.json')
with zipfile.ZipFile(root/'Astraea_Editable_District_Study.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(root)))
print(json.dumps({'pdf':str(root/'Astraea_District_Planning_Study.pdf'),'zip':str(root/'Astraea_Editable_District_Study.zip'),'zip_bytes':(root/'Astraea_Editable_District_Study.zip').stat().st_size,'validation':'passed'}))
