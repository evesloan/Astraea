"""Freeze/read-only binding and exact runtime cost summary for original use family."""
from pathlib import Path
import json,hashlib,struct,sys
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for mp in sorted(BASE.glob('AST-CUL-*.manifest.json')):
 rec=json.loads(mp.read_text());p=BASE/rec['export'];raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);groups=[]
 for node in d['nodes']:
  if 'mesh'not in node:continue
  m=d['meshes'][node['mesh']];groups.append({'node':node['name'],'material_role':node.get('extras',{}).get('material_role'),'semantic_parts':json.loads(node.get('extras',{}).get('semantic_parts','[]')),'triangles':sum(d['accessors'][pr['indices']]['count']//3 for pr in m['primitives'])})
 records.append({'catalogue_id':rec['catalogue_id'],'primary_export':rec['export'],'primary_export_bytes':len(raw),'evaluated_triangles':rec['evaluated_triangles'],'material_roles':rec['material_roles'],'mesh_groups':len(groups),'groups':groups,'terminal_derivatives_are_not_new_designs':[s['export']for s in rec['state_derivatives']],'optional_close_detail_derivative':None,'performance_claim':None})
(BASE/'qa/export_cost_breakdown.json').write_text(json.dumps({'assets':records,'scope':'Measured actual primary exports; no engine performance or crowd claim'},indent=2)+'\n')
files=[BASE/'source/build_auditorium_use.py',BASE/'source/draw_markings.py',BASE/'source/rehearsal_notes.png']+sorted((BASE/'source').glob('AST-CUL-*.blend'))+sorted((BASE/'exports').glob('*.glb'))
freeze=BASE/'qa/frozen_sources_r07.json'
if '--freeze'in sys.argv:
 assert not freeze.exists(),'Keep earlier freezes; do not overwrite silently'
 freeze.write_text(json.dumps({'revision':'r07_retained_pivots','scope':'All source/material/exports frozen before imported capture','files':[{'path':str(p.relative_to(BASE)),'sha256':sha(p)}for p in files]},indent=2)+'\n')
else:
 fr=json.loads(freeze.read_text());states=[{'path':r['path'],'frozen_sha256':r['sha256'],'current_sha256':sha(BASE/r['path']),'unchanged':sha(BASE/r['path'])==r['sha256']}for r in fr['files']]
 checks={name:json.loads((BASE/'qa'/name).read_text()).get('all_passed')for name in('source_reload_checks.json','geometry_checks.json','glb_validation.json','native_marker_checks.json','light_aperture_paths.json','retained_bearing_checks.json','source_only_rebuild.json')}
 image_checks=[]
 if (BASE/'qa/render_evidence.json').exists():
  for v in json.loads((BASE/'qa/render_evidence.json').read_text())['views']:
   valid=sha(BASE/'qa'/v['image'])==v['image_sha256'] and all(sha(BASE.parents[1]/f['file'])==f['sha256']for f in v['inputs'])and all(sha(BASE/r['source'])==r['sha256']for r in v['source_bindings']);image_checks.append({'image':v['image'],'bound_current_sources_exports_image':valid,'whole_target_visible':v['camera_preflight']['whole_target_visible']})
 report={'frozen_files':states,'author_checks':checks,'images':image_checks,'capture_complete':len(image_checks)==4,'all_passed':len(image_checks)==4 and all(x['unchanged']for x in states)and all(checks.values())and all(v['bound_current_sources_exports_image']and v['whole_target_visible']for v in image_checks)};(BASE/'qa/final_binding_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_passed':report['all_passed'],'checks':checks,'images':image_checks},indent=2))
 paths=sorted(p for p in BASE.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'and not any(part.startswith('source_only_r')for part in p.relative_to(BASE).parts[:-1]))
 (BASE/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(BASE))+'\n'for p in paths))
