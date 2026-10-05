"""Reproducible planning plates from the current source crosswalk, not game renders."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/whole_ship_plans';OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'data/whole_ship_layout.json').read_text());L=json.loads((ROOT/'data/spatial_layout.json').read_text());G=json.loads((ROOT/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];A=json.loads((ROOT/'data/reference/historical_atlas_allocations.json').read_text());H=json.loads((ROOT/'data/hull_envelope.json').read_text())['plan_xz_m']
CREW=json.loads((ROOT/'data/reference/D03_crew_envelopes.json').read_text())['records']
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(n):return ImageFont.truetype(font,n)
def plan(draw,deck,origin,scale,labels=False):
 def point(x,z):return(origin[0]+(z+541)*scale,origin[1]+(x+120)*scale)
 def polygon(points,fill,outline=None,width=1):draw.polygon([point(x,z)for x,z in points],fill=fill,outline=outline,width=width)
 def rectangle(x,z,fill,outline=None,width=1):polygon([(x[0],z[0]),(x[1],z[0]),(x[1],z[1]),(x[0],z[1])],fill,outline,width)
 polygon(H,'#edf0f1','#465962',2)
 for r in L['regions']:
  if r['deck']==deck:polygon(r['boundary'],'#d7dfe2')
 for v in L['voids']:
  if deck in v['decks']:polygon(v['boundary'],'#ffffff','#dc9850',1)
 for r in P['programmes']:
  if r['deck']!=deck:continue
  rectangle(r['allocation_x'],r['allocation_z'],None,'#237c88'if r['geometry_owner']else'#647984',2 if labels else 1)
 for c in CREW:
  if deck=='D03':rectangle(c['x'],c['z'],'#93a9b4','#54717f')
 for g in G:
  if f"D{g['deck']:02}"==deck:rectangle(g['x'],g['z'],'#d6bd79','#a49060')
 for r in A:
  if r['kind']=='unlabelled_shop_allocation'and f"D{r['deck']:02}"==deck:rectangle(r['x'],r['z'],'#bdcadb','#748caa')
 if int(deck[1:])in range(13,18):
  for c in P['residential_court_reservations']:
   polygon(c['boundary'],'#e0cce9','#8e55a7',2)
   rectangle(c['arrival_focus_x'],c['arrival_focus_z'],'#faf9f5','#8e55a7',1)
 if deck in ['D08','D09']:
  for c in P['aquatic_section_reservations']:rectangle(c['x'],c['z'],'#abd7db','#3f8d97',2)
 for c in P['longitudinal_vertical_core_reservations']:rectangle(c['x'],c['z'],'#68b39c' if c.get('geometry_owner') else '#e38c88','#296b5d' if c.get('geometry_owner') else '#a34b46',2)
 for c in P.get('staff_riser_reservations',[]):rectangle(c['shaft_x'],c['shaft_z'],'#52747e','#284a56',1)
 if labels:
  for r in P['programmes']:
   if r['deck']==deck:
    x=sum(r['allocation_x'])/2;z=sum(r['allocation_z'])/2
    draw.text(point(x,z),r['programme_key'][-2:],font=f(11),fill='#203943',anchor='mm')
for deck in P['decks']:
 im=Image.new('RGB',(1440,650),'#faf9f5');d=ImageDraw.Draw(im)
 key=deck['deck'];d.text((36,20),f"ASTRAEA / {key} / floor {deck['floor_y']:g} m",font=f(25),fill='#203943')
 d.text((36,57),'Working plan: allocation crosswalk + proposed vertical reservations. NOT final architecture.',font=f(15),fill='#555f65')
 plan(d,key,(65,94),1.2,True)
 d.text((36,392),'Bow left / port above | Light grey: hull guide / darker grey: structural regions / outlines: programmes | Gold: guest allocations | Blue-grey: retail addresses',font=f(11),fill='#465962')
 d.text((36,414),'Purple: proposed residential courts | Red: public lift/stair cores; dark blue: staff risers | Cyan: proposed pool/market section | Orange: existing voids',font=f(11),fill='#465962')
 rows=sorted([r for r in P['programmes']if r['deck']==key],key=lambda r:r['programme_key'])
 for i,r in enumerate(rows):
  x=36+(i//7)*700;y=452+(i%7)*25
  d.text((x,y),r['programme_key'][-2:]+'  '+r['name'],font=f(15),fill='#203943')
 im.save(OUT/(key+'.png'))
canvas=Image.new('RGB',(1440,1100),'#faf9f5');d=ImageDraw.Draw(canvas)
d.text((25,18),'ASTRAEA / WHOLE-SHIP LAYOUT ACCOUNTING',font=f(29),fill='#203943')
d.text((25,58),'18 decks · 161 directory programmes · 1,000 guest allocations · 100 retail addresses · 400 crew target',font=f(17),fill='#465962')
d.text((25,87),'Working plans: central/forward cores authored; other reservations proposed. Source coverage is not finished construction.',font=f(16),fill='#8c4b45')
for i,deck in enumerate(P['decks']):
 col=i%3;row=i//3;x=25+col*472;y=139+row*142
 d.text((x,y),f"{deck['deck']}   {deck['floor_y']:g} m   {len(deck['programme_keys'])} programmes / {deck['crew_bank_envelope_count'] if deck['deck']=='D03' else deck['guest_envelope_count']} {'crew allocations' if deck['deck']=='D03' else 'guest units'}",font=f(14),fill='#203943')
 plan(d,deck['deck'],(x,y+29),.40)
d.text((25,1010),'Gold: guest allocations. Blue-grey: retail addresses. Purple: proposed landscaped house courts; pale centres retain local arrivals.',font=f(17),fill='#465962')
d.text((25,1037),'Green: authored public cores. Red: planned public cores. Dark blue: staff risers. Cyan: pool reservation. Outlines: programmes.',font=f(17),fill='#465962')
d.text((25,1064),'Crew berth fit, luxury replacement layouts, hull section and complete guest/service routes remain open gates.',font=f(17),fill='#8c4b45')
canvas.save(OUT/'overview.png')
print(OUT/'overview.png')
# Longitudinal coordination section. Deliberately labelled vertical exaggeration.
section=Image.new('RGB',(1440,720),'#faf9f5');d=ImageDraw.Draw(section)
d.text((28,18),'ASTRAEA / LONGITUDINAL SECTION COORDINATION',font=f(27),fill='#203943')
d.text((28,59),'Working reservations. Port and starboard projected together. Vertical scale is 2.61x horizontal for readability.',font=f(16),fill='#8c4b45')
sx=1.15;sy=3.0;ox=110;oy=462
def sec(z,y):return(ox+(z+541)*sx,oy-y*sy)
def block(z0,z1,y0,y1,fill,outline):
 a=sec(z0,y1);b=sec(z1,y0);d.rectangle([a,b],fill=fill,outline=outline,width=2)
d.rectangle([sec(-541,118),sec(541,0)],outline='#8f999d',width=1)
for deck in P['decks']:
 y=deck['floor_y'];d.line([sec(-541,y),sec(541,y)],fill='#dce2e3',width=1)
 d.text((18,sec(0,y)[1]-6),f"{deck['deck']}  {y:g}m",font=f(10),fill='#465962')
block(-64,64,6,106.5,'#ffffff','#dca364')
d.text(sec(-52,66),'Central atrium',font=f(14),fill='#915b2c')
d.text(sec(-52,60),'D02–D17',font=f(13),fill='#915b2c')
block(-265,-115,78,93,'#f7e8d3','#dca364')
d.text(sec(-256,88),'Theater upper volume',font=f(11),fill='#915b2c')
for court in P['residential_court_reservations']:
 block(court['z'][0],court['z'][1],84,106.5,'#e0cce9','#8e55a7')
for z in [-370,370]:d.text(sec(z-53,113),'P/S house courts',font=f(12),fill='#714283')
for core in P['longitudinal_vertical_core_reservations']:
 block(core['z'][0],core['z'][1],0,106.5,'#68b39c' if core.get('geometry_owner') else '#e8b2ae','#296b5d' if core.get('geometry_owner') else '#a34b46')
 z=sum(core['z'])/2;d.text(sec(z-22,-5),f'{z:g}m',font=f(12),fill='#a34b46')
block(-459,-405,44,61,'#abd7db','#3f8d97')
d.text(sec(-510,74),'Raised pool / market',font=f(12),fill='#347883')
d.line([sec(-453,67),sec(-432,61)],fill='#347883',width=2)
d.text(sec(-256,88),'Theater upper volume',font=f(11),fill='#915b2c')
d.text((110,502),'Five public lift/stair cores plus ten separate staff risers. Shaft, landing, route and hull fitting remain unfinished',font=f(15),fill='#465962')
d.text((28,544),'KEY SECTION DECISIONS',font=f(19),fill='#203943')
notes=['Four proposed residential courts span D13–D17, following the room banks, with22.5m between base and cover.',
'Forward pool: arrival 44m; proposed wet deck 46.2m; basin bottom 44.8m; market overlook 52.5m; dining above 61m.',
'Proposed basin stays above D08 floor; sports clearances, ramp, lift and water structure still require verification.',
'The 118m box is the reference height envelope, not a resolved hull section. No new slab openings are made by this diagram.']
for i,text in enumerate(notes):d.text((28,582+i*28),text,font=f(15),fill='#465962')
section.save(OUT/'longitudinal_section.png')
