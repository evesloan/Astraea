"""Regenerate the three original source textures into a new output directory."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
recipes={'quiet_ivory':(187,190,178),'sage_acoustic':(75,112,108),'warm_sand':(146,126,96)}
for name,base in recipes.items():
    image=Image.new('RGB',(256,256));pixel=image.load()
    for y in range(256):
        for x in range(256):
            n=((x*374761393+y*668265263)^((x//4+y//4)*1274126177))%11-5
            if name=='sage_acoustic':n+=3 if x%8<2 or y%8<2 else -2
            if name=='warm_sand':n+=((x//3+y//64)%4-2)*2
            pixel[x,y]=tuple(max(0,min(255,v+n)) for v in base)
    image.save(out/f'{name}.png')
print(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')},indent=2))
