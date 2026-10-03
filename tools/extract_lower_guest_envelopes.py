"""Complete the historical accommodation footprint inventory; never invent room IDs."""
from pathlib import Path
import fitz,json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'data/reference/historical_atlas.pdf';page=fitz.open(source)[5];drawings=page.get_drawings()
hull=next(d for d in drawings if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=hull.width/1082;cy=(hull.y0+hull.y1)/2
records=[]
for index,d in enumerate(drawings):
 r=d['rect']
 if not (hull.contains(r) and d['fill'] and len(d['items'])==1 and d['items'][0][0]=='re'):continue
 if abs(r.width/scale-7.2)>.01 or abs(r.height/scale-12.9)>.01:continue
 if max(abs(x-y) for x,y in zip(d['fill'],[.72549,.690196,.811765]))>.002:continue
 records.append({'deck':4,'atlas_page':6,'drawing_index':index,'stable_id':None,'name':None,'kind':'unlabelled_guest_allocation','historical_class':'specialty; does not determine current species or luxury tier','x':[round((r.y0-cy)/scale,3),round((r.y1-cy)/scale,3)],'z':[round((r.x0-hull.x0)/scale-541,3),round((r.x1-hull.x0)/scale-541,3)]})
assert len(records)==120
(root/'data/reference/D04_guest_envelopes.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Main diagram purple accommodation rectangles, measured7.2m by12.9m and counted120; atlas page6 visually reviewed. This is historical spatial evidence, not final geometry or recovered persistent identity.','records':records},indent=2)+'\n')
upper=json.loads((root/'data/reference/historical_atlas_allocations.json').read_text());guests=[x for x in upper if x['kind']=='unlabelled_guest_allocation']+records
assert len(guests)==1000
(root/'data/reference/historical_guest_census.json').write_text(json.dumps({'status':'1000 historical allocation envelopes accounted for; no finished rooms or current berth assignment implied','guest_envelopes':guests,'count':len(guests),'new_luxury_reallocation':'Pending architectural fitting within1000units; passenger admission remains2000 independently of bed capacity'},indent=2)+'\n')
print('PASS: 880 upper plus120 D04 historical guest envelopes;1000 total; no IDs invented')
