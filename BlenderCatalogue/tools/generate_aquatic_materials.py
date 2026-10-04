"""Original restrained aquatic-finish pixels; references guide palette, not source pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib,random
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'materials/aquatic';OUT.mkdir(parents=True,exist_ok=True)
SPEC={'aquatic_clay_sling':((176,99,68),.80,0,'sling',[.6,.6]),'aquatic_teal_sling':((44,105,104),.81,0,'sling',[.6,.6]),'aquatic_satin_alloy':((155,169,170),.47,.7,'alloy',[.75,.75]),'aquatic_orange_float':((208,111,53),.58,0,'moulded',[.8,.8]),'aquatic_pearl_float':((210,214,207),.62,0,'moulded',[.8,.8]),'aquatic_dark_grip':((35,48,48),.9,0,'grip',[.4,.4]),'aquatic_edge_tile':((51,109,112),.48,0,'tile',[.8,.8])}
rows={}
for i,(role,(col,rough,metal,kind,scale)) in enumerate(SPEC.items()):
 rng=random.Random(52400+i);im=Image.new('RGB',(256,256));p=im.load();phase=rng.random()*math.tau
 for y in range(256):
  for x in range(256):
   u,v=x/256,y/256;d=1.1*math.sin(math.tau*(u+2*v)+phase)+.7*math.cos(math.tau*(3*u-v))
   if kind=='sling':d+=2.5*(1 if (x//4+y//4)%2 else -1)+1.3*math.cos(math.tau*x/8)
   elif kind=='alloy':d+=.8*math.cos(math.tau*x/16)
   elif kind=='grip':d+=1.5*(1 if (x//8+y//8)%2 else -1)
   elif kind=='tile':
    tile=(x//64+3*(y//64))%5;d+=(tile-2)*1.8
    if x%64<2 or y%64<2:d=-18
   p[x,y]=tuple(max(0,min(255,round(c+d))) for c in col)
 im.save(OUT/(role+'.png'));rows[role]={'file':role+'.png','colour_srgb_8bit':col,'roughness':rough,'metallic':metal,'meters_per_tile_uv':scale,'alpha_mode':'OPAQUE','double_sided':False,'sha256':hashlib.sha256((OUT/(role+'.png')).read_bytes()).hexdigest()}
(OUT/'manifest.json').write_text(json.dumps({'revision':'astraea-aquatic-materials-01','provenance':'Original deterministic colour textures. No reference pixels, external texture packs or game shader. Finish intent only, no real-world material certification.','materials':rows},indent=2)+'\n')
s=Image.new('RGB',(768,852),(22,30,31));d=ImageDraw.Draw(s)
for i,role in enumerate(SPEC):
 x=i%3*256;y=i//3*284;s.paste(Image.open(OUT/(role+'.png')),(x,y));d.text((x+5,y+262),role,fill='white')
s.save(OUT/'contact_sheet.png');print('Created',len(rows),'original aquatic roles')
