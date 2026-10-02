"""Original deterministic 256px clinical architecture material sources, Python/Pillow."""
from pathlib import Path
import random, math, json, hashlib
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
ROLES={
 'privacy_sage':((76,110,105),.88,.0,.8),
 'clinical_ink':((31,61,59),.83,.0,.65),
}
def make():
 (BASE/'textures').mkdir(exist_ok=True)
 rows={}
 for idx,(role,(col,rough,metal,scale)) in enumerate(ROLES.items()):
  rng=random.Random(41200+idx);im=Image.new('RGB',(256,256));pix=im.load()
  for y in range(256):
   for x in range(256):
    n=rng.randint(-2,2)
    if role=='privacy_sage':n+=2 if (x//8+y//8)%2==0 else -2
    if role=='clinical_nickel':n+=1 if y%4==0 else 0
    if role=='clinical_porcelain':n+=1 if (x*19+y*37)%127<3 else 0
    pix[x,y]=tuple(max(0,min(255,c+n))for c in col)
  p=BASE/'textures'/f'{role}.png';im.save(p)
  rows[role]={'base_color_file':f'textures/{role}.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'texture_resolution':[256,256],'meters_per_tile_uv':[scale,scale],'roughness':rough,'metallic':metal,'colour_srgb_8bit':col,'provenance':'Original deterministic pixel texture; muted care palette, no claimed antimicrobial or cleaning properties'}
 (BASE/'material_manifest.json').write_text(json.dumps({'revision':'clinical-architecture-materials-01','generator':'source/make_clinical_textures.py','materials':rows},indent=2)+'\n')
if __name__=='__main__':make()
