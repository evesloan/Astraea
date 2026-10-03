"""Original vector-like pixel artwork, reproducible with Python/Pillow; no reference pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
B=Path(__file__).resolve().parents[1]
F=Path(__file__).parent/'fonts/DejaVuSans.ttf'
def font(s): return ImageFont.truetype(str(F),s)
def center(d,s,y,size,col):
 bb=d.textbbox((0,0),s,font=font(size));d.text(((768-bb[2])/2,y),s,font=font(size),fill=col)
im=Image.new('RGB',(768,1280),(26,36,53));d=ImageDraw.Draw(im)
cream=(224,209,167);gold=(190,143,72);orange=(164,77,42)
d.rectangle((32,32,735,1247),outline=gold,width=3)
center(d,'GRAND LANTERN',74,34,cream);center(d,'THEATRE  /  D11',124,22,gold)
# Abstract authored orrery, twelve worlds with differing angular positions.
for r in (112,192,272):d.ellipse((384-r,565-r,384+r,565+r),outline=gold,width=3)
for i in range(12):
 a=i*math.pi/6+.18;r=(112,192,272)[i%3];x=384+r*math.cos(a);y=565+r*math.sin(a);rr=10+3*(i%3)
 d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=cream if i%3==0 else orange,outline=gold,width=2)
d.ellipse((353,534,415,596),fill=cream)
center(d,'A THOUSAND',910,45,cream);center(d,'SMALL WORLDS',973,45,cream)
center(d,'PROGRAMME STUDY',1100,23,gold)
center(d,'WORLDS IN MOTION · STORIES TOGETHER',1160,17,cream)
im.save(B/'textures/programme_original.png')
im=Image.new('RGB',(768,256),(26,36,53));d=ImageDraw.Draw(im);d.rectangle((10,10,757,245),outline=gold,width=3)
center(d,'USHER',42,60,cream);center(d,'PROGRAMMES  /  WAYFINDING',144,28,gold)
im.save(B/'textures/usher_original.png')
