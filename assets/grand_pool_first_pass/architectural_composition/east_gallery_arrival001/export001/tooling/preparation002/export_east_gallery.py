"""DEFERRED Blender job. Four new GLBs from actual evaluated selected source.
Retain all 76 mesh identities and actual parent/local frames. No joins, procedural
geometry, UV synthesis, world baking, source save or native import. Reused plant
geometry is neither copied nor exported. Only selected in-memory copies receive
explicitly recorded export-exclusion overrides.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE/'vendor')]
import argparse,json,traceback
import bpy
import numpy as np
from gate import gate,sha,read,require,run_path,write_new,INPUTS
from snapshot_source import C,props
from source_common import material_signature
from precise_normal_export import precise_normals
from static_evaluation import evaluation_state

def export_one(g,a,s,target):
    require(not target.exists(),'Never overwrite a GLB')
    bpy.ops.wm.open_mainfile(filepath=g['source'],load_ui=False)
    require(bpy.app.version_string==g['blender_version'],'Unreviewed Blender version')
    bpy.context.view_layer.update();scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
    require(sorted([o.name,o.type,o.parent.name if o.parent else None] for o in scene.objects)==s['scene_inventory'],'Saved inventory differs from independent snapshot')
    require(props(scene)==s['scene_extras'],'Saved scene metadata changed')
    expected={x['name']:x for x in s['objects']};names=tuple(sorted(expected))
    originals={n:scene.objects[n] for n in names};materials={};copies={};overrides=[]
    for name,ob in originals.items():
        row=expected[name]
        require(ob.type==row['type'] and props(ob)==row['extras'],'Source properties changed: '+name)
        require(evaluation_state(ob,g)==row['source_evaluation'],'Static source evaluation changed: '+name)
        for actual,key in [(ob.matrix_basis,'matrix_basis_blender'),(ob.matrix_parent_inverse,'matrix_parent_inverse_blender')]:require(np.array_equal(np.asarray(actual,dtype=float),row[key]),'Saved local frame changed: '+name)
        require(np.array_equal(C@np.asarray(ob.matrix_world,dtype=float)@C.T,row['world_matrix_godot']),'Saved world frame changed: '+name)
        if ob.type=='MESH':
            for mat in ob.data.materials:materials[mat.name]=mat
    require(set(materials)==set(s['full_material_graphs']),'Material inventory changed')
    for n,m in materials.items():require(material_signature(m)==s['full_material_graphs'][n],'Material graph/packed bytes changed: '+n)
    runtime=bpy.data.scenes.new('EAST_GALLERY_SELECTED_EXPORT_ONLY')
    # ob.copy retains the actual TRS channels and parent-inverse matrix. Change
    # only the parent pointer to its corresponding copy, never reassign world
    # matrices or decompose/reconstruct mesh transforms.
    for name in names:
        old=originals[name];cp=old.copy()
        if old.type=='MESH':
            cp.data=bpy.data.meshes.new_from_object(old.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
            # The actual source stack is already evaluated into this new mesh.
            # Remove only copied modifiers, avoiding a second bevel/normal pass.
            for modifier in tuple(cp.modifiers):cp.modifiers.remove(modifier)
            require(not cp.modifiers,'Evaluated export copy retained a modifier')
            cp.data.calc_loop_triangles()
            require(len(cp.data.loop_triangles)==expected[name]['triangles'],'Evaluated copy changed triangulation')
            require(len(cp.data.uv_layers)==1 and cp.data.uv_layers.active.name==expected[name]['uv_layer'],'Evaluated copy changed UV layer')
            require(len(cp.data.materials)==1 and cp.data.materials[0].name==expected[name]['material'],'Evaluated copy changed material')
        runtime.collection.objects.link(cp);copies[name]=cp
    for name,cp in copies.items():cp.parent=copies.get(expected[name]['parent'])
    # Release names in this unsaved Blender process only. Source bytes remain
    # pinned before and after. No bpy library transfer lists are used.
    for name,old in originals.items():old.name='__UNSAVED_SOURCE_ONLY__'+name
    for name,cp in copies.items():
        cp.name=name;row=expected[name]
        if row['extras'].get('export_excluded'):
            require(a['programme_export'] or name in a['empty_objects'],'Unapproved export-exclusion override')
            cp['export_excluded']=False
            overrides.append(dict(node=name,key='export_excluded',source_value=True,export_value=False,
                reason='Selected standalone programme derivative' if a['programme_export'] else 'Selected source light-position reserve, no native light'))
        cp['selected_source_properties_json']=json.dumps(row['extras'],sort_keys=True)
        cp['selected_source_scene_properties_json']=json.dumps(s['scene_extras'],sort_keys=True)
        cp['selected_source_evaluation_json']=json.dumps(row['source_evaluation'],sort_keys=True)
        cp['selected_source_frame_json']=json.dumps({k:row[k] for k in ['parent','matrix_basis_blender','matrix_parent_inverse_blender','local_matrix_godot','world_matrix_godot']},sort_keys=True)
        cp['exported_source_blend_sha256']=g['source_sha256'];cp['exported_source_snapshot_sha256']=s['_snapshot_sha256']
        cp['parent_design_id']=a['parent_design_id'];cp['unique_catalogue_design']=False
        cp['selected_derivative_name']=a['name'];cp['export_exclusion_override_scope']='copy_only_selected_standalone_derivative' if row['extras'].get('export_excluded') else 'none'
    bpy.context.window.scene=runtime;bpy.context.view_layer.update()
    require(set(o.name for o in runtime.objects)==set(names),'Extra/missing runtime objects')
    for name,cp in copies.items():
        row=expected[name]
        require(cp.parent==copies.get(row['parent']),'Parent copy mismatch')
        for actual,key in [(cp.matrix_basis,'matrix_basis_blender'),(cp.matrix_parent_inverse,'matrix_parent_inverse_blender')]:require(np.array_equal(np.asarray(actual,dtype=float),row[key]),'Copy local frame changed: '+name)
        require(np.array_equal(C@np.asarray(cp.matrix_world,dtype=float)@C.T,row['world_matrix_godot']),'Copy world frame changed: '+name)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,use_active_scene=True,
        export_apply=False,export_yup=True,export_extras=True,export_materials='EXPORT',export_image_format='AUTO',
        export_texcoords=True,export_normals=True,export_tangents=False,export_cameras=False,export_lights=False,
        export_animations=False,export_draco_mesh_compression_enable=False)
    require(target.is_file() and sha(g['source'])==g['source_sha256'],'GLB missing or source changed')
    for n,m in materials.items():require(material_signature(m)==s['full_material_graphs'][n],'Export mutated source material graph: '+n)
    return dict(asset=a['name'],source=g['source'],source_sha256=g['source_sha256'],snapshot_sha256=s['_snapshot_sha256'],export=str(target),export_sha256=sha(target),
        meshes=len(a['mesh_parts']),triangles=a['triangles'],nodes=list(names),export_only_metadata_overrides=overrides,
        hierarchy='one source object to one export node, no batching or world baking',source_material_graphs_unchanged=True,source_modifier_fingerprints_preserved=True,export_copy_modifiers_cleared_after_evaluated_mesh_copy=True,
        light_note='Actual reserve positions retained; placeholder aims unchanged; separate optical proposal and native light tuning remain pending.',
        status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE',source_saved=False,native_imported=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);g=gate();out=run_path(args.run)
    sr=read(out/'SNAPSHOT_RECEIPT.json');require(sr['status']=='PASS_FOUR_READ_ONLY_SOURCE_SNAPSHOTS' and sr['inputs_sha256']==sha(INPUTS),'Wrong snapshot gate')
    require({r['asset'] for r in sr['assets']}=={a['name'] for a in g['assets']},'Incomplete snapshots')
    for row in sr['assets']:require(sha(row['snapshot'])==row['snapshot_sha256'],'Independent snapshot changed')
    dest=out/'exports';require(not dest.exists(),'Preserve all prior exports');dest.mkdir();reports=[]
    try:
        with precise_normals() as precision:
            for a in g['assets']:
                row=next(r for r in sr['assets'] if r['asset']==a['name']);s=read(row['snapshot']);s['_snapshot_sha256']=row['snapshot_sha256']
                require(s['source_sha256']==g['source_sha256'] and s['inputs_sha256']==sha(INPUTS),'Snapshot input pin mismatch')
                result=export_one(g,a,s,dest/a['file']);reports.append(result);write_new(out/(a['name']+'_EXPORT.json'),result)
                print('SELECTED_DERIVATIVE_EXPORTED_PENDING_EQUIVALENCE',a['name'],flush=True)
        gate();write_new(out/'EXPORT_RECEIPT.json',dict(status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE',inputs_sha256=sha(INPUTS),snapshot_receipt_sha256=sha(out/'SNAPSHOT_RECEIPT.json'),assets=reports,normal_precision=precision,native_acceptance='NOT_RUN'))
    except BaseException:
        write_new(out/'EXPORT_FAILURE.json',dict(status='FAILED_PRESERVE_ALL_OUTPUTS',assets_completed=reports,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
