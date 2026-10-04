"""Original deterministic textile weave and encoded glyph label art. No fonts or source images.
Python stdlib only; authorship/licence: original ASTRAEA component artwork, same project licence.
"""
from pathlib import Path
import struct,zlib,json,hashlib
BASE=Path(__file__).resolve().parent
GLYPHS={
'C':['01111','10000','10000','10000','10000','10000','01111'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'A':['01110','10001','10001','11111','10001','10001','10001'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'D':['11110','10001','10001','10001','10001','10001','11110']}
def png(path,w,h,pix):
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(pix[y*w*3:(y+1)*w*3])for y in range(h)),9))+chunk(b'IEND',b''))
def label(word,bg):
 w,h=512,128;p=list(bg)*(w*h)
 def rect(x,y,ww,hh,col):
  for j in range(y,y+hh):
   for i in range(x,x+ww):p[(j*w+i)*3:(j*w+i)*3+3]=col
 rect(16,16,8,96,(214,222,218));scale=11;left=49
 for n,ch in enumerate(word):
  for y,row in enumerate(GLYPHS[ch]):
   for x,v in enumerate(row):
    if v=='1':rect(left+n*66+x*scale,25+y*scale,scale,scale,(225,230,224))
 # Original folded-cloth pictogram, intentionally abstract; no hygiene symbol.
 for k in range(3):rect(420,42+k*20,60,8,(225,230,224))
 rect(420,34,60,7,(225,230,224));rect(420,34,7,68,(225,230,224));rect(473,34,7,68,(225,230,224))
 png(BASE/(word.lower()+'.png'),w,h,p)
def build():
 BASE.mkdir(exist_ok=True,parents=True);label('CLEAN',(38,83,80));label('USED',(117,79,44))
 roles={}
 for name,col in [('handling_canvas',(107,116,115)),('handling_linen',(196,209,204))]:
  p=[]
  for y in range(128):
   for x in range(128):
    v=(2 if x%4==0 else 0)+(-2 if y%4==0 else 0)+(1 if (x+y)%3==0 else 0);p.extend(max(0,min(255,c+v))for c in col)
  png(BASE/(name+'.png'),128,128,p);roles[name]={'file':name+'.png','meters_per_tile_uv':[.25,.25],'roughness':.94,'metallic':0}
 for word in ('clean','used'):roles['handling_'+word+'_graphic']={'file':word+'.png','meters_per_tile_uv':[1,1],'roughness':.86,'metallic':0}
 for r in roles.values():r['sha256']=hashlib.sha256((BASE/r['file']).read_bytes()).hexdigest()
 (BASE/'manifest.json').write_text(json.dumps({'provenance':'Original encoded 5x7 glyphs, folded textile pictogram and low-contrast weave; no external fonts or reference pixels','generator':'draw_handling_art.py','materials':roles},indent=2)+'\n')
if __name__=='__main__':build()
