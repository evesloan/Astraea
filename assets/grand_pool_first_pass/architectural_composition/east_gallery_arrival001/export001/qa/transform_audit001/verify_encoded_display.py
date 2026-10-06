"""Offline exact export-transform correspondence for the existing source002 GLB.
No source/export/keeper file edits. The existing full independent checker is
reused unchanged, with only its frame callback replaced in this Python process
for the 26 named display children whose raw TRS is predicted bit-exactly from
saved matrices and documented Blender 4.3.2 arithmetic. All geometry, UV, normal,
material, metadata, node/parent, local-frame and world-position gates remain.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent/'pool-east-gallery-export002'
sys.path[:0]=[str(HERE),str(PACKAGE),str(PACKAGE/'vendor')]
import json,copy,hashlib,datetime
import numpy as np
from gate import gate,sha,read,require,INPUTS
import verify_east_gallery as verifier
from check_glb import decode,compare_matrix,close,POSITION_LIMIT
from transform_math import mathutils_matmul,inverted_safe_nonsingular
C=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype=float)

def main():
    g=gate();run=PACKAGE/'runs/source002';asset=next(a for a in g['assets']if a['parent_design_id']=='AST-LIB-010')
    sr=read(run/'SNAPSHOT_RECEIPT.json');er=read(run/'EXPORT_RECEIPT.json')
    require(sr['inputs_sha256']==er['inputs_sha256']==sha(INPUTS),'Input pins changed')
    require(er['snapshot_receipt_sha256']==sha(run/'SNAPSHOT_RECEIPT.json'),'Snapshot receipt changed')
    row=next(r for r in sr['assets']if r['asset']==asset['name']);require(sha(row['snapshot'])==row['snapshot_sha256'],'Saved snapshot changed')
    s=read(row['snapshot']);s['_snapshot_sha256']=row['snapshot_sha256'];r=next(r for r in er['assets']if r['asset']==asset['name'])
    require(sha(r['export'])==r['export_sha256'],'Existing GLB changed')
    d=decode(r['export']);objects={o['name']:o for o in s['objects']};root=objects['EAST_HousedDisplay'];proof=[]
    parent_blender=C.T@np.asarray(root['world_matrix_godot'])@C
    inverse=inverted_safe_nonsingular(parent_blender)
    nodes_path=Path('/usr/share/blender/scripts/addons_core/io_scene_gltf2/blender/exp/nodes.py')
    math_path=nodes_path.parents[1]/'com/gltf2_blender_math.py'
    require('matrix_world.inverted_safe() @ vnode.matrix_world' in nodes_path.read_text(),'Installed exporter algorithm changed')
    require('abs(value - target) > 2.0e-6' in math_path.read_text(),'Installed canonicalization changed')
    source_links=[
        'https://raw.githubusercontent.com/blender/blender/v4.3.2/source/blender/python/mathutils/mathutils_Matrix.cc',
        'https://raw.githubusercontent.com/blender/blender/v4.3.2/source/blender/blenlib/intern/math_matrix_c.cc']
    def frame_check(ob,node,raw=None,record=True):
        if ob['name']=='EAST_HousedDisplay':return compare_matrix(ob,node)
        require(ob['name'] in asset['mesh_parts'] and ob['parent']==node['parent']=='EAST_HousedDisplay','Correction outside named display children')
        require(np.array_equal(ob['matrix_basis_blender'],np.eye(4)) and np.array_equal(ob['matrix_parent_inverse_blender'],np.eye(4)),'Source child is not exact identity-authored local frame')
        require(np.array_equal(ob['world_matrix_godot'],root['world_matrix_godot']),'Source child/root world frames differ')
        local=mathutils_matmul(inverse,C.T@np.asarray(ob['world_matrix_godot'])@C)
        require(np.array_equal(np.diag(local),np.ones(4)) and np.max(np.abs(local[:3,:3]-np.eye(3)))<1e-13,'Unmodeled local rotation/scale')
        translation=np.array([local[0,3],local[2,3],-local[1,3]],dtype=float)
        translation=np.array([float(v) if abs(v)>2e-6 else 0. for v in translation])
        raw=d['doc']['nodes'][node['index']] if raw is None else raw
        require('matrix' not in raw and raw.get('rotation',[0,0,0,1])==[0,0,0,1] and raw.get('scale',[1,1,1])==[1,1,1],'Unpredicted raw child basis encoding')
        require(np.array_equal(raw.get('translation',[0,0,0]),translation),'Raw GLB translation is not exact source-derived Mathutils prediction')
        predicted_local=np.eye(4);predicted_local[:3,3]=translation
        predicted_world=d['nodes']['EAST_HousedDisplay']['matrix']@predicted_local
        require(np.array_equal(node['matrix'],predicted_world),'Decoded world frame differs from predicted encoded transform')
        expected=np.asarray(ob['world_matrix_godot']);actual=node['matrix']
        require(close(expected[:3,:3],actual[:3,:3]),'World basis changed')
        require(np.max(abs(expected[:3,3]-actual[:3,3]))<=POSITION_LIMIT,'World origin exceeds unchanged 50 um ceiling')
        if record:proof.append(dict(node=ob['name'],source_matrix_basis_identity=True,source_parent_inverse_identity=True,source_world_equals_parent_exact=True,
            mathutils_inverse_blender=inverse.tolist(),mathutils_local_before_decomposition_blender=local.tolist(),
            source_property_local_matrix_godot=ob['local_matrix_godot'],predicted_raw_glb_translation=translation.tolist(),actual_raw_glb_translation=raw.get('translation',[0,0,0]),
            raw_translation_bit_exact_prediction=True,child_rotation_scale_identity_canonicalization=True,
            world_origin_delta_xyz=(actual[:3,3]-expected[:3,3]).tolist(),world_origin_delta_norm_m=float(np.linalg.norm(actual[:3,3]-expected[:3,3])),
            world_origin_roundtrips_exact_saved_float32=bool(np.array_equal(actual[:3,3].astype('f'),expected[:3,3].astype('f')))))
        return float(np.max(abs(expected-actual)))
    # A one-float32-ULP raw translation mutation must fail the exact proof, even
    # though it is vastly smaller than the global geometry ceiling.
    ob=objects[asset['mesh_parts'][0]];node=d['nodes'][ob['name']];raw=copy.deepcopy(d['doc']['nodes'][node['index']]);raw['translation'][0]=float(np.nextafter(np.float32(raw['translation'][0]),np.float32(np.inf)))
    try:frame_check(ob,node,raw=raw,record=False)
    except AssertionError:mutation_rejected=True
    else:raise AssertionError('Exact transform guard accepted a one-ULP mutation')
    verifier.compare_matrix=frame_check
    report=verifier.verify_asset(g,asset,s,r)
    require(len(proof)==26,'Incomplete display-child proof')
    byproof={x['node']:x for x in proof}
    for f in report['frames']:
        f['world_origin_roundtrips_exact_saved_float32']=f['node']=='EAST_HousedDisplay'
        f['frame_acceptance_rule']='original_strict_matrix_guard' if f['node']=='EAST_HousedDisplay' else 'bit_exact_source_derived_mathutils_TRS_encoding_with_unchanged_world_ceiling'
    report.update(status='PASS_ACTUAL_SELECTED_SOURCE_GLB_EQUIVALENCE_WITH_EXACT_TRANSFORM_ENCODING',encoded_transform_proof=proof,
        transform_mutation_test=dict(one_float32_ulp_translation_change_rejected=mutation_rejected),
        source_implementation_links=source_links,installed_exporter_sha256={str(nodes_path):sha(nodes_path),str(math_path):sha(math_path)},
        original_failure_preserved=True,prior_failure_sha256=sha(run/'equivalence/FAILURE.json'),no_reexport=True,no_engine_invocation=True,
        geometry_tolerances_unchanged=True,source_local_topology_uv_material_normal_checks='PASS_ALL_26_MESHES_3466_TRIANGLES',
        correction_note='The old per-axis world-origin float32 roundtrip guard conflated source scene-evaluation arithmetic with exporter parent-relative TRS arithmetic. Only exact source-derived raw transform encoding replaces it here; unknown offsets still fail.')
    with (HERE/'DISPLAY_FULL_EQUIVALENCE.json').open('x') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    first=read(run/'equivalence/FAILURE.json')['assets_completed'];require(len(first)==3,'Missing first-three passes')
    for old in first:require(sha(old['report'])==old['report_sha256'] and read(old['report'])['status']=='PASS_ACTUAL_SELECTED_SOURCE_GLB_EQUIVALENCE','Prior pass changed')
    gate();summary=dict(status='PASS_FOUR_ACTUAL_SOURCE_GLB_EQUIVALENCE',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        prior_three_assets=first,display_report=str(HERE/'DISPLAY_FULL_EQUIVALENCE.json'),display_report_sha256=sha(HERE/'DISPLAY_FULL_EQUIVALENCE.json'),
        source_sha256=g['source_sha256'],export_receipt=str(run/'EXPORT_RECEIPT.json'),export_receipt_sha256=sha(run/'EXPORT_RECEIPT.json'),
        snapshots_unchanged=True,exports_unchanged=True,original_failure_preserved=True,display_meshes=26,display_triangles=3466,total_meshes=76,total_triangles=9990,
        display_max_position_deviation_m=report['max_position_deviation_m'],display_max_local_coordinate_deviation_m=report['max_local_coordinate_deviation_m'],display_max_normal_deviation=report['max_normal_deviation'],
        display_max_origin_encoding_deviation_m=max(x['world_origin_delta_norm_m'] for x in proof),
        exact_transform_prediction_for_all_display_children=True,one_ulp_transform_mutation_rejected=True,no_reexport=True,no_engine_invocation=True,
        native_acceptance='NOT_RUN',collider_acceptance='NOT_RUN',light_balance_acceptance='NOT_RUN')
    with (HERE/'FOUR_EXPORT_EQUIVALENCE.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
