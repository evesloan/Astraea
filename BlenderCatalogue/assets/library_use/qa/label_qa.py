"""Label evidence, keeping raw rendered pixels and exact metadata alongside it."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa';p=QA/'RENDER_MANIFEST.json';info=json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for rec in info['images']:
 raw=QA/rec['file'];im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im);scale=im.width/640
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(10*scale))
 except OSError:f=ImageFont.load_default()
 height=round(33*scale);d.rectangle((0,0,im.width,height),fill=(24,34,37));d.rectangle((0,im.height-round(19*scale),im.width,im.height),fill=(24,34,37))
 title=rec['file'].replace('.png','').replace('_',' ')+' | eye Z '+format(rec['camera_height_m'],'.2f')+' m'
 d.text((round(7*scale),round(4*scale)),title,font=f,fill=(241,242,229));d.text((round(7*scale),round(18*scale)),'BLENDER COMPONENT QA | actual imported GLB | fixed visual',font=f,fill=(193,217,220))
 footer='Original game / actor reach / interaction / physics / room fit pending'
 if 'existing_shared' in rec['file']:footer='Unchanged prior study table reused as QA context only'
 d.text((round(7*scale),im.height-round(15*scale)),footer,font=f,fill=(235,238,226))
 out=QA/(raw.stem+'_labelled.png');im.save(out);rec['labelled_file']=out.name;rec['labelled_image_sha256']=sha(out)
p.write_text(json.dumps(info,indent=2))
chosen=['008_fixture_seated_640','009_browser_standing_640','010_terminal_standing_640','008_existing_shared_table_context_640','009_browser_seated_640','010_terminal_actual_use_640']
sheet=Image.new('RGB',(1920,720),(24,34,37))
for i,name in enumerate(chosen):sheet.paste(Image.open(QA/(name+'_labelled.png')),(i%3*640,i//3*360))
sheet.save(QA/'library_use_component_contact_sheet.png')
print('LABELLED',len(info['images']))
