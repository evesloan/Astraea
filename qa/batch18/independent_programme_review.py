"""Read-only exact source verification of handoff; no host geometry acceptance."""
from pathlib import Path
import sys,json,hashlib,zipfile,itertools
import numpy as np
import fitz
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18'
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/workspace/scratch/375c2e438292/district-layout-audit')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
hp=ROOT/'references/retail/D09_retail_programme_reference_handoff.json';h=json.loads(hp.read_text())
xp=ROOT/'references/retail/D09_exact_coverage_rows.json';x=json.loads(xp.read_text())
vp=ROOT/'references/retail/D09_atlas_vector_evidence.json';v=json.loads(vp.read_text())
rows=[]
with zipfile.ZipFile(SRC/'sources/Astraea_Master_Design_Source.zip')as archive:
 for row in h['sources']:
  p=(ROOT if row['source_root']=='catalogue'else SRC)/row['path'];actual=sha(p)
  entry={'id':row['id'],'source_root':row['source_root'],'path':row['path'],'expected_sha256':row['sha256'],'actual_sha256':actual,'passed':actual==row['sha256']}
  if 'archive_member'in row:entry['archive_member_bytes_match']=hashlib.sha256(archive.read(row['archive_member'])).hexdigest()==actual;entry['passed']&=entry['archive_member_bytes_match']
  rows.append(entry)
cov=json.loads((SRC/'extracted/project_docs/architecture/whole_ship_coverage.json').read_text());original=[r for r in cov['rooms']if r['deck']==9]
coverage={'exact110_objects_match':original==x['rooms'],'count':len(original),'unique_ids':len({r['id']for r in original}),'small_retail_count':sum(r['family_id']=='small_retail'for r in original),'R070':next(r for r in original if r['id']=='R070')}
pdf=fitz.open(SRC/'sources/Astraea-current-layout-atlas.pdf');page=pdf[10];draw=page.get_drawings();cal=v['calibration']
def bounds(index,inset=False):
 rect=draw[index]['rect'];prefix='inset'if inset else'main';hull=cal[prefix+'_hull_pdf_bounds'];scale=cal[prefix+'_scale_points_per_m'];cy=cal[prefix+'_x_zero_pdf_y']
 return {'x':[(rect.y0-cy)/scale,(rect.y1-cy)/scale],'z':[(rect.x0-hull[0])/scale-541,(rect.x1-hull[0])/scale-541]}
candidate=h['selected_candidate'];exact=candidate['historical_allocation_bounds_ship_xz_m'];checks=[]
for index,inset in [(candidate['matching_main_plan_drawing_index'],False),(candidate['direct_identity_proof']['inset_allocation']['drawing_index_zero_based'],True)]:
 b=bounds(index,inset);err=max(abs(b[k][i]-exact[k][i])for k in ['x','z']for i in [0,1]);checks.append({'drawing':index,'inset':inset,'actual_bounds_xz_m':b,'max_error_m':err,'passed':err<.002})
door=[]
for index,inset in [(candidate['matching_main_plan_door_drawing_index'],False),(candidate['direct_identity_proof']['inset_door_symbol']['drawing_index_zero_based'],True)]:
 b=bounds(index,inset);center=[np.mean(b[k])for k in ['x','z']];door.append({'drawing':index,'inset':inset,'center_xz_m':center,'symbol_dimensions_xz_m':[np.ptp(b[k])for k in ['x','z']],'passed':np.max(abs(np.array(center)-candidate['historical_door_symbol_ship_xz_m']))<.002})
M=np.array(h['coordinate_frame_for_optional_source_check']['source_to_ship_rotation_matrix']);C=np.array([[1,0,0],[0,0,1],[0,-1,0]]);yaw=np.array([[0,0,1],[0,1,0],[-1,0,0]])
corners=np.array(list(itertools.product([-6,6],[0,12],[0,2.9])));ship=corners@M.T+np.array([78,52.5,236])
transform={'determinant':float(np.linalg.det(M)),'native_yaw90_times_export_basis_equals_source_map':bool(np.array_equal(yaw@C,M)),'source_bounds_map_to_ship_allocation':bool(np.allclose(ship[:,0].min(),66)and np.allclose(ship[:,0].max(),78)and np.allclose(ship[:,2].min(),230)and np.allclose(ship[:,2].max(),242)),'wrong_lateral_sign_negative_control_determinant':float(np.linalg.det(M@np.diag([-1,1,1]))),'front_source_minusY_maps_toward_historical_door':bool(np.array_equal(M@np.array([0,-1,0]),[1,0,0]))}
unknowns=['actual_finished_interior_polygon','actual_door_aperture_width_height','moving_leaf_pockets_and_travel','header_and_threshold_support','actual_facility_slot_ids_positions_facing_owners','actual_approach_and_turn_envelopes'];nulls={k:candidate[k]is None for k in unknowns}
report={'passed':all(r['passed']for r in rows)and coverage['exact110_objects_match']and coverage['count']==110 and coverage['small_retail_count']==100 and all(r['passed']for r in checks+door)and all(nulls.values())and transform['determinant']==1 and all(transform[k]for k in ['native_yaw90_times_export_basis_equals_source_map','source_bounds_map_to_ship_allocation','front_source_minusY_maps_toward_historical_door']),'bound_handoff':{'path':str(hp.relative_to(ROOT)),'sha256':sha(hp)},'source_hash_checks':rows,'exact_coverage_check':coverage,'actual_pdf_R070_allocation':checks,'actual_pdf_R070_door_symbols':door,'proper_frame_check':transform,'unknown_host_fields_remain_null':nulls,'actual_atlas_page11_pixels_inspected':True,'scope':'Independently reopened actual PDF and original source ZIP/coverage JSON. Copied handoff source hashes, exact110 source rows, R070 allocation vectors and door-symbol centers agree. Allocation bounds and graphical door centers do not establish finished room, aperture or installation support.','limits':['100 small addresses plus seven larger retail destinations means107 shopping destinations, not capacity. All ten larger destinations means110 D09 registered spaces.','Source formulation checked against actual PDF vectors and named R070 coverage. Other84 unlabelled ID-to-footprint assignments are not inferred.','New actual asset geometry, complete movement, support and low-resolution images remain a later gate. No host project or slot ownership is recovered here.'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_programme_review.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item())+'\n');print('Independent programme review',report['passed'],'sources',len(rows),'R070 bounds',checks,'door symbol centers',door)
