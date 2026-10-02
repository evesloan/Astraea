"""Original abstract arrival art; deterministic raster, no external font or artwork."""
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(512,1024),(221,218,203));d=ImageDraw.Draw(im)
teal=(56,98,97);clay=(179,108,83);wal=(79,73,61);pale=(194,191,174)
font={'A':['01110','10001','10001','11111','10001','10001','10001'],'E':['11111','10000','10000','11110','10000','10000','11111'],'G':['01111','10000','10000','10111','10001','10001','01111'],'I':['11111','00100','00100','00100','00100','00100','11111'],'L':['10000','10000','10000','10000','10000','10000','11111'],'R':['11110','10001','10001','11110','10100','10010','10001'],'S':['01111','10000','10000','01110','00001','00001','11110'],'T':['11111','00100','00100','00100','00100','00100','00100'],'U':['10001','10001','10001','10001','10001','10001','01110'],'V':['10001','10001','10001','10001','10001','01010','00100']}
def word(s,x,y,k,c):
 for l in s:
  for j,row in enumerate(font[l]):
   for i,b in enumerate(row):
    if b=='1':d.rectangle((x+i*k,y+j*k,x+(i+1)*k-1,y+(j+1)*k-1),fill=c)
  x+=6*k
word('GUEST',50,65,14,teal);word('ARRIVAL',50,185,7,wal)
d.rectangle((50,280,462,288),fill=wal)
# Offset nested court silhouettes: illustration only, no asserted route or map.
d.rounded_rectangle((70,360,426,740),radius=92,fill=teal)
d.rounded_rectangle((133,419,366,682),radius=61,fill=(221,218,203))
d.rectangle((277,594,438,753),fill=(221,218,203))
d.ellipse((311,658,397,744),fill=clay)
d.rectangle((70,810,438,818),fill=pale)
for x,w in ((70,160),(266,172)):
 d.rectangle((x,858,x+w,877),fill=teal)
 d.rectangle((x,904,x+w-44,916),fill=clay)
im.save(P/'guest_arrival_original.png',optimize=True)
