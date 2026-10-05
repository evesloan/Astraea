"""Retain the D03 source crew-bank footprints without inventing persistent IDs."""
from pathlib import Path
import fitz,json,hashlib
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'data/reference/historical_atlas.pdf';page=fitz.open(source)[4];drawings=page.get_drawings()
hull=next(d for d in drawings if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=hull.width/1082;cy=(hull.y0+hull.y1)/2
records=[]
for index,d in enumerate(drawings):
 r=d['rect']
 if not(hull.contains(r)and d['fill']and len(d['items'])==1 and d['items'][0][0]=='re'):continue
 if abs(r.width/scale-9.5)>.02 or abs(r.height/scale-12)>.02:continue
 if max(abs(a-b)for a,b in zip(d['fill'],[.607843,.674510,.709804]))>.002:continue
 records.append({'deck':3,'atlas_page':5,'drawing_index':index,'stable_id':None,'name':None,'kind':'unlabelled_crew_bank_allocation','x':[round((r.y0-cy)/scale,3),round((r.y1-cy)/scale,3)],'z':[round((r.x0-hull.x0)/scale-541,3),round((r.x1-hull.x0)/scale-541,3)]})
assert len(records)==200
result={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'200 main-diagram crew-colour rectangles on visually inspected atlas page5, calibrated to the1082m hull;9.5x12m allocation envelopes, not mandatory cabin walls','records':records,'bed_assignment_status':'Unresolved current fit: source footnote assigns399 beds to C001-C200 and a separate player berth; latest shared player home must reassign an existing crew member within400 total, never add a401st person or infer all source rectangles are occupied doubles','employee_home_programme_key':'D03_directory_01'}
(ROOT/'data/reference/D03_crew_envelopes.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:200 historical crew-bank allocations extracted; current400-person shared-home assignment remains a separate gate')
