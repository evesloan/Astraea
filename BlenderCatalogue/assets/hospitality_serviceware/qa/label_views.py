"""Append QA caption bands to unchanged raw render pixels."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1];QA=BASE/'qa'
captions={'005_ordinary':['AST-HSP-005  |  Aster plate/tray service credenza','Guest −Y: bowed walnut joinery, stone top. Imported GLB component QA.'], '005_use':['AST-HSP-005  |  Staff standing eye Z1.65 m','Rear +Y access: three tray shelves, two plate shelves, supported nested stock.'], '005_detail':['AST-HSP-005  |  Reachable stock and shelf-support detail','Actual imported GLB. Folded shelf cleats, contact-derived nesting; no food/fit certification.'], '006_ordinary':['AST-HSP-006  |  Aster two-tier dining service trolley','Two useful levels, four castors and a connected rear push grip. Component QA.'], '006_use':['AST-HSP-006  |  Staff standing eye Z1.65 m','Rear +Y grip; upper inset contact Z0.791 m. No rolling/controller implementation.'], '006_detail':['AST-HSP-006  |  Castor, support and lower-tier detail','Actual exported geometry: fork/wheel space, bearing contact and useful tray support.']}
files=[];evidence=json.loads((QA/'render_evidence.json').read_text())
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for key,lines in captions.items():
 raw=QA/(key+'_raw.png');im=Image.open(raw).convert('RGB');h=68 if im.width==640 else 100;out=Image.new('RGB',(im.width,im.height+h),(20,28,32));out.paste(im,(0,0));d=ImageDraw.Draw(out);f1=ImageFont.truetype(fontpath,15 if im.width==640 else 25);f2=ImageFont.truetype(fontpath,11 if im.width==640 else 18);d.text((14,im.height+10),lines[0],font=f1,fill=(234,232,219));d.text((14,im.height+38),lines[1],font=f2,fill=(183,198,199));dest=QA/(key+'_labelled.png');out.save(dest)
 aid='AST-HSP-'+key[:3];files.append({'asset':aid,'view':key[4:],'raw_file':str(raw.relative_to(BASE)),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'labelled_file':str(dest.relative_to(BASE)),'labelled_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':evidence['assets'][aid]['source_sha256'],'glb_sha256':evidence['assets'][aid]['glb_sha256'],'caption':lines,'raw_pixels_unchanged':True})
(QA/'review_media_manifest.json').write_text(json.dumps({'scope':'Imported-GLB component QA; neutral floor/lights/cameras are inspection aids. No engine, species fit or physical certification.','views':files},indent=2)+'\n')
print('LABELLED',len(files))
