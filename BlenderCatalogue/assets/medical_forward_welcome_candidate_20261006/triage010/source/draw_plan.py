"""Draw declared footprints and routes. Technical plan, not a game render."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];p=json.loads((R/'qa/UNBUILT_TRIAGE_ARRANGEMENT_PROPOSAL.json').read_text())
im=Image.new('RGB',(1440,1320),'#f4f2eb');d=ImageDraw.Draw(im)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda s:ImageFont.truetype(font_path,s)
def P(x,z):return(90+(x+44)*29,135+(z+468)*29)
def rect(v,color,width=3):
 x0,x1,z0,z1=v;a=P(x0,z0);b=P(x1,z1);d.rectangle((*a,*b),fill=color,outline='#344341',width=width)
def label(v,text,color='#213b39',size=17):
 x0,x1,z0,z1=v;a=P((x0+x1)/2,(z0+z1)/2);d.multiline_text(a,text,fill=color,font=f(size),anchor='mm',align='center',spacing=6)
d.text((75,35),'D05 | Connected medical source 010',font=f(32),fill='#1c3937')
d.text((75,83),'Proposed eight-pod wing and real admission link. Uninstalled source; existing Game remains the bounded welcome baseline.',font=f(17),fill='#374542')
old=[(-42,-450),(-8,-450),(-8,-433.8),(-7.8,-433.8),(-7.8,-430.2),(-8,-430.2),(-8,-429),(-14,-429),(-14,-442),(-42,-442)]
d.polygon([P(x,z)for x,z in old],fill='#ddd7c5',outline='#685d43',width=3)
for pod in p['proposed_pod_records']:
 v=pod['rect_x0_x1_z0_z1'];rect(v,'#c5d8d0');n=int(pod['id'][-2:]);label(v,f'TRIAGE {n:02}\n7 × 6 m gross\nSource fit only')
rect(p['cross_corridor_rect_xz'],'#e9efe5');label(p['cross_corridor_rect_xz'],'4 m CLINICAL CORRIDOR | 3.6 m clear route',size=18)
rect(p['admission_extension_rect_xz'],'#e7e5d9');label(p['admission_extension_rect_xz'],'ADMISSION\nEXTENSION\n\n3.6 m route',size=18)
# Source receiving opening across the existing admission end wall, X -12.8..-9.2.
a=P(-12.8,-450);b=P(-9.2,-450);d.line((*a,*b),fill='#258471',width=10)
label([-42,-28,-450,-442],'Existing diagnostic\nsupport child\n(partial source architecture)',size=16)
label([-28,-14,-450,-442],'Waiting / escort\n008 finish retained\n006 installed baseline',size=16)
label([-14,-8,-442,-429],'EXISTING\nADMISSION\n\nTO CORE →',size=17)
# Key at right.
x=1160;y=155
d.text((x,y),'PROPOSED ADDITION',font=f(19),fill='#1c3937');y+=40
for s in ['8 × 42 m² rooms','112 m² cross corridor','96 m² admission','544 m² total union','','Only pods 01–04 shift','4 m farther forward.','Pods 05–08 stay put.','','All eight IDs and','gross dimensions stay.','','Green threshold:','3.6 × 3.0 m aperture','with real shoulders','and a supported lintel.','','No new floor adopted.','No clinical operation','or capacity accepted.']:
 d.text((x,y),s,font=f(16),fill='#374542');y+=27
d.text((75,1245),'World X/Z metres. The technical footprint drawing does not show detailed source furniture or all wall thicknesses.',font=f(17),fill='#374542')
d.text((75,1276),'Floor 21 m | source vault top 25.73 m | recorded service band ends 26.76 m | D06 datum 27 m',font=f(17),fill='#374542')
out=R/'renders/010_declared_plan_source_proposal.png';assert not out.exists();im.save(out)
(R/'qa/PLAN_DRAWING_010.json').write_text(json.dumps({'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'Technical drawing of declared footprints, not a native game render or collision test','input':str(R/'qa/UNBUILT_TRIAGE_ARRANGEMENT_PROPOSAL.json')},indent=2)+'\n')
