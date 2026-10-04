"""Consolidate independent measurements and final hashes without changing authored files."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch04'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exports=json.loads((OUT/'independent_glb_report.json').read_text());sources=[]
for p in OUT.glob('independent_botanical_*_blend_report.json'):sources+=json.loads(p.read_text())
sources={Path(x['path']).stem:x for x in sources};checks=[]
texture_hashes={sha(p):str(p.relative_to(ROOT)) for p in (ROOT/'materials').rglob('*.png')}
for e in exports:
 p=Path(e['path']);a=p.stem;s=sources[a.removesuffix('_START')];base=p.parent if p.parent.name!='exports' else p.parent.parent
 manifest=base/(a+'.manifest.json');m=json.loads(manifest.read_text()) if manifest.exists() else {}
 declared_triangles=m.get('triangles',m.get('evaluated_triangles'))
 bounds=m.get('bounds_blender_z_up',m);dims=bounds.get('dimensions_m')
 sh=m.get('source_sha256',m.get('source_blend_sha256',m.get('hashes',{}).get('blend_sha256')));gh=m.get('glb_sha256',m.get('hashes',{}).get('glb_sha256'))
 row={'asset':a,'same_design_variant':a.endswith('_START'),'source':str(Path(s['path']).relative_to(ROOT)),'export':str(p.relative_to(ROOT)),'source_sha256':s['sha256'],'export_sha256':e['sha256'],'source_current_matches_read':sha(Path(s['path']))==s['sha256'],'export_current_matches_read':sha(p)==e['sha256'],'manifest_source_hash_match':sh==s['sha256'] if sh else None,'manifest_export_hash_match':gh==e['sha256'] if gh else None,'triangles':e['triangles'],'source_evaluated_triangles':sum(o.get('evaluated_triangles',0) for o in s['objects']),'manifest_triangles_match':declared_triangles==e['triangles'] if declared_triangles is not None else None,'dimension_max_error_m':max(abs(x-y) for x,y in zip(dims,e['dimensions_xyz'])) if dims else None,'editable_parts':len([o for o in s['objects'] if o['type'] in ['MESH','CURVE']]),'all_file_textures_packed':all(i['packed'] for i in s['image_assets'] if i['filepath']),'all_embedded_export_textures_match_source_files':all(i.get('embedded_sha256') in texture_hashes for i in e['images']),'collapsed_uv_triangles':sum(p.get('collapsed_uv_triangles',0) for n in e['nodes'] for p in n['primitives']),'opaque_materials':e['opaque_material_audit'],'parser_issues':e['issues']}
 checks.append(row)
(OUT/'independent_manifest_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
guard=json.loads((OUT/'independent_prior_batch_guard.json').read_text())['files'];changed=[];missing=[]
for rel,h in guard.items():
 p=ROOT/rel
 if not p.exists():missing.append(rel)
 elif sha(p)!=h:changed.append(rel)
(OUT/'independent_prior_batch_stability.json').write_text(json.dumps({'guarded_files':len(guard),'changed':changed,'missing':missing,'all_unchanged':not changed and not missing},indent=2)+'\n')
print(json.dumps([{'asset':x['asset'],'triangles':x['triangles'],'source_matches':x['source_current_matches_read'],'export_matches':x['export_current_matches_read'],'manifest_matches':[x['manifest_source_hash_match'],x['manifest_export_hash_match'],x['manifest_triangles_match']],'dimension_max_error_m':x['dimension_max_error_m']} for x in checks],indent=2))
print('PRIOR_BATCH_UNCHANGED',not changed and not missing)
