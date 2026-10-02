"""Bind final review media and update the complete local package checksum inventory."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[json.loads(p.read_text())for p in sorted(BASE.glob('AST-BOT-*.manifest.json'))];by={r['catalogue_id']:r for r in records};p=BASE/'qa/render_evidence.json';e=json.loads(p.read_text());old=json.loads((BASE/'qa/pre_consolidation/render_evidence.json').read_text());retained=[]
for v in old['views']:
 if v['mode']=='source'and v['catalogue_id']!='AST-BOT-009':
  assert v['source_sha256']==by[v['catalogue_id']]['source_sha256'];assert sha(BASE/v['image'])==v['image_sha256'];v['glb_sha256_at_historical_capture']=v.pop('glb_sha256');v['retained_scope']='Source .blend pixels and camera only; exact source unchanged. Current GLB is separately captured and fully compared geometrically.';v['current_glb_sha256_verified_by_triangle_qa']=by[v['catalogue_id']]['glb_sha256'];retained.append(v)
e['retained_unchanged_source_views']=retained;p.write_text(json.dumps(e,indent=2)+'\n')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);titlefont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
board=Image.new('RGB',(1280,3*398+54),(22,31,29));draw=ImageDraw.Draw(board);draw.text((20,16),'BOTANICAL CLUSTERS • EDITABLE SOURCE / ACTUAL IMPORTED GLB',font=titlefont,fill=(236,237,223));media=[]
for i,r in enumerate(records):
 for j,mode in enumerate(('source','imported')):
  path=BASE/'qa'/f"{r['catalogue_id']}_{mode}_640.png";im=Image.open(path).convert('RGB');board.paste(im,(j*640,54+i*398));draw.text((j*640+15,54+i*398+369),r['catalogue_id']+'  '+('EDITABLE BLENDER SOURCE'if mode=='source'else 'ACTUAL IMPORTED GLB')+'  •  640×360',font=font,fill=(235,235,220));media.append({'catalogue_id':r['catalogue_id'],'mode':mode,'image':str(path.relative_to(BASE)),'image_sha256':sha(path),'source_sha256':r['source_sha256'],'glb_sha256':r['glb_sha256'],'scope':'Exact source evidence or final imported export; render_evidence.json specifies individual camera/hash capture scope'})
boardpath=BASE/'qa/Botanical_Clusters_Source_Imported_Comparison.png';board.save(boardpath)
(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'images':media,'comparison_board':str(boardpath.relative_to(BASE)),'comparison_board_sha256':sha(boardpath),'scope':'Blender Eevee component comparison only; not game or host views'},indent=2)+'\n')
p=BASE/'dependency_manifest.json';d=json.loads(p.read_text());d['qa_helpers']=[{'catalogue_relative_path':str(x.relative_to(CAT)),'sha256':sha(x)}for x in sorted((BASE/'qa').glob('*.py'))]+[{'catalogue_relative_path':'standards/qa_frame.py','sha256':sha(CAT/'standards/qa_frame.py')}];d['qa_context_inputs']=[{'catalogue_relative_path':'assets/botanical_transition/source/AST-BOT-010.blend','scope':'Actual rear coping/wall check only; not needed to regenerate plants','sha256':json.loads((BASE/'qa/trailing_transition_clearance.json').read_text())['transition_source_sha256']}];p.write_text(json.dumps(d,indent=2)+'\n')
for r in records:
 r['evidence_media_manifest']='qa/review_media_manifest.json';r['source_and_export_verified']=True;(BASE/(r['catalogue_id']+'.manifest.json')).write_text(json.dumps(r,indent=2)+'\n')
(BASE/'manifest.json').write_text(json.dumps({'family':'Joined botanical cluster silhouettes','unique_design_count':3,'assets':records},indent=2)+'\n')
checks={n:json.loads((BASE/'qa'/(n+'.json')).read_text())for n in ['source_reload_checks','glb_validation','source_native_geometry','collision_profile_checks','source_only_rebuild_receipt','trailing_transition_clearance']};assert all(d.get('all_passed',d.get('passes',False))for d in checks.values())
receipt={'catalogue_ids':[r['catalogue_id']for r in records],'asset_hashes':[{k:r[k]for k in('catalogue_id','source_sha256','glb_sha256','generator_sha256')}for r in records],'all_author_checks_passed':True,'all_source_and_imported_views_exist':len(media)==6,'independent_reviewer_gate':'Separate batch13 report; author checks are not independent signoff','inspection_scope':'Editable Blender components and native exchange only; engine/host/biology/species acceptance remains pending'}
(BASE/'qa/author_handoff_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Final media and receipts ready')
