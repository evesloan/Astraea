"""Read retained GLBs; no import, rewrite, tolerance, or material equivalence claim."""
import collections
import hashlib
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[2]
rows = []
seen = set()
for key in ['788', '812', '824', '836', '818']:
    path = ROOT / 'Game/assets/group2_completion' / (key + '.glb')
    data = path.read_bytes()
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    document = json.loads(data[20:20 + size])
    binary_size, kind = struct.unpack_from('<II', data, 20 + size)
    assert kind == 0x004E4942
    binary = data[28 + size:28 + size + binary_size]
    def accessor(index):
        value = dict(document['accessors'][index])
        view = document['bufferViews'][value.pop('bufferView')]
        assert view.get('buffer', 0) == 0 and 'sparse' not in value
        offset = view.get('byteOffset', 0)
        return [value, {k: v for k, v in view.items() if k not in ('buffer', 'byteOffset')},
                hashlib.sha256(binary[offset:offset + view['byteLength']]).hexdigest()]
    geometry = []
    with_material_index = []
    for mesh in document['meshes']:
        primitives = []
        materials = []
        for primitive in mesh['primitives']:
            value = dict(primitive)
            materials.append(value.pop('material', None))
            value['attributes'] = {k: accessor(v) for k, v in value['attributes'].items()}
            if 'indices' in value:
                value['indices'] = accessor(value['indices'])
            assert 'targets' not in value  # Do not silently omit morph data.
            primitives.append(value)
        payload = [primitives, {k: v for k, v in mesh.items() if k not in ('primitives', 'name')}]
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        geometry.append(digest)
        with_material_index.append((digest, tuple(materials)))
    unique = set(geometry)
    rows.append(dict(key=key, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                     nodes=len(document['nodes']), meshes=len(geometry),
                     exact_geometry_groups=len(unique), new_geometry_groups=len(unique-seen),
                     exact_geometry_and_local_material_index_groups=len(set(with_material_index))))
    seen |= unique
print(json.dumps({'scope': 'Exact source accessor bytes/layout and primitive semantics; material differences intentionally separated. No runtime RID-owner proof or implemented optimization.',
                  'rows': rows, 'total_mesh_definitions': sum(r['meshes'] for r in rows),
                  'cross_file_geometry_groups': len(seen)}, indent=2))
