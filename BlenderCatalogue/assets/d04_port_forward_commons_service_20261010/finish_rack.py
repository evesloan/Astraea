from pathlib import Path
import json,shutil,hashlib
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';d=W/'attempt02_linen_rack_contact_review';d.mkdir()
for f in ['PLAN.json','PREIMAGE_SUPPORT.json','PREIMAGE_SUPPORT.log']:shutil.copy2(W/f,d/f)
p=json.load(open(W/'PLAN.json'));parts=p['parts']
for q in parts:
 if q['name'].startswith('D04CS_LinenRackLeg_'):
  j=int(q['name'].split('_')[-1]);center=sum([min(v[2]for v in q['verts']),max(v[2]for v in q['verts'])])/2;target=-358.2 if j%2==0 else-357.75
  for v in q['verts']:v[2]+=target-center
 if q['name'].startswith('D04CS_LinenFold_'):
  k=int(q['name'].split('_')[-1]);center=sum([min(v[2]for v in q['verts']),max(v[2]for v in q['verts'])])/2
  for v in q['verts']:v[2]+=-358.12+k*.14-center
# Prove each shelf physically contacts all four floor-bearing uprights and linen starts exactly at shelf top.
def bounds(q):return[[min(v[k]for v in q['verts'])for k in range(3)],[max(v[k]for v in q['verts'])for k in range(3)]]
contacts=[]
for j in range(2):
 shelf=next(q for q in parts if q['name']=='D04CS_CleanLinenShelf_'+str(j));lo,hi=bounds(shelf)
 for leg in [q for q in parts if q['name'].startswith('D04CS_LinenRackLeg_')]:
  a,b=bounds(leg);assert all(a[k]<hi[k] and b[k]>lo[k]for k in range(3));assert a[1]==16.5;contacts.append([shelf['name'],leg['name']])
 for linen in [q for q in parts if q['name'].startswith('D04CS_LinenFold_'+str(j)+'_')]:
  a,b=bounds(linen);assert abs(a[1]-hi[1])<1e-8 and all(lo[k]<=a[k]<=b[k]<=hi[k]for k in [0,2]);contacts.append([linen['name'],shelf['name']])
p['linen_rack_exact_contacts']=contacts;(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');(W/'finish_rack.py').write_bytes(Path(__file__).read_bytes());(d/'REVIEW.json').write_text(json.dumps({'status':'SOURCE_CONTACT_REVISION','actual_main_preimage_pass':344,'reason':'Shelf-to-upright and linen-to-shelf source review found floating rack details; precise contacts corrected before native authoring','files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in d.iterdir()}},indent=2)+'\n');print('CONTACTS',len(contacts))
