"""Label rendered Blender evidence and write reproducible hashes/provenance."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont,PngImagePlugin
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
RAW=ROOT/'qa/raw';RAW.mkdir(exist_ok=True)
titles={
 'neutral_640.png':('BLENDER COMPONENT QA | AST-VR-01','Complete neutral assembly | 3.35 m W / 3.25 m H'),
 'standing_640.png':('BLENDER COMPONENT QA | STANDING','Eye 1.65 m | isolated architectural component'),
 'seated_640.png':('BLENDER COMPONENT QA | SEATED','Eye 1.15 m | isolated architectural component'),
 'detail_1280.png':('BLENDER COMPONENT QA | PROFILE + HEADER/JAMB SEAM','Sculpted ivory shoulder / deep timber throat / 2 mm module joint'),
 'join_exploded_1280.png':('BLENDER COMPONENT QA | EXPLODED JOIN PROOF','H crown + S sill + two handed J jambs | nominal joins match; assembly gap 2 mm'),
 'terminal_closed_1280.png':('BLENDER COMPONENT QA | CLOSED CROWN TERMINAL','H to T compatible seam | shaped return and closed distal cap'),
 'terminal_rear_1280.png':('BLENDER COMPONENT QA | TERMINAL REAR / END','Watertight ivory and timber parts | no wall or hull cut supplied')}
for name,(title,subtitle) in titles.items():
    src=ROOT/'qa'/name;raw=RAW/name
    # Idempotent: raw captures the latest clean render when newer than final annotation.
    current=Image.open(src)
    if not raw.exists() or not current.info.get('astraea_qa_labelled'):shutil.copy2(src,raw)
    im=Image.open(raw).convert('RGB');w,h=im.size;bar=40 if w==640 else 70
    canvas=Image.new('RGB',(w,h),(25,34,38));ratio=(h-bar)/h;fit=im.resize((round(w*ratio),h-bar),Image.Resampling.LANCZOS);canvas.paste(fit,((w-fit.width)//2,bar))
    d=ImageDraw.Draw(canvas);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=ImageFont.truetype(font,12 if w==640 else 21);s=ImageFont.truetype(font,10 if w==640 else 17)
    d.text((12,5 if w==640 else 9),title,fill=(242,238,224),font=f);d.text((12,23 if w==640 else 38),subtitle,fill=(178,204,204),font=s);info=PngImagePlugin.PngInfo();info.add_text('astraea_qa_labelled','true');canvas.save(src,pnginfo=info)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
path=ROOT/'manifest.json';m=json.loads(path.read_text());m['generator']={'file':'source/build_reveal.py','sha256':sha(ROOT/'source/build_reveal.py'),'authoring':'Original, intentionally designed script-assisted cross-section modelling; editable mesh/modifier source retained'}
m['shared_material_dependency']={'file':'../../standards/materials.py','sha256':sha(CAT/'standards/materials.py'),'manifest_sha256':sha(CAT/'materials/material_manifest.json')}
m['reference_sources']=[{'file':str(p.relative_to(CAT)),'sha256':sha(p),'use':'Directly inspected shape/material/use guidance only'} for p in sorted((CAT/'references').rglob('*.png'))]
for a in m['assets']:
    a['source_sha256']=sha(ROOT/a['source_blend']);a['runtime_sha256']=sha(ROOT/a['runtime_glb']);a['export']['material_role_consolidation']=True;a['export']['runtime_mesh_count']=2;a['export']['runtime_primitive_count']=2;a['uv']='Metric pathwise sides, planar end caps, tiny evaluated bevel slivers get metric dominant-plane projection'
m['assembly']['source_blend']='source/AST-VR-01-ASSEMBLY.blend';m['assembly']['source_sha256']=sha(ROOT/'source/AST-VR-01-ASSEMBLY.blend');m['assembly']['runtime_glb']='exports/AST-VR-01-ASSEMBLY.glb';m['assembly']['runtime_sha256']=sha(ROOT/'exports/AST-VR-01-ASSEMBLY.glb');m['assembly']['runtime_mesh_count']=2;m['assembly']['runtime_primitive_count']=2
m['evidence']={'renderer':'Blender 4.3.2 Eevee Next, 128 temporal samples, four CPU threads','label':'BLENDER COMPONENT QA','renders':[{'file':'qa/'+n,'sha256':sha(ROOT/'qa'/n),'size_px':list(Image.open(ROOT/'qa'/n).size)} for n in titles],'raw_render_directory':'qa/raw','not_accepted':['original room fit','hull geometry','physical glass','view','Godot integration','actor contact','game performance','CRT response']}
m['verification']={k:json.loads((ROOT/'qa'/k).read_text())['all_passed'] for k in ('glb_validation.json','source_reload_validation.json','join_validation.json')}
m['source_hashes']={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'source').glob('*')) if p.suffix in ('.blend','.py')}
path.write_text(json.dumps(m,indent=2));files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt' and p.suffix not in ('.blend1','.pyc') and 'raw' not in p.parts]
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+str(p.relative_to(ROOT)) for p in files)+'\n')
print('FINALIZED',len(files),'files; all verification:',all(m['verification'].values()))
