"""Pure independent decoded-GLB equivalence: no Blender/Godot invocation.
Full cyclic-winding triangle bijections and exact representable UVs for every
selected source mesh; unchanged local vertices, material graph semantics and
packed image bytes; exact node identity/parent and guarded matrix correspondence.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE/'vendor')]
import argparse,json,traceback,re
import numpy as np
from gate import gate,sha,read,require,run_path,write_new,INPUTS
from check_glb import decode,compare_matrix,material_check,concat,close,POSITION_LIMIT,NUMERIC_LIMIT
from provenance_match import match_with_provenance

def godot_node_name(name):
    # Godot Node.validate_node_name replaces . : @ / " % with underscore.
    # Approved selected names contain none of those characters; no engine-side
    # cleanup or hand-replaced subset is needed for the predicted bijection.
    return re.sub(r'[.:@/"%]', '_', name)

def expected_extras(g,a,s,row):
    extras=dict(row['extras'])
    if extras.get('export_excluded'):extras['export_excluded']=False
    extras.update(selected_source_properties_json=json.dumps(row['extras'],sort_keys=True),
        selected_source_scene_properties_json=json.dumps(s['scene_extras'],sort_keys=True),
        selected_source_evaluation_json=json.dumps(row['source_evaluation'],sort_keys=True),
        selected_source_frame_json=json.dumps({k:row[k] for k in ['parent','matrix_basis_blender','matrix_parent_inverse_blender','local_matrix_godot','world_matrix_godot']},sort_keys=True),
        exported_source_blend_sha256=g['source_sha256'],exported_source_snapshot_sha256=s['_snapshot_sha256'],
        parent_design_id=a['parent_design_id'],unique_catalogue_design=False,selected_derivative_name=a['name'],
        export_exclusion_override_scope='copy_only_selected_standalone_derivative' if row['extras'].get('export_excluded') else 'none')
    return extras

def verify_asset(g,a,s,r):
    require(sha(r['export'])==r['export_sha256'],'Export receipt pin mismatch')
    require(r['source_sha256']==g['source_sha256'] and r['snapshot_sha256']==s['_snapshot_sha256'],'Wrong source/snapshot receipt')
    d=decode(r['export']);doc=d['doc'];nodes=d['nodes'];source={x['name']:x for x in s['objects']}
    require(set(nodes)==set(source)==set(a['mesh_parts']+a['empty_objects']),'Node identity bijection failed')
    require(len(nodes)==len({godot_node_name(n) for n in nodes}),'Godot node names would collide')
    require(all(n==godot_node_name(n) for n in nodes),'Unreviewed Godot node name normalization')
    require(not doc.get('extensions',{}).get('KHR_lights_punctual'),'Unexpected real exported light')
    require(len([n for n in nodes.values() if n['mesh'] is not None])==len(a['mesh_parts']),'Wrong mesh count')
    reports=[];matreports={};markers=[];frame_reports=[];actual_overrides=[]
    for name,row in source.items():
        node=nodes[name];require(node['parent']==row['parent'],'Changed parent: '+name)
        require(node['extras']==expected_extras(g,a,s,row),'Changed/unapproved node metadata: '+name)
        if row['extras'].get('export_excluded'):
            require(a['programme_export'] or name in a['empty_objects'],'Unapproved source-excluded selection')
            actual_overrides.append(dict(node=name,key='export_excluded',source_value=True,export_value=False,
                reason='Selected standalone programme derivative' if a['programme_export'] else 'Selected source light-position reserve, no native light'))
        wd=compare_matrix(row,node)
        actual_local=np.linalg.inv(nodes[node['parent']]['matrix'])@node['matrix'] if node['parent'] else node['matrix']
        expected_local=np.asarray(row['local_matrix_godot'],dtype=float)
        require(close(actual_local[:3,:3],expected_local[:3,:3]),'Changed local basis: '+name)
        require(np.max(np.abs(actual_local[:3,3]-expected_local[:3,3]))<=POSITION_LIMIT,'Changed local translation: '+name)
        # World origins must additionally round-trip EXACTLY to saved float32
        # coordinates (compare_matrix), so this bound cannot sanction relocation.
        frame_reports.append(dict(node=name,parent=row['parent'],max_world_matrix_representation_difference=wd,
            max_local_basis_difference=float(np.max(np.abs(actual_local[:3,:3]-expected_local[:3,:3]))),
            max_local_translation_representation_difference_m=float(np.max(np.abs(actual_local[:3,3]-expected_local[:3,3]))),
            world_origin_roundtrips_exact_saved_float32=True))
        if row['type']=='EMPTY':
            require(node['mesh'] is None and not node['primitives'],'Marker/root gained geometry')
            markers.append(dict(node=name,parent=row['parent'],world_origin_xyz=node['matrix'][:3,3].tolist(),source_extras=row['extras']));continue
        require(node['mesh'] is not None and len(node['primitives'])==1,'Source mesh split/missing/unexpected primitive')
        primitive=node['primitives'][0];mat=row['material'];mi=primitive['material']
        key=(mat,mi)
        if key not in matreports:matreports[key]=material_check(s['materials'][mat],mi,d)
        result=match_with_provenance(concat([row]),concat([primitive]),check_local=True)
        require(result['triangles']==a['expected_mesh_triangles'][name],'Wrong source triangle count')
        correspondence=[dict(item,source_polygon=row['triangle_provenance'][item['source_triangle']]['polygon'],source_vertices=row['triangle_provenance'][item['source_triangle']]['vertices'],source_loops=row['triangle_provenance'][item['source_triangle']]['loops']) for item in result.pop('triangle_correspondence')]
        reports.append(dict(node=name,source_part=name,material=mat,**result,triangle_correspondence=correspondence))
    require(sorted(actual_overrides,key=lambda r:r['node'])==sorted(r['export_only_metadata_overrides'],key=lambda r:r['node']),'Export override receipt differs from actual nodes')
    require(sum(x['triangles'] for x in reports)==a['triangles'],'Lost/extra triangles')
    require(set(k[1] for k in matreports)==set(range(len(doc.get('materials',[])))),'Unused/unverified exported material')
    require({im['image_index'] for row in matreports.values() for im in row['images']}==set(range(len(d['images']))),'Unused/unverified packed image')
    return dict(status='PASS_ACTUAL_SELECTED_SOURCE_GLB_EQUIVALENCE',asset=a['name'],source_sha256=g['source_sha256'],snapshot_sha256=s['_snapshot_sha256'],export_sha256=r['export_sha256'],
        source_meshes=len(reports),source_triangles=a['triangles'],source_nodes=len(nodes),parent_design_id=a['parent_design_id'],
        max_position_deviation_m=max(x['max_position_deviation_m'] for x in reports),max_local_coordinate_deviation_m=max(x['max_local_coordinate_deviation_m'] for x in reports),max_normal_deviation=max(x['max_normal_deviation'] for x in reports),
        triangle_groups=reports,materials=list(matreports.values()),markers_and_roots=markers,frames=frame_reports,export_only_metadata_overrides=actual_overrides,
        predicted_godot_node_bijection={n:godot_node_name(n) for n in nodes},light_proposal_sha256=sha(g['light_proposal']),
        native_acceptance='NOT_RUN',collider_acceptance='NOT_RUN',light_balance_acceptance='NOT_RUN')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);args=ap.parse_args();g=gate();out=run_path(args.run)
    sr=read(out/'SNAPSHOT_RECEIPT.json');er=read(out/'EXPORT_RECEIPT.json')
    require(sr['status']=='PASS_FOUR_READ_ONLY_SOURCE_SNAPSHOTS' and er['status']=='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE','Wrong previous stage')
    require(sr['inputs_sha256']==er['inputs_sha256']==sha(INPUTS),'Changed input set')
    require(er['snapshot_receipt_sha256']==sha(out/'SNAPSHOT_RECEIPT.json'),'Snapshot receipt changed')
    require(len(sr['assets'])==len(er['assets'])==4,'Wrong asset count')
    dest=out/'equivalence';require(not dest.exists(),'Preserve previous checks');dest.mkdir();reports=[]
    try:
        for a in g['assets']:
            row=next(x for x in sr['assets'] if x['asset']==a['name']);require(sha(row['snapshot'])==row['snapshot_sha256'],'Snapshot modified')
            s=read(row['snapshot']);s['_snapshot_sha256']=row['snapshot_sha256'];require(s['source_bytes_unchanged'] and s['source_sha256']==g['source_sha256'],'Wrong snapshot source')
            r=next(x for x in er['assets'] if x['asset']==a['name']);report=verify_asset(g,a,s,r);p=dest/(a['name']+'.json');write_new(p,report)
            reports.append(dict(asset=a['name'],status=report['status'],report=str(p),report_sha256=sha(p),meshes=report['source_meshes'],triangles=report['source_triangles'],max_position_deviation_m=report['max_position_deviation_m'],max_normal_deviation=report['max_normal_deviation']))
            print('PASS_ACTUAL_SELECTED_SOURCE_GLB_EQUIVALENCE',a['name'],flush=True)
        gate();write_new(dest/'GLB_EQUIVALENCE.json',dict(status='PASS_FOUR_ACTUAL_SOURCE_GLB_EQUIVALENCE',source_sha256=g['source_sha256'],inputs_sha256=sha(INPUTS),export_receipt_sha256=sha(out/'EXPORT_RECEIPT.json'),assets=reports,meshes=76,triangles=9990,native_acceptance='NOT_RUN',source_saved=False,shared_project_writes=False))
    except BaseException:
        write_new(dest/'FAILURE.json',dict(status='FAIL_PRESERVE_ALL_OUTPUTS',assets_completed=reports,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
