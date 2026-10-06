"""Independent saved-source to actual GLB equivalence; never imports exporter.

Reopen the retained .blend, independently collect evaluated source triangles and
corner data, decode the actual GLB buffers and prove a complete role-by-role
bijection. Runtime fragment is emitted only after every selected GLB passes.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,json,argparse,traceback,datetime,importlib.util
import numpy as np
from mathutils import Matrix
from export_gate import read_gate,sha,source_unchanged,CAT
from glb_equivalence import decode,match_triangles,material_check,POSITION_TOLERANCE

def source_snapshot(a,source,material_specs):
    bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert objects.keys()=={p['name'] for p in a['parts']};assert bpy.data.objects[a['name']].matrix_world==Matrix.Identity(4);roles={};counts={}
    for p in a['parts']:
        ob=objects[p['name']];assert ob.matrix_world==Matrix.Identity(4);ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();assert len(me.uv_layers)==1;uv=me.uv_layers.active;role=p['material_role'];assert len(me.materials)==1 and me.materials[0]['astraea_material_role']==role;mat=me.materials[0];tex=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(tex)==1 and tex[0].image.packed_file
        import hashlib
        assert hashlib.sha256(bytes(tex[0].image.packed_file.data)).hexdigest()==material_specs[role]['sha256'];rows=roles.setdefault(role,dict(positions=[],uvs=[],normals=[],semantic_parts=[]));rows['semantic_parts'].append(p['name']);counts[p['name']]=len(me.loop_triangles)
        for tri in me.loop_triangles:
            vv=[];uu=[];nn=[]
            for vi,li in zip(tri.vertices,tri.loops):
                v=me.vertices[vi].co;n=me.corner_normals[li].vector;t=uv.data[li].uv;vv.append([float(v.x),float(v.z),float(-v.y)]);nn.append([float(n.x),float(n.z),float(-n.y)]);uu.append([float(t.x),1.0-float(t.y)])
            rows['positions'].append(vv);rows['uvs'].append(uu);rows['normals'].append(nn)
        ev.to_mesh_clear()
    markers={}
    for m in a['markers']:
        p=bpy.data.objects[m['name']].matrix_world.translation;markers['RT_'+m['name']]=dict(position=[float(p.x),float(p.z),float(-p.y)],source=m)
    return roles,counts,markers

def verify_one(a,q,g,package,candidate,material_specs,retained_reader):
    source=candidate/a['source'];glb=candidate/a['export'];assert glb.is_file();source_hash=sha(source);assert source_hash==q['source_sha256'];expected,counts,markers=source_snapshot(a,source,material_specs);decoded=decode(glb);doc=decoded['doc'];root=next(n for n in decoded['nodes'] if n['name']=='RUNTIME_'+a['name']);assert np.max(np.abs(root['matrix']-np.eye(4)))<=POSITION_TOLERANCE;ex=root['extras'];assert ex['parent_design_id']==a['parent_design_id'] and ex['runtime_instance_count']==1 and not ex['unique_catalogue_design'];assert ex['source_blend_sha256']==source_hash;assert ex['contract_sha256']==g['contract_sha256'];assert ex['retention_record_sha256']==sha(g['retention_record']);assert ex['source_qa_sha256']==sha(candidate/'qa/SOURCE_QA_all.json');assert ex['retained_commit']==g['retained_commit'];assert ex['placement_name']==a['name'] and ex['collision']=='noncolliding_foliage'
    actual={};role_materials={};batches=[]
    for p in decoded['primitives']:
        props=p['node']['extras'];role=props['material_role'];assert role in expected and role not in actual,'Exactly one batch primitive per source material role';assert props['parent_design_id']==a['parent_design_id'];assert props['source_blend_sha256']==source_hash;assert props['collision']=='noncolliding_foliage';names=json.loads(props['source_semantic_parts']);assert names==expected[role]['semantic_parts'];batch_counts=json.loads(props['source_part_triangle_counts']);assert batch_counts=={n:counts[n] for n in names};assert props['batch_part_count']==len(names);assert props['batch_triangle_count']==sum(counts[n] for n in names)==p['triangles'];actual[role]=p;role_materials[role]=p['material_index'];batches.append(dict(name=p['node']['name'],role=role,source_parts=names,source_part_triangle_counts=batch_counts,triangles=p['triangles']))
    assert actual.keys()==expected.keys();assert len(decoded['primitives'])==len(expected)==len(doc['materials'])==len(doc['images'])==len(doc['textures']);assert set(role_materials.values())==set(range(len(doc['materials'])));assert len(decoded['nodes'])==1+len(actual)+len(markers)
    reports=[]
    for role in sorted(expected):
        eq=match_triangles(expected[role],actual[role]);mat=material_check(decoded,role,role_materials[role],material_specs[role]);reports.append(dict(material=mat,equivalence=eq));assert np.all(np.linalg.norm(np.cross(actual[role]['positions'][:,1]-actual[role]['positions'][:,0],actual[role]['positions'][:,2]-actual[role]['positions'][:,0]),axis=1)>1e-10),'Degenerate actual exported triangles'
    actual_nodes={n['name']:n for n in decoded['nodes']};marker_report=[]
    for name,m in markers.items():
        n=actual_nodes[name];assert n['mesh'] is None;assert np.max(np.abs(n['matrix'][:3,:3]-np.eye(3)))<=POSITION_TOLERANCE;delta=float(np.linalg.norm(n['matrix'][:3,3]-np.asarray(m['position'],np.float64)));assert delta<=POSITION_TOLERANCE;props=n['extras'];assert props['source_marker_name']==m['source']['name'];assert props['physical_part']==m['source']['physical_part'];assert props['marker_kind']==m['source']['kind'];assert np.linalg.norm(np.asarray(props['native_position_xyz'])-np.asarray(m['position']))<=POSITION_TOLERANCE;marker_report.append(dict(name=name,native_position_xyz=n['matrix'][:3,3].tolist(),max_position_deviation_m=delta,physical_source_part=props['physical_part']))
    all_vertices=np.concatenate([p['positions'].reshape((-1,3)) for p in decoded['primitives']]);bounds=[all_vertices.min(axis=0).tolist(),all_vertices.max(axis=0).tolist()];triangles=sum(p['triangles'] for p in decoded['primitives']);assert triangles==q['evaluated_triangles']==a['planned_triangle_count'];secondary=retained_reader.read_glb(glb);assert len(secondary['triangles'])==triangles;secondary_bounds=np.array(retained_reader.bounds(secondary['vertices']));assert np.max(np.abs(secondary_bounds-np.array(bounds)))<=POSITION_TOLERANCE;assert sha(source)==source_hash
    return dict(name=a['name'],parent_design_id=a['parent_design_id'],source=str(source),source_sha256=source_hash,glb=str(glb),glb_sha256=sha(glb),status='PASS_ACTUAL_GLB_SOURCE_EQUIVALENCE',bounds_native_gltf=bounds,evaluated_source_parts=a['part_count'],batch_count=len(actual),triangles=triangles,batches=batches,material_and_corner_checks=reports,markers=marker_report,source_unchanged=True)

def runtime_fragment(plan,results,g):
    by={r['name']:r for r in results};models={};placements=[]
    for a in plan['assets']:
        if a['name'] not in by:continue
        r=by[a['name']];key='comfort_greenery_'+a['name'];glb=Path(r['glb']);source=Path(r['source']);models[key]=dict(file=glb.name,sha256=r['glb_sha256'],source_path=str(glb.relative_to(CAT)),source_sha256=r['source_sha256'],editable_source_path=str(source.relative_to(CAT)),parent_design_id=a['parent_design_id'],family=a['family'],runtime_present_and_identical=False,collision='noncolliding_foliage',batch_count=r['batch_count'],triangles=r['triangles'])
        bound=np.asarray(r['bounds_native_gltf'])+np.asarray(a['position_xyz']);placements.append(dict(name=a['name'],asset=key,model_file=glb.name,retained_export=str(glb.relative_to(CAT)),parent_design_id=a['parent_design_id'],position_xyz=a['position_xyz'],yaw_radians=0,scale_xyz=[1,1,1],support=a['support'],purpose='Checked additive fuller '+a['kind']+' derivative; original planted source retained',envelope_min_xyz=bound[0].tolist(),envelope_max_xyz=bound[1].tolist(),collision='noncolliding_foliage',source_geometry_checked=True,engine_visual_acceptance='PENDING'))
    return dict(schema=1,status='GLB_CHECKED_ADDITIVE_FRAGMENT_NOT_YET_INSTALLED',component='comfort_greenery',contract_sha256=g['contract_sha256'],independently_retained_source_commit=g['retained_commit'],budget=plan['budget'],new_botanical_placement_count=len(placements),models=models,placements=placements,original51_and_earlier48='Retain unchanged; this fragment never removes/replaces their records',media_parent_owned_placements=4,new_catalogue_ids=0,pending=['Copy exact verified GLBs and apply additive runtime records','Native engine import and loaded route/contact/marker checks','Matched ordinary/effects-off market, seated and long-pool pixels','Continue aesthetic refinement from actual-world evidence'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs');ap.add_argument('--only');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);g,plan,qa,source_qa,package,candidate=read_gate(args.inputs);assets=[a for a in plan['assets'] if args.only is None or a['name']==args.only];assert assets
    receipt=candidate/'qa'/('GLB_EQUIVALENCE_'+(args.only or 'all')+'.json');fragment=candidate/'qa'/('GREENERY_RUNTIME_FRAGMENT_'+(args.only or 'all')+'.json');assert not receipt.exists() and not fragment.exists(),'Preserve previous independent results';pins=json.loads((package/'INPUT_PINS.json').read_text());specs=pins['material_spec']['materials'];reader_path=CAT/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py';sp=importlib.util.spec_from_file_location('retained_geometry_reader',reader_path);reader=importlib.util.module_from_spec(sp);sp.loader.exec_module(reader);results=[]
    try:
        for a in assets:
            results.append(verify_one(a,source_qa[a['name']],g,package,candidate,specs,reader));print('GREENERY_GLB_EQUIVALENT',a['name'],flush=True)
        source_unchanged(g,qa);read_gate(args.inputs);report=dict(status='PASS_ACTUAL_GLB_SOURCE_EQUIVALENCE',asset_count=len(results),contract_sha256=g['contract_sha256'],position_tolerance_m=2e-6,corner_uv_tolerance=2e-6,normal_tolerance=2e-6,all_original_source_hashes_unchanged=True,assets=results,engine_adoption_and_visual_review='NOT_RUN');receipt.write_text(json.dumps(report,indent=2)+'\n');fragment.write_text(json.dumps(runtime_fragment(plan,results,g),indent=2)+'\n')
    except Exception:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');failure=candidate/'qa'/('GLB_EQUIVALENCE_FAILURE_'+stamp+'.json');failure.write_text(json.dumps(dict(status='FAILED_PRESERVE_ALL_OUTPUTS',verified_assets=results,traceback=traceback.format_exc()),indent=2)+'\n');raise
if __name__=='__main__':main()
