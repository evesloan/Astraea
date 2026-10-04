"""Original restrained staff-only tiles; no reference-image pixels are sampled."""
from pathlib import Path
import math,random,json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'materials/staff';OUT.mkdir(parents=True,exist_ok=True)
SPEC={
 'staff_white_paint':((181,187,183),.76,0,'paint',(1,1)),
 'staff_bluegrey_paint':((81,98,103),.78,0,'paint',(1,1)),
 'staff_zinc':((133,143,146),.61,.65,'metal',(.75,.75)),
 'staff_rubber':((31,39,39),.91,0,'rubber',(.75,.75)),
 'staff_opal':((205,219,218),.45,0,'opal',(.75,.75)),
 'staff_cable_red':((124,67,61),.82,0,'rubber',(.5,.5)),
 'staff_cable_blue':((47,79,97),.82,0,'rubber',(.5,.5)),
 'staff_label':((197,199,187),.86,0,'paint',(.5,.5)),
 'staff_floor':((119,127,124),.87,0,'floor',(.8,.8)),
}
rows={}
for num,(role,(colour,rough,metal,kind,scale)) in enumerate(SPEC.items()):
 rng=random.Random(326001+num);im=Image.new('RGB',(256,256));pix=im.load()
 phases=[rng.random()*math.tau for _ in range(3)]
 for y in range(256):
  for x in range(256):
   u,v=x/256,y/256
   broad=(math.sin(math.tau*(2*u+v)+phases[0])+math.sin(math.tau*(5*u-3*v)+phases[1])+math.cos(math.tau*(3*u+7*v)+phases[2]))/3
   delta=1.7*broad if kind in ('paint','opal') else 1.0*broad
   if kind=='metal':delta+=.9*math.sin(math.tau*y/16)
   if kind=='floor':delta=3.2*broad
   pix[x,y]=tuple(max(0,min(255,round(c+delta))) for c in colour)
 if kind=='floor':
  draw=ImageDraw.Draw(im)
  for i in range(155):
   x,y=rng.randrange(256),rng.randrange(256);r=rng.choice([1,1,2]);shift=rng.choice([-13,-8,7])
   cc=tuple(max(0,min(255,c+shift)) for c in colour)
   for a in [-256,0,256]:
    for b in [-256,0,256]:draw.ellipse((x-r+a,y-r+b,x+r+a,y+r+b),fill=cc)
 im.save(OUT/(role+'.png'))
 rows[role]={'file':role+'.png','colour_srgb_8bit':colour,'roughness':rough,'metallic':metal,'meters_per_tile_uv':scale,'sha256':hashlib.sha256((OUT/(role+'.png')).read_bytes()).hexdigest()}
(OUT/'manifest.json').write_text(json.dumps({'revision':'astraea-staff-materials-01','provenance':'Original deterministic staff-only texture art. Reference photographs guide purpose/finish only. No photo pixels copied.','materials':rows},indent=2)+'\n')
sheet=Image.new('RGB',(768,3*284),(25,31,32));d=ImageDraw.Draw(sheet)
for i,role in enumerate(SPEC):
 x=(i%3)*256;y=(i//3)*284;sheet.paste(Image.open(OUT/(role+'.png')),(x,y));d.text((x+6,y+263),role,fill='white')
sheet.save(OUT/'contact_sheet.png');print(json.dumps({'roles':len(rows),'output':str(OUT)}))
