"""Bind final source/export/evidence hashes and measured resource cost records."""
import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
glb=json.loads((BASE/'qa/glb_validation.json').read_text());src=json.loads((BASE/'qa/source_reload_checks.json').read_text());coord=json.loads((BASE/'qa/connection_node_checks.json').read_text());assert glb['all_passed'] and src['all_passed'] and coord['all_passed']
records=[];costs=[];dependencies=[]
for r in glb['results']:
 ident=Path(r['file']).stem;p=BASE/f'{ident}.manifest.json';m=json.loads(p.read_text());assert r['sha256']==sha(BASE/m['export'])
 m['removable_export_nodes']=next(a['removable_mesh_nodes'] for a in coord['results'] if a['file']==ident+'.glb')
 m['generator_sha256']=sha(BASE/'source/build_utility_machines.py');m['collision_generator']='source/build_collision_proposals.py';m['source_sha256']=sha(BASE/m['source']);m['glb_sha256']=r['sha256']
 m['measured_runtime_cost']={'triangles':r['triangle_count'],'mesh_count':r['runtime_mesh_count'],'primitive_count':r['runtime_primitive_count'],'embedded_texture_count':r['embedded_png_texture_count'],'glb_bytes':(BASE/m['export']).stat().st_size,'source_blend_bytes':(BASE/m['source']).stat().st_size,'performance_status':'File-level resource evidence; no target-PC runtime timing or engine profiling'}
 m['QA']={'source_reload':'qa/source_reload_checks.json','source_passed':True,'actual_glb':'qa/glb_validation.json','actual_glb_passed':True,'connection_nodes':'qa/connection_node_checks.json','connection_nodes_passed':True,'camera_preflight':'qa/camera_preflight.json','render_evidence':'qa/render_evidence.json','review_media_manifest':'qa/review_media_manifest.json','UV_normal_status':'All actual exported triangles have finite noncollapsed UVs, nonzero area, unit normals and coherent winding. Used embedded textures match unchanged staff source pixels.'}
 m['dependencies'] += ['source/build_collision_proposals.py'] if 'source/build_collision_proposals.py' not in m['dependencies'] else []
 p.write_text(json.dumps(m,indent=2)+'\n');records.append(m);costs.append({'catalogue_id':ident,**m['measured_runtime_cost'],'geometry_groups':m['runtime_material_group_meshes'],'material_roles':m['material_roles'],'collision_proxy_count':len(json.loads((BASE/'collision_proposals.json').read_text())[ident]['primitives']),'collision_status':'Offline conservative proposal, requires engine-side cost/simplification review'})
for p in [CAT/'standards/staff_materials.py',CAT/'standards/utility_ports.py',CAT/'standards/utility_port_spec.json',CAT/'standards/COORDINATE_CONTRACT.md',CAT/'materials/staff/manifest.json']+list((CAT/'materials/staff').glob('*.png')):
 dependencies.append({'path':str(p.relative_to(CAT)),'sha256':sha(p),'unchanged_shared_dependency':True})
(BASE/'manifest.json').write_text(json.dumps({'family':'Purpose-shaped engineering utility machines','unique_design_count':2,'assets':records},indent=2)+'\n');(BASE/'qa/runtime_cost.json').write_text(json.dumps({'scope':'Measured file cost, not device performance','assets':costs},indent=2)+'\n');(BASE/'dependency_manifest.json').write_text(json.dumps({'dependencies':dependencies},indent=2)+'\n');print('MACHINE_RECORDS_FINALIZED')
