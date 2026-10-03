"""Extract lower aquatic/sports allocations from embedded atlas vector and number evidence."""
from pathlib import Path
import fitz,json,hashlib
root=Path(__file__).resolve().parents[1]
source=root/'data/reference/historical_atlas.pdf'
pdf=fitz.open(source)
records=[]
for deck in [7,8]:
 p=pdf[deck+1];ds=p.get_drawings()
 h=next(d for d in ds if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect']
 scale=h.width/1082;cy=(h.y0+h.y1)/2
 for i,d in enumerate(ds):
  r=d['rect']
  if not (h.contains(r) and d['fill'] and len(d['items'])==1 and d['items'][0][0]=='re' and r.width/scale>30 and r.height/scale>30):continue
  numbers=[int(w[4]) for w in p.get_text('words',clip=r) if w[4].isdigit() and 1<=int(w[4])<=10]
  if not numbers:continue
  assert len(numbers)==1
  records.append({'programme_key':f'D{deck:02}_directory_{numbers[0]:02}','deck':deck,'atlas_page':deck+2,'drawing_index':i,'x':[round((r.y0-cy)/scale,3),round((r.y1-cy)/scale,3)],'z':[round((r.x0-h.x0)/scale-541,3),round((r.x1-h.x0)/scale-541,3)]})
assert len(records)==20
(root/'data/reference/lower_allocations.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'PDF vector extents calibrated by1082m hull, matched to visible numbered directory markers; atlas pages9/10 visually inspected. Allocation envelopes only, not precise final architectural instructions.','records':records},indent=2)+'\n')
