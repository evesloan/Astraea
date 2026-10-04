"""Original raster cover/sign/screen layouts. Pillow only; no external fonts or images."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'textures';OUT.mkdir(parents=True,exist_ok=True)
# Original compact five-column display alphabet; glyphs are pixel construction data.
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','11011','10001'],'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],'9':['01110','10001','10001','01111','00001','00001','01110'],
'-':['00000','00000','00000','11111','00000','00000','00000'],':':['00000','00100','00100','00000','00100','00100','00000'],'/':['00001','00010','00010','00100','01000','01000','10000'],'.':['00000','00000','00000','00000','00000','00100','00100'],'>':['10000','01000','00100','00010','00100','01000','10000']}
def text(draw,xy,txt,scale,color):
 x,y=xy
 for char in txt:
  for row,line in enumerate(FONT.get(char,['00000']*7)):
   for col,val in enumerate(line):
    if val=='1':draw.rectangle((x+col*scale,y+row*scale,x+(col+1)*scale-1,y+(row+1)*scale-1),fill=color)
  x+=6*scale
records={}
def save(name,im,description):
 p=OUT/(name+'.png');im.save(p);records[name]={'file':str(p.relative_to(ROOT)),'size_px':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'description':description,'meters_per_tile_uv':[1,1],'roughness':.73}
cream=(232,221,188);ink=(37,57,58);teal=(45,90,94);clay=(142,65,48);ochre=(175,131,66)
for i,(name,title,sub,col) in enumerate([('periodical_orbit','ORBIT','SKY / FIELD',teal),('periodical_terra','TERRA','LIVING SYSTEMS',clay),('periodical_form','FORM','CRAFT / DESIGN',ochre)]):
 im=Image.new('RGB',(384,512),cream);d=ImageDraw.Draw(im);d.rectangle((0,0,384,150),fill=col);text(d,(24,30),title,10,cream);text(d,(24,113),'JOURNAL  0'+str(i+1),3,cream)
 if i==0:
  d.ellipse((87,211,297,421),fill=teal);d.ellipse((145,258,244,357),fill=cream);d.arc((27,253,360,377),5,355,fill=ink,width=7);d.line((48,200,316,434),fill=ochre,width=5)
 elif i==1:
  for j in range(5):d.polygon([(30+j*60,409),(47+j*60,245-j%2*45),(65+j*60,409)],fill=col)
  d.arc((34,226,347,440),180,357,fill=ink,width=7)
 else:
  for j in range(3):
   x=48+j*98;d.polygon([(x,404),(x+70,404),(x+58,240+j*25),(x+28,216+j*25)],fill=col);d.line((x+18,405,x+35,240+j*25),fill=cream,width=5)
 text(d,(24,459),sub,3,ink);save(name,im,'Original face-out journal cover, purpose-drawn diagram and title; no copied pixels')
im=Image.new('RGB',(1024,640),(25,49,55));d=ImageDraw.Draw(im)
d.rectangle((0,0,1024,110),fill=(210,222,211));text(d,(32,28),'ASTRAEA LIBRARY',7,ink)
text(d,(34,141),'FIND A BOOK',6,cream);d.rectangle((30,212,992,277),fill=(232,230,205));text(d,(51,229),'TITLE / AUTHOR / SUBJECT',4,ink)
text(d,(35,321),'BROWSE',4,(127,186,178));text(d,(35,377),'01  NATURAL WORLD',4,cream);text(d,(35,430),'02  ARTS AND CRAFT',4,cream);text(d,(35,483),'03  VOYAGE RECORDS',4,cream)
d.rectangle((654,318,990,563),outline=(127,186,178),width=3);text(d,(679,341),'DIRECTORY',4,cream)
# A simple collection index, deliberately no assertion of the missing ship's plan.
for j,col in enumerate([(125,172,159),(176,130,81),(174,97,74)]):
 d.rectangle((680+j*98,404,741+j*98,477),fill=col);text(d,(697+j*98,422),str(j+1),5,ink)
d.line((684,507,952,507),fill=cream,width=5);d.polygon([(950,498),(967,507),(950,516)],fill=cream);text(d,(702,529),'COLLECTIONS',3,cream)
d.line((30,588,992,588),fill=(97,137,137),width=2);text(d,(35,605),'SELECT A COLLECTION  >',3,cream)
save('catalogue_screen',im,'Original static catalogue and collection-index screen art. Illustrative information architecture, not original ship plan or functional UI')
for name,txt in [('label_current','CURRENT ISSUES'),('label_archive','BACK ISSUES / STORAGE'),('label_search','SEARCH'),('label_map','INDEX'),('label_back','BACK'),('label_select','SELECT'),('label_service','SERVICE'),('label_light','LIGHT')]:
 im=Image.new('RGB',(max(256,len(txt)*24+24),64),cream);d=ImageDraw.Draw(im);text(d,(12,18),txt,4,ink);save(name,im,'Original purpose label: '+txt)
for name,col in [('opal_diffuser',(233,230,207)),('reflector',(224,227,215)),('display_glass',(41,66,69))]:
 im=Image.new('RGB',(64,64),col);d=ImageDraw.Draw(im)
 for y in range(0,64,4):d.line((0,y,63,y),fill=tuple(max(0,c-3) for c in col))
 save(name,im,'Original restrained component color and texture')
(ROOT/'texture_manifest.json').write_text(json.dumps({'revision':'library-use-art-01','provenance':'Original pixel geometry and compact display alphabet, no external font/model/reference pixel inputs','generator':'source/make_use_art.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'materials':records},indent=2))
print('ART_READY',len(records))
