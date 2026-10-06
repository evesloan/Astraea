"""Original printed calibration markings. No photographed or external artwork."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
R=Path(__file__).resolve().parents[1];p=R/'textures/dense_instruments.png'
im=Image.new('RGB',(1024,1024),(191,199,190));d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
labels=['01 / PRESSURE BALANCE','02 / PHASE COURTESY','03 / RELAY VERIFICATION','CALIBRATION / LOCAL ONLY','RELAY CASSETTE / 04','SERVICE MODULE / 07','RETURN / CHECKED','DIAGNOSTIC / ISOLATED','BALANCE TRIM','PHASE TRIM','RELAY TRIM','BENCH TESTER / STATIC','SUN CORP / MORALE','MORALE CALIBRATION','CONTACT TEST / LOCAL','BENCH / SWITCH TEST']
for i in range(32):
 x=(i%4)*256;y=(i//4)*128
 d.rectangle((x+2,y+2,x+253,y+125),fill=(185,193,184),outline=(53,68,67),width=3)
 if i<16:
  title=labels[i];size=19
  while ImageFont.truetype(bold,size).getlength(title)>236:size-=1
  d.rectangle((x+10,y+12,x+245,y+38),fill=(54,72,73))
  d.text((x+14,y+17),title,font=ImageFont.truetype(bold,size),fill=(205,214,205))
  for j in range(9):
   xx=x+15+j*27;d.line((xx,y+69,xx,y+91-(j%3)*7),fill=(63,77,72),width=2)
  d.text((x+14,y+99),'ASTRAEA / SVC 02   •   INSPECTED',font=ImageFont.truetype(font,12),fill=(55,70,68))
 elif 16<=i<20:
  d.rectangle((x+4,y+4,x+251,y+123),fill=(204,210,196))
  cx=x+128;cy=y+73
  for j in range(21):
   a=math.radians(198+j*7.2);rr=80;rr2=66 if j%5==0 else 73
   d.line((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.68,cx+math.cos(a)*rr2,cy+math.sin(a)*rr2*.68),fill=(40,57,57),width=3 if j%5==0 else 2)
  d.text((x+77,y+91),['kPa / TEST','DELTA / 01','BALANCE','INDEX'][i-16],font=ImageFont.truetype(bold,14),fill=(40,57,57))
  d.line((x+17,y+119,x+238,y+119),fill=(78,95,87),width=2)
 elif i==20:
  d.rectangle((x+4,y+4,x+251,y+123),fill=(23,48,49))
  for xx in range(16,246,23):d.line((x+xx,y+12,x+xx,y+111),fill=(44,73,71))
  for yy in range(12,112,20):d.line((x+15,y+yy,x+246,y+yy),fill=(44,73,71))
  pts=[(x+16+j,y+65+int(24*math.sin(j*.073)+9*math.sin(j*.14))) for j in range(230)];d.line(pts,fill=(152,190,166),width=3)
  d.text((x+22,y+15),'SAMPLE  04.6',font=ImageFont.truetype(font,12),fill=(155,187,174))
 else:
  text=['FUSES / 3A','BOLTS / M08','RETURNED','SERVICE / 02','MEASURE','VERIFIED','LOCAL ONLY','DATUM','CHECKED','TRIM','CLOSED'][i-21]
  d.text((x+15,y+22),text,font=ImageFont.truetype(bold,24),fill=(42,61,63));d.text((x+15,y+84),'AST / ENGINEERING',font=ImageFont.truetype(font,16),fill=(61,78,76))
im.save(p);(R/'textures/artwork_manifest.json').write_text(json.dumps({'original':True,'source':'draw_dense_graphics.py','image':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions_px':[1024,1024],'cells':[4,8],'use':'Pigment only; does not claim live telemetry or emissive lighting'},indent=2)+'\n');print(p)
