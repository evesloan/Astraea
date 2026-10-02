"""Label only two added eye-height contexts and append their evidence metadata."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
QA=Path(__file__).resolve().parent;ROOT=QA.parent
mf=json.loads((QA/'RENDER_MANIFEST.json').read_text())
views=json.loads((QA/'eye_context_camera_records.json').read_text())
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',9)
for v in views:
    p=QA/v['file'];im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);w,h=im.size
    d.rectangle((0,0,w,34),fill=(28,35,39));d.text((8,3),v['catalogue_id']+' | '+v['camera_label'],font=font,fill=(242,240,228))
    d.text((8,19),'BLENDER COMPONENT QA | ACTUAL FINAL IMPORTED GLB | Materials02',font=small,fill=(187,205,207))
    d.rectangle((0,h-18,w,h),fill=(28,35,39));d.text((8,h-14),'Reused batch01 chair(s). Measured camera height; original rig / game fit untested.',font=small,fill=(221,224,220));im.save(p)
    v['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();v['size_pixels']=[w,h]
    mf['renders']=[r for r in mf['renders'] if r['file']!=v['file']];mf['renders'].append(v)
(QA/'RENDER_MANIFEST.json').write_text(json.dumps(mf,indent=2))
preserved=json.loads((QA/'preserved_final_asset_and_view_hashes.json').read_text())
checks=[{'file':f,'sha256':h,'unchanged':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h} for f,h in preserved.items()]
assert all(r['unchanged'] for r in checks),'Final source/export or previous image changed'
(QA/'final_evidence_guard.json').write_text(json.dumps({'status':'PASS','checked_files':checks,'final_render_count':len(mf['renders']),'new_camera_heights_m':[1.650,1.190],'scope':'Evidence only; final source meshes, exports, original three review PNGs and shared materials unchanged'},indent=2))
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.suffix!='.log' and p.name!='STUDY_SHA256SUMS.txt' and '__pycache__' not in p.parts)
(ROOT/'STUDY_SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in files))
