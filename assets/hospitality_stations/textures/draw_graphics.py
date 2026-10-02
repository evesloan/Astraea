from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
im=Image.new('RGB',(1024,512),(38,45,43));d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def label(box,title,sub):
 x,y,w,h=box
 d.rounded_rectangle((x+4,y+4,x+w-4,y+h-4),12,fill=(42,49,46),outline=(153,133,99),width=3)
 d.text((x+w/2,y+h*.30),title,font=ImageFont.truetype(font,40),anchor='mm',fill=(231,223,200))
 d.text((x+w/2,y+h*.69),sub,font=ImageFont.truetype(font,21),anchor='mm',fill=(181,199,185))
label((0,0,512,256),'STILL','PRESS TO POUR')
label((512,0,512,256),'SPARK','PRESS TO POUR')
label((0,256,512,256),'DISH RETURN','PLACE TRAY HERE')
label((512,256,512,256),'SERVICE CADDY','PULL TO REMOVE')
im.save(P/'station_graphics.png')
(P/'station_graphics.json').write_text(json.dumps({'original':True,'method':'Original local PIL drawn type and panel lines; DejaVu Sans lettering','size':[1024,512],'regions':{'still':[0,0,.5,.5],'spark':[.5,0,1,.5],'return':[0,.5,.5,1],'service':[.5,.5,1,1]},'sha256':hashlib.sha256((P/'station_graphics.png').read_bytes()).hexdigest()},indent=2))
