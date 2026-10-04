"""Run with Blender --background --python SCRIPT -- ROOT OUTPUT.
Read-only source reloading and evaluated-geometry measurements; no render/save.
"""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--')+1:]
root, output = map(Path, args)
reports = []
for path in sorted(root.rglob('*.blend')):
    row = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'objects': [], 'issues': []}
    try:
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
        scene = bpy.context.scene
        row['blender_version'] = bpy.app.version_string
        row['units'] = {'system': scene.unit_settings.system, 'scale_length': scene.unit_settings.scale_length}
        deps = bpy.context.evaluated_depsgraph_get()
        for obj in scene.objects:
            rec = {'name': obj.name, 'type': obj.type, 'location': list(obj.location), 'scale': list(obj.scale),
                   'parent': obj.parent.name if obj.parent else None, 'modifiers': [{'name': m.name, 'type': m.type, 'enabled':m.show_viewport} for m in obj.modifiers],
                   'custom_properties': {k: str(v) for k,v in obj.items() if k != '_RNA_UI'}}
            if obj.type in {'MESH', 'CURVE'}:
                ev = obj.evaluated_get(deps); mesh = ev.to_mesh(); mesh.calc_loop_triangles()
                vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
                if obj.type == 'MESH': rec['source_vertices'] = len(obj.data.vertices)
                else: rec['source_control_points'] = sum(len(s.points)+len(s.bezier_points) for s in obj.data.splines)
                rec['evaluated_vertices'] = len(vertices)
                rec['evaluated_triangles'] = len(mesh.loop_triangles)
                rec['materials'] = [m.name if m else None for m in obj.data.materials]
                rec['uv_layers'] = list(obj.data.uv_layers.keys()) if obj.type == 'MESH' else ['Curve-generated UVs']
                if vertices:
                    rec['min_xyz'] = [min(v[i] for v in vertices) for i in range(3)]
                    rec['max_xyz'] = [max(v[i] for v in vertices) for i in range(3)]
                    rec['vertices_at_z0'] = sum(abs(v.z) < 1e-6 for v in vertices)
                    rec['signed_volume_m3'] = sum(vertices[t.vertices[0]].dot(vertices[t.vertices[1]].cross(vertices[t.vertices[2]])) for t in mesh.loop_triangles)/6
                    rec['degenerate_triangles'] = sum((vertices[t.vertices[1]]-vertices[t.vertices[0]]).cross(vertices[t.vertices[2]]-vertices[t.vertices[0]]).length < 2e-12 for t in mesh.loop_triangles)
                ev.to_mesh_clear()
            row['objects'].append(rec)
        row['image_assets'] = [{'name':im.name,'packed':bool(im.packed_file),'filepath':im.filepath,'size':list(im.size),
                                'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None} for im in bpy.data.images]
        row['load_success'] = True
    except Exception as exc: row['load_success'] = False; row['issues'].append(repr(exc))
    reports.append(row)
output.write_text(json.dumps(reports, indent=2)+'\n')
print('INDEPENDENT_RELOAD_COMPLETE', len(reports), str(output))
