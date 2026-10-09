"""Original compact auditorium cloth roles; no sampled reference pixels."""
from pathlib import Path
from PIL import Image
import random,json,hashlib
D=Path(__file__).resolve().parent
roles={'auditorium_amber_velvet':{'colour_srgb_8bit':[160,75,43],'roughness':.88,'metallic':0,'meters_per_tile_uv':[.8,.8]},'auditorium_navy_fibre':{'colour_srgb_8bit':[38,48,62],'roughness':.94,'metallic':0,'meters_per_tile_uv':[.7,.7]}}
for n,(role,rec) in enumerate(roles.items()):
 rng=random.Random(1600+n);im=Image.new('RGB',(256,256));pix=im.load()
 for y in range(256):
  for x in range(256):
   weave=(1 if x%4<2 else -1)+(1 if y%4<2 else -1);variation=weave+rng.choice([-2,-1,0,0,1,2]);pix[x,y]=tuple(max(0,min(255,c+variation))for c in rec['colour_srgb_8bit'])
 p=D/(role+'.png');im.save(p);rec.update({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'texture_pixels':[256,256],'intent':'Original restrained warp/weft colour structure with directional metric UVs; runtime filtering and final lighting require host review'})
(D/'manifest.json').write_text(json.dumps({'revision':'auditorium-original-01','original_source':'draw_textures.py','provenance':'Original deterministic textures for user-authorized Blender catalogue; no reference pixels sampled','materials':roles},indent=2)+'\n')
