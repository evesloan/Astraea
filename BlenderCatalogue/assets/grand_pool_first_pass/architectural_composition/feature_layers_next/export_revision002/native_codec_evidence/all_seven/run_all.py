from pathlib import Path
import json,sys,datetime,hashlib
import diagnose_arrays as d
from check_materials_transforms import inspect_asset
S=Path(__file__).resolve().parent;inputs=d.read(d.STUDY/'NATIVE_INPUTS.json');summaries=[];all_issues=[]
protected={p:d.sha(p) for p in d.STUDY.iterdir() if p.is_file()}
for index,a in enumerate(inputs['assets']):
 sys.argv=['diagnose_arrays.py','--asset',a['name'],'--out',f'asset{index:02d}'];d.main()
 geometry=d.read(S/f'asset{index:02d}/DIAGNOSIS.json');materials=inspect_asset(a)
 p=S/f'asset{index:02d}/MATERIALS_TRANSFORMS.json';p.write_text(json.dumps(materials,indent=2,default=d.jsonable)+'\n')
 rows=geometry['surfaces'];summary={'asset':a['name'],'triangles':sum(x['native_triangles'] for x in rows),'exact_position_uv_cyclic':all(x['exact_position_uv_cyclic_multiset'] for x in rows),'exact_codec_bits':all(x['source_derived_codec_diagnostic']['native_triangles_bits_exact_to_codec']==x['native_triangles'] and x['source_derived_codec_diagnostic']['complete_source_codec_numeric_bijection'] for x in rows),'codec_residual_max':max(x['source_derived_codec_diagnostic']['native_vs_codec_max'] for x in rows),'old_bound_exceeding_corners':sum(x['normal_exceeding_corners'] for x in rows),'old_bound_exceeding_triangles':sum(x['normal_exceeding_triangles'] for x in rows),'native_delta_max':max(x['normal_error_max'] for x in rows),'arrays_before_after_draw_bit_exact':all(x['after_draw_comparison']['all_slots_bit_identical'] for x in rows),'format_before_after_draw_exact':all(x['format_unchanged'] for x in rows),'material_transform_issues':materials['issues'],'texture_occurrences':materials['texture_occurrences'],'geometry_report_sha256':d.sha(S/f'asset{index:02d}/DIAGNOSIS.json'),'materials_transforms_report_sha256':d.sha(p)};summaries.append(summary);all_issues.extend(materials['issues']);print(json.dumps(summary),flush=True)
for p,h in protected.items():d.require(d.sha(p)==h,'Frozen study file changed during offline work')
out={'status':'SEVEN_ASSET_OFFLINE_DIAGNOSIS_COMPLETE','verification':'UNVERIFIED_IMPORT_EQUIVALENCE','installed':False,'geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'engine_launched':False,'threshold_changed':False,'old_normal_limit':d.NORMAL_LIMIT,'frozen_study_files_unchanged':True,'assets':summaries,'total_triangles':sum(x['triangles'] for x in summaries),'remaining_material_transform_discrepancies':all_issues,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p=S/'SEVEN_ASSET_SUMMARY.json';p.write_text(json.dumps(out,indent=2)+'\n');print('SUMMARY',p,d.sha(p))
