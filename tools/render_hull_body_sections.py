from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
b=json.loads((R/'data/architecture/LOWER_HULL_BODY.json').read_text());s=json.loads((R/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text());u=json.loads((R/'data/architecture/UPPER_SECTION_COORDINATION.json').read_text())
im=Image.new('RGB',(1500,1080),'#f7f5ee');d=ImageDraw.Draw(im)
def f(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def text(p,t,n=17,c='#233943'):d.text(p,t,font=f(n),fill=c)
def dashed(a,b,c='#aa763d',width=2):
 dx=b[0]-a[0];dy=b[1]-a[1];count=max(1,int((dx*dx+dy*dy)**.5/9))
 for i in range(0,count,2):d.line([(a[0]+dx*i/count,a[1]+dy*i/count),(a[0]+dx*min(i+1,count)/count,a[1]+dy*min(i+1,count)/count)],fill=c,width=width)
text((36,24),'ASTRAEA / BODY AND ROOF SECTIONS',30)
text((36,70),'Built lower shell and circulation, with the upper enclosing volumes still proposed',20)
text((36,104),'Selected structure only; fitted districts are omitted. Room fit, windows and the upper hull remain unfinished.',16,'#7c6250')
def lon(z,y):return(91+(z+541)*1.21,514-y*2.8)
text((36,150),'LONGITUDINAL / centreline body; upper pavilions projected from both sides',18)
for level in s['levels']:
 y=level['floor_y'];d.line([lon(-541,y),lon(541,y)],fill='#d8d9d2');text((20,lon(0,y)[1]-7),level['deck'],11,'#66747b')
outline=[lon(min(p[1]for p in ring['outer']),ring['y'])for ring in b['rings']]+[lon(max(p[1]for p in ring['outer']),ring['y'])for ring in reversed(b['rings'])]
d.polygon(outline,fill='#d7e0e2',outline='#486a77',width=3)
for zlo,zhi,ylo,yhi in [(-445,-412,0,105.9),(-113,-80,0,109.85),(106,139,102,109.85)]:d.rectangle([lon(zlo,yhi),lon(zhi,ylo)],fill='#77a295',outline='#356f5f',width=2)
for zlo,zhi,top in [(-180,202,114.5)]+[(min(q[1]for q in p['boundary']),max(q[1]for q in p['boundary']),p['external_roof_limit_y'])for p in u['private_upper_pavilions']]:
 for a,c in [(lon(zlo,106.5),lon(zlo,top)),(lon(zlo,top),lon(zhi,top)),(lon(zhi,top),lon(zhi,106.5))]:dashed(a,c)
text((91,535),'1,082 m calibrated plan length; vertical scale exaggerated for legibility',15,'#66747b')
text((36,582),'TRANSVERSE / midship lower body and reserved upper crown',18)
def cross(x,y):return(360+x*2.2,962-y*2.8)
points=[cross(min(p[0]for p in r['outer']),r['y'])for r in b['rings']]+[cross(max(p[0]for p in r['outer']),r['y'])for r in reversed(b['rings'])]
d.polygon(points,fill='#d7e0e2',outline='#486a77',width=3)
for y in [0,6,12,16.5,52.5,84,102,106.5]:
 d.line([cross(-120,y),cross(120,y)],fill='#d8d9d2');text((635,cross(0,y)[1]-7),str(y)+' m',11,'#66747b')
for a,c in [(cross(-120,16.5),cross(-120,106.5)),(cross(120,16.5),cross(120,106.5)),(cross(-120,106.5),cross(120,106.5)),(cross(-52,106.5),cross(-52,114.5)),(cross(-52,114.5),cross(52,114.5)),(cross(52,114.5),cross(52,106.5))]:dashed(a,c)
text((803,626),'CHECKED SECTION FIT',21)
for n,t in enumerate(['18 canonical deck elevations','161 directory allocations','1,000 guest source envelopes','200 crew-bank source envelopes','Existing compiled floors preserved']):text((810,675+n*34),'• '+t,19)
text((803,860),'Blue-grey: installed lower body',17,'#486a77')
text((803,890),'Green: installed public connections',17,'#356f5f')
text((803,920),'Dashed amber: future enclosing volumes',17,'#aa763d')
text((36,1010),'Keel −3.5 m · Maximum roof reservation 114.5 m · Overall height budget 118 m',18)
text((36,1043),'This plate is a design/implementation crosswalk, not a finished-ship render or structural engineering certification.',15,'#7c6250')
im.save(R/'docs/whole_ship_plans/hull_body_sections.png')
