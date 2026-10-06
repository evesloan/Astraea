"""Future coordinated Blender job: read-only fresh saved-source snapshots.
No build, save, export, render, Godot, Game, Catalogue, or installed-file writes.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'vendor'))
import argparse, json
import bpy
import numpy as np
from gate import gate, sha, read, require, run_path, write_new, INPUTS
from snapshot_source import C, props, material
from source_common import material_signature

def snapshot(a):
    p = Path(a['source']); before = sha(p)
    bpy.ops.wm.open_mainfile(filepath=str(p), load_ui=False)
    require(bpy.app.version_string == '4.3.2', 'Unreviewed Blender version')
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene; objects = []; materials = {}; full_materials = {}
    require({o.name for o in sc.objects if o.type == 'MESH'} == set(a['mesh_parts']), 'Unexpected source meshes')
    require({o.name for o in sc.objects if o.type == 'EMPTY'} == set(a['empty_objects']), 'Unexpected source root/markers')
    require(all(o.type in {'MESH', 'EMPTY'} for o in sc.objects), 'Unsupported source objects')
    for ob in sorted(sc.objects, key=lambda x: x.name):
        require(not ob.modifiers and not ob.constraints and not ob.animation_data, 'Unsupported evaluation state: ' + ob.name)
        eo = ob.evaluated_get(dg); mw = np.asarray(eo.matrix_world, dtype=float)
        row = dict(name=ob.name, type=ob.type, parent=ob.parent.name if ob.parent else None, extras=props(ob),
                   world_matrix_godot=(C @ mw @ C.T).tolist())
        if ob.type == 'MESH':
            require(np.array_equal(mw, np.eye(4)), 'Only existing identity-authored source meshes may batch')
            me = eo.to_mesh(preserve_all_data_layers=True, depsgraph=dg); me.calc_loop_triangles()
            require(len(me.uv_layers) == 1 and me.uv_layers.active is not None, 'Expected exactly one source UV layer')
            require(len(me.materials) == 1 and me.materials[0] is not None, 'Expected one actual source material')
            mat = me.materials[0]; materials[mat.name] = material(mat); full_materials[mat.name] = material_signature(mat)
            require(not mat.animation_data and not mat.node_tree.animation_data, 'Animated source material unsupported')
            row.update(material=mat.name, uv_layer=me.uv_layers.active.name, triangles=len(me.loop_triangles),
                       evaluated_vertices=len(me.vertices), positions=[], local_positions=[], normals=[], uvs=[], triangle_provenance=[])
            xyz = np.asarray([tuple(v.co) for v in me.vertices], dtype=float)
            xyz = (C[:3, :3] @ xyz.T).T
            normals = np.asarray([tuple(n.vector) for n in me.corner_normals], dtype=float)
            normals = (C[:3, :3] @ normals.T).T; normals /= np.linalg.norm(normals, axis=1)[:, None]
            uv = np.asarray([tuple(v.uv) for v in me.uv_layers.active.data], dtype=float); uv[:, 1] = 1 - uv[:, 1]
            for ti, t in enumerate(me.loop_triangles):
                require(t.material_index == 0, 'Unexpected material slot')
                row['positions'].append(xyz[list(t.vertices)].tolist()); row['local_positions'].append(xyz[list(t.vertices)].tolist())
                row['normals'].append(normals[list(t.loops)].tolist()); row['uvs'].append(uv[list(t.loops)].tolist())
                row['triangle_provenance'].append(dict(source_triangle=ti, polygon=t.polygon_index, vertices=list(t.vertices), loops=list(t.loops)))
            eo.to_mesh_clear()
        objects.append(row)
    require(sum(x.get('triangles', 0) for x in objects) == a['triangles'], 'Source triangle inventory changed')
    require(sha(p) == before == a['source_sha256'], 'Source bytes changed')
    return dict(schema=1, kind='feature', asset=a['name'], source=str(p), source_sha256=before, source_bytes_unchanged=True,
                blender=bpy.app.version_string, inputs_sha256=sha(INPUTS), scene_extras=props(sc), objects=objects,
                materials=materials, full_material_graphs=full_materials, placement_and_support=a['placement_and_support'],
                coordinate_frame='glTF/Godot XYZ; source Blender x,y,z maps to x,z,-y',
                uv_method='Actual evaluated triangle corner UVs; glTF V=1-Blender V, no reconstruction',
                native_acceptance='NOT_RUN')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run', required=True)
    args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:]); g = gate(); out = run_path(args.run)
    require(not out.exists(), 'Preserve surviving run; choose a new label')
    out.parent.mkdir(exist_ok=True); out.mkdir(); (out / 'snapshots').mkdir()
    rows = []
    for a in g['assets']:
        p = out / 'snapshots' / (a['name'] + '.json'); write_new(p, snapshot(a))
        rows.append(dict(asset=a['name'], snapshot=str(p), snapshot_sha256=sha(p), source_sha256=a['source_sha256']))
        print('READ_ONLY_SOURCE_SNAPSHOT', a['name'], flush=True)
    gate(); write_new(out / 'SNAPSHOT_RECEIPT.json', dict(status='PASS_READ_ONLY_SOURCE_SNAPSHOTS', inputs_sha256=sha(INPUTS), assets=rows, exports_created=False, source_saved=False))
if __name__ == '__main__': main()
