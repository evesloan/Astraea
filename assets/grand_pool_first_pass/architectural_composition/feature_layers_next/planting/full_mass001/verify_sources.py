"""DEFERRED independent reopen adapter of retained greenery verify_sources.py.
Example: blender -b -t 2 --python-exit-code 1 --python verify_sources.py -- --candidate candidate_v001
Read-only source reopen. Writes new QA receipts only in the fresh scratch
candidate. No render, export, engine or catalogue write. No authoring calls.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,json,argparse,copy,collections
import numpy as np
from mathutils import Matrix
from source_common import HERE,CONTRACT,sha,guard_inputs,candidate_path,append_materials,material_signature,material_specs,check_material_spec
from check_geometry import geometry_checks,retained_screens
from geometry_plan import world

def evaluated(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
    v=[[float(c) for c in ev.matrix_world@q.co] for q in me.vertices]
    tri=[list(t.vertices) for t in me.loop_triangles];faces=[list(f.vertices) for f in me.polygons]
    assert me.uv_layers.active is not None
    uv=[list(x.uv) for x in me.uv_layers.active.data];smooth=[p.use_smooth for p in me.polygons]
    ev.to_mesh_clear();return v,tri,faces,uv,smooth

def graph_connected(part):
    adj=collections.defaultdict(set)
    for face in part['faces']:
        for x,y in zip(face,face[1:]+face[:1]):adj[x].add(y);adj[y].add(x)
    seen={0};todo=[0]
    while todo:
        for nxt in adj[todo.pop()]-seen:seen.add(nxt);todo.append(nxt)
    return len(seen)==len(part['vertices'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True)
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    pins,plan=guard_inputs();out=candidate_path(args.candidate);assert out.is_dir()
    qa=out/'qa/SOURCE_QA.json';snapshot=out/'qa/REOPENED_GEOMETRY.json'
    assert not qa.exists() and not snapshot.exists(),'Preserve existing QA evidence; use a fresh candidate for correction'
    receipt=json.loads((out/'qa/BUILD_RECEIPT.json').read_text());assert receipt['status']=='SOURCE_AUTHORED_NOT_YET_REOPENED'
    assert receipt['contract_sha256']==sha(CONTRACT)
    receipts={r['name']:r for r in receipt['outputs']};assert len(receipts)==len(plan['assets'])==6
    actual_plan=copy.deepcopy(plan);records=[];specs=material_specs()
    for a in actual_plan['assets']:
        path=out/a['source'];before=sha(path);r=receipts[a['name']]
        assert before==r['source_sha256'],'Built source changed before independent QA'
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();sc=bpy.context.scene
        assert sc['contract_sha256']==sha(CONTRACT) and sc['parent_design_id']=='AST-BOT-002'
        assert not any(o.type in {'CAMERA','LIGHT'} for o in sc.objects)
        assert not sc.animation_data
        root=sc.objects[a['name']];assert root.parent is None and root.matrix_world==Matrix.Identity(4)
        assert root['placement_name']==a['replaces_instance'] and root['instance_count']==1
        assert list(root['placement_world_xyz'])==a['position_xyz'] and root['placement_yaw_radians']==a['yaw_radians']
        meshes={o.name:o for o in sc.objects if o.type=='MESH'};expected={p['name']:p for p in a['parts']}
        assert meshes.keys()==expected.keys() and len(sc.objects)==len(meshes)+len(a['markers'])+1
        candidate_mats={};maxdeviation=0;triangles=0;volumes={};uvdeviation=0
        for name,ob in meshes.items():
            p=expected[name];assert ob.parent==root and ob.matrix_world==Matrix.Identity(4)
            assert not ob.modifiers and not ob.constraints and not ob.animation_data
            assert ob['parent_design_id']=='AST-BOT-002' and ob['surface_kind']==p['surface_kind']
            assert ob['material_role']==p['material_role'] and not ob.hide_render
            vertices,tri,faces,uv,smooth=evaluated(ob)
            assert len(vertices)==len(p['vertices']) and faces==p['faces'] and not any(smooth)
            deviation=float(np.max(np.linalg.norm(np.asarray(vertices,dtype=np.float64)-np.asarray(p['vertices'],dtype=np.float64),axis=1)))
            assert deviation<2e-6,(name,deviation);maxdeviation=max(maxdeviation,deviation)
            assert len(uv)==len(p['loop_uvs'])
            duv=max(abs(c-d) for x,y in zip(uv,p['loop_uvs']) for c,d in zip(x,y));assert duv<2e-6;uvdeviation=max(uvdeviation,duv)
            assert len(ob.data.materials)==1;mat=ob.data.materials[0];role=p['material_role']
            assert role not in candidate_mats or candidate_mats[role]==mat
            candidate_mats[role]=mat;check_material_spec(mat,role,specs[role])
            assert material_signature(mat)==r['material_provenance'][role]['material_signature'],'Saved material graph differs from unchanged appended graph: '+role
            p['vertices']=vertices;p['faces']=faces;p['loop_uvs']=uv;p['evaluated_triangle_indices']=tri
            assert graph_connected(p),'Disconnected semantic part: '+name
            if p['surface_kind']=='closed_support':
                v=np.asarray(vertices,dtype=np.float64);v-=np.mean(v,axis=0);t=np.asarray(tri,dtype=np.int64)
                volume=float(np.sum(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])),dtype=np.float64)/6)
                assert volume>1e-12,'Inverted/zero support volume: '+name;volumes[name]=volume
            triangles+=len(tri)
        assert triangles==a['planned_triangle_count']
        local_vertices=np.asarray([v for p in a['parts'] for v in p['vertices']])
        world_vertices=np.asarray([world(v,a) for v in local_vertices])
        a['bounds_local']=[local_vertices.min(axis=0).tolist(),local_vertices.max(axis=0).tolist()]
        a['bounds_world']=[world_vertices.min(axis=0).tolist(),world_vertices.max(axis=0).tolist()]
        a['maximum_height_above_soil_m']=float(local_vertices[:,2].max()-a['soil_surface_local_z'])
        for marker in a['markers']:
            ob=sc.objects[marker['name']];assert ob.type=='EMPTY' and ob.parent==root
            assert ob['physical_part']==marker['physical_part'] and ob['marker_kind']==marker['kind']
            assert np.max(np.abs(np.asarray(list(ob.matrix_world.translation))-marker['point_local']))<2e-6
        # Append fresh source material definitions after independent reload, not
        # merely compare the candidate to its own saved receipt. Name suffixes
        # are irrelevant; role graphs and actual packed image bytes must match.
        refs,provenance,availability=append_materials(bpy,plan)
        for role,mat in candidate_mats.items():
            assert material_signature(mat)==material_signature(refs[role]),'Saved graph differs from exact retained reference: '+role
            assert provenance[role]['library']==r['material_provenance'][role]['library']
            assert provenance[role]['library_sha256']==r['material_provenance'][role]['library_sha256']
        assert sha(path)==before,'QA mutated source file'
        records.append(dict(name=a['name'],source=str(path),source_sha256=before,parts=len(meshes),triangles=triangles,max_vertex_deviation_m=maxdeviation,max_loop_uv_deviation=uvdeviation,closed_support_signed_volumes_m3=volumes,material_provenance=provenance,material_library_availability=availability))
        print('REOPENED_GEOMETRY_MATERIALS',a['name'],flush=True)
    # Unlike the old verifier, world conversion includes the actual pi/2 yaw;
    # root plane/footprint uses the real reopened28-gon rather than market boxes.
    errors,geometry,worldtri=geometry_checks(actual_plan)
    more,screens=retained_screens(actual_plan,worldtri);errors+=more
    assert not errors,errors
    guard_inputs()
    for r in records:assert sha(r['source'])==r['source_sha256'],'Source changed during QA'
    for p,h in screens['read_only_runtime_input_pins'].items():assert sha(p)==h,'Current route/media evidence changed during QA'
    actual_plan['status']='INDEPENDENTLY_REOPENED_SOURCE_GEOMETRY_NOT_RENDERED_OR_EXPORTED'
    snapshot.write_text(json.dumps(actual_plan,indent=2)+'\n')
    report=dict(status='PASS_SOURCE_QA_ONLY',contract_sha256=sha(CONTRACT),reopened_geometry_sha256=sha(snapshot),sources=records,geometry_checks=geometry,retained_constraints=screens,retained_input_hashes_unchanged=True,source_files_unchanged_by_qa=True,no_export=True,no_render=True,no_game_or_catalogue_write=True,pending=['Parent-coordinated matched composed image review','Independent source retention before later export','Export equivalence and native engine QA only after separate coordination'])
    qa.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS_SOURCE_QA_ONLY',len(records),'NO_RENDER_NO_EXPORT_NO_GAME_WRITE',flush=True)
if __name__=='__main__':main()
