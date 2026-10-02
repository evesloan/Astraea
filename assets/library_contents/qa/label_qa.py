from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
QA=Path(__file__).resolve().parent;ROOT=QA.parent
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
items=[('006_imported_glb_standing_640.png','AST-LIB-006_upright_book_group.glb','standing camera 1.62 m'),('006_imported_glb_detail_1280.png','AST-LIB-006_upright_book_group.glb','binding detail'),('007_imported_glb_seated_640.png','AST-LIB-007_open_folio_stack.glb','seated camera 1.19 m'),('007_imported_glb_detail_1280.png','AST-LIB-007_open_folio_stack.glb','original page detail'),('006_reordered_imported_glb_640.png','AST-LIB-006_upright_book_group_reordered.glb','same books reordered'),('006_short_flat_imported_glb_640.png','AST-LIB-006_upright_book_group_short_flat.glb','same books short / flat')]
records=[]
for file,glb,desc in items:
 p=QA/file;im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);h=24 if im.width==640 else 32;f=ImageFont.truetype(font,10 if im.width==640 else 17)
 d.rectangle((0,im.height-h,im.width,im.height),fill=(26,34,39));d.text((10,im.height-h+6),'BLENDER COMPONENT EVIDENCE | imported GLB | '+desc+' | no game validation',font=f,fill=(229,235,233));im.save(p,optimize=True)
 records.append({'file':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_imported_glb':glb,'imported_glb_sha256':hashlib.sha256((ROOT/glb).read_bytes()).hexdigest(),'camera_note':desc,'resolution_px':list(im.size)})
canvas=Image.new('RGB',(1920,394),(27,35,39));d=ImageDraw.Draw(canvas);f=ImageFont.truetype(font,16)
for i,(file,label) in enumerate([('006_imported_glb_standing_640.png','BASE | 802 triangles'),('006_reordered_imported_glb_640.png','REORDERED ASSEMBLY | 802 triangles'),('006_short_flat_imported_glb_640.png','SHORT / FLAT ASSEMBLY | 580 triangles')]):
 canvas.paste(Image.open(QA/file),(640*i,34));d.text((640*i+12,8),label,font=f,fill=(232,236,235))
canvas.save(QA/'006_same_books_arrangement_contact_sheet.png',optimize=True)
(QA/'RENDER_MANIFEST.json').write_text(json.dumps({'scope':'Actual GLB imports in Blender only, no Godot, actor, species or performance validation','renderer':'Blender 4.3.2 Cycles CPU, 24 samples; denoiser unavailable in installed build; neutral QA support and lights only','renders':records,'derived_arrangement_sheet':'006_same_books_arrangement_contact_sheet.png'},indent=2))
