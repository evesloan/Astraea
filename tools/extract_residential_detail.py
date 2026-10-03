"""Recover explicit D13 addresses, class colours and markers from the historical atlas.
Evidence only: rectangles are allocations, not architectural templates or a new registry.
"""
from pathlib import Path
import fitz,json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'data/reference/historical_atlas.pdf';pdf=fitz.open(source);page=pdf[14];ds=page.get_drawings();words=page.get_text('words')
known=next(a for a in json.loads((root/'data/reference/directory_allocations.json').read_text())['records']if a['programme_key']=='D13_directory_05')
anchors=[]
for i,d in enumerate(ds):
 r=d['rect']
 if r.y0<600 or len(d['items'])!=1 or d['items'][0][0]!='re' or not d['fill'] or r.width<40 or r.height<40:continue
 if any(w[4]=='5' and r.contains(fitz.Rect(w[:4]))for w in words):anchors.append((i,r))
assert len(anchors)==1,anchors
_,anchor=anchors[0];sx=anchor.height/(known['x'][1]-known['x'][0]);sz=anchor.width/(known['z'][1]-known['z'][0]);assert abs(sx-sz)<.0001
scale=(sx+sz)/2
mapx=lambda y:round(known['x'][0]+(y-anchor.y0)/scale,3)
mapz=lambda x:round(known['z'][0]+(x-anchor.x0)/scale,3)
classes={(174,197,214):'standard',(185,176,207):'specialty'}
rows=[];census=json.loads((root/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
for index,d in enumerate(ds):
 r=d['rect'];colour=tuple(round(v*255)for v in d['fill'])if d['fill']else None
 if r.y0<600 or colour not in classes or len(d['items'])!=1 or d['items'][0][0]!='re':continue
 labels=[w[4]for w in words if w[4].isdigit() and len(w[4])==5 and r.contains(fitz.Rect(w[:4]))]
 assert len(labels)==1,(index,labels)
 x=[mapx(r.y0),mapx(r.y1)];z=[mapz(r.x0),mapz(r.x1)]
 matches=[a for a in census if a['deck']==13 and max(abs(a[k][i]-v)for k,vals in [('x',x),('z',z)]for i,v in enumerate(vals))<.005]
 assert len(matches)==1,(labels,x,z)
 markers=[]
 for candidate in ds[index+1:index+4]:
  cr=candidate['rect'];center=(cr.tl+cr.br)*.5
  if cr.width>4 or cr.height>4:break
  if r.contains(center) or (r+(-2,-2,2,2)).contains(center):
   markers.append({'kind':'door_marker' if len(candidate['items'])==1 else 'bed_anchor','x':mapx(center.y),'z':mapz(center.x)})
 beds=[m for m in markers if m['kind']=='bed_anchor'];doors=[m for m in markers if m['kind']=='door_marker']
 assert len(doors)==1 and len(beds)==(2 if classes[colour]=='standard' else 1)
 rows.append({'historical_address':labels[0],'deck':'D13','historical_class':classes[colour],'allocation_x':x,'allocation_z':z,'markers':markers,'source_drawing':index,'persistent_id':None})
assert len({r['historical_address']for r in rows})==len(rows)==26
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'atlas_page':15,'calibration':'Inset commons5 matched to independently extracted D13_directory_05 allocation','scale_points_per_m':scale,'status':'Historical evidence, not an architectural layout or recovered persistent identity. Marker size is not door clearance. Class/totals predate luxury replacement decisions.','records':rows,'checks':{'unique_addresses':True,'all_match_existing_census':True,'one_door_marker_each':True,'bed_marker_counts_match_historical_class':True}}
(root/'data/reference/D13_named_residential_evidence.json').write_text(json.dumps(report,indent=2)+'\n');print('RESIDENTIAL DETAIL PASS:',len(rows),'addressed allocations reconciled; no rooms built or assigned')
