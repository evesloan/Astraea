"""Original deterministic care-role color tiles; no external images/fonts."""
from pathlib import Path
from PIL import Image
import json,hashlib,math,random
ROOT=Path(__file__).resolve().parents[1]
roles={'care_bluegreen_resin':{'colour_srgb_8bit':[79,129,132],'roughness':.71,'metallic':0.0,'meters_per_tile_uv':.75,'purpose':'Muted care-oriented painted/resin visual accent; no chemistry or compatibility claim'},'care_soft_pad':{'colour_srgb_8bit':[135,171,169],'roughness':.84,'metallic':0.0,'meters_per_tile_uv':.65,'purpose':'Low-contrast soft support finish, without anatomical/species suitability claim'},'care_brushed_metal':{'colour_srgb_8bit':[157,163,164],'roughness':.56,'metallic':.62,'meters_per_tile_uv':.75,'purpose':'Restrained neutral hardware finish; source grain runs along texture V'}}
for index,(role,row) in enumerate(roles.items()):
 rng=random.Random(12100+index);grid=[[rng.uniform(-1,1) for x in range(16)] for y in range(16)]
 def sample(x,y):
  a=x/16;b=y/16;ix=int(a);iy=int(b);u=a-ix;v=b-iy;u=u*u*(3-2*u);v=v*v*(3-2*v)
  return (grid[iy%16][ix%16]*(1-u)+grid[iy%16][(ix+1)%16]*u)*(1-v)+(grid[(iy+1)%16][ix%16]*(1-u)+grid[(iy+1)%16][(ix+1)%16]*u)*v
 image=Image.new('RGB',(256,256));pix=image.load()
 for y in range(256):
  for x in range(256):
   coarse=sample(x,y)
   delta=(2.1*math.sin(2*math.pi*x/32)+coarse*.8) if role=='care_brushed_metal' else coarse*(2.3 if role=='care_soft_pad' else 1.5)
   pix[x,y]=tuple(max(0,min(255,round(c+delta))) for c in row['colour_srgb_8bit'])
 path=ROOT/(role+'.png');image.save(path,compress_level=9);row['file']=path.name;row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();row['dimensions_px']=[256,256];row['alpha']=False
manifest={'revision':'original-care-roles-01','provenance':'New original script-assisted deterministic color textures for the fictional Astraea catalogue; no sampled source images','generator':'source/generate_care_materials.py','materials':roles,'limits':'Visual roles only, with ordinary Principled materials. They do not certify cleanability, medical suitability, load, fluid compatibility or engine performance.'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
