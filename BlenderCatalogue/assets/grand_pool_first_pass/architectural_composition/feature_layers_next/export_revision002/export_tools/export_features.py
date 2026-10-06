"""Future two-thread Blender export; fresh scratch derivatives only.
Copy actual evaluated meshes and original material datablocks; never rebuild UV,
normal, shape or material attributes from the earlier procedural contracts.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'vendor'))
import argparse, json, traceback
import bpy
from mathutils import Matrix
from gate import gate, sha, read, require, run_path, write_new, INPUTS
from snapshot_source import props
from source_common import material_signature
from precise_normal_export import precise_normals

def export_one(a, snapshot, target):
    require(not target.exists(), 'Never overwrite an existing GLB')
    source = Path(a['source']); bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    require(bpy.app.version_string == '4.3.2', 'Unreviewed Blender version')
    bpy.context.view_layer.update(); scene = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    source_objects = {o.name: o for o in scene.objects}; expected = {o['name']: o for o in snapshot['objects']}
    require(set(source_objects) == set(expected), 'Source inventory differs from independent snapshot')
    require(props(scene) == snapshot['scene_extras'], 'Source scene metadata changed')
    materials = {m.name: m for o in scene.objects if o.type == 'MESH' for m in o.data.materials}
    for name, mat in materials.items(): require(material_signature(mat) == snapshot['full_material_graphs'][name], 'Source material graph changed: ' + name)
    runtime = bpy.data.scenes.new('FEATURE_EXPORT_ONLY'); copies = {}; groups = {}
    for name, ob in sorted(source_objects.items()):
        row = expected[name]
        require(ob.type == row['type'] and props(ob) == row['extras'], 'Source semantic properties changed: ' + name)
        require(not ob.modifiers and not ob.constraints and not ob.animation_data, 'Unsupported dynamic source')
        if ob.type == 'EMPTY':
            cp = ob.copy(); cp.name = 'COPY_' + name; runtime.collection.objects.link(cp); copies[name] = cp
    # Original names are required by the independent checker. Rename only the
    # in-memory originals to release names, without saving the source scene.
    for name, ob in source_objects.items(): ob.name = '__SOURCE_ONLY__' + name
    for name, cp in copies.items(): cp.name = name
    for name, cp in copies.items():
        old = source_objects[name]; parent = expected[name]['parent']; cp.parent = copies[parent] if parent else None
        cp.matrix_world = old.matrix_world.copy()
    for name, ob in sorted(source_objects.items()):
        row = expected[name]
        if ob.type != 'MESH': continue
        require(ob.matrix_world == Matrix.Identity(4), 'No world-bake or changed mesh transform permitted')
        mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        require(len(mesh.uv_layers) == 1 and mesh.uv_layers.active.name == row['uv_layer'], 'Actual UV layer changed')
        mesh.calc_loop_triangles(); require(len(mesh.loop_triangles) == row['triangles'], 'Triangulation changed before batching')
        require(len(mesh.materials) == 1 and mesh.materials[0].name == row['material'], 'Material assignment changed')
        cp = bpy.data.objects.new('COPY_' + name, mesh); runtime.collection.objects.link(cp)
        parent = row['parent']; cp.parent = copies[parent] if parent else None; cp.matrix_world = ob.matrix_world.copy()
        extras = row['extras']
        key = (row['material'], extras.get('material_role'), extras.get('collision_contract'), extras.get('collision'), extras.get('cast_shadow', True), parent, row['uv_layer'])
        groups.setdefault(key, []).append((name, cp))
    bpy.context.window.scene = runtime; bpy.context.view_layer.update(); batches = []
    for index, (key, entries) in enumerate(sorted(groups.items(), key=lambda x: json.dumps(x[0]))):
        bpy.ops.object.select_all(action='DESELECT')
        for _, cp in entries: cp.select_set(True)
        bpy.context.view_layer.objects.active = entries[0][1]
        if len(entries) > 1: bpy.ops.object.join()
        batch = bpy.context.view_layer.objects.active; batch.name = a['name'] + '__batch_%02d' % index
        require(batch.matrix_world == Matrix.Identity(4), 'Batch transform changed')
        batch.data.calc_loop_triangles(); names = [name for name, _ in entries]
        require(len(batch.data.materials) == 1 and batch.data.materials[0].name == key[0], 'Mixed actual source materials')
        require(len(batch.data.loop_triangles) == sum(expected[n]['triangles'] for n in names), 'Batch lost source triangles')
        provenance = {n: {k: expected[n][k] for k in ['extras', 'parent', 'material', 'uv_layer', 'triangles', 'world_matrix_godot']} for n in names}
        batch['source_part_names'] = json.dumps(names)
        batch['source_part_provenance_json'] = json.dumps(provenance, sort_keys=True)
        batch['source_scene_properties_json'] = json.dumps(snapshot['scene_extras'], sort_keys=True)
        batch['source_blend_sha256'] = a['source_sha256']; batch['source_snapshot_sha256'] = snapshot['_snapshot_sha256']
        batch['parent_design_id'] = a['parent_design_id']; batch['unique_catalogue_design'] = False
        batch['material_role'] = key[1]; batch['cast_shadow'] = key[4]
        if key[2] is not None: batch['collision_contract'] = key[2]
        if key[3] is not None: batch['collision'] = key[3]
        batches.append(dict(name=batch.name, source_parts=names, material=key[0], material_role=key[1], collision_contract=key[2], collision=key[3], cast_shadow=key[4], parent=key[5], triangles=len(batch.data.loop_triangles)))
    if a['family'] == 'plant': require(len(batches) == 5, 'Expected five source-material batches per plant')
    require(len(runtime.objects) == len(batches) + len(a['empty_objects']), 'Unexpected runtime objects')
    bpy.ops.object.select_all(action='SELECT'); bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', use_selection=True, use_active_scene=True,
        export_apply=False, export_yup=True, export_extras=True, export_materials='EXPORT', export_image_format='AUTO',
        export_texcoords=True, export_normals=True, export_tangents=False, export_cameras=False, export_lights=False,
        export_animations=False, export_draco_mesh_compression_enable=False)
    require(target.is_file() and sha(source) == a['source_sha256'], 'Source bytes changed or missing GLB')
    for name, mat in materials.items(): require(material_signature(mat) == snapshot['full_material_graphs'][name], 'Material graph/packed images mutated during export: ' + name)
    return dict(asset=a['name'], source=str(source), source_sha256=a['source_sha256'], snapshot_sha256=snapshot['_snapshot_sha256'],
                export=str(target), export_sha256=sha(target), batches=batches, source_materials_unchanged=True,
                status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE', source_saved=False, native_imported=False)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run', required=True)
    args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:]); g = gate(); out = run_path(args.run)
    sr = read(out / 'SNAPSHOT_RECEIPT.json')
    require(sr['status'] == 'PASS_READ_ONLY_SOURCE_SNAPSHOTS' and sr['inputs_sha256'] == sha(INPUTS), 'Wrong snapshot gate')
    require({x['asset'] for x in sr['assets']} == {a['name'] for a in g['assets']}, 'Incomplete snapshots')
    for r in sr['assets']: require(sha(r['snapshot']) == r['snapshot_sha256'], 'Snapshot hash changed')
    dest = out / 'exports'; require(not dest.exists(), 'Preserve existing exports; new run required'); dest.mkdir()
    completed = []; precision = None
    try:
        with precise_normals() as precision:
            for a in g['assets']:
                r = next(x for x in sr['assets'] if x['asset'] == a['name']); s = read(r['snapshot'])
                require(s['source_sha256'] == a['source_sha256'], 'Wrong source snapshot')
                s['_snapshot_sha256'] = r['snapshot_sha256']; target = dest / (a['name'] + '.glb')
                report = export_one(a, s, target); completed.append(report)
                write_new(out / (a['name'] + '_EXPORT.json'), report)
                print('FEATURE_EXPORTED_PENDING_EQUIVALENCE', a['name'], flush=True)
        gate(); write_new(out / 'EXPORT_RECEIPT.json', dict(status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE', inputs_sha256=sha(INPUTS),
            snapshot_receipt_sha256=sha(out / 'SNAPSHOT_RECEIPT.json'), assets=completed, normal_precision=precision, native_acceptance='NOT_RUN'))
    except Exception:
        write_new(out / 'EXPORT_FAILURE.json', dict(status='FAILED_PRESERVE_ALL_OUTPUTS', assets_completed=completed, traceback=traceback.format_exc()))
        raise
if __name__ == '__main__': main()
