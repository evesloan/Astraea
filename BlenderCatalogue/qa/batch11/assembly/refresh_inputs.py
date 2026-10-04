"""Bind current author-declared fixture transforms and inspection eye to the plan."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
p=OUT/'plan.json';d=json.loads(p.read_text())
paths={'guest':'assets/landing_guest/qa_context_placements.json','staff':'assets/landing_service/interface_api.json'}
g=json.loads((ROOT/paths['guest']).read_text());s=json.loads((ROOT/paths['staff']).read_text())['assets']
ga=g['AST-LND-001']['fixture'];sa=s['AST-LND-003']['fixture_context']
d['context']=[{'key':'guest_sconce','parent':'guest_directory','catalogue_id':ga['catalogue_id'],'path':ga['path_from_catalogue_root'],'parent_local_source_matrix':ga['source_local_transform_4x4'],'declared_placement_source':paths['guest'],'counted_as_new':False},{'key':'staff_fixture','parent':'staff_return','catalogue_id':sa['asset_id'],'path':str((ROOT/'assets/landing_service'/sa['existing_export']).resolve().relative_to(ROOT)),'parent_local_source_matrix':sa['matrix_source_local'],'declared_placement_source':paths['staff'],'counted_as_new':False}]
eye=g['AST-LND-002']['waiting_eye_proposal']['source_m'];parent=next(r for r in d['items'] if r['key']=='guest_waiting');assert parent['source_z_rotation_deg']==0
d['views']['guest_waiting_directory']['source_eye_m']=[a+b for a,b in zip(eye,parent['inspection_source_origin_m'])]
d['views']['guest_waiting_directory']['meaning']='Author-declared nonphysical waiting-eye proposal looking toward the inward-canted directory. No species or actor fit.'
d['author_interface_inputs']=[{'path':v,'sha256':hashlib.sha256((ROOT/v).read_bytes()).hexdigest()} for v in paths.values()]
p.write_text(json.dumps(d,indent=2)+'\n');print('Two fixture transforms and exact waiting eye updated from author interfaces')
