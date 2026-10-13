from pathlib import Path
import json
C=Path(__file__).parent;P=C/'street_floor_successor';G=Path('/workspace/astraea-protected-integration-20261012/Game')
ns={'__file__':str(P/'verify_export.py')};exec((P/'verify_export.py').read_text().split('new=triangles(')[0],ns);triangles=ns['triangles'];overlap=ns['ns']['overlap'];area=ns['ns']['area']
new=triangles(C/'g3_crossing_staging/Game/assets/models/group3_commons_crossings_20261012/AST-STF-G3-063.glb');old=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 d=json.loads((G/rel).read_text())
 for row in d.get('regions',[]):
  if abs(float(row.get('floor_y',-999))-12)<.001:old.extend((row['id'],t)for t in row['triangles'])
plan=json.loads((P/'FLOOR_RECEIVING_SUCCESSOR_PLAN.json').read_text());old.extend((x['source']+'/'+x['mesh'],x['triangle'])for x in plan['current_floor_triangles']);old.extend(('corrected_streets',t)for t in triangles(P/'proposed/AST-STF-G3-058_current_receiving_successor001.glb'))
# Add the other installed G3 proposed floor metadata, which is retained in separate exact receipts.
for f in C.rglob('*FLOOR*.json'):
 if any(s in str(f)for s in ['street_floor_successor','g3_street_preflight','g3_receiving_metadata']):continue
 try:d=json.loads(f.read_text())
 except (ValueError,OSError):continue
 if not isinstance(d,dict)or not isinstance(d.get('parts'),list):continue
 for p in d['parts']:
  if not isinstance(p,dict):continue
  if 'triangles'in p and abs(float(p.get('y',[-999,-999])[-1])-12)<.001:old.extend((str(f.relative_to(C)),t)for t in p['triangles'])
hits=[]
for i,t in enumerate(new):
 for owner,b in old:
  a=overlap(t,b)
  if a>1e-6:hits.append({'triangle':i,'owner':owner,'area_m2':a})
r={'status':'PASS_STATIC_CURRENT_THRESHOLD_NO_OVERLAP'if not hits else'HOLD_THRESHOLD_OVERLAP','new_triangles':len(new),'exported_threshold_m2':sum(area(t)for t in new),'overlap_m2':sum(x['area_m2']for x in hits),'hits':hits,'runtime_receiving_required':True};(C/'G3_CROSSING_THRESHOLD_PREFLIGHT.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items()if k!='hits'})
