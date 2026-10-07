from pathlib import Path
import math,json,hashlib,random
from PIL import Image
S=Path(__file__).parent;O=S/'textures';O.mkdir(exist_ok=True);N=128
recipes=[('finish_mineral_cream',(221,205,170),(2.,2.),.82),('finish_honey_timber',(142,95,50),(1.6,.36),.74)]
rows=[]
for name,base,tile,roughness in recipes:
 im=Image.new('RGB',(N,N));pixels=[]
 for y in range(N):
  for x in range(N):
   u=x/N;v=y/N
   if name=='finish_mineral_cream':
    # Original low-frequency warm mineral mottling, with restrained pores.
    value=3.3*math.sin(2*math.pi*(u+v))+2.0*math.sin(2*math.pi*(3*u-2*v))+1.4*math.cos(2*math.pi*(5*u+4*v))
    pore=1 if ((x*31+y*67+x*y*3)%127)<3 else 0
    delta=(value-2*pore,value*.92-2*pore,value*.70-pore)
   else:
    # Broad painted grain; no photographic input or fine high-contrast noise.
    phase=2*math.pi*(5*v+.08*math.sin(2*math.pi*u)+.03*math.sin(6*math.pi*u));g=8*math.sin(phase)+3*math.sin(2*phase)+2*math.cos(2*math.pi*u)
    delta=(g,g*.77,g*.45)
   pixels.append(tuple(round(max(0,min(255,b+d)))for b,d in zip(base,delta)))
 im.putdata(pixels);path=O/(name+'.png');im.save(path);rows.append({'role':name,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'image_size':[N,N],'meters_per_tile_uv':list(tile),'roughness':roughness,'metallic':0,'emission':False,'sampling':'Closest/REPEAT','scope':'Local new-source finish material only; no shared palette mutation'})
(S/'MATERIALS.json').write_text(json.dumps({'status':'ORIGINAL_LOCAL_FINISH_TEXTURES','materials':rows},indent=2)+'\n');print('MATERIALS_READY',len(rows))
