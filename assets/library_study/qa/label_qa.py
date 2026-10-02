"""Label deterministic Blender component evidence after render_and_audit.py."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
QA=Path(__file__).resolve().parent;ROOT=QA.parent;BASE=ROOT.parent.parent
labels=[('01_shared_chair_context_640.png','AST-LIB-STUDY-01 | Shared reading / four candidate chairs',False),('02_single_chair_context_640.png','AST-LIB-STUDY-02 | Sheltered single reading edge',False),('02_single_join_detail_1280.png','AST-LIB-STUDY-02 | Wing, shelf and housed desk join detail',True)]
records=[]
for filename,title,detail in labels:
    p=QA/filename;im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);w,h=im.size;k=w/640
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(11*k));small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(9*k))
    d.rectangle((0,0,w,round(34*k)),fill=(28,35,39));d.text((round(8*k),round(3*k)),title,font=font,fill=(242,240,228));d.text((round(8*k),round(19*k)),'BLENDER COMPONENT QA | ACTUAL IMPORTED GLB | Materials02',font=small,fill=(187,205,207))
    d.rectangle((0,h-round(18*k),w,h),fill=(28,35,39));note='Join detail; extents cropped. Original game / rig fit untested.' if detail else 'Reused batch01 seating. Proposed positions; original game / rig fit untested.'
    d.text((round(8*k),h-round(14*k)),note,font=small,fill=(221,224,220));im.save(p)
    records.append({'file':filename,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_pixels':[w,h],'input':'Actual imported study GLB; optional batch01 chair GLB context','scope':'Blender component evidence, no game acceptance'})
inputs=[{'file':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(ROOT.glob('*.glb'))]
chair=BASE/'assets/furniture/AST-FUR-002_day_reading_chair.glb';inputs.append({'file':str(chair.relative_to(BASE)),'sha256':hashlib.sha256(chair.read_bytes()).hexdigest(),'use':'Scale/QA only, not supplied or counted as a new asset'})
(QA/'RENDER_MANIFEST.json').write_text(json.dumps({'renderer':'Blender4.3.2 EEVEE32samples','inputs':inputs,'renders':records,'scope':'Bounded component inspection. No Godot, native performance, species fit or room acceptance.'},indent=2))
