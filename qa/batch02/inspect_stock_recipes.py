"""Read base .blend, apply recorded transforms in memory, collect actual points.

No authoring helper is imported; nothing is saved to the source. Run with
Blender background, one thread. Exported-byte comparison is done separately.
"""
from pathlib import Path
import bpy
import hashlib
import json
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'assets/library_contents'
source = BASE/'AST-LIB-006_upright_book_group.blend'
recipes = json.loads((BASE/'stock_assembly_recipes.json').read_text())
reports = []
before = hashlib.sha256(source.read_bytes()).hexdigest()
for recipe in recipes['derived_assemblies']:
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    for number in recipe['omitted_book_numbers']:
        parent = bpy.data.objects.get(f'STOCK_volume_{number:02d}_editable_volume')
        assert parent is not None
        children = list(parent.children_recursive)
        for child in children:
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(parent, do_unlink=True)
    for name, matrix in recipe['transforms_blender_world_row_major'].items():
        if bpy.data.objects.get(name) is None and any(name == f'STOCK_volume_{n:02d}_editable_volume' for n in recipe['omitted_book_numbers']):
            continue
        bpy.data.objects[name].matrix_world = Matrix(matrix)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    points_by_role = {}
    count = 0
    contacts = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        ev = obj.evaluated_get(dg)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        count += len(mesh.loop_triangles)
        assert len(mesh.materials) == 1
        role = mesh.materials[0].name
        points = [list(obj.matrix_world @ vertex.co) for vertex in mesh.vertices]
        points_by_role.setdefault(role, []).extend(points)
        if 'continuous_boards' in obj.name:
            contacts.append({'part': obj.name,
                             'min_xyz': [min(p[i] for p in points) for i in range(3)],
                             'max_xyz': [max(p[i] for p in points) for i in range(3)]})
        ev.to_mesh_clear()
    reports.append({'variant': recipe['variant'], 'export': recipe['export'],
                    'source_sha256': before, 'triangles': count,
                    'points_by_role': points_by_role, 'actual_board_bounds': contacts})
after = hashlib.sha256(source.read_bytes()).hexdigest()
(ROOT/'qa/batch02/independent_recipe_source_geometry.json').write_text(json.dumps({'sources_unchanged': before == after, 'reports': reports}, separators=(',', ':'))+'\n')
print('RECIPE_SOURCE_READ_COMPLETE', len(reports), 'unchanged', before == after)
