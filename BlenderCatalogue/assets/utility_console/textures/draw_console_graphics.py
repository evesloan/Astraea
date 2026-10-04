"""Original utility-console print artwork. No reference-photo pixels or live data.
Run with system Python + Pillow. The PNG is an ordinary unlit-by-itself base color.
"""
from pathlib import Path
import json, math, hashlib
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
I=Image.new('RGB',(1024,1024),(193,200,190));d=ImageDraw.Draw(I)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(x,y,s,n=24,fill=(208,220,213),bold=False):
 d.text((x,y),s,font=ImageFont.truetype(BOLD if bold else FONT,n),fill=fill)
def line(pts,fill=(116,161,166),w=6):d.line(pts,fill=fill,width=w,joint='curve')
zones={'schematic':[0,0,640,440],'header':[0,460,640,540], 'button_legend':[0,560,640,640], 'service_label':[0,660,640,760], 'selector_legend':[660,0,1024,300], 'gauge_dial':[660,340,1024,704], 'cable_tag':[660,740,1024,850]}
# Recessed printed circuit mimic. Its quiet palette is pigment, never emission.
d.rectangle((0,0,639,439),fill=(31,47,50));d.rounded_rectangle((14,14,625,425),radius=12,outline=(119,145,145),width=3)
text(34,26,'UTILITY RETURN',35,bold=True);text(36,77,'FLOW PATH  /  03',19,fill=(164,187,181))
line([(66,270),(66,150),(223,150),(223,224),(396,224),(396,150),(564,150),(564,320),(65,320)])
for x,y in [(150,150),(470,150),(150,320),(470,320)]:
 d.polygon([(x,y-10),(x+18,y),(x,y+10)],fill=(184,202,182))
d.rectangle((168,120,275,186),fill=(45,66,69),outline=(185,204,195),width=4)
for x in range(181,265,18):line([(x,130),(x-8,174)],(158,180,172),3)
d.ellipse((349,180,441,270),fill=(48,67,71),outline=(185,204,195),width=4)
d.polygon([(380,199),(421,225),(380,251)],fill=(148,181,182))
text(163,192,'FILTER',21);text(344,280,'CIRCULATE',20);text(33,352,'RETURN',25,bold=True)
text(390,370,'PRINTED MIMIC',15,fill=(146,166,165))
d.rectangle((0,460,639,539),fill=(193,200,190));text(17,472,'WATER RECOVERY',33,fill=(40,53,54),bold=True)
text(491,483,'UC-03',24,fill=(40,53,54),bold=True)
d.rectangle((0,560,639,639),fill=(193,200,190))
for x,s in [(10,'START'),(235,'HOLD'),(438,'ISOLATE')]:text(x,578,s,33,fill=(40,53,54),bold=True)
d.rectangle((0,660,639,759),fill=(193,200,190));text(20,672,'SERVICE ACCESS',34,fill=(40,53,54),bold=True);text(23,719,'CONTROL WIRING  /  UC-03',19,fill=(66,80,78))
d.rectangle((660,0,1023,299),fill=(193,200,190));text(711,15,'MODE',39,fill=(40,53,54),bold=True)
text(668,135,'LOCAL',16,fill=(40,53,54));text(944,135,'REMOTE',16,fill=(40,53,54))
text(776,263,'OFF',24,fill=(40,53,54),bold=True)
# A static analogue dial. Separate geometry supplies the pointer in the model.
d.rectangle((660,340,1023,703),fill=(202,210,198));cx,cy=842,522
for i in range(21):
 a=math.radians(145+i*12.5);r1=123 if i%5==0 else 132;r2=146
 p=(cx+r1*math.cos(a),cy+r1*math.sin(a));q=(cx+r2*math.cos(a),cy+r2*math.sin(a));line([p,q],(50,65,64),5 if i%5==0 else 3)
text(770,452,'FILTER',29,fill=(40,53,54),bold=True);text(810,550,'ΔP',28,fill=(40,53,54),bold=True)
text(726,597,'RELATIVE',26,fill=(40,53,54));text(780,647,'STATIC',16,fill=(72,88,83))
d.rectangle((660,740,1023,849),fill=(193,200,190));text(680,751,'POWER / DATA',29,fill=(40,53,54),bold=True);text(682,798,'REAR ENTRY',25,fill=(40,53,54))
I.save(ROOT/'console_graphics.png')
(ROOT/'console_graphics.json').write_text(json.dumps({'authorship':'Original deterministic drawn lettering and circuit symbols, 2026-10-02. No photo pixels copied.','purpose':'Static printed purpose/legend artwork; no live telemetry, operating limits or simulated state.','resolution':[1024,1024],'zones_pixels_top_left':zones,'sha256':hashlib.sha256((ROOT/'console_graphics.png').read_bytes()).hexdigest(),'source':'draw_console_graphics.py','font_source':FONT},indent=2))
