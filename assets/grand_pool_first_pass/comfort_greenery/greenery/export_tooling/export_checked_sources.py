"""Coordinated two-thread Blender export only. Never saves editable sources.

Fresh distinct candidate_v001/exports outputs only; passed independent source
QA and independently retained exact source bytes are mandatory at action time.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,json,argparse,traceback,datetime
from mathutils import Matrix
from export_gate import read_gate,sha,source_unchanged

def export_one(a,g,q,package,candidate):
    source=candidate/a['source'];target=candidate/a['export'];assert not target.exists(),'Preserve existing export '+str(target)
    bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();source_scene=bpy.context.scene;source_root=bpy.data.objects[a['name']];assert source_root.matrix_world==Matrix.Identity(4)
    source_meshes={o.name:o for o in source_scene.objects if o.type=='MESH'};assert set(source_meshes)=={p['name'] for p in a['parts']};source_markers={m['name']:bpy.data.objects[m['name']] for m in a['markers']};dg=bpy.context.evaluated_depsgraph_get()
    runtime=bpy.data.scenes.new('GREENERY_EXPORT_ONLY');root=bpy.data.objects.new('RUNTIME_'+a['name'],None);runtime.collection.objects.link(root)
    root['parent_design_id']=a['parent_design_id'];root['placement_name']=a['name'];root['unique_catalogue_design']=False;root['runtime_instance_count']=1;root['source_blend_sha256']=q['source_sha256'];root['contract_sha256']=g['contract_sha256'];root['source_qa_sha256']=g['guard_file_hashes'][str(candidate/'qa/SOURCE_QA_all.json')];root['retention_record_sha256']=g['guard_file_hashes'][g['retention_record']];root['retained_commit']=g['retained_commit'];root['collision']='noncolliding_foliage';root['native_axis_mapping']='source (x,y,z) -> glTF (x,z,-y)';root['editable_source_relative_to_catalogue']=str(source.relative_to(package.parents[3])) if source.is_relative_to(package.parents[3]) else str(source)
    groups={};counts={}
    # Evaluate only linked/updated source objects; copy their full polygon and UV
    # topology before joining, so source corner normals/triangulation survive.
    for part in a['parts']:
        ob=source_meshes[part['name']];assert ob.matrix_world==Matrix.Identity(4) and not ob.modifiers and not ob.constraints
        mesh=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);assert len(mesh.uv_layers)==1;mesh.uv_layers.active.name='botanical_shape_uv';mesh.uv_layers.active.active_render=True;mesh.calc_loop_triangles();counts[part['name']]=len(mesh.loop_triangles)
        copy=bpy.data.objects.new('TMP_'+part['name'],mesh);runtime.collection.objects.link(copy);copy.parent=root;groups.setdefault(part['material_role'],[]).append(copy)
    marker_names=[]
    for m in a['markers']:
        old=source_markers[m['name']];new=bpy.data.objects.new('RT_'+m['name'],None);runtime.collection.objects.link(new);new.parent=root;new.location=old.matrix_world.translation;new['source_marker_name']=m['name'];new['physical_part']=m['physical_part'];new['marker_kind']=m['kind'];new['native_position_xyz']=[float(new.location.x),float(new.location.z),float(-new.location.y)];marker_names.append(new.name)
    bpy.context.window.scene=runtime;bpy.context.view_layer.update();batches=[]
    for role,objects in sorted(groups.items()):
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();batch=objects[0];batch.name='RT_'+a['name']+'__'+role.replace('botanical_','');batch.parent=root;bpy.context.view_layer.update();assert batch.matrix_world==Matrix.Identity(4);batch.data.calc_loop_triangles()
        names=[p['name'] for p in a['parts'] if p['material_role']==role];tri=sum(counts[n] for n in names);assert len(batch.data.loop_triangles)==tri;assert len(batch.data.materials)==1;assert batch.data.materials[0]['astraea_material_role']==role
        batch['parent_design_id']=a['parent_design_id'];batch['material_role']=role;batch['source_semantic_parts']=json.dumps(names);batch['source_part_triangle_counts']=json.dumps({n:counts[n] for n in names},sort_keys=True);batch['batch_part_count']=len(names);batch['batch_triangle_count']=tri;batch['source_blend_sha256']=q['source_sha256'];batch['collision']='noncolliding_foliage';batches.append(dict(name=batch.name,material_role=role,semantic_parts=names,source_part_triangle_counts={n:counts[n] for n in names},triangles=tri))
    assert len([o for o in runtime.objects if o.type=='MESH'])==len(groups);assert len(runtime.objects)==len(groups)+1+len(marker_names);bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=root;bpy.context.view_layer.update()
    target.parent.mkdir(exist_ok=True);bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=False,export_yup=True,export_extras=True,export_materials='EXPORT',export_image_format='AUTO',export_texcoords=True,export_normals=True,export_tangents=False,export_cameras=False,export_lights=False,export_animations=False,export_draco_mesh_compression_enable=False)
    assert target.is_file() and sha(source)==q['source_sha256'];return dict(name=a['name'],parent_design_id=a['parent_design_id'],source=str(source),source_sha256=q['source_sha256'],export=str(target),export_sha256=sha(target),batches=batches,marker_names=marker_names,triangles=sum(b['triangles'] for b in batches),status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs');ap.add_argument('--only');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);g,plan,qa,source_qa,package,candidate=read_gate(args.inputs);assets=[a for a in plan['assets'] if args.only is None or a['name']==args.only];assert assets
    dest=candidate/'qa'/('EXPORT_RECEIPT_'+(args.only or 'all')+'.json');assert not dest.exists(),'Preserve prior export receipt'
    for a in assets:assert not (candidate/a['export']).exists(),'Preserve prior exported/failed candidate '+a['name']
    completed=[]
    try:
        for a in assets:
            row=export_one(a,g,source_qa[a['name']],package,candidate);completed.append(row);print('GREENERY_EXPORTED',a['name'],row['triangles'],flush=True)
        source_unchanged(g,qa);read_gate(args.inputs)
        result=dict(status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE',contract_sha256=g['contract_sha256'],source_qa_sha256=sha(candidate/'qa/SOURCE_QA_all.json'),retention_record_sha256=sha(g['retention_record']),sources_unchanged=True,outputs=completed,write_scope='New GLBs in the approved source candidate exports directory plus this receipt; no source saves or Game/registry edits')
        dest.write_text(json.dumps(result,indent=2)+'\n')
    except Exception:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');failure=candidate/'qa'/('EXPORT_FAILURE_'+stamp+'.json');failure.write_text(json.dumps(dict(status='FAILED_PRESERVE_ALL_OUTPUTS',completed=completed,traceback=traceback.format_exc()),indent=2)+'\n');raise
if __name__=='__main__':main()
