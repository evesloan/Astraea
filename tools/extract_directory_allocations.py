"""Extract historical directory allocations; rectangles remain envelopes, never final rooms."""
from pathlib import Path
import fitz,json,hashlib
root=Path(__file__).resolve().parents[1]
source=root/'data/reference/historical_atlas.pdf';pdf=fitz.open(source)
programme=json.loads((root/'data/programme_ledger.json').read_text())
records=[];missing=[]
for deck in range(1,19):
 p=pdf[deck+1];ds=p.get_drawings()
 h=next(d for d in ds if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect']
 scale=h.width/1082;cy=(h.y0+h.y1)/2
 expected=[e for e in programme['destinations'] if e['historical_deck']==f'D{deck:02}']
 for e in expected:
  number=int(e['programme_key'].rsplit('_',1)[1]);candidates=[]
  for i,d in enumerate(ds):
   r=d['rect']
   if not (h.contains(r) and d['fill'] and len(d['items'])==1 and d['items'][0][0]=='re' and r.width/scale>15 and r.height/scale>15):continue
   words=p.get_text('words',clip=r)
   matches=[w for w in words if w[4].isdigit() and int(w[4])==number and len(w[4])<=2]
   if len(matches)==1:candidates.append((r.get_area(),i,r))
  if not candidates:missing.append(e['programme_key']);continue
  _,i,r=max(candidates,key=lambda v:v[0])
  records.append({'programme_key':e['programme_key'],'name':e['name'],'deck':deck,'atlas_page':deck+2,'drawing_index':i,'x':[round((r.y0-cy)/scale,3),round((r.y1-cy)/scale,3)],'z':[round((r.x0-h.x0)/scale-541,3),round((r.x1-h.x0)/scale-541,3)],'candidate_rectangles':len(candidates)})
result={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Largest filled main-diagram rectangle containing the exact one/two-digit directory number. Checked against existing known upper and aquatic/sports envelopes; candidates are historical allocations, not final walls or validated room volumes.','records':records,'unresolved':missing}

known=json.loads((root/'data/reference/historical_atlas_allocations.json').read_text())
comparisons=0
for r in records:
 old=next((a for a in known if a['deck']==r['deck'] and a.get('atlas_directory_number')==int(r['programme_key'].rsplit('_',1)[1])),None)
 if old:
  difference=max(abs(x-y) for axis in ['x','z'] for x,y in zip(r[axis],old[axis]))
  if difference>=.01:
   r['rejected_parent_volume_candidate']={'x':r['x'],'z':r['z'],'drawing_index':r['drawing_index']}
   r['x'],r['z']=old['x'],old['z'];r['drawing_index']=None
   r['source_note']='Retain previously verified named entry envelope; numbered marker lies inside a larger parent volume. Do not replace an entry by its whole theater.'
  else:comparisons+=1
(root/'data/reference/directory_allocations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'records':len(records),'verified_existing_matches':comparisons,'unresolved':missing}))
