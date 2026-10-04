from pathlib import Path
import json, math, textwrap, hashlib, zipfile
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("AuditSans", str(Path(__file__).parent/"inputs/fonts/DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("AuditSansBold", str(Path(__file__).parent/"inputs/fonts/DejaVuSans-Bold.ttf")))

ROOT=Path(__file__).parent
SRC=ROOT.parent
OUT=ROOT/'editable'; OUT.mkdir(exist_ok=True)
W,H=1440,900
INK='#203F48'; MUT='#5F7274'; BG='#F8F6EF'; LINE='#C9D3D0'; GREEN='#BDD2BD'; BLUE='#CBDCE5'; GOLD='#E8D7A8'; ROSE='#D6BCC7'; TEAL='#547F80'; RUST='#B76543'; PALE='#EBECE5'; PURPLE='#826A96'
PDF=canvas.Canvas(str(ROOT/'Astraea_Hybrid_District_Study_v2.pdf'),pagesize=(1080,675))
PDF.setTitle('Astraea Preferred Hybrid District Study v2');PDF.setAuthor('Astraea planning')

class Page:
 def __init__(self,n,title,sub):
  self.n=n;self.parts=[];PDF.saveState();PDF.scale(.75,.75)
  self.rect(0,0,W,H,BG,None)
  self.text(62,62,title,30,INK,True)
  self.para(62,97,sub,1295,17,MUT,leading=23)
 def rect(self,x,y,w,h,fill=None,stroke=LINE,sw=1,dash=None):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setLineWidth(sw);PDF.setDash([float(a) for a in dash.split(',')] if dash else [])
  if fill:PDF.setFillColor(HexColor(fill))
  if stroke:PDF.setStrokeColor(HexColor(stroke))
  PDF.rect(x,H-y-h,w,h,fill=int(bool(fill)),stroke=int(bool(stroke)))
 def line(self,x1,y1,x2,y2,color=LINE,sw=1,dash=None):
  self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setStrokeColor(HexColor(color));PDF.setLineWidth(sw);PDF.setDash([float(a) for a in dash.split(',')] if dash else []);PDF.line(x1,H-y1,x2,H-y2)
 def poly(self,pts,fill=None,stroke=INK,sw=1,dash=None):
  self.parts.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  PDF.setDash([float(a) for a in dash.split(',')] if dash else []); PDF.setLineWidth(sw)
  if fill:PDF.setFillColor(HexColor(fill))
  if stroke:PDF.setStrokeColor(HexColor(stroke))
  p=PDF.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
  for x,y in pts[1:]:p.lineTo(x,H-y)
  p.close();PDF.drawPath(p,fill=int(bool(fill)),stroke=int(bool(stroke)))
 def text(self,x,y,s,size=18,color=INK,bold=False,anchor='start'):
  s=str(s);font='AuditSansBold' if bold else 'AuditSans'
  self.parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(s)}</text>')
  PDF.setFont(font,size);PDF.setFillColor(HexColor(color))
  if anchor=='middle':PDF.drawCentredString(x,H-y,s)
  elif anchor=='end':PDF.drawRightString(x,H-y,s)
  else:PDF.drawString(x,H-y,s)
 def para(self,x,y,s,width,size=18,color=INK,bold=False,leading=None):
  leading=leading or size*1.38;font='AuditSansBold' if bold else 'AuditSans'; yy=y
  for para in s.split('\n'):
   words=para.split();line=''
   for word in words:
    test=(line+' '+word).strip()
    if stringWidth(test,font,size)>width and line:self.text(x,yy,line,size,color,bold);yy+=leading;line=word
    else:line=test
   if line:self.text(x,yy,line,size,color,bold);yy+=leading
   elif not words:yy+=leading
  return yy
 def circle(self,x,y,r,fill=BG,stroke=INK,sw=2):
  self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>');PDF.setFillColor(HexColor(fill));PDF.setStrokeColor(HexColor(stroke));PDF.setLineWidth(sw);PDF.setDash([]);PDF.circle(x,H-y,r,fill=1,stroke=1)
 def arrow(self,x1,y1,x2,y2,color=TEAL,sw=3,dash=None):
  self.line(x1,y1,x2,y2,color,sw,dash);a=math.atan2(y2-y1,x2-x1);l=9
  self.poly([(x2,y2),(x2-l*math.cos(a-.5),y2-l*math.sin(a-.5)),(x2-l*math.cos(a+.5),y2-l*math.sin(a+.5))],color,color)
 def box(self,x,y,w,h,title,body,fill=PALE,dash=None):
  self.rect(x,y,w,h,fill,INK,1.3,dash);self.text(x+17,y+29,title,21,INK,True);self.para(x+17,y+56,body,w-34,16,MUT,leading=22)
 def finish(self,source):
  self.line(62,849,1378,849,LINE)
  self.text(62,874,source,10,MUT)
  self.text(1378,874,f'STUDY  |  02 OCT 2026  |  {self.n:02}',10,MUT,anchor='end')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"><title>Astraea planning sheet {self.n}</title>'+''.join(self.parts)+'</svg>'
  (OUT/f'{self.n:02}_planning_sheet.svg').write_text(svg)
  PDF.restoreState();PDF.showPage()

baseline=json.loads((ROOT/'inputs/historical_baseline.json').read_text())
features=json.loads((ROOT/'inputs/atlas_allocations.json').read_text())
before=json.loads((ROOT/'inputs/before_conflicts.json').read_text())
hull=baseline['hull_plan_zx_m']
Y=[0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5]

def convex(points):
 pts=sorted(set(points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[]
 for p in pts:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 hi=[]
 for p in reversed(pts):
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]

def source_key(r):return (r['deck'],tuple(r['x']),tuple(r['z']),r['kind'])
# Study affiliation masks select entire historical allocations; they are not new construction footprints or ID assignments.
wing_defs=[('F-P','Forward port hotel','A1','Port forward commons',GOLD),('F-S','Forward starboard hotel','A2','Starboard forward commons',BLUE),('A-P','Aft hotel / port wing','B3','Port aft commons',GREEN),('A-S','Aft hotel / starboard wing','B4','Starboard aft commons',GREEN)]
wing_data=[]
for code,name,old,common,col in wing_defs:
 oldr=next(x for x in before['results'] if x['hotel']==old)
 selected=[{k:v for k,v in r.items() if k not in ['intersection_area_m2','fully_inside_proposal']} for r in oldr['overlapping_historical_allocations'] if r['kind']=='unlabelled_guest_allocation']
 commons=[r for r in features if r['kind']=='named_allocation' and r['deck']>=13 and r['name']==common]
 wing_data.append({'label':code,'proposed_identity':name,'historical_seed':old,'color':col,'entire_guest_allocations':selected,'retained_common_allocations':commons,'registry_room_membership':'unresolved; no IDs assigned','geometry_status':'affiliation study, not a wall/slab/shaft envelope'})

def hullplan(p,x,y,s,deck=13):
 z=lambda v:x+(v+541)*s; xx=lambda v:y+(v+120)*s
 p.poly([(z(zz),xx(a)) for zz,a in hull],PALE,INK,1.6)
 for r in features:
  if r['deck']==deck and r['kind']=='unlabelled_guest_allocation':p.rect(z(r['z'][0]),xx(r['x'][0]),(r['z'][1]-r['z'][0])*s,(r['x'][1]-r['x'][0])*s,'#D9E0DC',None)
 p.rect(z(-64),xx(-48),128*s,96*s,BG,TEAL,1.7)
 p.text(z(0),xx(0)+4,'ATRIUM',14,TEAL,True,'middle')
 p.rect(z(-265),xx(-118),150*s,84*s,ROSE,INK,1.3)
 p.text(z(-190),xx(-76),'THEATER',13,INK,True,'middle')
 p.text(x,y-16,'BOW  Z -541',14,MUT);p.text(x+1082*s,y-16,'STERN  Z +541',14,MUT,False,'end')
 return z,xx

# 1 preferred hybrid, representative actual upper allocations
p=Page(1,'Preferred hybrid   shared districts and distinct hotels','Three proposed hotel identities, with two aft wings. Existing public destinations remain shared; upper affiliation regions follow complete historical allocations.')
z,xx=hullplan(p,90,192,1.16,13)
for wing in wing_data:
 rr=[r for r in wing['entire_guest_allocations']+wing['retained_common_allocations'] if r['deck']==13]
 pts=[]
 for r in rr:
  p.rect(z(r['z'][0]),xx(r['x'][0]),(r['z'][1]-r['z'][0])*1.16,(r['x'][1]-r['x'][0])*1.16,wing['color'],INK,.45)
  pts += [(z(zz),xx(a)) for zz in r['z'] for a in r['x']]
 p.poly(convex(pts),None,TEAL,1.8,'6,5')
 common=next(r for r in rr if r['kind']=='named_allocation');cx=z(sum(common['z'])/2);cy=xx(sum(common['x'])/2)
 p.text(cx,cy+5,wing['label'],16,INK,True,'middle')
for zz in [-432,-216,-72,216,432]:p.circle(z(zz),xx(0),4,BG,RUST,2)
p.line(z(-541),xx(0),z(-64),xx(0),TEAL,2);p.line(z(64),xx(0),z(541),xx(0),TEAL,2)
p.text(90,519,'Representative D13 plan. Dashed outlines indicate proposed affiliation only, not walls, floor cuts or capacity.',17,MUT)
p.text(90,549,'Selected neighborhoods: 327 of 880 historical upper guest rectangles; geometry records, not assigned units or capacity.',17,INK,True)
p.text(90,575,'Remaining accommodations are unaffiliated. Atrium floor ring and detailed supported routes are omitted.',16,MUT)
p.box(62,595,405,150,'F-P   forward port','Upper homes use complete allocations and the port forward commons. Orchard market, Shared table, music and D12 quiet rooms remain shared destinations.',GOLD)
p.box(517,595,405,150,'F-S   forward starboard','Upper homes use complete allocations and starboard forward commons. Thread & shell, Orchard food hall, two cinemas and Stillroom remain public.',BLUE)
p.box(972,595,405,150,'A-P / A-S   one aft hotel','Two upper wings retain their complete aft commons. Many worlds gallery and Reading nooks remain public; the shared ship route connects the wings.',GREEN)
p.para(62,799,'Preferred direction, pending review: hotel identity comes from its arrival, local service and residential character. It does not privatize every destination below its neighborhood.',1310,18,INK)
p.finish('Revision 2 | Atlas pp. 11-19 and preserved v1 conflict screen. No unit assignment, physical core or upper-hull fit is claimed.')

# 2 arrivals and double circulation
p=Page(2,'Arrival and service relationships','Use retained commons as shared arrival places. Proposed local cores connect neighborhoods; their shafts, doors, capacity and structural fit remain unallocated.')
p.box(62,162,340,126,'Existing ship arrival','Townline fore Z -432 / aft +432\nCurrent express deck travel retained\nPublic access stays available',PALE)
p.box(529,162,352,126,'Public district destinations','D09 retail / D10 dining / D11 culture\nD12 Horizon, libraries and salons\nMoonwell stack remains a shared anchor',GOLD)
p.box(1008,162,370,126,'Proposed local guest core','Legible hotel arrival and wayfinding\nConnect to stacked commons\nNo shaft footprint selected',BLUE,'7,5')
p.arrow(405,225,521,225,TEAL,3);p.arrow(885,225,1000,225,TEAL,3,'7,5')
p.text(62,337,'Retained commons and upper home relationships',24,INK,True)
rows=[('F-P','Port forward commons','X -97..-63 / Z -384..-356','Quiet forward cluster'),('F-S','Starboard forward commons','X +63..+97 / Z -384..-356','Forward social / family cluster'),('A-P','Port aft commons','X -97..-63 / Z +356..+384','Aft court-facing homes'),('A-S','Starboard aft commons','X +63..+97 / Z +356..+384','Aft court-facing homes')]
y=382
for code,title,bounds,relation in rows:
 p.text(62,y,code,20,TEAL,True);p.text(139,y,title+' on D13-D17',20,INK,True);p.text(139,y+26,bounds,16,MUT)
 p.arrow(668,y+5,758,y+5,TEAL,2,'6,4');p.text(783,y+3,relation,19,INK);p.text(783,y+28,'Whole allocations; exact unit affiliation and views unresolved',16,MUT)
 y+=82
p.text(62,755,'Separate staff route',23,RUST,True)
p.para(62,786,'D03 crew / D01 supplies -> existing service network -> proposed local service core -> floor support edge. Keep cart access, guest privacy and both public/service door mechanisms distinct. Exact landings and apertures remain unknown.',1308,18,MUT)
p.finish('Relationship diagram only. Commons bounds are historical atlas allocations. Dashed links are proposed; they certify no walking or lift path.')

# 3 true-elevation sectional strategy
p=Page(3,'Section strategy   retain public layers and connect above','Hotel arrival and residential character grow around stacked commons. The public programs and their capacity remain in their existing historical allocations.')
ys=lambda v:705-(v-44)*7.1
columns=[(182,327,'Forward port','F-P'),(582,327,'Forward starboard','F-S'),(982,327,'Aft paired wings','A-P / A-S')]
for x,w,title,lab in columns:
 p.text(x,161,title,22,INK,True)
 p.rect(x,ys(106.5),w,ys(84)-ys(106.5),BLUE,INK,1.2,'7,5')
 p.text(x+w/2,ys(99),'Upper residential clusters',17,INK,True,'middle')
 p.text(x+w/2,ys(94.5),'Unit sizes and level ownership open',14,MUT,False,'middle')
 p.rect(x,ys(88.5),w,ys(84)-ys(88.5),GREEN,INK,1)
 p.text(x+w/2,ys(85.5),'D13 shared commons / arrival',14,INK,True,'middle')
 p.rect(x,ys(84),w,ys(52.5)-ys(84),GOLD,INK,1)
 p.text(x+w/2,ys(80.5),'D12 public library / salons',14,INK,True,'middle')
 p.text(x+w/2,ys(73.5),'D11 culture retained',15,INK,False,'middle')
 p.text(x+w/2,ys(65.5),'D10 dining retained',15,INK,False,'middle')
 p.text(x+w/2,ys(56.5),'D09 retail retained',15,INK,False,'middle')
 # cores are connection intent at undefined lateral position
 p.line(x+w-27,ys(52.5),x+w-27,ys(106.5),TEAL,3,'6,5')
 p.line(x+w-14,ys(52.5),x+w-14,ys(106.5),RUST,3,'6,5')
for d in range(8,19):
 v=Y[d-1];p.text(62,ys(v)+5,f'D{d:02}  {v:g} m',15,MUT)
 for x,w,_,_ in columns:p.line(x,ys(v),x+w,ys(v),LINE,1)
p.text(182,205,'81 luxury units shipwide; exact locations and upper roof clearance remain unresolved.',17,RUST)
p.text(62,745,'Section is schematic across three neighborhoods; it does not project one continuous private hotel volume.',17,MUT)
p.para(62,781,'Dashed guest/service cores show connection intent only. Shafts and penetrations remain unlocated. Preserve theater openings D12-D14 and gallery interfaces D12/D13.',635,17,INK)
p.para(765,781,'Multistory luxury units must reconcile occupied levels, clear heights and a single bookable identity. No second floor or expanded room adds a guest unit or establishes permitted passenger capacity.',610,17,MUT)
p.finish('Exact Y levels retained. Colored program layers describe ownership/use, not measured room-area availability or structural feasibility.')

# 4 explicit public conflict disposition
p=Page(4,'Before and after   preserve the affected public program','The hybrid removes the assumption that a hotel outline owns its full vertical projection. All listed public footprints, IDs and recorded capacities are retained.')
cols=[62,383,817,1378]
for a,b,t in zip(cols,cols[1:],['v1 intersection','Retained allocation / capacity','v2 disposition']):p.rect(a,163,b-a,42,INK,None);p.text(a+12,190,t,17,'#FFFFFF',True)
rows=[
('A1 / A2 on D09','Orchard market; Thread & shell','Shared public retail base. No storefront or function removed.'),
('A1 / A2 on D10','Shared table 240; Orchard food hall 240','Retain both complete venues and reservations; hotel identity grants no exclusive ownership.'),
('A1 / A2 on D11','Music room; Cinemas 2 and 3, 200 each','Public culture remains continuous. Local hotel cores must find space without taking those envelopes.'),
('A1 / B1 on D12','Horizon room; Listening salon','Retain public entries and quiet destination use beneath/alongside the forward port neighborhood.'),
('A2 / B2 on D12','Stillroom; Long library','Retain public entries and library activity. Link by wayfinding to forward starboard arrival.'),
('A3 / B3 / B4 on D12','Many worlds gallery; Reading nooks','Retain public programs serving both aft wings and the rest of the ship.'),
('Forward commons D13-D17','Entire port and starboard forward commons','Use as shared arrival/court anchors. No boundary cuts or assumed privatization.'),
('Guest footprint boundary cuts','Complete historical allocations retained','Remove clipped boundary fragments from the study. Affiliation remains provisional until IDs and actual contours return.'),
('Aft commons outside v1 masks','Entire port and starboard aft commons','Include them as retained shared arrival anchors, without changing either physical allocation.')]
y=205
for i,row in enumerate(rows):
 h=59
 for j,txt in enumerate(row):
  p.rect(cols[j],y,cols[j+1]-cols[j],h,'#FFFFFF' if i%2==0 else '#EEF1ED',LINE,.7)
  p.para(cols[j]+12,y+19,txt,cols[j+1]-cols[j]-24,15,INK if j<2 else MUT,leading=19)
 y+=h
p.para(62,791,'Disposition is a planning commitment to preserve these allocations. It does not prove a new core fits, that the final guest polygon is recovered, or that a hotel can accommodate its eventual unit mix.',1300,18,INK)
p.finish('Named allocations matched to atlas directories and source IDs. Full before/after records and exact bounds are in the editable disposition ledger.')

# 5 actual vertically aligned public anchors + hard gates
p=Page(5,'Public vertical anchors and the remaining fit decisions','The preferred hybrid links to real destinations. Historical planar alignment is useful evidence; it is not permission for a new void, water route or floor opening.')
p.text(62,168,'Moonwell has a corroborated historical stack',22,INK,True)
p.para(62,206,'All three allocations share X -54..-8 and Z -250..-182 in the atlas:',612,18,MUT)
for y,title,body,col in [(263,'D10   Lantern restaurant','D10_banquet2 | 240 recorded places',GOLD),(352,'D09   Paper Moon books','D09_books2 | retained public bookshop',BLUE),(441,'D08   Mineral springs','D08_bath2 | retained aquatic destination',GREEN)]:
 p.box(62,y,610,71,title,body,col)
p.para(62,562,'Keep these rooms and their public access. Connect the forward hotel neighborhoods to the shared stack through the existing ship network and proposed local arrival links. Internal Moonwell shafts, sculpted contours and openings remain unrecovered.',610,18,INK)
p.text(62,709,'Vesper requires the missing change record',22,INK,True)
p.para(62,746,'Vesper dining and D08 Gentle waters align at X +8..+54 / Z +182..+250. The old D09 Living gifts allocation lies between them. Preserve all three until the later two-level/waterfall revision is reconciled.',610,17,MUT)
p.text(769,168,'Hard evidence gates before physical layout',22,INK,True)
gates=[('1','Recover ID-to-room geometry','Actual room polygons, doors, beds, floor aliases and the accepted pre-loss changes.'),('2','Reconcile 1,000 units and 81 luxury','Exact unit sizes, berths, tier IDs and multistory ownership; no capacity inferred from footprint counts.'),('3','Fit the local circulation','Distinct guest/service shafts, landings, turning space, moving doors and supported paths.'),('4','Verify the upper envelope','Local hull/roof profile, usable headroom and structural/service depth.'),('5','Preserve useful existing programs','Any genuine change to a protected footprint, interface or capacity needs an explicit decision.')]
y=214
for n,t,b in gates:p.text(769,y,n,19,TEAL,True);p.text(806,y,t,20,INK,True);p.para(806,y+27,b,558,17,MUT);y+=112
p.para(769,809,'The D09 connected component kit can progress with adjustable interfaces while these ship-level checks remain open.',606,17,INK)
p.finish('Moonwell/Vesper: atlas pp. 10-12 plus historical conversation. Name equivalence and later modifications remain explicitly subject to review.')
PDF.save()

# Before/after disposition and unchanged source crosswalk
named={}
for result in before['results']:
 for r in result['overlapping_historical_allocations']:
  if r['stable_id'] and r['kind']=='named_allocation':
   if r['stable_id'] not in named:named[r['stable_id']]={'stable_id':r['stable_id'],'historical_name':r['name'],'deck':r['deck'],'x_m':r['x'],'z_m':r['z'],'historical_capacity':next(q['registered_capacity'] for q in baseline['rooms'] if q['id']==r['stable_id']),'v1_intersections':[]}
   named[r['stable_id']]['v1_intersections'].append(result['hotel'])
for r in named.values():r.update({'v2_disposition':'retain full public allocation, use, ID and recorded capacity','hotel_exclusive_ownership':False,'room_reassignment':None,'implementation_status':'proposal only; no runtime modification'})
ledger={'schema':'astraea_preferred_hybrid_v2','date':'2026-10-02','preferred_strategy':'three hotel identities with four upper wings; mixed-use public lower levels retained','authority':'preferred proposal, not accepted canon or implemented layout','v1_history':'Unchanged delivered v1 PDF and editable archive preserved under history/','source_policy':'Historical source allocations, not a current runtime survey','illustrated_coverage':{'selected_upper_guest_geometry_records':327,'total_historical_upper_guest_geometry_records':880,'remaining_accommodation_affiliation':'unaffiliated','count_meaning':'geometry records, not assigned units or capacity'},'public_allocation_dispositions':list(named.values()),'upper_wing_studies':wing_data,'commons_policy':'Retain complete forward/aft commons on D13-D17 as shared arrival/court anchors; do not privatize or cut them.','core_policy':'Guest and service core relationships are proposed. Footprints, apertures, capacity and penetrations remain unallocated; current express travel stays.','units':{'guest_total':1000,'luxury_within_total':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'registry_to_new_hotel_assignment':None,'capacity_from_intersected_footprint_counts':None,'passenger_hard_cap':2000,'normal_occupancy':[1200,2000]},'moonwell':{'status':'old atlas horizontal allocations corroborate historical three-level grouping; internal new geometry not recovered','x_m':[-54,-8],'z_m':[-250,-182],'ids':['D08_bath2','D09_books2','D10_banquet2']},'vesper':{'status':'later two-level/waterfall report requires missing change record; D09 intervening allocation retained','x_m':[8,54],'z_m':[182,250],'old_stack_ids':['D08_pool7','D09_florist7','D10_banquet7']},'unresolved':['Exact room ID-to-geometry mapping','Final sculpted guest polygons and accepted later changes','81 luxury unit sizes, levels, berths and IDs','Local guest/service core footprint and safe routes','Upper hull profile and usable headroom','Moonwell internal connections','Vesper second level and water path']}
ledger['units']['crew_including_player']=400
ledger['units']['player_home']='shared crew room; exact current ID unresolved'
ledger['units']['species']=['Koblins','Mantelids','Humans','Baelins','Munkos','Mindos']
ledger['units']['privacy']='Court-facing sleeping rooms are allowed; privacy and acoustics are selective design decisions.'
(OUT/'Astraea_hybrid_disposition_ledger_v2.json').write_text(json.dumps(ledger,indent=2))
programs={1:'logistics',2:'engineering',3:'crew_homes_and_operations',4:'habitat_homes',5:'medical_species_care',6:'botanical',7:'active_resort',8:'aquatic_wellness',9:'retail_social',10:'dining',11:'culture',12:'library_observation',13:'quiet_homes',14:'mixed_homes',15:'adaptive_homes',16:'family_homes',17:'premier_homes',18:'command'}
cross={'schema':'astraea_reversible_program_crosswalk_v2','total_records':len(baseline['rooms']),'rooms':[{'existing_id':r['id'],'historical_name':r['name'],'deck':r['deck'],'historical_kind':r['kind'],'historical_family':r['family_id'],'historical_capacity':r['registered_capacity'],'program_group':programs[r['deck']],'proposed_hotel_id':None,'hybrid_disposition':named[r['id']]['v2_disposition'] if r['id'] in named else 'Retained; exact new hotel membership unresolved'} for r in baseline['rooms']]}
(OUT/'Astraea_1462_ID_crosswalk_v2.json').write_text(json.dumps(cross,indent=2))
readme='''Astraea Preferred Hybrid District Study v2\n02 October 2026\n\nThis is a reversible planning revision. No runtime, floor cuts, room moves, new capacity or current-project edits were made.\n\nPreferred strategy\nThree proposed hotel identities with four upper residential wings. The lower public programs remain shared destinations in their existing historical allocations. Whole historical guest allocations and complete forward/aft commons replace boundary-clipped rectangles as study references. These affiliation regions are not new walls, slab edges or final unit assignments.\n\nFiles\nAstraea_Hybrid_District_Study_v2.pdf: five reviewed planning sheets\neditable/: vector SVG sheets, before/after conflict disposition ledger, unchanged-ID program crosswalk\ninputs/: retained source metadata, atlas-extracted allocation bounds, v1 conflict findings and licensed DejaVu fonts\nbuild_hybrid_study.py and validate_hybrid_study.py: self-contained regeneration and checks (Python 3 with reportlab and PyMuPDF)\nhistory/: unchanged delivered v1 PDF, editable archive and manifest\n\nLimits\nAll 1,462 IDs are retained. No room IDs are assigned to a new hotel. Complete historical rectangles are used for affiliation sketches because current room polygons and door/bed mappings are missing. Intersected rectangle counts are not hotel capacity. Only 327 of 880 historical upper guest geometry records are illustrated; remaining accommodations are unaffiliated. These are geometry records, not assigned units or capacity. The exact 81 luxury allocations, unit sizes, multistory floor relationships and upper-hull fit remain open. Proposed local guest and service cores have no assigned shafts or floor penetrations.\n\nHistorical evidence\nAstraea-current-layout-atlas.pdf, 1 October 2026, pages 10-19: named rooms and actual allocation rectangles. Coordinate conversion calibrated against the 1,082m hull, 46x68m salon allocation and 84x150m theater.\nAstraea_Master_Design_Source.zip, version 2: whole_ship_coverage.json, SHIP_DESIGN.md, AUDITORIUMS.md and D09 architectural briefs. These are dated source claims, not verification of the missing current runtime.\nMoonwell conversation grouping is corroborated by aligned D08/D09/D10 old allocations. The Vesper two-level waterfall design is still a historical conversation report; the old atlas has D09 Living gifts between Vesper and Gentle waters. No unsupported floor opening is implied.\n\nRevision disposition\nAll named public overlaps remain public in the hybrid. Physical feasibility of added cores and final room geometry is still unproven. A genuine protected-capacity, footprint or interface change requires a separate decision.\n'''
(ROOT/'README.txt').write_text(readme)
print('Created v2 five-sheet PDF, editable SVGs, disposition ledger and unchanged-ID crosswalk')
