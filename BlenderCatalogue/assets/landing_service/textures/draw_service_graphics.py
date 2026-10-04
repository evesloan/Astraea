"""Original simple service symbols and bitmap lettering, no external art/fonts.
Pillow is used only to reproduce these authored raster inputs, not by Blender build.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parent
CREAM=(224,229,216);DARK=(31,39,39);BLUE=(47,79,97);OPAL=(205,219,218)
roles={}
def save(role,im,colour):
 p=BASE/(role+'.png');im.save(p,optimize=False);roles[role]={'file':p.name,'colour_srgb_8bit':list(colour),'roughness':.78,'metallic':0,'meters_per_tile_uv':[1,1],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Original family-local service graphic; no new shared material revision'}
im=Image.new('RGB',(128,128),BLUE);d=ImageDraw.Draw(im)
# Attention bell: domed cap, two solid sides, flared lip and visible clapper.
d.ellipse((40,24,88,80),fill=CREAM);d.rectangle((39,50,89,88),fill=CREAM);d.polygon([(39,77),(28,94),(100,94),(89,77)],fill=CREAM);d.ellipse((56,98,72,111),fill=CREAM);d.rectangle((60,16,68,26),fill=CREAM)
save('landing_service_request_symbol',im,BLUE)
im=Image.new('RGB',(128,128),DARK);d=ImageDraw.Draw(im)
# Open-jaw wrench, robust diagonal handle with contrasting circular end eye.
d.line([(40,89),(83,45)],fill=CREAM,width=19);d.ellipse((23,78,53,108),fill=CREAM);d.ellipse((32,87,44,99),fill=DARK);d.ellipse((67,19,111,63),fill=CREAM);d.polygon([(93,15),(117,35),(91,41),(83,31)],fill=DARK)
save('landing_service_inspection_symbol',im,DARK)
im=Image.new('RGB',(128,128),OPAL);d=ImageDraw.Draw(im)
# Inactive status: open circular indicator plus centred horizontal dash.
d.ellipse((25,25,103,103),outline=DARK,width=10);d.rectangle((44,59,84,69),fill=DARK)
save('landing_service_inactive_symbol',im,OPAL)
# Own compact 5x7 bitmap alphabet; no font or generated lettering dependency.
font={'S':['01111','10000','10000','01110','00001','00001','11110'],'E':['11111','10000','10000','11110','10000','10000','11111'],'R':['11110','10001','10001','11110','10100','10010','10001'],'V':['10001','10001','10001','10001','10001','01010','00100'],'I':['11111','00100','00100','00100','00100','00100','11111'],'C':['01111','10000','10000','10000','10000','10000','01111']}
im=Image.new('RGB',(512,64),CREAM);d=ImageDraw.Draw(im);text='SERVICE';scale=8;x=(512-(len(text)*6-1)*scale)//2;y=4
for ch in text:
 for yy,row in enumerate(font[ch]):
  for xx,value in enumerate(row):
   if value=='1':d.rectangle((x+xx*scale,y+yy*scale,x+(xx+1)*scale-1,y+(yy+1)*scale-1),fill=DARK)
 x+=6*scale
save('landing_service_legend_graphic',im,CREAM)
(BASE/'manifest.json').write_text(json.dumps({'provenance':'Original authored raster symbols and hand-coded bitmap letters; no external artwork or fonts','revision':'landing-service-graphics-01','roles':roles},indent=2))
