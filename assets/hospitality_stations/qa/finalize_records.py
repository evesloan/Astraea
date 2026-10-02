"""Bind finished source/export/evidence hashes and measured costs; does not touch sources or exports."""
import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
glb=json.loads((BASE/'qa/glb_validation.json').read_text());src=json.loads((BASE/'qa/source_reload_checks.json').read_text());motion=json.loads((BASE/'qa/native_motion_and_clearance_checks.json').read_text());renders=json.loads((BASE/'qa/render_evidence.json').read_text());assert glb['all_passed']and src['all_passed']and motion['all_passed']
records=[];costs=[];media=[]
for r in glb['results']:
 ident=Path(r['file']).stem;p=BASE/f'{ident}.manifest.json';m=json.loads(p.read_text());assert r['sha256']==sha(BASE/m['export']);assert m['source_sha256']==sha(BASE/m['source']);assert next(a['source_sha256']for a in src['assets']if a['catalogue_id']==ident)==m['source_sha256'];assert next(a['glb_sha256']for a in motion['assets']if a['catalogue_id']==ident)==r['sha256']
 m['generator_sha256_at_source_creation']=m.get('generator_sha256_at_source_creation',m['generator_sha256']);m['generator_sha256']=sha(BASE/m['generator']);m['generator_compatibility_note']='Latest generator fixes quad UV assignment; beverage source/export preserved byte-identical because its quad UVs already matched. --only supports focused regeneration.'
 m['measured_runtime_cost']={'triangles':r['triangle_count'],'mesh_count':r['runtime_mesh_count'],'primitive_count':r['runtime_primitive_count'],'embedded_texture_count':r['embedded_png_texture_count'],'glb_bytes':(BASE/m['export']).stat().st_size,'source_blend_bytes':(BASE/m['source']).stat().st_size,'status':'Measured file cost, no target-PC timing'}
 m['limitations'] += ['Caddy extraction is a hand-supported removal proposal; no loaded full-extension operating support is proven']if ident=='AST-HSP-004'and not any('hand-supported' in s for s in m['limitations'])else[]
 m['QA']={'source_reload':'qa/source_reload_checks.json','actual_glb':'qa/glb_validation.json','contact_motion_frames':'qa/native_motion_and_clearance_checks.json','camera_preflight':'qa/camera_preflight.json','render_evidence':'qa/render_evidence.json','review_media_manifest':'qa/review_media_manifest.json','visual_review':'qa/visual_review.json','graphic_orientation':'qa/graphic_uv_orientation.json'}
 p.write_text(json.dumps(m,indent=2)+'\n');records.append(m);costs.append({'catalogue_id':ident,**m['measured_runtime_cost'],'proposed_collision_box_count':len(json.loads((BASE/'collision_proposals.json').read_text())[ident]['boxes'])})
 for name,e in renders['views'].items():
  if e['camera']['id']!=ident:continue
  assert e['glb_sha256']==r['sha256'];p=BASE/'qa'/f'{name}.png';assert p.exists();media.append({'path':str(p.relative_to(BASE)),'catalogue_id':ident,'sha256':sha(p),'source_sha256_at_capture':e.get('source_sha256_at_capture',m['source_sha256']),'current_editable_source_sha256':m['source_sha256'],'source_only_equivalence':m.get('source_only_revision'),'glb_sha256':r['sha256'],'kind':'Actual imported GLB neutral component view','purpose':e['camera']['purpose']})
deps=[]
for p in [CAT/'standards/materials.py',CAT/'standards/staff_materials.py',CAT/'standards/utility_ports.py',CAT/'standards/qa_frame.py',CAT/'standards/COORDINATE_CONTRACT.md',CAT/'materials/material_manifest.json',CAT/'materials/staff/manifest.json']+list((CAT/'materials').glob('*.png'))+list((CAT/'materials/staff').glob('*.png')):
 deps.append({'path':str(p.relative_to(CAT)),'sha256':sha(p),'unchanged_shared_dependency':True})
(BASE/'manifest.json').write_text(json.dumps({'family':'Hospitality service stations','unique_design_count':2,'assets':records},indent=2)+'\n');(BASE/'qa/runtime_cost.json').write_text(json.dumps({'scope':'Actual exported file cost, not runtime performance','assets':costs},indent=2)+'\n');(BASE/'dependency_manifest.json').write_text(json.dumps({'dependencies':deps},indent=2)+'\n');(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'images':media},indent=2)+'\n');print('STATION_RECORDS_FINALIZED',len(media))
