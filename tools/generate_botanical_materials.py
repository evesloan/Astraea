"""Original coarse botanical texture art. No reference pixels sampled."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib,random
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'materials/botanical';OUT.mkdir(exist_ok=True,parents=True)
SPEC={'botanical_bark':((105,87,64),.91,'bark',[.6,1.2]),'botanical_leaf_jade':((50,95,63),.70,'leaf',None),'botanical_leaf_sage':((98,132,83),.77,'leaf',None),'botanical_leaf_olive':((116,128,61),.75,'leaf',None),'botanical_flower':((165,113,130),.79,'flower',None),'botanical_soil':((43,35,27),.96,'soil',[.5,.5])}
rows={}
for i,(role,(col,rough,kind,scale)) in enumerate(SPEC.items()):
 rng=random.Random(42410+i);soil_grid=[[rng.uniform(-5,5) for _ in range(16)] for _ in range(16)] if kind=='soil' else None;im=Image.new('RGB',(256,256));p=im.load()
 for y in range(256):
  for x in range(256):
   u,v=x/256,y/256
   broad=math.sin(math.tau*(u+2*v))*.7+math.cos(math.tau*(3*u-v))*.3
   delta=2.2*broad
   if kind=='bark':
    w=u+.013*math.sin(math.tau*v)+.009*math.cos(math.tau*(3*v+u))
    delta+=5*math.sin(math.tau*w*11)+2*math.sin(math.tau*w*23)
   elif kind=='leaf':
    # Per-leaf UV: U across midrib, V from root to tip. Broad stripes survive mip reduction.
    center=math.exp(-((u-.5)/.022)**2)*9
    seam=abs((v-(abs(u-.5)*.75))*7-round((v-abs(u-.5)*.75)*7))
    veins=math.exp(-(seam/.11)**2)*3.5
    delta+=center+veins+4*(1-abs(u-.5)*2)-4*v
   elif kind=='flower':delta+=8*(1-v)+3*math.cos(math.tau*u*3)
   elif kind=='soil':
    gx,gy=x/16,y/16;ix,iy=int(gx)%16,int(gy)%16;fx,fy=gx%1,gy%1;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
    aa=soil_grid[iy][ix]*(1-fx)+soil_grid[iy][(ix+1)%16]*fx
    bb=soil_grid[(iy+1)%16][ix]*(1-fx)+soil_grid[(iy+1)%16][(ix+1)%16]*fx
    delta=aa*(1-fy)+bb*fy
   p[x,y]=tuple(max(0,min(255,round(c+delta))) for c in col)
 if kind=='soil':
  d=ImageDraw.Draw(im)
  for j in range(65):
   x,y=rng.randrange(256),rng.randrange(256);rr=rng.choice([2,3]);shift=rng.choice([-5,5]);cc=tuple(c+shift for c in col)
   for a in (-256,0,256):
    for b in (-256,0,256):d.ellipse((x+a-rr,y+b-rr,x+a+rr,y+b+rr),fill=cc)
 im.save(OUT/(role+'.png'));rows[role]={'file':role+'.png','colour_srgb_8bit':col,'roughness':rough,'metallic':0,'uv_contract':'U across blade, V root-to-tip' if kind in ('leaf','flower') else 'metric repeat','meters_per_tile_uv':scale,'alpha_mode':'OPAQUE','double_sided':kind in ('leaf','flower'),'sha256':hashlib.sha256((OUT/(role+'.png')).read_bytes()).hexdigest()}
(OUT/'manifest.json').write_text(json.dumps({'revision':'astraea-botanical-materials-01','provenance':'Original deterministic texture art for new botanical components. References guide composition only; no reference pixels copied. Opaque RGB textures, no alpha masks, no wind or game shader.','materials':rows},indent=2)+'\n')
s=Image.new('RGB',(768,568),(25,31,29));d=ImageDraw.Draw(s)
for i,role in enumerate(SPEC):
 x=i%3*256;y=i//3*284;s.paste(Image.open(OUT/(role+'.png')),(x,y));d.text((x+5,y+262),role,fill='white')
s.save(OUT/'contact_sheet.png')
print('Created',len(rows),'original opaque botanical roles')
