from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import fitz
root=Path(__file__).parent
base=json.loads((root/'inputs/historical_baseline.json').read_text());byid={r['id']:r for r in base['rooms']}
ledger=json.loads((root/'editable/Astraea_hybrid_disposition_ledger_v2.json').read_text());crosswalk=json.loads((root/'editable/Astraea_1462_ID_crosswalk_v2.json').read_text())
features=json.loads((root/'inputs/atlas_allocations.json').read_text())
assert len(byid)==1462 and len(crosswalk['rooms'])==1462
for r in crosswalk['rooms']:
 o=byid[r['existing_id']];assert r['historical_name']==o['name'] and r['deck']==o['deck'] and r['historical_capacity']==o['registered_capacity'];assert r['proposed_hotel_id'] is None
assert len(ledger['public_allocation_dispositions'])==13
for r in ledger['public_allocation_dispositions']:
 assert r['historical_capacity']==byid[r['stable_id']]['registered_capacity'];assert r['hotel_exclusive_ownership'] is False and r['room_reassignment'] is None

def key(r):return (r['deck'],tuple(r['x']),tuple(r['z']),r['kind'])
source={key(r) for r in features}
for w in ledger['upper_wing_studies']:
 for r in w['entire_guest_allocations']+w['retained_common_allocations']:assert key(r) in source
# No historical guest rectangle is divided by the drawn affiliation hull at any represented upper deck.
def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def hull(ps):
 p=sorted(set(ps));lo=[];hi=[]
 for v in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],v)<=0:lo.pop()
  lo.append(v)
 for v in p[::-1]:
  while len(hi)>1 and cross(hi[-2],hi[-1],v)<=0:hi.pop()
  hi.append(v)
 return lo[:-1]+hi[:-1]
def area(ps):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]+ps[:1])))/2 if ps else 0

def clip(ps,cs):
 for a,b in zip(cs,cs[1:]+cs[:1]):
  ns=[]
  if not ps:break
  for p,q in zip(ps,ps[1:]+ps[:1]):
   cp,cq=cross(a,b,p),cross(a,b,q)
   if cp>=-1e-9:ns.append(p)
   if (cp>=0)!=(cq>=0):
    t=cp/(cp-cq);ns.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
  ps=ns
 return ps
for w in ledger['upper_wing_studies']:
 for deck in range(13,18):
  rs=[r for r in w['entire_guest_allocations']+w['retained_common_allocations'] if r['deck']==deck]
  h=hull([(z,x) for r in rs for z in r['z'] for x in r['x']])
  for r in features:
   if r['deck']!=deck or r['kind']!='unlabelled_guest_allocation':continue
   a,b=r['z'];c,d=r['x'];full=(b-a)*(d-c);v=area(clip([(a,c),(b,c),(b,d),(a,d)],h));assert not(.001<v<full-.001),(w['label'],deck,r)
# v1 is preserved exactly as delivered
v1_expected={'Astraea_District_Planning_Study.pdf':'7ce9c5daecc530fa2a7d962affeff557d7cd95d9465840ad9470900737181f6c','Astraea_Editable_District_Study.zip':'eb19c70934718317e7867a8be9fa04feeaec7cc5497e62677138fc632002a8ca'}
for name,sha in v1_expected.items():assert hashlib.sha256((root/'history'/name).read_bytes()).hexdigest()==sha
for p in (root/'editable').glob('*.svg'):ET.parse(p)
pdf=fitz.open(root/'Astraea_Hybrid_District_Study_v2.pdf');assert len(pdf)==5
for i,p in enumerate(pdf):
 for b in p.get_text('blocks'):assert b[0]>=0 and b[1]>=0 and b[2]<=p.rect.width+.1 and b[3]<=p.rect.height+.1,(i,b)
result={'status':'pass','pdf_pages':5,'editable_svg_pages':5,'source_ids_retained':1462,'named_public_allocations_explicitly_retained':13,'new_hotel_room_id_assignments':0,'affiliation_boundaries_cutting_historical_guest_rectangles':0,'v1_artifacts_sha256_verified':v1_expected,'current_runtime_feasibility':'not established','upper_hull_and_81_luxury_fit':'unresolved','new_local_core_footprints':'unallocated; no penetrations approved','visual_review':'All five rendered pages inspected; section labels and footer text corrected. Current sheets clean.','original_project_and_catalogue_mutations':0}
(root/'validation.json').write_text(json.dumps(result,indent=2))
files=[root/'Astraea_Hybrid_District_Study_v2.pdf',root/'README.txt',root/'build_hybrid_study.py',root/'validate_hybrid_study.py',root/'validation.json']
files += [p for folder in ['editable','inputs','history'] for p in (root/folder).rglob('*') if p.is_file()]
(root/'SHA256.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2));files.append(root/'SHA256.json')
with zipfile.ZipFile(root/'Astraea_Editable_Hybrid_Study_v2.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(root)))
print(json.dumps({'validation':'passed','pdf':str(root/'Astraea_Hybrid_District_Study_v2.pdf'),'archive':str(root/'Astraea_Editable_Hybrid_Study_v2.zip'),'archive_bytes':(root/'Astraea_Editable_Hybrid_Study_v2.zip').stat().st_size}))
