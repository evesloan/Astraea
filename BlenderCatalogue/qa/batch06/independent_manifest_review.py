"""Stable IDs, dimensions, material roles, actual costs and dependency hashes."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for p in sorted((ROOT/'assets').glob('utility*/AST-ENG-*.manifest.json')):
    m=json.loads(p.read_text());ident=m['catalogue_id'];g=json.loads((OUT/('independent_export_'+ident+'.json')).read_text())
    src=p.parent/(m.get('source') or m['source_file']);export=p.parent/(m.get('export') or m.get('exchange') or m.get('export_file'));generator=p.parent/m['generator']
    dims=m.get('dimensions_blender_source_xyz_m')
    if dims is None:dims=m.get('bounds_blender_z_up',m.get('bounds_blender_source'))['dimensions_m']
    tris=m.get('triangles',m.get('evaluated_triangles',m.get('evaluated_source_triangles')))
    roles=m.get('material_roles',m.get('used_material_roles'))
    row={'catalogue_id':ident,'manifest':str(p.relative_to(ROOT)),'manifest_sha256':sha(p),'source_sha256':sha(src),'export_sha256':sha(export),'generator_sha256':sha(generator),
         'source_hash_matches':m['source_sha256']==sha(src),'export_hash_matches':m['glb_sha256']==sha(export),
         'generator_hash_matches_if_recorded':m.get('generator_sha256',sha(generator))==sha(generator),
         'dimensions_max_error_m':float(np.max(np.abs(np.asarray(dims)-g['dimensions_xyz']))),'triangle_count_matches':tris==g['triangles'],
         'material_roles_match':set('ASTRAEA_'+x for x in roles)==set(x['name'] for x in g['materials']),
         'actual_runtime_cost':g['runtime_cost'],'actual_export_issues':g['issues']}
    row['pass']=all(row[k] for k in ['source_hash_matches','export_hash_matches','generator_hash_matches_if_recorded','triangle_count_matches','material_roles_match']) and row['dimensions_max_error_m']<1e-6 and not row['actual_export_issues']
    rows.append(row)
out={'assets':rows,'unique_design_count':len(rows),'expected_ids_match':set(r['catalogue_id'] for r in rows)==set('AST-ENG-00'+str(i) for i in range(1,7)),
     'total_six_glb_triangles':sum(r['actual_runtime_cost']['triangles'] for r in rows),'total_glb_bytes':sum(r['actual_runtime_cost']['glb_bytes'] for r in rows),'pass':len(rows)==6 and all(r['pass'] for r in rows),
     'limits':'These measured costs are offline asset data, not a draw-call guarantee or target-GPU/engine budget acceptance. Generator hashes bind the current reproducible delivery instructions.'}
(OUT/'independent_manifest_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
