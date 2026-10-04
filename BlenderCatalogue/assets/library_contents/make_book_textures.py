"""Original 256px book materials. All pixels are generated; no reference sampling.
Raster letters use a tiny deliberately limited hand-authored glyph alphabet.
"""
from pathlib import Path
import json, random, math, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
TEX=ROOT/'textures'; TEX.mkdir(exist_ok=True)
records={}

def tile(role,base,kind,scale):
    rng=random.Random(211+len(role));im=Image.new('RGB',(256,256));p=im.load()
    for y in range(256):
        for x in range(256):
            n=rng.uniform(-2.3,2.3)
            if kind=='cloth':n+=(1.7 if (x%4==0) != (y%4==0) else -1.0)+.5*math.sin(x*.08)
            elif kind=='edges':n+=(-12 if y%11==0 else -4 if y%4==0 else 1)+1.4*math.sin(x*.04)
            else:n+=.8*math.sin(x*.03)+.5*math.cos(y*.08)
            p[x,y]=tuple(max(0,min(255,round(v+n))) for v in base)
    im.save(TEX/(role+'.png'),optimize=True)
    records[role]={'base_color_file':role+'.png','colour_srgb_8bit':base,'meters_per_tile_uv':scale,'roughness':.82,'metallic':0,'original_pixel_recipe':kind}
    return im
for role,base in [('book_cover_teal',(54,101,101)),('book_cover_clay',(155,76,54)),('book_cover_ochre',(172,137,73))]:tile(role,base,'cloth',[.07,.10])
tile('book_paper_edges',(210,201,169),'edges',[.08,.0256])
tile('book_label_paper',(230,222,192),'paper',[.028,.037])
tile('book_print_ink',(64,72,63),'paper',[.06,.08])
GLYPHS={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'E':['11111','10000','10000','11110','10000','10000','11111'],
 'F':['11111','10000','10000','11110','10000','10000','10000'],
 'I':['111','010','010','010','010','010','111'],
 'L':['10000','10000','10000','10000','10000','10000','11111'],
 'N':['10001','11001','11001','10101','10011','10011','10001'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],
 'R':['11110','10001','10001','11110','10100','10010','10001'],
 'S':['01111','10000','10000','01110','00001','00001','11110'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'V':['10001','10001','10001','10001','10001','01010','00100'],
 'D':['11110','10001','10001','10001','10001','10001','11110'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],
 'C':['01111','10000','10000','10000','10000','10000','01111'],
 'B':['11110','10001','10001','11110','10001','10001','11110'],
 ' ':['000','000','000','000','000','000','000']}
def word(draw,text,xy,scale=1):
 x,y=xy
 for ch in text:
  g=GLYPHS[ch]
  for j,row in enumerate(g):
   for i,b in enumerate(row):
    if b=='1':draw.rectangle((x+i*scale,y+j*scale,x+(i+1)*scale-1,y+(j+1)*scale-1),fill=(70,82,75))
  x+=(len(g[0])+1)*scale
for role,is_chart in [('folio_text_page',False),('folio_chart_page',True)]:
 im=tile(role,(231,223,195),'paper',[.176,.219]);d=ImageDraw.Draw(im)
 word(d,'ASTRAEA',(28,22),2);d.line((28,42,225,42),fill=(128,111,79),width=2)
 word(d,'FIELD NOTES' if not is_chart else 'ORBITAL ATLAS',(28,51),1)
 if not is_chart:
  word(d,'OBSERVATIONS',(28,82),1)
  for block in range(3):
   for line in range(5):
    yy=98+block*43+line*6;end=213 if line<4 else 161+block*13
    d.line((28,yy,end,yy),fill=(130,128,107),width=1)
    for xx in (53+line*2,99+block*3,140-line*4,178+line):d.line((xx,yy,xx+4,yy),fill=(231,223,195))
  d.rectangle((28,226,31,232),fill=(140,107,74));d.line((37,229,89,229),fill=(140,107,74))
 else:
  d.ellipse((48,86,206,218),outline=(151,131,87),width=1)
  d.ellipse((72,104,183,199),outline=(96,118,111),width=2)
  d.ellipse((98,126,158,177),outline=(151,131,87),width=1)
  d.ellipse((118,142,134,158),fill=(178,134,79),outline=(120,99,65))
  for p in [(91,111),(182,154),(71,207)]:d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=(80,105,98))
  d.line((32,153,225,153),fill=(150,150,125),width=1);d.line((127,76,127,224),fill=(150,150,125),width=1)
  d.line((34,226,72,211),fill=(155,87,64),width=2);d.line((34,226,42,224),fill=(155,87,64),width=2)
  for i in range(4):d.line((31,236+i*3,94+i*17,236+i*3),fill=(125,133,114),width=1)
 im.save(TEX/(role+'.png'),optimize=True)
 records[role]['original_pixel_recipe']='Original hand-designed typography, research page marks and orbital diagram; all generated from code'
 records[role]['mapping']='Single semantic page layout with physical .176 by .219 metre UV rectangle, not a mixed-role atlas'
for r in records.values():r['sha256']=hashlib.sha256((TEX/r['base_color_file']).read_bytes()).hexdigest()
(ROOT/'texture_manifest.json').write_text(json.dumps({'interface_revision':'library-texture-paths-02','texture_root':'textures','path_base':'directory_containing_this_manifest','base_color_file_resolution':'texture_root/base_color_file','resolution_px':[256,256],'provenance':'Original procedural colour pixels and hand-authored glyphs. No copied image pixels, external models, or font files.','materials':records},indent=2))
