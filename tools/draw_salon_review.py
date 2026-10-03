"""Plan and section evidence derived from the current authored salon profile."""
from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1];d=json.loads((root/'data/architecture/D09_salon5_profile.json').read_text());out=root/'artifacts';out.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="960" viewBox="0 0 1200 960">','<rect width="1200" height="960" fill="#14232b"/>','<style>text{font-family:sans-serif;fill:#e5efed;font-size:15px}.small{font-size:12px;fill:#a9bfbe}.title{font-size:25px;font-weight:bold}</style>']
def text(x,y,t,cls=''):s.append(f'<text x="{x}" y="{y}" class="{cls}">{t}</text>')
def line(a,b,color='#8ca5a7',width=2,dash=''):s.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
def pt(x,z):return (100+(x-46)*14,130+(z+36)*14)
def polygon(points,fill,stroke='#c1d3cd',width=2):s.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
text(50,48,'D09 CONVERSATION SALON | architectural review','title');text(50,76,'D09_salon5 • partial allocation • authored plan and ceiling section • unfinished interior','small')
# The current source's softened outer wall, with front glazing line retained.
P=d['boundary_xz'];path=[P[0]]
for i in range(1,len(P)-1):
 p=P[i];prev=P[i-1];nxt=P[i+1];la=math.dist(prev,p);lb=math.dist(nxt,p);r=min(1.4,la*.2,lb*.2);a=[p[k]+(prev[k]-p[k])*r/la for k in range(2)];b=[p[k]+(nxt[k]-p[k])*r/lb for k in range(2)]
 for j in range(5):t=j/4;path.append([(1-t)**2*a[k]+2*(1-t)*t*p[k]+t*t*b[k] for k in range(2)])
path.append(P[-1]);polygon([pt(*p) for p in path],'#30454b')
for z in [-30,-24,-18,-12,-6,0]:line(pt(52,z),pt(76,z),'#40575c',1,'3,6')
for lo,hi in [(-34,-27),(-27,-21),(-21,-15),(-15,-9),(-9,-2.64),(2.64,4)]:line(pt(52,lo),pt(52,hi),'#8be0de',5)
line(pt(50.72,-2.64),pt(52,-2.64),'#dbb76f',5);line(pt(50.72,2.64),pt(52,2.64),'#dbb76f',5)
for a,b in zip([(58,-3),(58.3,-6),(59.2,-8.5)],[(58.3,-6),(59.2,-8.5),(61,-10)]):line(pt(*a),pt(*b),'#58a4a8',5)
outer=[pt(68+3.8*math.cos(math.radians(a)),-12+3.8*math.sin(math.radians(a))) for a in range(-75,76,5)]
inner=[pt(68+2.55*math.cos(math.radians(a)),-12+2.55*math.sin(math.radians(a))) for a in reversed(range(-75,76,5))]
polygon(outer+inner,'#4b8d93','#e8d9ae',2)
route=[(48,0),(56,0),(63,-4),(66,-12),(63,-20.5),(63,-24)]
for a,b in zip(route,route[1:]):line(pt(*a),pt(*b),'#eca75c',3,'6,4')
for x,z,label in [(63.5,-27,'Book / seat return'),(61,-15,'Higher gathering'),(55,-24,'Glazed gallery')]:
 p=pt(x,z);s.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="4" fill="#f5d8a0"/>');text(p[0]+8,p[1]-8,label,'small')
text(95,710,'PLAN: source-derived schematic in ship X/Z; final furnishing remains incomplete.','small')
text(170,122,'X52','small');text(495,122,'X76','small');text(65,164,'Z-34','small');text(65,690,'Z+4','small')
text(290,141,'24 m overall','small');text(540,380,'38 m','small')
line((690,700),(730,700),'#eca75c',3,'6,4');text(740,705,'Tested player route','small')
text(690,160,'SECTION THROUGH X60 m');text(690,185,'Room ceiling stays below the next deck','small')
def sec(z,h):return (690+(z+34)*11,570-h*38)
polygon([sec(-34,8.26),sec(4,8.26),sec(4,8.5),sec(-34,8.5)],'#a6b3b0')
profile=[(-34,4.2),(-24,4.2),(-18,5.6),(4,5.6)]
polygon([sec(z,h) for z,h in profile]+[sec(z,h+.18) for z,h in reversed(profile)],'#d4c6a6')
line(sec(-34,0),sec(4,0),'#dbe4df',4)
for h,label in [(0,'D09 floor'),(4.2,'Reading: 4.2 m'),(5.6,'Gathering: 5.6 m'),(8.5,'D10 floor: 8.5 m')]:
 a=sec(-34,h);line(a,(a[0]+418,a[1]),'#57717a',1,'3,5');text(a[0]+4,a[1]-9,label,'small')
text(690,620,'Furniture omitted from this section','small');text(690,643,'The gallery edge has its own lower profile','small')
text(50,770,'Checked in the running ship:','title')
for i,t in enumerate(['• Existing portal and terrace routes remain connected','• Oblique arrival, gathering and reading approach pass player-capsule sweeps','• Six section probes include the exact transition crease; nine optical exits checked','• No loaded-cart, all-species, NPC seating or final visual acceptance is claimed']):text(60,808+i*28,t)
s.append('</svg>');svg='\n'.join(s);(out/'D09_salon_plan_section.svg').write_text(svg)
try:
 import cairosvg
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out/'D09_salon_plan_section.png'))
except ImportError:
 from PIL import Image,ImageDraw,ImageFont
 import xml.etree.ElementTree as ET
 canvas=Image.new('RGB',(1200,960));draw=ImageDraw.Draw(canvas)
 for e in ET.fromstring(svg):
  tag=e.tag.split('}')[-1];a=e.attrib
  if tag=='rect':draw.rectangle((0,0,float(a['width']),float(a['height'])),fill=a['fill'])
  elif tag=='polygon':
   points=[tuple(map(float,p.split(','))) for p in a['points'].split()];draw.polygon(points,fill=a['fill']);draw.line(points+[points[0]],fill=a['stroke'],width=int(float(a['stroke-width'])))
  elif tag=='circle':
   x,y,r=map(float,(a['cx'],a['cy'],a['r']));draw.ellipse((x-r,y-r,x+r,y+r),fill=a['fill'])
  elif tag=='line':
   x,y,u,v=map(float,(a['x1'],a['y1'],a['x2'],a['y2']));dash=a.get('stroke-dasharray','')
   if not dash:draw.line((x,y,u,v),fill=a['stroke'],width=int(float(a['stroke-width'])))
   else:
    on,off=map(float,dash.split(','));length=math.hypot(u-x,v-y);position=0
    while position<length:
     end=min(length,position+on);draw.line((x+(u-x)*position/length,y+(v-y)*position/length,x+(u-x)*end/length,y+(v-y)*end/length),fill=a['stroke'],width=int(float(a['stroke-width'])));position+=on+off
  elif tag=='text':
   c=a.get('class','');size=25 if c=='title' else 12 if c=='small' else 15
   font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if c=='title' else '')+'.ttf'
   font=ImageFont.truetype(font_path,size) if Path(font_path).exists() else ImageFont.load_default()
   draw.text((float(a['x']),float(a['y'])),e.text or '',font=font,fill='#a9bfbe' if c=='small' else '#e5efed',anchor='ls')
 canvas.save(out/'D09_salon_plan_section.png')
print(out/'D09_salon_plan_section.svg')
