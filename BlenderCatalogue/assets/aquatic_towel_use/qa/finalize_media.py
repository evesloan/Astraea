"""Bind executed cameras and exact visual inputs; raw imported pixels preserved."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=json.loads((ROOT/'qa/render_evidence.json').read_text());bound={}
for folder,key in [('source','source_hashes'),('exports','export_hashes')]:
 for name,h in e[key].items():
  now=sha(ROOT/folder/name);assert now==h;bound[folder+'/'+name]={'before':h,'after':now,'unchanged':True}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
rows=[]
for name,view in e['views'].items():
 p=ROOT/'qa'/f'{name}_raw.png';im=Image.open(p).convert('RGB');w,h=im.size
 labelled=Image.new('RGB',(w,h+56),(25,33,35));labelled.paste(im,(0,0));draw=ImageDraw.Draw(labelled)
 title=view['camera']['asset']+' | '+name.replace('_',' ')+' | actual imported GLB'
 line='1.65 m camera; component QA only' if view['camera']['full'] else 'Detail crop; component QA only'
 draw.text((12,h+8),title,font=font,fill=(237,235,225));draw.text((12,h+30),line,font=font,fill=(183,198,197));out=ROOT/'qa'/f'{name}_labelled.png';labelled.save(out)
 rows.append({'view':name,'raw_path':str(p.relative_to(ROOT)),'raw_sha256':sha(p),'raw_size_px':list(im.size),'labelled_path':str(out.relative_to(ROOT)),'labelled_sha256':sha(out),'camera':view['camera'],'framing':view['framing']})
sheet=Image.new('RGB',(1920,416),(25,33,35))
for i,name in enumerate(('dry_standing','return_standing','return_withdrawn_rear')):sheet.paste(Image.open(ROOT/'qa'/f'{name}_labelled.png'),(i*640,0))
sheetpath=ROOT/'qa/towel_use_contact_sheet.png';sheet.save(sheetpath)
report={'scope':'Actual imported GLB render evidence; all raw images retained unmodified. Label bands only added outside the raw frame. No engine, room, physics or species claim.','visual_inputs_verified_unchanged':bound,'render_script':{'path':'qa/render_imported.py','sha256':sha(ROOT/'qa/render_imported.py'),'execution_log_path':'qa/render.log','execution_log_sha256':sha(ROOT/'qa/render.log')},'render_evidence_sha256':sha(ROOT/'qa/render_evidence.json'),'metadata_timing':'Collision proposal and generator collision declarations were amended during capture. No .blend, GLB or executed render script changed. This receipt binds only the unchanged visual inputs; it does not claim the generator/proposals were frozen throughout capture. Previous declarations are retained; the current generator passed a new clean rebuild.','views':rows,'contact_sheet':{'path':str(sheetpath.relative_to(ROOT)),'sha256':sha(sheetpath)},'visual_inspection':'All five raw images inspected. Original DRY and RETURN glyphs read at640x360. Protected stock, guarded mouth and supported rear withdrawal are distinct; folds, material joins and real throat visible in detailed crops.'}
(ROOT/'qa/review_media_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('MEDIA_BOUND',len(rows),'UNCHANGED_INPUTS',len(bound))
