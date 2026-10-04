"""Bind current evidence, input dependency closure and file hashes without editing geometry."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p,base):return {'path':str(p.relative_to(base)),'bytes':p.stat().st_size,'sha256':sha(p)}
qa=BASE/'qa';(qa/'review').mkdir(parents=True,exist_ok=True)
evidence=json.loads((qa/'render_evidence.json').read_text());media=[]
labels={'AST-SAL-004':'EXISTING PLANTS ARE QA CONTEXT','AST-SAL-005':'INFILL ABSENT; NOT A COMPLETE GUARD','AST-SAL-006':'FIXED OPEN STORAGE; NO DOOR MECHANISM'}
for name,ev in evidence['views'].items():
 p=qa/(name+'.png');im=Image.open(p).convert('RGB');scale=2 if im.width>640 else 1
 draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',9*scale)
 label=ev['camera']['id']+' | COMPONENT QA | '+labels[ev['camera']['id']]
 if ev['intentional_detail_crop']:label+=' | DETAIL CROP'
 draw.rectangle((0,0,im.width,18*scale),fill=(25,32,35));draw.text((7*scale,3*scale),label,font=font,fill=(236,239,234))
 target=qa/'review'/p.name;im.save(target)
 media.append({'path':str(target.relative_to(BASE)),'raw_render':str(p.relative_to(BASE)),'sha256':sha(target),'raw_render_sha256':sha(p),'dimensions_px':list(im.size),'catalogue_id':ev['camera']['id'],'purpose':ev['camera']['purpose'],'view':ev['camera'],'glb_sha256':ev['glb_sha256'],'source_sha256_at_capture':ev['source_sha256_at_capture'],'context':ev['context'],'label_method':'Small evidence label in top neutral margin; unaltered raw Blender render retained','scope':'Actual imported-GLB component inspection, not game/room or guard-safety acceptance'})
(qa/'review_media_manifest.json').write_text(json.dumps({'media':media,'scope':'Six bounded current component views, four ordinary640×360 views and two1280×960 detail crops'},indent=2)+'\n')
manifest=json.loads((BASE/'manifest.json').read_text())
for rec in manifest['assets']:
 ident=rec['catalogue_id'];rec['source_sha256']=sha(BASE/rec['source']);rec['glb_sha256']=sha(BASE/rec['export']);rec['generator_sha256']=sha(BASE/rec['generator'])
 rec['validation_files']=['qa/source_reload_checks.json','qa/glb_validation.json','qa/native_interfaces_and_voids.json','qa/source_only_rebuild.json','qa/camera_preflight.json','qa/render_evidence.json','qa/exposed_surface_review.json'];rec['validation_files']+=['qa/plant_context_contacts.json']if ident=='AST-SAL-004'else[];rec['evidence_media_manifest']='qa/review_media_manifest.json';rec['source_and_export_verified']=True
 (BASE/(ident+'.manifest.json')).write_text(json.dumps(rec,indent=2)+'\n')
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Both helpers intentionally read their complete manifests, so all opened inputs are listed.
inputs=[CAT/'standards/materials.py',CAT/'standards/botanical_materials.py',CAT/'materials/material_manifest.json',CAT/'materials/botanical/manifest.json']
inputs.extend(CAT/'materials'/x['base_color_file']for x in json.loads((CAT/'materials/material_manifest.json').read_text())['materials'].values())
inputs.extend(CAT/'materials/botanical'/x['file']for x in json.loads((CAT/'materials/botanical/manifest.json').read_text())['materials'].values())
external=[]
for p in sorted(set(inputs)):
 row=record(p,CAT);row['path_from_catalogue_root']=row.pop('path');row['path_from_family']='../../'+row['path_from_catalogue_root'];external.append(row)
production=[p for p in BASE.rglob('*')if p.is_file()and'qa'not in p.relative_to(BASE).parts and p.name not in('SHA256SUMS.txt','dependency_manifest.json')and'__pycache__'not in p.parts]
dep={'scope':'Production source and actual shared input dependencies. No other asset/QA/render/context is read by generator.','generator_command_from_catalogue_root':'blender --background --threads 2 --python-exit-code 1 --python assets/salon_edges/source/build_salon_edges.py','external_input_files':external,'files':[record(p,BASE)for p in sorted(production)],'qa_only_context':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'sha256':sha(p),'production_source_dependency':False}for p in(CAT/'assets/botanical_understory/exports/AST-BOT-002.glb',CAT/'assets/botanical_understory/exports/AST-BOT-003.glb')],'all_under_8MB':all(p.stat().st_size<8*1024*1024 for p in production)}
(BASE/'dependency_manifest.json').write_text(json.dumps(dep,indent=2)+'\n')
files=[p for p in BASE.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'and'__pycache__'not in p.parts]
(BASE/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(BASE))+'\n'for p in sorted(files)))
print('FINALIZED',len(production),'production files,',len(external),'actual material inputs,',len(media),'current review images')
