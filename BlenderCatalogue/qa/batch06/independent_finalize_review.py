"""Bind independent bounded acceptance to final source/export/review bytes."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text())
names=['independent_reference_check.json','independent_export_summary.json','independent_manifest_report.json','independent_preservation_report.json','independent_port_report.json','independent_wheel_report.json','independent_console_report.json','independent_machine_report.json','independent_collision_report.json','independent_assembly_report.json','independent_visual_pipework.json','independent_visual_machines.json','independent_visual_console.json','independent_visual_assembly.json']
files=[]
for family in ['utility_machines','utility_console','utility_pipework']:
    for p in sorted((ROOT/'assets'/family).rglob('*')):
        if p.is_file() and not any(x in p.relative_to(ROOT/'assets'/family).parts for x in ['qa','renders','__pycache__']) and p.suffix in ['.blend','.glb','.py','.png','.json','.md','.txt']:
            files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)})
for rel in ['standards/utility_ports.py','standards/utility_port_spec.json','standards/COORDINATE_CONTRACT.md','standards/staff_materials.py','materials/staff/manifest.json','batches/batch06/CONTRACT.md','batches/batch06/reference_manifest.json']:
    p=ROOT/rel;files.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
known={x['path'] for x in files}
for ident in ['AST-ENG-00'+str(i) for i in range(1,7)]:
    audit=read('independent_source_'+ident+'.json')
    for im in audit['used_images']:
        p=((ROOT/audit['path']).parent/im['filepath'][2:]).resolve() if im['filepath'].startswith('//') else Path(im['filepath'])
        if p.is_absolute() and p.is_file() and p.is_relative_to(ROOT):
            rel=str(p.relative_to(ROOT))
            if rel not in known:files.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)});known.add(rel)
(OUT/'independent_final_source_hash_receipt.json').write_text(json.dumps({'scope':'Final active six-asset source/export/dependency receipt; QA renders and historical superseded images are scoped separately in review evidence.','files':files},indent=2)+'\n')
m=read('independent_manifest_report.json');ports=read('independent_port_report.json');pres=read('independent_preservation_report.json');assembly=read('independent_assembly_report.json')
checks={'six_unique_ids_costs_hashes':m['pass'],'source_export_geometry_materials_textures':all(not x['issues'] for x in read('independent_export_summary.json')),
        'frozen_prior_assets_materials':pres['no_frozen_changes'] and pres['all_other_changes_authorized'],
        'ten_actual_port_profiles_and_bores':ports['all_port_checks_pass'] and ports['all_profile_mates_pass'],
        'wheel_pivot_grips_correct_and_wrong_axis_sweeps':read('independent_wheel_report.json')['pass'],
        'console_controls_hatch_mounts':read('independent_console_report.json')['pass'],
        'machine_support_caps_receivers_service_access':read('independent_machine_report.json')['pass'],
        'numeric_collision_open_space_proposals':read('independent_collision_report.json')['pass'],
        'native_GLb_assembly_seams_and_service_reserves':assembly['numeric_pass'],
        'final_assembly_actual_GLB_pixels':read('independent_visual_assembly.json').get('bounded_visual_acceptance',False),
        'final_individual_actual_GLB_pixels':all(read(x)['bounded_visual_acceptance'] for x in ['independent_visual_machines.json','independent_visual_pipework.json','independent_visual_console.json'])}
scope_current=[]
for report in read('independent_export_summary.json'):
    scope_current.append({'path':report['path'],'export_report_hash_current':sha(ROOT/report['path'])==report['sha256']})
checks['all_export_reports_current']=all(x['export_report_hash_current'] for x in scope_current)
out={'decision':'PASS for bounded component source/export/visual/interoperability review' if all(checks.values()) else 'INCOMPLETE: see checks',
     'checks':checks,'asset_count':6,'measured_total_GLb_triangles':m['total_six_glb_triangles'],'measured_total_GLb_bytes':m['total_glb_bytes'],'protected_prior_file_count':pres['frozen_asset_material_and_coordinate_files'],
     'reports':[{'path':'qa/batch06/'+x,'sha256':sha(OUT/x)} for x in names],
     'final_source_receipt':'qa/batch06/independent_final_source_hash_receipt.json','current_export_evidence':scope_current,
     'resolved_during_review':['Wheel geometry translation corrected relative to actual pivot and grip records.','Real console service opening and coherent hatch children; annular moving-control sockets.','Filter support caps retained inside the hollow wall; grip centres labelled as centreline proposals.','Real pump front service aperture and separately tagged cover parts; coupling guard connected to a dedicated crossmember.','Numeric collision proposals preserve meaningful bores, open bays and control/service spaces.','Console dial, selector index and rear pad surfaces corrected before final hash-matched renders.'],
     'meaningful_remaining_limits':['Script-assisted original editable components, not recovered original game assets.','No installed room/ship route, native engine, actor/controller, electrical/fluid behavior, engineering/load/pressure/safety certification or target-GPU acceptance.','Finite sample sweeps/rays and support-cap checks are bounded geometric evidence, not continuous mechanical proof.','65,585 triangles across six base assets and many coarse compound collision pieces require runtime/scene-density budgeting and simplification; no LOD set is authored.','Fine secondary labels require closer views; original low-resolution/CRT pipeline readability and shading remain untested.','Shared ports are artistic dimensions; hardware release/threading, gasket compression and operating internals are not modelled or certified.','Durable backup/archive restore verification belongs to the lead’s final delivery gate and is not implied by this review.']}
(OUT/'independent_final_review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'decision':out['decision'],'checks':checks,'receipt_files':len(files),'triangles':m['total_six_glb_triangles']},indent=2))
