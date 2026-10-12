"""Read immutable selected natives to scope four owned overhead successors."""
import bpy, json, hashlib
import numpy as np
from pathlib import Path

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
(P / 'source/natives').mkdir(parents=True, exist_ok=True)
(P / 'exports').mkdir(exist_ok=True)
bases = [(C / 'source/natives/G7_Completion_r003.blend',
          '21ea0a9cda7942bacf81e288ab89e12b979ffef1933d192eb200d0f0c438b327',
          ['G7C3_Aft_Closure', 'G7C3_Fore_Closure']),
         (C / 'continuation_r004/source/natives/G7_FiniteSeams_r004b.blend',
          'a79684c1d71be0023206a13395bb91920497043595a3899eefbef935267785d1',
          ['G7C4_Aft_NeckLanding', 'G7C4_Fore_NeckLanding'])]

def signature(ob):
    h = hashlib.sha256(); h.update(np.array(ob.matrix_world).tobytes()); h.update(ob.type.encode())
    h.update(np.array([v.co[:] for v in ob.data.vertices], dtype='<f4').tobytes())
    h.update(json.dumps([list(f.vertices) for f in ob.data.polygons]).encode())
    for uv in ob.data.uv_layers: h.update(np.array([q.uv[:] for q in uv.data], dtype='<f4').tobytes())
    h.update(json.dumps([m.name if m else None for m in ob.data.materials]).encode())
    return h.hexdigest()

parts = []; materials = []; source_rows = []
for base, sha, cells in bases:
    assert hashlib.sha256(base.read_bytes()).hexdigest() == sha
    bpy.ops.wm.open_mainfile(filepath=str(base))
    names = set()
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH' or ob.get('group7_cell') not in cells: continue
        assert np.max(abs(np.array(ob.matrix_world)-np.eye(4))) < 1e-10
        vs = [(v.co.x, v.co.z, -v.co.y) for v in ob.data.vertices]
        row = {'name': ob.name, 'cell': ob['group7_cell'], 'category': ob['contact_category'],
               'vertices_world_xyz': vs, 'faces': [list(f.vertices) for f in ob.data.polygons],
               'uv_layers': [{'name': uv.name, 'coordinates': [list(q.uv) for q in uv.data]} for uv in ob.data.uv_layers],
               'material_names': [m.name if m else None for m in ob.data.materials],
               'original_signature': signature(ob), 'properties': dict(ob.items()),
               'base_native': base.relative_to(R).as_posix(), 'base_native_sha256': sha}
        assert len(row['material_names']) == 1
        names.update(row['material_names']); parts.append(row)
    materials.append({'base_native': base.relative_to(R).as_posix(), 'base_native_sha256': sha, 'names': sorted(names)})
    source_rows.append({'base_native': base.relative_to(R).as_posix(), 'sha256': sha, 'cells': cells})
    assert hashlib.sha256(base.read_bytes()).hexdigest() == sha
plan = {'schema': 'astraea.group7.owned_neck_headroom.r009', 'sources': source_rows,
        'materials_to_append_exact': materials, 'parts': parts,
        'export_cells': sorted(q for _, _, cells in bases for q in cells),
        'native_filename': 'G7_D18Overhead_r009.blend', 'roof_and_hardware_raise_m': .4,
        'fixed_floor_wall_foot_y': 106.5, 'original_source_or_protected_roof_changed': False,
        'additional_owned_air_height_m': 4.0, 'original_route_criteria_changed': False,
        'primary_capacity_accepted': False}
(P / 'docs/OWNED_NECK_PREIMAGE.json').write_text(json.dumps(plan, separators=(',', ':'))+'\n')
preimage = P / 'docs/PREIMAGE_GROUP7_COMPLETION.json'; assert not preimage.exists()
preimage.write_bytes((R / 'Game/data/architecture/GROUP7_COMPLETION.json').read_bytes())
print('G7_R009_IMMUTABLE_SOURCE_SURVEY', len(parts), 'parts', len(plan['export_cells']), 'cells')
