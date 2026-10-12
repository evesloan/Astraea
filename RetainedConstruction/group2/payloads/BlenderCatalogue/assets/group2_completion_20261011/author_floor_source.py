"""Editable source of the missing-only floor interface, never a live slab owner."""
import bpy, bmesh, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
data_path = ROOT / 'Game/data/group2_completion/FLOOR_INTERFACE.json'
data = json.loads(data_path.read_text())
assert data['790_excluded'] and data['production_adoption'] is False
bpy.ops.wm.read_factory_settings(use_empty=True)
mat = bpy.data.materials.new('Group2_Private_Compiler_Floor_Review')
mat.diffuse_color = (.29, .32, .34, 1)
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.29, .32, .34, 1)
bsdf.inputs['Roughness'].default_value = .85
for row in data['rows']:
    vertices, faces, lookup = [], [], {}
    def vert(p, y):
        key = (float(p[0]), -float(p[1]), float(y))
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(key)
        return lookup[key]
    top = row['floor_y']
    low = top - row['thickness']
    for triangle in row['triangles']:
        faces.append(tuple(vert(p, top) for p in triangle))
        faces.append(tuple(vert(p, low) for p in reversed(triangle)))
    for loop in [row['boundary']] + row['holes']:
        for i, a in enumerate(loop):
            b = loop[(i+1) % len(loop)]
            faces.append((vert(a, low), vert(b, low), vert(b, top), vert(a, top)))
    mesh = bpy.data.meshes.new(row['id'])
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    assert all(e.is_manifold for e in bm.edges), row['id']
    assert bm.calc_volume(signed=True) > 0, row['id']
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(row['id'], mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    obj['source_owner'] = row['source_owner']
    obj['interface_sha256'] = hashlib.sha256(data_path.read_bytes()).hexdigest()
    obj['status'] = 'HELD missing-only private source; real compiler adoption and bearing required'
    obj['new_unit'] = False
    obj['world_floor_y'] = top
    obj['material_role'] = 'guest_floor'
source = P / 'source/FLOOR_INTERFACE_r001.blend'
source.parent.mkdir(exist_ok=True)
assert not source.exists(), 'Immutable revision already exists'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
receipt = {'pass': True, 'mesh_count': len(data['rows']), 'closed_manifold_positive_volume': True,
           'native_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'interface_sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
           'live_floor_owner': False, '790_excluded': True}
(P / 'evidence/FLOOR_NATIVE_r001.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS editable missing-only floor source', len(data['rows']))
