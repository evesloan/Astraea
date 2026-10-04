"""Read-only PDF vector audit. Writes derivatives only beside this script."""
from pathlib import Path
import json, hashlib, fitz
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'inputs/route_evidence'
OUT.mkdir(parents=True,exist_ok=True)
PDF=ROOT/'inputs/Astraea-current-layout-atlas.pdf'
ALLOC=ROOT/'inputs/atlas_allocations.json'
pdf=fitz.open(PDF); alloc=json.loads(ALLOC.read_text())
cores=[
 {'name':'guest_core_test','x':[-62,-56],'z':[-386,-378]},
 {'name':'guest_landing_test','x':[-63,-54],'z':[-378,-374]},
 {'name':'service_core_test','x':[-62,-56],'z':[-362,-354]},
 {'name':'service_landing_test','x':[-63,-54],'z':[-366,-362]},
]
data={'source':str(PDF.relative_to(ROOT)), 'source_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
 'status':'Historical drawing evidence only. No runtime, clearance, occupancy, structural, or vertical-core feasibility certification.',
 'method':'PyMuPDF get_drawings; zero-based drawing indices; main hull x extent calibrated to Z -541..541; X zero at main hull vertical center. Widths are diagram stroke widths transformed to world metres, not independently measured built clear widths. Drawing item endpoints are X,Z. Rounded to 0.001 m; this is extraction precision, not architectural survey accuracy.',
 'pymupdf_version':fitz.VersionBind,'decks':[]}
for deck in range(5,18):
 p=pdf[deck+1];ds=p.get_drawings();h=next(d for d in ds if 1000<d['rect'].width<1100 and 230<d['rect'].height<245 and d['fill'])['rect'];scale=h.width/1082;cy=(h.y0+h.y1)/2
 def pt(q):return [round((q.y-cy)/scale,3),round((q.x-h.x0)/scale-541,3)]
 def bounds(r):return {'x':[pt(r.tl)[0],pt(r.br)[0]],'z':[pt(r.tl)[1],pt(r.br)[1]]}
 def rec(i):
  d=ds[i];items=[]
  for it in d['items']:
   if it[0]=='re':items.append({'operator':'re','bounds_m':bounds(it[1]),'orientation':it[2]})
   else:items.append({'operator':it[0],'points_xz_m':[pt(q) for q in it[1:] if isinstance(q,fitz.Point)]})
  return {'drawing_index_zero_based':i,'pdf_seqno':d['seqno'],'type':d['type'],'color':d['color'],'fill':d['fill'],'width_pdf_points':d['width'],'diagram_width_m':round(d['width']/scale,3) if d['width'] else None,'line_cap':d.get('lineCap'),'line_join':d.get('lineJoin'),'bounds_m':bounds(d['rect']),'items':items}
 routes=[rec(i) for i in range(14,40)]
 # Above are the full main-diagram circulation primitives, before rooms. Some are hidden by later room drawings.
 doors=[];features=[]
 for i,d in enumerate(ds):
  r=d['rect']; fill=d['fill']; c=pt((r.tl+r.br)/2)
  if not h.contains(r):continue
  if fill and abs(fill[0]-.141176)<.0001 and -490<c[1]<-300 and -110<c[0]<80 and r.width/scale<4 and r.height/scale<4:
   doors.append({**rec(i),'symbol_center_xz_m':c,'note':'Door marker center; marker size is symbolic, not aperture width.'})
  if fill and len(d['items'])==1 and d['items'][0][0]=='re' and -490<c[1]<-300 and -110<c[0]<80 and r.width/scale>4 and r.height/scale>4:
   features.append(rec(i))
 trams=[rec(i) for i,d in enumerate(ds) if h.contains(d['rect']) and d['color'] and abs(d['color'][0]-.705882)<.0001]
 d={'deck':deck,'atlas_page_one_based':deck+2,'calibration':{'hull_pdf_rect':list(h),'scale_points_per_m':scale,'X0_pdf_y':cy},'main_circulation_primitives':routes,'forward_door_markers':doors,'forward_rectangles':features,'tram_primitives':trams}
 data['decks'].append(d)
(OUT/'atlas_forward_arrival_vectors.json').write_text(json.dumps(data,indent=2)+'\n')

def area(a,b):
 return round(max(0,min(a['x'][1],b['x'][1])-max(a['x'][0],b['x'][0]))*max(0,min(a['z'][1],b['z'][1])-max(a['z'][0],b['z'][0])),6)
