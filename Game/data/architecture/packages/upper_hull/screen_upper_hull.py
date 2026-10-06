#!/usr/bin/env python3
"""Pure allocation/section screen. Does not inspect meshes or change geometry."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
Y=[16.5,61,69.5,78,84,88.5,93,97.5,102,106.5]
S=[1,1,.985,.96,.94,.925,.91,.895,.88,.865]
# Transverse scale of calibrated outline, not a polygon inward offset.
outline=json.loads((ROOT/'data/hull_envelope.json').read_text())['plan_xz_m']
stations=sorted({(z,abs(x)) for x,z in outline if x>=0})
def interp(t,knots,values):
 if t<=knots[0]:return values[0]
 if t>=knots[-1]:return values[-1]
 for i in range(len(knots)-1):
  if knots[i]<=t<=knots[i+1]:return values[i]+(values[i+1]-values[i])*(t-knots[i])/(knots[i+1]-knots[i])
def half(y,z):
 return interp(z,[a for a,b in stations],[b for a,b in stations])*interp(y,Y,S)
def screen(poly,y,reserve=1):
 # Piecewise-affine boundary: endpoints + longitudinal station crossings suffice.
 witnesses=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ts=[0,1]
  if b[1]!=a[1]:ts += [(z-a[1])/(b[1]-a[1]) for z,w in stations if 0<(z-a[1])/(b[1]-a[1])<1]
  for t in ts:
   x=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1]); witnesses.append({'x':x,'z':z,'inner_halfbeam':half(y,z)-reserve,'shortfall':abs(x)+reserve-half(y,z)})
 w=max(witnesses,key=lambda w:w['shortfall']);return {'fits':w['shortfall']<=1e-8,'worst_witness':w}
def rect(r):return [[r['x'][0],r['z'][0]],[r['x'][1],r['z'][0]],[r['x'][1],r['z'][1]],[r['x'][0],r['z'][1]]]
datums=[0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5]
rows=[]
for source,key in [('data/reference/directory_allocations.json','records'),('data/reference/historical_guest_census.json','guest_envelopes')]:
 for i,r in enumerate(json.loads((ROOT/source).read_text())[key]):
  if r['deck']<4:continue
  y=datums[r['deck']-1]
  rows.append({'source':source,'index':i,'identity':r.get('programme_key',r.get('stable_id')),'deck':r['deck'],'floor_y':y,**screen(rect(r),y)})
coord=json.loads((ROOT/'data/architecture/UPPER_SECTION_COORDINATION.json').read_text())
pavilions=[{'identity':r['unit_proposal_key'],'floor_y':r['upper_floor_y'],'roof_y':r['external_roof_limit_y'],**screen(r['boundary'],106.5)} for r in coord['private_upper_pavilions']]
layout=json.loads((ROOT/'data/spatial_layout.json').read_text())
floors=[{'identity':r['id'],'deck':r['deck'],**screen(r['boundary'],datums[int(r['deck'][1:])-1],0)} for r in layout['regions'] if int(r['deck'][1:])>=4]
theater=[{'y':y,**screen([[-118,-265],[-34,-265],[-34,-115],[-118,-115]],y)} for y in [69.5,78,84,88.5,91.5,92]]
sources=['data/hull_envelope.json','data/reference/directory_allocations.json','data/reference/historical_guest_census.json','data/spatial_layout.json','data/architecture/UPPER_SECTION_COORDINATION.json','docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx']
result={'status':'Unadopted design-choice taper; conflict screen only, no physical shell acceptance','section_knots':[{'y':y,'transverse_scale':s,'outer_midbody_halfbeam':120*s,'inner_midbody_halfbeam':120*s-1} for y,s in zip(Y,S)],'rule':'X_outer(Y,Z) = historical halfbeam(Z) * linearly interpolated transverse_scale(Y); inner usable bound is 1m inward transversely, NOT a normal-thickness pressure-shell model. No Z rescaling. General body roof106.5; crown/pavilions separate.','source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'theater_full_rectangle':theater,'allocation_floor_screen':rows,'private_upper_screen_at_general_body_top':pavilions,'structural_region_boundary_screen_no_wall_margin':floors,'summary':{'allocation_failures':sum(not r['fits'] for r in rows),'private_upper_failures':sum(not r['fits'] for r in pavilions),'structural_boundary_failures':sum(not r['fits'] for r in floors)}}
(OUT/'TAPER_CANDIDATE_SCREEN.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary']));print(json.dumps(theater))
# Detailed occupied theater tests, separate from maximum allocation reservation.
import math
T=json.loads((ROOT/'data/architecture/packages/theater/THEATER_SECTION_PROPOSAL.json').read_text())
C=json.loads((ROOT/'data/architecture/packages/theater/CHAIR_FOOTPRINT_SCREENING.json').read_text())
lo,hi=C['chair_bounds_local_gltf_m']['min_m'],C['chair_bounds_local_gltf_m']['max_m']
seats=[]
for s in T['seat_proposals']:
 x,y,z=s['position'];a=s['orientation_yaw_radians']
 poly=[[x+u*math.cos(a)+v*math.sin(a),z-u*math.sin(a)+v*math.cos(a)] for u,v in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]]
 seats.append({'identity':s['id'],'tier':s['tier'],'chair_top_y':y+hi[1],**screen(poly,y+hi[1])})
tier_y={'stalls':69.5,'first_gallery':78,'crown_gallery':84}
aisles=[{'identity':r['id'],'headroom_test_y':tier_y[r['tier']]+3,'headroom_assumption_m':3,**screen(r['boundary'],tier_y[r['tier']]+3)} for r in C['aisle_reservations']]
stage=screen([[-94,-252],[-58,-252],[-58,-238],[-94,-238]],86.1)
backstage=screen([[-116,-263],[-36,-263],[-36,-252],[-116,-252]],74.3)
occupied={'status':'Existing proposed occupied footprint vs unadopted tapered section; exact closed-chair bounds, NOT anatomy or body sweep','closed_chairs':seats,'aisles_at_provisional_3m_headroom':aisles,'stage_proscenium_to_y86_1':stage,'backstage_to_y74_3':backstage,'summary':{'closed_chair_failures':sum(not s['fits'] for s in seats),'aisle_headroom_failures':sum(not s['fits'] for s in aisles),'stage_fits':stage['fits'],'backstage_fits':backstage['fits']},'source_sha256':{str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/architecture/packages/theater/THEATER_SECTION_PROPOSAL.json','data/architecture/packages/theater/CHAIR_FOOTPRINT_SCREENING.json']}}
(OUT/'THEATER_OCCUPIED_TAPER_SCREEN.json').write_text(json.dumps(occupied,indent=2)+'\n')
print(json.dumps(occupied['summary']))
for s in aisles:
 if not s['fits']:print(s)
# Occupancy-responsive shoulder: only theater district, terminating below top canopy.
shoulder_knots=[61,69.5,87.5,92]
shoulder_half=[120,118.5,118.5,109.6]
def shoulder(y,z):
 return max(half(y,z),interp(y,shoulder_knots,shoulder_half)) if -265<=z<=-115 and 61<=y<=92 else half(y,z)
# Monkey-patch only for same detailed tests; no report/source geometry mutation.
old_half=half
# Preserve old function in a wrapper to avoid recursive lookup.
def half(y,z):
 general=interp(z,[a for a,b in stations],[b for a,b in stations])*interp(y,Y,S)
 return max(general,interp(y,shoulder_knots,shoulder_half)) if -265<=z<=-115 and 61<=y<=92 else general
b_seats=[]
for s in T['seat_proposals']:
 x,y,z=s['position'];a=s['orientation_yaw_radians'];poly=[[x+u*math.cos(a)+v*math.sin(a),z-u*math.sin(a)+v*math.cos(a)] for u,v in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]]
 b_seats.append(screen(poly,y+hi[1]))
b_aisles=[screen(r['boundary'],tier_y[r['tier']]+3) for r in C['aisle_reservations']]
B={'status':'Alternative bounded theater shoulder design choice only; not accepted or constructed','west_outer_knots':[{'y':y,'x':-w} for y,w in zip(shoulder_knots,shoulder_half)],'z_extent':[-265,-115],'construction_reservation_x_m':1,'top_behavior':'Shoulder returns inward from y87.5 to92; no full-height allocation box. Roof near westmost galleries is lower than central ceiling91.5. Detailed occupant heads/fixtures/supports still require fitting.','summary':{'closed_chair_failures':sum(not s['fits'] for s in b_seats),'aisle_3m_headroom_failures':sum(not s['fits'] for s in b_aisles),'stage_fits':screen([[-94,-252],[-58,-252],[-58,-238],[-94,-238]],86.1)['fits'],'backstage_fits':screen([[-116,-263],[-36,-263],[-36,-252],[-116,-252]],74.3)['fits']},'shell_interfaces':'West-only district shoulder. Fore/aft return surfaces, normal shell thickness, frame apertures, roof supports, ventilation and maintenance remain undesigned. Outer119.5 would add1m tolerance but is NOT adopted.'}
(OUT/'PRESERVATION_SHOULDER_PROPOSAL.json').write_text(json.dumps(B,indent=2)+'\n');print('shoulder',B['summary'])
