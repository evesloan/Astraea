"""Recover actual authored gallery contours from the atlas, distinct from slab cut-outs."""
from pathlib import Path
import fitz,json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'data/reference/historical_atlas.pdf';pdf=fitz.open(source);records=[]
for deck in range(2,18):
 page=pdf[deck+1];ds=page.get_drawings();h=next(d for d in ds if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=h.width/1082;cy=(h.y0+h.y1)/2
 def point(q):return [round((q.y-cy)/scale,3),round((q.x-h.x0)/scale-541,3)]
 candidates=[]
 for index,d in enumerate(ds):
  r=d['rect'];bounds=point(r.tl)+point(r.br)
  if d['fill'] and len(d['items'])==36 and all(it[0]=='l' for it in d['items']) and h.contains(r) and -60<bounds[0]<-20 and 20<bounds[2]<60 and -90<bounds[1]<-30 and 30<bounds[3]<90:
   candidates.append((r.get_area(),index,d))
 assert len(candidates)==2,(deck,len(candidates))
 candidates.sort(reverse=True,key=lambda x:x[0]);outer,inner=candidates
 records.append({'deck':f'D{deck:02}','atlas_page':deck+2,'outer_drawing':outer[1],'inner_drawing':inner[1],'outer':[point(it[1]) for it in outer[2]['items']],'inner':[point(it[1]) for it in inner[2]['items']]})
(root/'data/reference/atrium_contours.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Actual historical authored terrace contours. The96x128m rectangle is the structural slab opening, not the final clear walking-floor boundary. Final finish and vertical composition still require refinement.','decks':records},indent=2)+'\n')
print('PASS: recovered16 authored outer/inner terrace contours')
