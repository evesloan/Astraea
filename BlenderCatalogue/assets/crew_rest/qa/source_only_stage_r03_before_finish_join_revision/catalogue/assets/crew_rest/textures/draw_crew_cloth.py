from PIL import Image
from pathlib import Path
import random,hashlib,json
P=Path(__file__).resolve().parent
roles={'crew_ecru_sheet':([178,167,143],.90),'crew_terracotta_blanket':([123,77,59],.93),'crew_sage_privacy':([100,111,91],.94)}
out={}
for role,(base,rough) in roles.items():
 rng=random.Random(role);im=Image.new('RGB',(256,256));px=im.load()
 for y in range(256):
  for x in range(256):
   weave=(2 if x%4<2 else -2)+(1 if y%4<2 else -1);v=rng.choice([-2,-1,0,0,0,1,2])+weave
   px[x,y]=tuple(max(0,min(255,c+v))for c in base)
 path=P/(role+'.png');im.save(path)
 out[role]={'file':path.name,'colour_srgb_8bit':base,'roughness':rough,'metallic':0,'meters_per_tile_uv':[.4,.4],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(P/'manifest.json').write_text(json.dumps({'revision':'crew-rest-cloth-01','provenance':'Original deterministic woven texture pixels; no reference pixels. Warp along declared cloth U/developed pleat length, weft along V/vertical.','materials':out},indent=2))
