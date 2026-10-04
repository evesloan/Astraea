"""Original deterministic 256px woven linen; no source/reference pixels."""
from pathlib import Path
from PIL import Image
import random,json,hashlib
root=Path(__file__).resolve().parents[1];rng=random.Random(107);im=Image.new('RGB',(256,256));p=im.load()
for y in range(256):
 for x in range(256):
  weave=(2 if y%4<2 else -2)+(-1 if x%4<2 else 1);noise=rng.choice([-2,-1,0,0,0,1,2]);p[x,y]=tuple(v+weave+noise for v in (225,225,220))
out=root/'textures/guest_linen.png';im.save(out);(root/'textures/manifest.json').write_text(json.dumps({'role':'guest_linen','size':[256,256],'metres_per_tile':[.8,.8],'roughness':.93,'provenance':'Original deterministic woven pixel pattern; no reference pixels','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n')
