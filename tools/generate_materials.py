"""Original low-frequency colour tiles for the independent Astraea catalogue.

Deterministic script-assisted texture authoring. No downloaded image source.
Run with ordinary Python, not Blender. Grain runs along V; tiles are seamless.
"""
from pathlib import Path
import json, math, random, hashlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials'
OUT.mkdir(exist_ok=True)
SIZE = 256
PALETTE = {
 'ivory_enamel': ((210, 204, 187), .68, 0.0, 'enamel', (1.0,1.0)),
 'warm_walnut': ((106, 65, 38), .65, 0.0, 'wood', (.65,1.30)),
 'teal_weave': ((43, 91, 93), .91, 0.0, 'weave', (.80,.80)),
 'clay_weave': ((158, 87, 68), .91, 0.0, 'weave', (.80,.80)),
 'oatmeal_weave': ((186, 174, 150), .92, 0.0, 'weave', (.80,.80)),
 'champagne_metal': ((160, 134, 88), .47, .72, 'metal', (.60,.60)),
 'dark_rubber': ((30, 35, 35), .90, 0.0, 'rubber', (.60,.60)),
 'warm_stone': ((200, 190, 166), .78, 0.0, 'stone', (1.0,1.0)),
}

def wave(x, y, p, q, phase=0):
 return math.sin(math.tau*(p*x+q*y)+phase)

def tile(name, colour, kind):
 rng=random.Random(210026 + list(PALETTE).index(name))
 coarse=[(rng.randint(1,8),rng.randint(1,8),rng.random()*math.tau,rng.uniform(.4,1.0)) for _ in range(9)]
 im=Image.new('RGB',(SIZE,SIZE));pix=im.load()
 for y in range(SIZE):
  for x in range(SIZE):
   u,v=x/SIZE,y/SIZE
   broad=sum(wave(u,v,p,q,phase)*w for p,q,phase,w in coarse)/9
   if kind=='wood':
    # Long grain has slow wavering, wide tonal ribbons, and narrow understated pores.
    drift=.11*wave(0,v,0,1)+.05*wave(0,v,0,3,1.1)
    a=math.sin(math.tau*(u*9+drift));b=math.sin(math.tau*(u*23+drift*.3))
    delta=10*a+3*b+3*broad
   elif kind=='weave':
    # Deliberately coarse bands avoid subpixel checkerboard contrast.
    warp=1.3*math.sin(math.tau*x/8);weft=1.1*math.sin(math.tau*y/8)
    delta=warp+weft+6*broad
   elif kind=='stone': delta=5*broad+1.8*wave(u,v,2,3)
   elif kind=='metal': delta=1.8*math.sin(math.tau*y/16)+1.5*broad
   elif kind=='rubber': delta=1.3*broad
   else: delta=1.8*broad
   pix[x,y]=tuple(max(0,min(255,round(c+delta))) for c in colour)
 if kind=='stone':
  # Sparse inset aggregate; periodic copies keep tile edges continuous.
  d=ImageDraw.Draw(im)
  for i in range(100):
   x,y=rng.randrange(SIZE),rng.randrange(SIZE);r=rng.choice([1,1,2])
   cc=tuple(max(0,min(255,c+rng.choice([-15,-10,8]))) for c in colour)
   for sx in [-SIZE,0,SIZE]:
    for sy in [-SIZE,0,SIZE]: d.ellipse((x-r+sx,y-r+sy,x+r+sx,y+r+sy),fill=cc)
 im.save(OUT/f'{name}.png')

def main():
 manifest={'revision':'astraea-catalogue-materials-01','provenance':'Original deterministic texture art generated for this catalogue; no third-party pixels.','materials':{}}
 for name,(colour,rough,metal,kind,metric) in PALETTE.items():
  tile(name,colour,kind)
  f=OUT/f'{name}.png'
  manifest['materials'][name]={'base_color_file':f.name,'texture_resolution':[SIZE,SIZE], 'meters_per_tile_uv':list(metric),'grain_direction':'V' if kind=='wood' else None,'roughness':rough,'metallic':metal,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'colour_srgb_8bit':colour}
 (OUT/'material_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 # Contact sheet is just a texture inspection artifact, never game evidence.
 sheet=Image.new('RGB',(4*SIZE,2*(SIZE+28)),(28,31,32));draw=ImageDraw.Draw(sheet)
 for i,name in enumerate(PALETTE):
  x=(i%4)*SIZE;y=(i//4)*(SIZE+28);sheet.paste(Image.open(OUT/f'{name}.png'),(x,y));draw.text((x+6,y+SIZE+7),name,fill='white')
 sheet.save(OUT/'material_contact_sheet.png')
 print(json.dumps({'materials':len(PALETTE),'output':str(OUT)}))

if __name__=='__main__': main()
