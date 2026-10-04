from pathlib import Path
import fitz,json,collections
root=Path(__file__).parent;src=root.parent
pdf=fitz.open(src/'sources/Astraea-current-layout-atlas.pdf')
coverage=json.loads((src/'extracted/project_docs/architecture/whole_ship_coverage.json').read_text())
ledger=json.loads((src/'planning-package/editable/Astraea_allocation_constraint_ledger.json').read_text())
# Explicitly matched atlas destination directory entries; no assignment of unlabelled room rectangles to IDs.
ids={9:['D09_market0','D09_tea1','D09_books2','D09_tailor3','D09_maker4','D09_salon5','D09_parcel6','D09_florist7','D09_cafe8','D09_arcade9'],10:['D10_dining0','D10_dining1','D10_banquet2','D10_banquet3','D10_damp_dining4','D10_mineral5','D10_dining6','D10_banquet7','D10_dessert8','D10_stillroom9'],11:['D11_grand_theater']+[f'D11_cinema_{i}' for i in range(1,7)]+['D11_music','D11_greenroom','D11_arcade','D11_gallery','D11_listening','D11_service'],12:['D12_observation0','D12_library1','D12_listening2','D12_stillroom3','D12_stargazing4','D12_quiet_garden5','D12_gallery6','D12_reading7','D12_panorama8','D12_salon9','D12_theater_gallery']}
byid={r['id']:r for r in coverage['rooms']}
features=[];counts={}
for deck in range(9,18):
 p=pdf[deck+1];draw=p.get_drawings();h=next(d for d in draw if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=h.width/1082;cy=(h.y0+h.y1)/2
 def bounds(r):return {'z':[round((r.x0-h.x0)/scale-541,3),round((r.x1-h.x0)/scale-541,3)],'x':[round((r.y0-cy)/scale,3),round((r.y1-cy)/scale,3)]}
 rects=[d for d in draw if len(d['items'])==1 and d['items'][0][0]=='re' and d['fill'] and d['rect'].x0>=h.x0-.01 and d['rect'].x1<=h.x1+.01 and d['rect'].y0>=h.y0-.01 and d['rect'].y1<=h.y1+.01]
 for b in p.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   for sp in line['spans']:
    t=sp['text'];bb=fitz.Rect(sp['bbox']);pt=fitz.Point((bb.x0+bb.x1)/2,(bb.y0+bb.y1)/2)
    if t.isdigit() and 0<int(t)<20 and h.contains(pt):
     choices=[r for r in rects if r['rect'].contains(pt) and r['rect'].get_area()>10]
     if choices:
      d=min(choices,key=lambda q:q['rect'].get_area());label=int(t);fid=ids[deck][label-1] if deck in ids else None
      if fid:name=byid[fid]['name']
      elif deck==13 and label==1:name='Grand theater / Crown gallery'
      else:
       k=label-(2 if deck==13 else 1);name=['Port forward commons','Starboard forward commons','Port atrium commons','Starboard atrium commons','Port aft commons','Starboard aft commons'][k]
      features.append({'deck':deck,'atlas_page':deck+2,'atlas_directory_number':label,'stable_id':fid,'name':name,'kind':'named_allocation',**bounds(d['rect'])})
 for d in rects:
  w=d['rect'].width/scale;hh=d['rect'].height/scale
  if deck==9 and abs(w-12)<.01 and abs(hh-12)<.01:kind='unlabelled_shop_allocation'
  elif deck>=13 and abs(w-7.2)<.01 and abs(hh-12.9)<.01:kind='unlabelled_guest_allocation'
  else:continue
  features.append({'deck':deck,'atlas_page':deck+2,'stable_id':None,'name':None,'kind':kind,**bounds(d['rect'])})
 counts[deck]=collections.Counter(r['kind'] for r in features if r['deck']==deck)
assert counts[9]['unlabelled_shop_allocation']==100
for d,n in {13:160,14:240,15:180,16:200,17:100}.items():assert counts[d]['unlabelled_guest_allocation']==n
results=[]
for alt in ledger['hotel_alternatives']:
 for m in alt['masses']:
  matched=[]
  for r in features:
   floor=ledger['canonical']['floor_elevations_m'][r['deck']-1]
   if not m['y'][0]<=floor<m['y'][1]:continue
   dz=min(m['z'][1],r['z'][1])-max(m['z'][0],r['z'][0]);dx=min(m['x'][1],r['x'][1])-max(m['x'][0],r['x'][0])
   if dx>.001 and dz>.001:matched.append({**r,'intersection_area_m2':round(dx*dz,3),'fully_inside_proposal':all(m[k][0]<=r[k][0]+.001 and m[k][1]>=r[k][1]-.001 for k in ['x','z'])})
  results.append({'alternative':alt['key'],'hotel':m['id'],'new_proposed_envelope':m,'overlapping_historical_allocations':matched})
  print('\n'+m['id'])
  for r in matched:
   if r['kind']=='named_allocation':print(r['deck'],r['stable_id'] or '(ID not mapped)',r['name'],'Z',r['z'],'X',r['x'])
  cc=collections.Counter((r['deck'],r['kind'],r['fully_inside_proposal']) for r in matched if r['kind']!='named_allocation');print(dict(cc))
out={'status':'read-only historical atlas intersection screen; no current runtime or per-room reassignment','method':'Named allocations matched by atlas number and directory; bounds extracted from PDF vectors. Anonymous shop/guest footprint counts checked against historical deck totals; no invented ID coordinate mapping.','source':'Astraea-current-layout-atlas.pdf, October 1 2026; pages 11-19','precision':'bounds rounded to 0.001m from PDF vector transform; not architectural survey precision','results':results}
(root/'historical_allocation_conflicts.json').write_text(json.dumps(out,indent=2))