res={'status':'Historical 2D screen of NEW UNSIZED test inputs only. No permission to modify any source/runtime or imply free space.', 'candidate_inputs':cores,'allocation_source':str(ALLOC.relative_to(ROOT)), 'vector_source':'atlas_forward_arrival_vectors.json','results':[]}
for deck in range(9,18):
 d=next(x for x in data['decks'] if x['deck']==deck)
 bands=[]
 for r in d['main_circulation_primitives']:
  if r['type']!='s':continue
  for it in r['items']:
   if it['operator']!='l':continue
   p,q=it['points_xz_m'];w=r['diagram_width_m'];half=w/2
   if abs(p[0]-q[0])<.002:band={'x':[p[0]-half,p[0]+half],'z':[min(p[1],q[1]),max(p[1],q[1])]}
   elif abs(p[1]-q[1])<.002:band={'x':[min(p[0],q[0]),max(p[0],q[0])],'z':[p[1]-half,p[1]+half]}
   else:continue
   bands.append({**band,'drawing_index_zero_based':r['drawing_index_zero_based'],'color':r['color'],'diagram_width_m':w})
 for c in cores:
  hits=[{**r,'intersection_area_m2':area(c,r)} for r in alloc if r['deck']==deck and area(c,r)>.001]
  route_hits=[{**r,'intersection_area_m2':area(c,r)} for r in bands if area(c,r)>.001]
  res['results'].append({'deck':deck,'candidate':c['name'],'allocation_intersections':hits,'diagram_route_band_intersections':route_hits})
(OUT/'candidate_core_screen.json').write_text(json.dumps(res,indent=2)+'\n')
print('Saved',OUT)
for d in res['results']:
 print('D%02d'%d['deck'],d['candidate'],'allocation hits',len(d['allocation_intersections']),'route hits',[(r['drawing_index_zero_based'],r['intersection_area_m2']) for r in d['diagram_route_band_intersections']])

r3=[
 {'name':'R3_guest_core_test','x':[-40,-34],'z':[-386,-378]},
 {'name':'R3_service_core_test','x':[-54,-48],'z':[-386,-378]},
 {'name':'R3_guest_landing_test','x':[-40,-34],'z':[-378,-374]},
 {'name':'R3_service_landing_test','x':[-54,-48],'z':[-378,-374]},
]
r3_lower=[
 {'name':'R3_D12_proposed_guest_spur','x':[-40,-5.5],'z':[-374,-366]},
 {'name':'R3_D12_proposed_service_link','x':[-54.5,-54],'z':[-378,-374]},
]
r3result={'status':'Historical 2D room/ribbon intersection screen ONLY. R3 footprints, landings and D12 connectors are NEW UNSIZED planning inputs, not historical geometry or feasibility approval.',
 'vertical_scope':'D12 through D17. No shaft below D12 inferred. D11 diagnostic is separately labeled rejected extension.',
 'source_sha256':data['source_sha256'],'candidate_inputs':r3,'new_D12_connectors':r3_lower,
 'tolerance_m':0.002,'method':'Positive-area rectangle intersections. Line widths are diagram ribbon widths. Boundary contacts recorded separately; no clearance allowance, wall thickness, structure, mechanical sizing, fire or accessibility evidence implied.', 'results':[]}
for deck in range(12,18):
 d=next(x for x in data['decks'] if x['deck']==deck);bands=[]
 for r in d['main_circulation_primitives']:
  if r['type']!='s':continue
  for it in r['items']:
   if it['operator']!='l':continue
   p,q=it['points_xz_m'];w=r['diagram_width_m'];half=w/2
   if abs(p[0]-q[0])<.002:band={'x':[p[0]-half,p[0]+half],'z':[min(p[1],q[1]),max(p[1],q[1])]}
   elif abs(p[1]-q[1])<.002:band={'x':[min(p[0],q[0]),max(p[0],q[0])],'z':[p[1]-half,p[1]+half]}
   else:continue
   bands.append({**band,'drawing_index_zero_based':r['drawing_index_zero_based'],'color':r['color'],'diagram_width_m':w})
 for c in r3+(r3_lower if deck==12 else []):
  hits=[{**r,'intersection_area_m2':area(c,r)} for r in alloc if r['deck']==deck and area(c,r)>.001]
  route_hits=[{**r,'intersection_area_m2':area(c,r)} for r in bands if area(c,r)>.001]
  touches=[]
  for r in bands:
   dx=min(c['x'][1],r['x'][1])-max(c['x'][0],r['x'][0]);dz=min(c['z'][1],r['z'][1])-max(c['z'][0],r['z'][0])
   if area(c,r)<.001 and dx>=-.002 and dz>=-.002 and (dx>.002 or dz>.002):touches.append(r)
  r3result['results'].append({'deck':deck,'candidate':c['name'],'allocation_intersections':hits,'diagram_route_band_intersections':route_hits,'diagram_route_band_boundary_contacts':touches})
r3result['rejected_D11_extension_diagnostic']=[{'candidate':c['name'],'allocation_intersections':[{**r,'intersection_area_m2':area(c,r)} for r in alloc if r['deck']==11 and area(c,r)>.001]} for c in r3]
(OUT/'R3_candidate_core_screen.json').write_text(json.dumps(r3result,indent=2)+'\n')
print('\nR3')
for d in r3result['results']:
 print('D%02d'%d['deck'],d['candidate'],'allocation hits',len(d['allocation_intersections']),'route hits',[(r['drawing_index_zero_based'],r['intersection_area_m2']) for r in d['diagram_route_band_intersections']],'touches',[r['drawing_index_zero_based'] for r in d['diagram_route_band_boundary_contacts']])
