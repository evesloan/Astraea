"""Cross-check manifests, saved source, exported geometry and immutable prior files."""
from pathlib import Path
import json,hashlib,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
sys.path.insert(0,str(ROOT/'qa'));from inspect_glb_independent import GLB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
glbs={Path(r['path']).name:r for r in json.loads((OUT/'independent_glb_report.json').read_text())}
sources={Path(r['path']).name:r for p in OUT.glob('independent_aquatic_*_blend_report.json') for r in json.loads(p.read_text())}
rows=[];texture_rows=[]
for family in ['aquatic_lounge','aquatic_edges','aquatic_float']:
 for p in sorted((ROOT/'assets'/family).rglob('*.manifest.json')):
  if 'qa' in p.relative_to(ROOT/'assets'/family).parts:continue
  j=json.loads(p.read_text());base=ROOT/'assets'/family;src=base/j['source'];glb=base/j.get('exchange',j.get('export'));gen=base/j['generator'];g=glbs.get(glb.name);s=sources.get(src.name)
  r={'manifest':str(p.relative_to(ROOT)),'catalogue_id':j['catalogue_id'],'source_sha256':sha(src),'glb_sha256':sha(glb),'generator_sha256':sha(gen),'issues':[]}
  for k in ['source_sha256','glb_sha256','generator_sha256']:
   r[k+'_matches']=r[k]==j.get(k) if k in j else None
   if r[k+'_matches'] is False:r['issues'].append(k+' mismatch')
  if not s or not g:r['issues'].append('Independent source/GLB inspection unavailable');rows.append(r);continue
  obs=[o for o in s['objects'] if 'evaluated_triangles' in o];lo=np.array([o['min_xyz'] for o in obs]).min(0);hi=np.array([o['max_xyz'] for o in obs]).max(0)
  r['source_parts']=len(obs);r['source_triangles']=sum(o['evaluated_triangles'] for o in obs);r['glb_triangles']=g['triangles'];r['glb_materials']=g['material_count'];r['glb_primitives']=g['primitive_count'];r['glb_dimensions_m']=g['dimensions_xyz'];r['source_dimensions_m']=(hi-lo).tolist()
  r['source_export_bounds_max_difference_m']=float(max(np.abs(lo-g['min_xyz']).max(),np.abs(hi-g['max_xyz']).max()))
  bounds=j.get('bounds_blender_z_up',{});dims=j.get('dimensions_m',bounds.get('dimensions_m'))
  r['manifest_dimensions_max_difference_m']=float(np.abs(np.array(dims)-g['dimensions_xyz']).max()) if dims else None
  r['manifest_triangles']=j.get('triangles',j.get('evaluated_triangles'))
  r['manifest_parts']=j.get('editable_semantic_parts',j.get('source_object_count'))
  if r['source_triangles']!=g['triangles'] or r['manifest_triangles']!=g['triangles']:r['issues'].append('Triangle count mismatch')
  if r['source_export_bounds_max_difference_m']>1e-5 or (r['manifest_dimensions_max_difference_m'] or 0)>1e-5:r['issues'].append('Bounds mismatch')
  if r['manifest_parts']!=len(obs):r['issues'].append('Editable source part count mismatch')
  r['material_roles_match']=sorted(m['name'].replace('ASTRAEA_','') for m in g['materials'])==sorted(j['material_roles'])
  if not r['material_roles_match']:r['issues'].append('Semantic role mismatch')
  r['source_uv_layers']=sorted({u for o in obs for u in o.get('uv_layers',[])})
  r['source_has_editable_modifiers']=any(o.get('modifiers') for o in obs)
  r['units']=s['units'];r['source_reloaded']=s['load_success'];rows.append(r)
  for m in g['materials']:
   role=m['name'].replace('ASTRAEA_','');paths=list((ROOT/'materials').rglob(role+'.png'));im=g['images'][m['image_index']] if 'image_index' in m else None
   texture_rows.append({'asset':j['catalogue_id'],'role':role,'material_file':str(paths[0].relative_to(ROOT)) if paths else None,'embedded_image':im,'matches_material_file':bool(im and len(paths)==1 and im.get('embedded_sha256')==sha(paths[0]))})
(OUT/'independent_manifest_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
(OUT/'independent_texture_source_check.json').write_text(json.dumps(texture_rows,indent=2)+'\n')
guard=json.loads((OUT/'independent_prior_batch_guard.json').read_text());changes=[]
for x in guard['files']:
 p=ROOT/x['path'];current=sha(p) if p.exists() else None
 if current!=x['baseline_sha256']:changes.append(x['path'])
exception_path=OUT/'independent_authorized_metadata_exception.json'
exception=json.loads(exception_path.read_text()) if exception_path.exists() else {'paths':[]}
unexpected=[p for p in changes if p not in exception['paths']]
(OUT/'independent_prior_batch_stability.json').write_text(json.dumps({'baseline_commit':guard['baseline_commit'],'guarded_files':len(guard['files']),'scope':guard['scope'],'changed':changes,'all_unchanged':not changes,'authorized_metadata_exception':exception,'unexpected_changed':unexpected,'outside_authorized_metadata_exception_unchanged':not unexpected},indent=2)+'\n')
print(json.dumps({'assets':[{'id':r['catalogue_id'],'issues':r['issues']} for r in rows],'texture_mismatches':[r for r in texture_rows if not r['matches_material_file']],'prior_file_changes':changes},indent=2))
