"""Add explicit scope labels to our own Blender component evidence renders."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,PngImagePlugin
QA=Path(__file__).resolve().parent
names={'001':'Day window bench','002':'Day reading chair','003':'Day table'}
for path in QA.rglob('*.png'):
 if path.name[:3] not in names:continue
 im=Image.open(path).convert('RGB');w,h=im.size;scale=w/640
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(12*scale))
 small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(9*scale))
 draw=ImageDraw.Draw(im);draw.rectangle((0,0,w,int(27*scale)),fill=(27,33,37))
 draw.text((int(11*scale),int(6*scale)),f'BLENDER ASSET QA  |  AST-FUR-{path.name[:3]}  |  {names[path.name[:3]]}',font=font,fill=(239,235,221))
 draw.rectangle((0,h-int(20*scale),w,h),fill=(27,33,37))
 footer='Independent component evidence • not an in-game view'
 if 'standing' in path.name:footer='Standing eye 1.66m • 1.75m scale proxy • not an actor rig / in-game view'
 if 'seated' in path.name:footer='Seated eye 1.19m • 1.75m scale proxy • not an actor rig / in-game view'
 if path.parent.name=='pre_material_02':footer='EARLIER MATERIAL PHASE • geometry / scale evidence only; not final texture proof'
 draw.text((int(11*scale),h-int(16*scale)),footer,font=small,fill=(221,224,223))
 meta=PngImagePlugin.PngInfo();meta.add_text('scope','Blender component QA only, no Godot or live performance claim')
 meta.add_text('material_phase','earlier material phase' if path.parent.name=='pre_material_02' else 'materials-02, final')
 im.save(path,pnginfo=meta)
