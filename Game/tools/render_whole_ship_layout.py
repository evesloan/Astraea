"""Reproducible planning plates from the current source crosswalk, not game renders."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/whole_ship_plans';OUT.mkdir(exist_ok=True)
P=json.loads((ROOT/'data/whole_ship_layout.json').read_text());L=json.loads((ROOT/'data/spatial_layout.json').read_text());G=json.loads((ROOT/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];A=json.loads((ROOT/'data/reference/historical_atlas_allocations.json').read_text());H=json.loads((ROOT/'data/hull_envelope.json').read_text())['plan_xz_m']
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
 for g in G:
  if f"D{g['deck']:02}"==deck:rectangle(g['x'],g['z'],'#d6bd79','#a49060')
 for r in A:
  if r['kind']=='unlabelled_shop_allocation'and f"D{r['deck']:02}"==deck:rectangle(r['x'],r['z'],'#bdcadb','#748caa')
 if int(deck[1:])in range(13,18):
  for c in P['residential_court_reservations']:rectangle(c['x'],c['z'],'#d0b4df','#8e55a7',2)
 if deck in ['D08','D09']:
  for c in P['aquatic_section_reservations']:rectangle(c['x'],c['z'],'#abd7db','#3f8d97',2)
 for c in P['longitudinal_vertical_core_reservations']:rectangle(c['x'],c['z'],'#e38c88','#a34b46',2)
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
 d.text((36,414),'Purple: proposed residential courts | Red: proposed vertical cores | Cyan: proposed pool/market section | Orange: existing voids',font=f(11),fill='#465962')
 rows=sorted([r for r in P['programmes']if r['deck']==key],key=lambda r:r['programme_key'])
 for i,r in enumerate(rows):
  x=36+(i//7)*700;y=452+(i%7)*25
  d.text((x,y),r['programme_key'][-2:]+'  '+r['name'],font=f(15),fill='#203943')
 im.save(OUT/(key+'.png'))
canvas=Image.new('RGB',(1440,1100),'#faf9f5');d=ImageDraw.Draw(canvas)
d.text((25,18),'ASTRAEA / WHOLE-SHIP LAYOUT ACCOUNTING',font=f(29),fill='#203943')
d.text((25,58),'18 decks · 161 directory programmes · 1,000 guest allocations · 100 retail addresses · 400 crew target',font=f(17),fill='#465962')
d.text((25,87),'Working reservations only. Complete source coverage does not mean a finalized or constructed ship.',font=f(16),fill='#8c4b45')
for i,deck in enumerate(P['decks']):
 col=i%3;row=i//3;x=25+col*472;y=139+row*142
 d.text((x,y),f"{deck['deck']}   {deck['floor_y']:g} m   {len(deck['programme_keys'])} programmes / {deck['guest_envelope_count']} guest units",font=f(14),fill='#203943')
 plan(d,deck['deck'],(x,y+29),.40)
d.text((25,1010),'Gold: guest allocations. Blue-grey: retail addresses. Purple: four proposed residential courts.',font=f(17),fill='#465962')
d.text((25,1037),'Red: five proposed vertical cores. Cyan: raised pool / market overlook reservation. Grey outlines: programmes.',font=f(17),fill='#465962')
d.text((25,1064),'Crew berth fit, luxury replacement layouts, hull section and complete guest/service routes remain open gates.',font=f(17),fill='#8c4b45')
canvas.save(OUT/'overview.png')
print(OUT/'overview.png')
