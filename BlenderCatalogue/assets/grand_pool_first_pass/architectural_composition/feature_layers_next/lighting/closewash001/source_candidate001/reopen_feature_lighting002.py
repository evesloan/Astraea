"""Independent, source-only reopen QA v002: ABI-correct serial snapshot/geometry stages.

Reads the new candidate, retained source exemplars and pinned source/native geometry.
Never saves a blend, exports, renders, executes the builder, or edits live inputs.
The only writes are new JSON evidence files in an unused candidate/qa subdirectory.
No source-only result is native, export, lighting-budget, visual, or gameplay approval.
"""
import argparse
import ast
import collections
import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path('/workspace/scratch/375c2e438292/pool-architectural-composition/fixture_layer_proposal001')
CANDIDATE = ROOT / 'source_candidate001'
SOURCE = CANDIDATE / 'source/AST-AQU-016_pool_feature_lighting.blend'
CAT = Path('/workspace/shared/astraea-catalogue-continuation-20261002')
GAME = Path('/workspace/shared/astraea-godot-production-20261003')
POOL = CAT / 'assets/grand_pool_first_pass'
ARCH = POOL / 'architectural_composition'
FINISH = POOL / 'finish_envelope'
EXEMPLAR_SOURCE = FINISH / 'source/grand_pool_finish_envelope.blend'
EXEMPLARS = {
    'champagne_metal': 'WetRestWash_444_SourceBackplate',
    'warm_walnut': 'WetRestWash_444_RecessHousing',
    'lens': 'WetRestWash_444_OpalLens',
}
FROZEN = {
    ROOT / 'PROPOSED_FIXTURE_LAYER.json': '230df56e7149bba6b4a089a99ed0ad3f09774d1e42c51be35a0fe17ab727c106',
    ROOT / 'GEOMETRY_CHECKS.json': '297b2b9c995458c01a5ca9314c17c97bb31135ba23668c1acee72d017bfb0703',
    ROOT / 'INPUT_PINS.json': '5ec19942630bbbd375de30ea0cfcc0d1f3736cdcb5f2058a5a6f7df77c4c6f93',
    FINISH / 'source/build_finish_envelope.py': 'ef5d07918f89de9f2a454e0a4dcd40221af8455d6c73d472e12dc9ccb69dd2d4',
}
TOL = 5e-5  # Retained source contact tolerance, never enlarged for this candidate.
FLOAT32_MAX_ERROR_M = 2e-5
ISSUES = []
PINNED = {}
REPORT = {}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read_json(path):
    path = Path(path)
    PINNED.setdefault(str(path), sha(path))
    return json.loads(path.read_text())


def require(test, message):
    if not test:
        raise AssertionError(message)


def check(test, category, **detail):
    if not test:
        ISSUES.append({'category': category, **detail})
    return bool(test)


def plain(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        require(math.isfinite(value), 'Non-finite saved value')
        return value
    if hasattr(value, 'to_dict'):
        return {str(k): plain(v) for k, v in value.to_dict().items()}
    if hasattr(value, 'to_list'):
        return [plain(v) for v in value.to_list()]
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    return [plain(v) for v in value]


def props(obj):
    return {k: plain(obj[k]) for k in obj.keys() if k != '_RNA_UI'}


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def native(point):
    return [float(point[0]), float(point[2]), -float(point[1])]


def face_key(indices):
    seq = tuple(indices)
    return min(seq[i:] + seq[:i] for i in range(len(seq))) if seq else seq


def unoriented_face_key(indices):
    return min(face_key(indices), face_key(tuple(indices)[::-1]))


def image_signature(image):
    packed = []
    if image.packed_files:
        packed = [hashlib.sha256(bytes(p.packed_file.data)).hexdigest() for p in image.packed_files]
    elif image.packed_file:
        packed = [hashlib.sha256(bytes(image.packed_file.data)).hexdigest()]
    require(packed and min(image.size) > 0, 'Missing actual packed texture bytes: ' + image.name)
    return {
        'packed_sha256': sorted(packed), 'size': list(image.size),
        'source': image.source, 'channels': image.channels, 'is_float': image.is_float,
        'colorspace': image.colorspace_settings.name, 'alpha_mode': image.alpha_mode,
    }


RNA_IGNORED = {
    'rna_type', 'name', 'name_full', 'id_data', 'original', 'library', 'override_library',
    'asset_data', 'preview', 'users', 'use_fake_user', 'use_extra_user', 'is_embedded_data',
    'is_evaluated', 'is_library_indirect', 'is_missing', 'is_runtime_data', 'tag',
    'session_uid', 'is_updated', 'is_updated_data', 'is_editable',
    'location', 'width', 'height', 'dimensions', 'width_hidden', 'select', 'show_options',
    'show_preview', 'show_texture', 'hide', 'label', 'parent', 'color', 'use_custom_color',
    'inputs', 'outputs', 'internal_links', 'node_tree', 'image', 'type', 'bl_idname',
    'bl_label', 'bl_description', 'bl_icon', 'bl_static_type', 'bl_width_default',
    'bl_width_min', 'bl_width_max', 'bl_height_default', 'bl_height_min', 'bl_height_max',
}


def scalar_rna(obj, ignore=()):
    """All exposed non-UI scalar/array RNA, including extension/UV/image-node modes."""
    result = {}
    for prop in obj.bl_rna.properties:
        name = prop.identifier
        if name in RNA_IGNORED or name in ignore or prop.type not in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            continue
        value = getattr(obj, name)
        result[name] = sorted(value) if isinstance(value, set) else plain(value)
    return result


def socket_signature(socket):
    result = {'identifier': socket.identifier, 'type': socket.bl_idname, 'enabled': socket.enabled}
    if hasattr(socket, 'default_value'):
        result['default_value'] = plain(socket.default_value)
    return result


def tree_signature(tree, stack=()):
    require(tree.as_pointer() not in stack, 'Recursive shader group')
    require(tree.animation_data is None, 'Animated/driven shader graphs are outside this fixed-source comparison')
    stack = stack + (tree.as_pointer(),)
    nodes = []
    for node in sorted(tree.nodes, key=lambda n: n.name):
        row = {'name': node.name, 'type': node.bl_idname, 'rna': scalar_rna(node),
               'properties': props(node), 'inputs': [socket_signature(s) for s in node.inputs],
               'outputs': [socket_signature(s) for s in node.outputs]}
        if getattr(node, 'image', None):
            row['image'] = image_signature(node.image)
            row['image_user'] = scalar_rna(node.image_user)
        if getattr(node, 'node_tree', None):
            row['group'] = tree_signature(node.node_tree, stack)
        if hasattr(node, 'color_ramp'):
            ramp = node.color_ramp
            row['color_ramp'] = {'rna': scalar_rna(ramp), 'elements': [
                {'position': e.position, 'color': list(e.color)} for e in ramp.elements]}
        if hasattr(node, 'mapping') and hasattr(node.mapping, 'curves'):
            row['curve_mapping'] = {'rna': scalar_rna(node.mapping), 'curves': [
                [{'location': list(p.location), 'handle_type': p.handle_type} for p in c.points]
                for c in node.mapping.curves]}
        row['internal_links'] = sorted([[list(node.inputs).index(x.from_socket) if x.from_socket in list(node.inputs) else -1,
                                         list(node.outputs).index(x.to_socket) if x.to_socket in list(node.outputs) else -1]
                                        for x in node.internal_links])
        nodes.append(row)
    links = sorted([[x.from_node.name, list(x.from_node.outputs).index(x.from_socket),
                     x.to_node.name, list(x.to_node.inputs).index(x.to_socket), x.is_muted]
                    for x in tree.links])
    return {'nodes': nodes, 'links': links, 'properties': props(tree)}


def material_signature(material):
    require(material is not None and material.use_nodes and material.node_tree, 'Missing node material')
    require(material.animation_data is None, 'Animated material outside fixed-source comparison')
    settings = scalar_rna(material, {'paint_active_slot', 'paint_clone_slot', 'pass_index'})
    return {'settings': settings, 'properties': props(material), 'graph': tree_signature(material.node_tree)}


def geometry_helpers():
    """Load only the pinned, retained read-only geometry primitives, never QA main bodies."""
    sys.path.insert(0, '/workspace/scratch/375c2e438292/geometry-deps')
    global np, Polygon, union_all
    import numpy as np
    from shapely.geometry import Polygon, Point
    from shapely import union_all
    path = FINISH / 'stock/geometry.py'
    spec = importlib.util.spec_from_file_location('retained_fixture_qa_geometry', path)
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    namespace = {key: getattr(geo, key) for key in dir(geo) if not key.startswith('_')}
    namespace.update({'np': np, 'Polygon': Polygon, 'Point': Point, 'TOL': TOL})
    functions = {'record', 'rayhits', 'surface_points', 'on_surface', 'strict_inside', 'contact_pair', 'cone_triangle'}
    path = FINISH / 'qa/pure_geometry/review_finish.py'
    body = [node for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef) and node.name in functions]
    require({node.name for node in body} == functions, 'Missing pinned retained predicates')
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def prepare(geom):
    geom['ta'] = np.asarray(geom['triangles'], dtype=float)
    geom['tmin'] = geom['ta'].min(axis=1)
    geom['tmax'] = geom['ta'].max(axis=1)
    return geom


def check_metadata(actual, expected, owner, tolerance=1e-10):
    for key, wanted in expected.items():
        got = actual.get(key)
        if isinstance(wanted, (list, tuple)):
            match = isinstance(got, (list, tuple)) and len(got) == len(wanted)
            match = match and max((abs(float(a) - float(b)) for a, b in zip(got, wanted)), default=0) <= tolerance
        elif isinstance(wanted, float):
            match = isinstance(got, (int, float)) and abs(got - wanted) <= tolerance
        else:
            match = got == wanted
        check(match, 'saved_metadata', owner=owner, key=key, expected=wanted, actual=got)


def inspect_candidate(bpy, proposal, helpers):
    from mathutils import Vector
    scene = bpy.context.scene
    mesh_rows, marker_rows, materials, material_by_name = [], [], {}, {}
    parts = {p['name']: p for p in proposal['proposed_parts']}
    fixtures = {p['name']: p for p in proposal['fixtures']}
    objects = list(scene.objects)
    check(len(bpy.data.scenes) == 1, 'single_scene', actual=len(bpy.data.scenes))
    check(set(bpy.data.objects) == set(objects), 'unlinked_object_datablocks')
    check(collections.Counter(o.type for o in objects) == {'MESH': 12, 'EMPTY': 3}, 'object_census',
          actual=dict(collections.Counter(o.type for o in objects)))
    require({o.name for o in objects} == set(parts) | set(fixtures), 'Saved object names differ from exact approved 12+3 roster')
    check(not bpy.data.lights and not bpy.data.cameras and scene.camera is None, 'lights_or_cameras')
    check(scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1, 'source_metres')
    check(not scene.animation_data, 'scene_animation')
    psha = FROZEN[ROOT / 'PROPOSED_FIXTURE_LAYER.json']
    for ob in sorted(objects, key=lambda o: o.name):
        require(ob.type in {'MESH', 'EMPTY'}, 'Unexpected object kind')
        check(ob.parent is None and not ob.constraints and not ob.animation_data, 'object_dynamic_transform', name=ob.name)
        custom = props(ob)
        if ob.type == 'EMPTY':
            expected = fixtures[ob.name]
            pos = native(ob.matrix_world.translation)
            snapped = [f32(x) for x in expected['position_xyz']]
            check(pos == snapped, 'marker_float32_position', name=ob.name, actual=pos, expected=snapped)
            check(max(abs(float(ob.matrix_world[i][j]) - float(i == j)) for i in range(3) for j in range(3)) < 1e-10,
                  'marker_rotation_scale', name=ob.name)
            mappings = {'direction_godot_xyz': 'direction_xyz', 'receiver_godot_xyz': 'receiver_xyz',
                        'visibility_sample_godot_xyz': 'visibility_sample_xyz', 'physical_housing': 'physical_housing',
                        'physical_lens': 'physical_lens', 'retained_host': 'host', 'receiver_source_part': 'receiver_source_part',
                        'source_support_anchor_godot_xyz': 'source_support_anchor_xyz',
                        'source_support_normal_godot_xyz': 'source_support_normal_xyz',
                        'suggested_range_m': 'suggested_range_m', 'suggested_energy': 'suggested_energy',
                        'suggested_spot_angle_degrees': 'suggested_spot_angle_degrees'}
            check_metadata(custom, {**{k: expected[v] for k, v in mappings.items()},
                                    'parent_design_id': 'AST-AQU-016', 'proposal_sha256': psha}, ob.name)
            marker_rows.append({'name': ob.name, 'position_xyz': pos, 'properties': custom})
            continue
        planned = parts[ob.name]
        check(not ob.modifiers and not ob.data.shape_keys and not ob.data.animation_data, 'mesh_deformation', name=ob.name)
        check(max(abs(float(ob.matrix_world[i][j]) - float(i == j)) for i in range(4) for j in range(4)) < 1e-10,
              'mesh_transform', name=ob.name)
        check(not ob.hide_render and not ob.hide_viewport, 'hidden_hardware', name=ob.name)
        mesh = ob.data
        vertices = [native(ob.matrix_world @ v.co) for v in mesh.vertices]
        expected_vertices = [[f32(x) for x in v] for v in planned['world_vertices']]
        require(len(vertices) == len(expected_vertices), 'Saved vertex count changed: ' + ob.name)
        vlookup = {tuple(v): i for i, v in enumerate(expected_vertices)}
        require(len(vlookup) == len(expected_vertices), 'Float32 proposal has duplicate vertices')
        exact_vertices = collections.Counter(map(tuple, vertices)) == collections.Counter(map(tuple, expected_vertices))
        check(exact_vertices, 'float32_vertex_equivalence', name=ob.name, actual=vertices, expected=expected_vertices)
        require(exact_vertices, 'Cannot prove topology after vertex mismatch: ' + ob.name)
        remap = [vlookup[tuple(v)] for v in vertices]
        faces = [list(p.vertices) for p in mesh.polygons]
        actual_faces = collections.Counter(unoriented_face_key([remap[i] for i in face]) for face in faces)
        expected_faces = collections.Counter(unoriented_face_key(face) for face in planned['faces'])
        check(actual_faces == expected_faces, 'face_topology_equivalence', name=ob.name)
        actual_by_plan = [None] * len(vertices)
        for index, plan_index in enumerate(remap):
            actual_by_plan[plan_index] = vertices[index]
        error = max(float(np.linalg.norm(np.asarray(a) - b)) for a, b in zip(actual_by_plan, planned['world_vertices']))
        check(error <= FLOAT32_MAX_ERROR_M, 'unsnapped_vertex_error', name=ob.name, maximum_m=error)
        edges = collections.Counter()
        directed = collections.Counter()
        for face in faces:
            for a, b in zip(face, face[1:] + face[:1]):
                edges[tuple(sorted((a, b)))] += 1
                directed[(a, b)] += 1
        check(all(n == 2 for n in edges.values()) and all(directed[(a, b)] == directed[(b, a)] == 1 for a, b in edges),
              'closed_oriented_manifold', name=ob.name)
        mesh.calc_loop_triangles()
        triangles = [[vertices[i] for i in t.vertices] for t in mesh.loop_triangles]
        center = np.mean(vertices, axis=0)
        volume = sum(float(np.dot(np.asarray(t[0]) - center, np.cross(np.asarray(t[1]) - center, np.asarray(t[2]) - center))) / 6 for t in triangles)
        areas = [float(np.linalg.norm(np.cross(np.asarray(t[1]) - t[0], np.asarray(t[2]) - t[0]))) / 2 for t in triangles]
        check(volume > 1e-8 and min(areas) > 1e-10, 'outward_nondegenerate_solid', name=ob.name, volume_m3=volume, minimum_triangle_area_m2=min(areas))
        check_metadata(custom, {'retained_host': planned['support'], 'material_role': planned['material_role'],
                               'collision_contract': planned['collision_contract'], 'parent_design_id': 'AST-AQU-016',
                               'proposal_sha256': psha}, ob.name)
        if planned['material_role'] == 'lens':
            check(custom.get('cast_shadow') is False, 'lens_shadow_contract', name=ob.name)
        else:
            check(custom.get('cast_shadow', True) is not False, 'hardware_shadow_contract', name=ob.name)
        require(len(mesh.materials) == 1 and all(p.material_index == 0 for p in mesh.polygons), 'Expected one actual material slot: ' + ob.name)
        mat = mesh.materials[0]
        sig = material_signature(mat)
        materials.setdefault(planned['material_role'], []).append({'object': ob.name, 'material': mat.name, 'signature': sig, 'sha256': digest(sig)})
        material_by_name[mat.name] = digest(sig)
        require(len(mesh.uv_layers) == 1 and mesh.uv_layers.active.name == 'MetreScaled', 'Wrong saved metre UV layer: ' + ob.name)
        scale = list(mat.get('meters_per_tile_uv', [1, 1]))
        require(len(scale) == 2 and min(scale) > 0, 'Invalid metre UV material scale')
        layer = mesh.uv_layers.active
        uv_error, uv_actual = 0.0, []
        for poly in mesh.polygons:
            n = poly.normal.normalized()
            u = (Vector((1, 0, 0)) - n * n.x).normalized() if abs(n.z) > .7 else Vector((-n.y, n.x, 0)).normalized()
            v = n.cross(u).normalized()
            for li in poly.loop_indices:
                point = mesh.vertices[mesh.loops[li].vertex_index].co
                expected_uv = (f32(point.dot(u) / scale[0]), f32(point.dot(v) / scale[1]))
                actual_uv = tuple(layer.data[li].uv)
                uv_actual.append({'loop': li, 'vertex': mesh.loops[li].vertex_index, 'uv': list(actual_uv)})
                uv_error = max(uv_error, max(abs(a - b) for a, b in zip(actual_uv, expected_uv)))
        check(uv_error <= 1e-7, 'retained_metre_uv_projection', name=ob.name, maximum_float32_uv_error=uv_error)
        row = {'name': ob.name, 'vertices': vertices, 'faces': faces, 'triangles': triangles,
               'uv_layer': layer.name, 'uv_loops': sorted(uv_actual, key=lambda r: r['loop']),
               'material_name': mat.name, 'properties': custom, 'max_proposal_error_m': error,
               'max_uv_error': uv_error, 'signed_volume_m3': volume}
        mesh_rows.append(row)
    check(len(bpy.data.meshes) == 12, 'mesh_datablock_census', actual=len(bpy.data.meshes))
    check(len(bpy.data.materials) == 3 and set(material_by_name) == {m.name for m in bpy.data.materials},
          'material_datablock_census', actual=[m.name for m in bpy.data.materials])
    check(not bpy.data.libraries, 'linked_external_libraries')
    return mesh_rows, marker_rows, materials


def retained_geometry(helpers):
    source, native_parts, cache = [], [], {}
    source_by = {}
    architecture = read_json(GAME / 'data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json')
    section = read_json(GAME / 'data/architecture/GRAND_POOL_SECTION_RUNTIME.json')
    finish = read_json(GAME / 'data/architecture/GRAND_POOL_FINISH_RUNTIME.json')
    first = read_json(GAME / 'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json')
    actual = read_json(ARCH / 'source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json')
    require(len(actual['parts']) == 451 and len(actual['plants']) == 12, 'Retained architecture count')
    require(finish['logical_furnishing_count'] == architecture['preserved_logical_furnishing_count'] == 126, 'Retained programme count')
    require(len(section['fixtures']) + len(finish['fixtures']) == 39 and not architecture['fixtures'], 'Retained source fixture count')
    for kind in ('loggia', 'focal_end', 'roof'):
        path = ARCH / ('export_tooling003/' + kind + '_snapshot.json')
        snapshot = read_json(path)
        eq = read_json(path.with_name(kind + '_EQUIVALENCE.json'))
        require(eq['status'] == 'PASS' and eq['snapshot_sha256'] == sha(path), 'Retained source snapshot equivalence')
        require(sha(Path(snapshot['source'])) == snapshot['source_sha256'] == eq['source_sha256'], 'Retained source hash mismatch')
        for ob in snapshot['objects']:
            if ob['type'] != 'MESH':
                continue
            rec = prepare(helpers['record'](ob['name'], [v for t in ob['positions'] for v in t], ob['positions'], meta=ob))
            source.append(rec)
            source_by[rec['name']] = rec
    require(len(source) == 451 and len(source_by) == 451, 'Retained snapshot roster')
    def add_model(file, label, position=None, yaw=0):
        path = GAME / 'assets/models' / file
        require(str(path) in PINNED, 'Unpinned native geometry: ' + str(path))
        if path not in cache:
            cache[path] = helpers['read_glb'](path)
        for mesh in cache[path]['meshes']:
            vertices = np.asarray(mesh['vertices'])
            triangles = np.asarray(mesh['triangles'])
            if position is not None:
                c, s = math.cos(yaw), math.sin(yaw)
                rotation = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
                vertices = vertices @ rotation.T + position
                triangles = triangles @ rotation.T + position
            native_parts.append(prepare(helpers['record'](label + '::' + mesh['name'], vertices.tolist(), triangles.tolist(),
                                                          native_file=file, native_mesh=mesh['name'], native_primitive=mesh['primitive'])))
    add_model('AST-AQU-016.glb', 'GrandPoolConnectedArchitecture')
    for contract in (finish, architecture):
        for assembly in contract['assemblies']:
            add_model(assembly['model_file'], assembly['name'])
    for placement in first['placements'] + finish['placements'] + architecture['plants']:
        add_model(placement['model_file'], placement['name'], placement['position_xyz'], placement['yaw_radians'])
    for contract in (first, finish, architecture):
        for model in contract['models'].values():
            require(sha(GAME / 'assets/models' / model['file']) == model['sha256'], 'Model contract mismatch: ' + model['file'])
    return source, source_by, native_parts, section, first, finish, architecture


def backplate_contact(part, host, marker):
    anchor = np.asarray(marker['properties']['source_support_anchor_godot_xyz'])
    normal = np.asarray(marker['properties']['source_support_normal_godot_xyz'])
    normal /= np.linalg.norm(normal)
    basis_seed = np.array([1., 0., 0.]) if abs(normal[0]) < .8 else np.array([0., 1., 0.])
    u = basis_seed - normal * float(basis_seed @ normal)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    project = lambda points: [[float((np.asarray(q) - anchor) @ u), float((np.asarray(q) - anchor) @ v)] for q in points]
    face_rows = []
    for face in part['faces']:
        points = np.asarray([part['vertices'][i] for i in face])
        distance = max(abs(float((q - anchor) @ normal)) for q in points)
        if distance > TOL:
            continue
        polygon = Polygon(project(points))
        face_normal = np.cross(points[1] - points[0], points[2] - points[0])
        face_normal /= np.linalg.norm(face_normal)
        host_polygons = []
        for triangle in host['ta']:
            if max(abs(float((q - anchor) @ normal)) for q in triangle) <= 1e-7:
                tri = Polygon(project(triangle))
                if tri.is_valid and tri.area > 1e-12:
                    host_polygons.append(tri)
        require(host_polygons, 'No actual retained coplanar host triangles')
        union = union_all(host_polygons)
        uncovered = polygon.difference(union).area
        face_rows.append({'face_indices': face, 'max_plane_error_m': distance,
                          'full_backplate_area_m2': polygon.area, 'covered_contact_area_m2': polygon.intersection(union).area,
                          'uncovered_area_m2': uncovered, 'normal_dot_support_normal': float(face_normal @ normal),
                          'pass': polygon.is_valid and polygon.area > .15 and uncovered < 1e-10 and float(face_normal @ normal) < -.9999})
    check(len(face_rows) == 1 and face_rows[0]['pass'], 'full_area_backplate_contact', name=part['name'], faces=face_rows)
    return {'part': part['name'], 'host': host['name'], 'faces': face_rows, 'tolerance_m': TOL}


def geometry_checks(mesh_rows, markers, proposal, baseline, helpers):
    source, source_by, native_parts, section, first, finish, arch = retained_geometry(helpers)
    new = [prepare(helpers['record'](r['name'], r['vertices'], r['triangles'], meta=r['properties'], faces=r['faces'])) for r in mesh_rows]
    by_name = {r['name']: r for r in new}
    planned = {r['name']: r for r in proposal['proposed_parts']}
    rayhits, contact_pair, overlap = helpers['rayhits'], helpers['contact_pair'], helpers['overlap']
    on_surface = helpers['on_surface']
    ray_parts = native_parts + new
    contacts, support, primary, fan_rows = [], [], [], []
    for marker in markers:
        name, m = marker['name'], marker['properties']
        p, axis = np.asarray(marker['position_xyz']), np.asarray(m['direction_godot_xyz'])
        target = np.asarray(m['receiver_godot_xyz'])
        check(abs(np.linalg.norm(axis) - 1) < 1e-10, 'marker_unit_direction', name=name)
        check(float(np.linalg.norm(np.cross((target - p) / np.linalg.norm(target - p), axis))) < 2e-5,
              'saved_marker_target_alignment', name=name)
        host = source_by[m['retained_host']]
        base = name.removeprefix('DATUM_finish_light_')
        contacts.append(backplate_contact(by_name[base + '_SourceBackplate'], host, marker))
        check(on_surface(m['source_support_anchor_godot_xyz'], host, TOL), 'saved_support_anchor', name=name)
        check(on_surface(target, source_by[m['receiver_source_part']], TOL), 'saved_receiver_surface', name=name)
        for part in [r for r in new if r['name'].startswith(base + '_')]:
            other_name = part['meta']['retained_host']
            other = source_by.get(other_name, by_name.get(other_name))
            require(other is not None, 'Unresolved actual support metadata')
            result = contact_pair(part, other)
            support.append({'part': part['name'], 'support': other_name, **result})
            check(result['touch'], 'actual_support_chain', part=part['name'], result=result)
        lens = by_name[m['physical_lens']]
        behind = rayhits(p, p - axis * .10, [lens])
        lens_hit = behind[0] if behind else None
        check(lens_hit is not None and abs(lens_hit['distance_m'] - .02) <= TOL, 'actual_lens_front_offset', name=name, hit=lens_hit)
        exit_hits = rayhits(p, p + axis * .06, ray_parts)
        lens_exit_hits = rayhits(np.asarray(lens_hit['point_xyz']) + axis * .0001, p + axis * .06, ray_parts) if lens_hit else []
        receiver_sample_hits = rayhits(p, m['visibility_sample_godot_xyz'], ray_parts)
        hits = rayhits(p, target + axis * .001, ray_parts)
        first_hit = hits[0] if hits else None
        distance = float(np.linalg.norm(target - p))
        expected_receiver = next(r for r in baseline['physical_fixture_checks'] if r['name'] == name)['first_native_receiver_hit']
        receiver_matches = False
        if first_hit:
            hit_part = next(r for r in native_parts if r['name'] == first_hit['part']) if first_hit['part'] not in by_name else by_name[first_hit['part']]
            receiver_matches = (hit_part.get('native_file') == expected_receiver['native_file'] and
                                hit_part.get('native_mesh') == expected_receiver['native_mesh'])
        check(first_hit is not None and abs(first_hit['distance_m'] - distance) <= TOL and receiver_matches,
              'actual_receiver_first_hit', name=name, first_hit=first_hit, expected_receiver=expected_receiver)
        check(not exit_hits and not lens_exit_hits and not receiver_sample_hits, 'actual_primary_light_paths', name=name,
              exit_hits=exit_hits, lens_exit_hits=lens_exit_hits, receiver_sample_hits=receiver_sample_hits)
        # Continuous analytical 60 mm finite cone against all retained/new triangles.
        radius = .06 * math.tan(math.radians(m['suggested_spot_angle_degrees']))
        box = [(p - radius - .06).tolist(), (p + radius + .06).tolist()]
        cone_hits = []
        for part in ray_parts:
            if not overlap(box, part['bounds'], -TOL):
                continue
            for index, triangle in enumerate(part['triangles']):
                hit = helpers['cone_triangle'](p, axis, m['suggested_spot_angle_degrees'], triangle)
                if hit is not None:
                    cone_hits.append({'part': part['name'], 'triangle': index, **hit})
        check(not cone_hits, 'actual_60mm_forward_cone', name=name, hits=cone_hits)
        primary.append({'name': name, 'position_xyz': p.tolist(), 'direction_xyz': axis.tolist(), 'lens_front_hit': lens_hit,
                        'exit_60mm_hits': exit_hits, 'lens_front_to_exit_hits': lens_exit_hits,
                        'receiver_sample_hits': receiver_sample_hits, 'first_hit': first_hit,
                        'receiver_distance_m': distance, 'finite_forward_cone_hits': cone_hits})
        # Target coordinates are independently located on retained surfaces below;
        # no proposed lens-exit point or old PASS boolean is used as evidence.
        targets = next(r['receiver_samples'] for r in baseline['receiver_fans'] if r['name'] == name)
        rows = []
        for retained in targets:
            q = np.asarray(retained['target_xyz'])
            delta = q - p
            length = float(np.linalg.norm(delta))
            direction = delta / length
            angle = math.degrees(math.acos(float(np.clip(axis @ direction, -1, 1))))
            backward_hits = rayhits(p, p - direction * .20, [lens])
            actual_exit = backward_hits[0] if backward_hits else None
            check(actual_exit is not None, 'actual_fan_lens_intersection', name=name, target=q.tolist())
            obstruction = rayhits(np.asarray(actual_exit['point_xyz']) + direction * .0001, q - direction * .02, ray_parts) if actual_exit else []
            hits = rayhits(p, q + direction * .001, ray_parts)
            hit = hits[0] if hits else None
            surface = any(on_surface(q, rec, TOL) for rec in source if overlap(helpers['bounds']([q]), rec['bounds'], -TOL))
            good = (actual_exit is not None and not obstruction and surface and hit is not None and
                    abs(hit['distance_m'] - length) <= TOL and angle < m['suggested_spot_angle_degrees'] and length < m['suggested_range_m'])
            check(good, 'actual_receiver_fan', name=name, target=q.tolist(), first_hit=hit,
                  actual_lens_exit=actual_exit, obstructions=obstruction, target_on_retained_source=surface)
            rows.append({'target_xyz': q.tolist(), 'actual_lens_exit': actual_exit, 'first_hit': hit,
                         'lens_to_receiver_sample_hits': obstruction, 'target_on_retained_source': surface,
                         'distance_m': length, 'axis_angle_degrees': angle, 'pass': good})
        fan_rows.append({'name': name, 'receiver_samples': rows})
    contact_inputs = source + [r for r in native_parts if not r['name'].startswith(('GrandPoolWetLoggias::', 'GrandPoolFocalEnd::', 'GrandPoolRoofComposition::'))]
    retained_contacts = []
    for part in new:
        for old in contact_inputs:
            if not overlap(part['bounds'], old['bounds'], -TOL):
                continue
            result = contact_pair(part, old)
            if not (result['touch'] or result['penetration']):
                continue
            allowed = part['name'].endswith('_SourceBackplate') and part['meta']['retained_host'] == old['name']
            row = {'new': part['name'], 'retained': old['name'], 'declared_backplate_host': allowed, **result}
            retained_contacts.append(row)
            check(allowed and not result['penetration'], 'unintended_retained_contact', **row)
    expected_joints = {frozenset((r['name'], r['support'])) for r in proposal['proposed_parts'] if r['support'] in planned}
    require(len(expected_joints) == 9, 'Approved joint roster changed')
    joints, found_joints = [], set()
    for index, a in enumerate(new):
        for b in new[index + 1:]:
            if not overlap(a['bounds'], b['bounds'], -TOL):
                continue
            result = contact_pair(a, b)
            if not (result['touch'] or result['penetration']):
                continue
            pair = frozenset((a['name'], b['name']))
            declared = pair in expected_joints
            joints.append({'a': a['name'], 'b': b['name'], 'declared': declared, **result})
            if declared and result['touch']:
                found_joints.add(pair)
            check(declared, 'unintended_new_contact', a=a['name'], b=b['name'], result=result)
    check(found_joints == expected_joints and len(joints) == 9, 'nine_actual_mechanical_joints',
          missing=[sorted(x) for x in expected_joints - found_joints], actual_count=len(joints))
    preserved, views, routes = [], [], []
    for fixture in section['fixtures'] + finish['fixtures']:
        p = np.asarray(fixture['position_xyz'])
        direction = np.asarray(fixture.get('direction_xyz', fixture.get('direction')))
        rays = [('exit_60mm', p + direction * .06)]
        if 'receiver_xyz' in fixture:
            rays += [('receiver', fixture['receiver_xyz']), ('visibility_sample', fixture.get('visibility_sample_xyz', fixture['receiver_xyz']))]
        rays += [('stock_' + r['receiver'], r['receiver_world_xyz']) for r in fixture.get('all_source_receiver_rays', [])]
        for kind, endpoint in rays:
            hits = rayhits(p, endpoint, new)
            preserved.append({'fixture': fixture['name'], 'kind': kind, 'hits': hits})
            check(not hits, 'preserved_old_fixture_ray', fixture=fixture['name'], kind=kind, hits=hits)
    for view in arch['preserved_view_probes']:
        hits = rayhits(view['eye_xyz'], view['target_xyz'], new)
        views.append({'name': view['name'], 'kind': view['kind'], 'hits': hits})
        check(not hits, 'preserved_view', name=view['name'], hits=hits)
    for view in arch['seat_approaches']:
        hits = rayhits(view['seated_eye_xyz'], view['pool_view_target_xyz'], new)
        views.append({'name': view['name'], 'kind': 'new_curved_seat_view', 'hits': hits})
        check(not hits, 'preserved_seated_view', name=view['name'], hits=hits)
    paths = [dict(name=p['item'], points=p['points'], r=.3, h=1.8) for p in first['approach_paths']]
    paths += [dict(name='wet_main', points=[[-45.9, 46.2, -458], [-45.9, 46.2, -405]], r=.5, h=2)]
    paths += [dict(name='dry_market', points=[[x, 52.5, z] for x, z in section['market']['adopted_dry_loop_centreline_xz']], r=.5, h=2)]
    paths += [dict(name='stock_' + p['display'], points=p['points_xyz'], r=.3, h=1.8) for p in finish['stock_approach_paths']]
    paths += [dict(name='ramp', points=section['accessible_ramp']['route_xyz'], r=.5, h=2),
              dict(name='lower_lift', points=section['wet_market_link']['lift']['lower_approach_xyz'], r=.5, h=2)]
    paths += [dict(name='curved_' + p['name'], points=p['approach_xyz'], r=p['swept_envelope_radius_m'], h=p['standing_height_m']) for p in arch['seat_approaches']]
    for path in paths:
        found = set()
        for a, b in zip(path['points'], path['points'][1:]):
            box = [[min(a[0], b[0]) - path['r'], min(a[1], b[1]) + .02, min(a[2], b[2]) - path['r']],
                   [max(a[0], b[0]) + path['r'], max(a[1], b[1]) + path['h'], max(a[2], b[2]) + path['r']]]
            found.update(r['name'] for r in new if overlap(box, r['bounds'], TOL))
        routes.append({'name': path['name'], 'continuous_broad_envelope_hits': sorted(found)})
        check(not found, 'preserved_route_envelope', name=path['name'], hits=sorted(found))
    check(len(preserved) == len(baseline['preserved_fixture_ray_checks']) == 91 and len(views) == 162 and len(routes) == 30,
          'preservation_probe_census', fixture_rays=len(preserved), views=len(views), routes=len(routes))
    return {'full_backplate_contacts': contacts, 'actual_support_chains': support, 'actual_primary_light_paths': primary,
            'actual_receiver_fans': fan_rows, 'retained_contacts': retained_contacts, 'new_mechanical_joints': joints,
            'preserved_fixture_rays': preserved, 'preserved_views': views, 'preserved_routes': routes,
            'retained_native_mesh_instances': len(native_parts), 'retained_native_triangles': sum(len(r['triangles']) for r in native_parts),
            'method': 'Actual reopened float32 candidate against hash-pinned native optical triangles; verified source decomposition replaces only architecture batch containers for solid-inside contact tests.'}


def write_new(path, value):
    require(path.resolve().is_relative_to((CANDIDATE / 'qa').resolve()), 'QA output escaped candidate')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def run(args, output):
    global np
    for path, expected in FROZEN.items():
        require(sha(path) == expected, 'Frozen approval input changed: ' + str(path))
        PINNED[str(path)] = expected
    pins = read_json(ROOT / 'INPUT_PINS.json')
    require(pins['inputs_unchanged_at_finish'], 'Proposal pins were not stable')
    for path, expected in pins['sha256'].items():
        require(sha(path) == expected, 'Retained proposal input changed: ' + path)
        PINNED[path] = expected
    proposal = read_json(ROOT / 'PROPOSED_FIXTURE_LAYER.json')
    baseline = read_json(ROOT / 'GEOMETRY_CHECKS.json')
    require(proposal['status'] == 'PROPOSAL_SOURCE_NUMERICAL_PASS' and baseline['status'] == 'PASS' and not baseline['issues'], 'Proposal numerical gate')
    require(len(proposal['proposed_parts']) == 12 and len(proposal['fixtures']) == 3, 'Approved candidate scope')
    require(proposal['preserved'] == {'original_source_fixtures': 39, 'architectural_parts': 451, 'architectural_plants': 12,
                                     'original_programme_furnishings': 126, 'active_source_budget': 8}, 'Preservation contract changed')
    source_hash = sha(SOURCE)
    PINNED[str(SOURCE)] = source_hash
    if args.expected_source_sha256:
        require(source_hash == args.expected_source_sha256, 'Parent-pinned candidate source hash mismatch')
    build = read_json(CANDIDATE / 'qa/BUILD_RECEIPT.json')
    require(build['source_sha256'] == source_hash and build['proposal_sha256'] == FROZEN[ROOT / 'PROPOSED_FIXTURE_LAYER.json'], 'Build receipt source identity mismatch')
    require(Path(build['source_path']).resolve() == SOURCE.resolve(), 'Build receipt source path mismatch')
    for path, expected in build['protected_input_sha256'].items():
        require(sha(path) == expected, 'Protected retained/proposal evidence changed: ' + path)
        if path in PINNED:
            require(PINNED[path] == expected, 'Protected build pin conflicts with independently frozen input')
        PINNED[path] = expected
    REPORT.update({'source_path': str(SOURCE), 'source_sha256': source_hash, 'proposal_sha256': FROZEN[ROOT / 'PROPOSED_FIXTURE_LAYER.json'],
                   'preserved': proposal['preserved']})
    if args.stage == 'snapshot':
        # The saved source is read by Blender's Python 3.13, using the installed
        # cp313 NumPy only. No cp312 packages and no Shapely enter this process.
        import bpy
        require(sys.version_info[:2] == (3, 13), 'Snapshot stage requires the verified Blender Python 3.13')
        require('/workspace/scratch/375c2e438292/geometry-deps' not in sys.path, 'Incompatible cp312 dependency path present')
        sys.path.insert(0, '/usr/lib/python3/dist-packages')
        import numpy as np
        require(Path(np.__file__).resolve().is_relative_to(Path('/usr/lib/python3/dist-packages/numpy')), 'Unexpected snapshot NumPy path')
        REPORT.update({'blender_version': bpy.app.version_string, 'snapshot_numpy_version': np.__version__, 'snapshot_numpy_path': np.__file__})
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
        require(Path(bpy.data.filepath).resolve() == SOURCE.resolve(), 'Wrong reopened source')
        meshes, markers, candidate_materials = inspect_candidate(bpy, proposal, None)
        source_evidence = {'source_sha256': source_hash, 'coordinate_frame': 'Godot/glTF XYZ metres', 'meshes': meshes, 'markers': markers}
        write_new(output / 'ACTUAL_REOPENED_SOURCE.json', source_evidence)
        # Open the retained blend separately. This reads its actual graph and packed bytes,
        # and avoids trusting any material hashes or names in the builder's receipt.
        bpy.ops.wm.open_mainfile(filepath=str(EXEMPLAR_SOURCE), load_ui=False, use_scripts=False)
        expected_materials, comparisons = {}, []
        for role, name in EXEMPLARS.items():
            ob = bpy.data.objects.get(name)
            require(ob is not None and ob.type == 'MESH' and len(ob.data.materials) == 1, 'Retained exemplar missing: ' + name)
            expected = material_signature(ob.data.materials[0])
            expected_materials[role] = {'exemplar': name, 'material': ob.data.materials[0].name, 'sha256': digest(expected), 'signature': expected}
            for actual in candidate_materials[role]:
                equal = actual['signature'] == expected
                check(equal, 'retained_material_graph_and_packed_image_equivalence', object=actual['object'], role=role,
                      actual_sha256=actual['sha256'], expected_sha256=digest(expected))
                comparisons.append({'object': actual['object'], 'role': role, 'exemplar': name, 'actual_sha256': actual['sha256'],
                                    'expected_sha256': digest(expected), 'equivalent': equal})
        write_new(output / 'MATERIAL_COMPARISON.json', {'candidate': candidate_materials, 'retained': expected_materials, 'comparisons': comparisons})
        REPORT.update({'mesh_count': len(meshes), 'marker_count': len(markers), 'material_comparisons': comparisons,
                       'maximum_unsnapped_vertex_error_m': max(r['max_proposal_error_m'] for r in meshes),
                       'maximum_float32_uv_error': max(r['max_uv_error'] for r in meshes)})
        return

    require(sys.version_info[:2] == (3, 12), 'Geometry stage requires the verified host Python 3.12 ABI')
    snapshot_dir = CANDIDATE / 'qa' / args.snapshot_run_id
    snapshot_receipt_path = snapshot_dir / 'REOPEN_RECEIPT.json'
    snapshot_receipt = read_json(snapshot_receipt_path)
    require(snapshot_receipt['status'] == 'PASS_SNAPSHOT_ONLY' and not snapshot_receipt['issues'], 'Snapshot stage did not pass')
    require(snapshot_receipt['source_sha256'] == source_hash and snapshot_receipt['inputs_unchanged_at_finish'], 'Snapshot/source binding or stability failed')
    require(snapshot_receipt['script_sha256'] == sha(Path(__file__)), 'Snapshot used a different verifier revision')
    for filename, expected in snapshot_receipt['evidence_sha256'].items():
        path = snapshot_dir / filename
        require(path.resolve().parent == snapshot_dir.resolve() and sha(path) == expected, 'Snapshot evidence hash mismatch')
        PINNED[str(path)] = expected
    for path, expected in snapshot_receipt['input_sha256'].items():
        require(sha(path) == expected, 'Input changed since actual source snapshot: ' + path)
        if path in PINNED:
            require(PINNED[path] == expected, 'Snapshot input pin conflicts with current verified input')
        PINNED[path] = expected
    require({'ACTUAL_REOPENED_SOURCE.json', 'MATERIAL_COMPARISON.json'} <= set(snapshot_receipt['evidence_sha256']), 'Missing actual snapshot artifacts')
    saved = read_json(snapshot_dir / 'ACTUAL_REOPENED_SOURCE.json')
    require(saved['source_sha256'] == source_hash, 'Actual snapshot source identity mismatch')
    meshes, markers = saved['meshes'], saved['markers']
    comparisons = read_json(snapshot_dir / 'MATERIAL_COMPARISON.json')['comparisons']
    require(len(comparisons) == 12 and all(row['equivalent'] for row in comparisons), 'Actual saved material comparisons failed')
    REPORT.update({'blender_version': snapshot_receipt['blender_version'], 'snapshot_receipt': str(snapshot_receipt_path),
                   'snapshot_receipt_sha256': sha(snapshot_receipt_path), 'snapshot_evidence_sha256': snapshot_receipt['evidence_sha256']})
    helpers = geometry_helpers()
    REPORT.update({'geometry_python_version': sys.version, 'geometry_numpy_version': np.__version__, 'geometry_numpy_path': np.__file__})
    geometry = geometry_checks(meshes, markers, proposal, baseline, helpers)
    write_new(output / 'REOPEN_GEOMETRY_CHECKS.json', geometry)
    REPORT.update({'mesh_count': len(meshes), 'marker_count': len(markers), 'material_comparisons': comparisons,
                   'maximum_unsnapped_vertex_error_m': max(r['max_proposal_error_m'] for r in meshes),
                   'maximum_float32_uv_error': max(r['max_uv_error'] for r in meshes),
                   'actual_joint_count': len(geometry['new_mechanical_joints']),
                   'receiver_fan_sample_count': sum(len(r['receiver_samples']) for r in geometry['actual_receiver_fans']),
                   'preserved_fixture_ray_count': len(geometry['preserved_fixture_rays']),
                   'preserved_view_count': len(geometry['preserved_views']), 'preserved_route_count': len(geometry['preserved_routes'])})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-source-sha256', help='Optional independent parent pin of the newly saved source')
    parser.add_argument('--stage', choices=['snapshot', 'geometry'], required=True)
    parser.add_argument('--run-id', help='Unused, alphanumeric QA subdirectory; existing evidence is never replaced')
    parser.add_argument('--snapshot-run-id', default='reopen002_snapshot', help='Passed source snapshot directory for geometry stage')
    tail = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = parser.parse_args(tail)
    require(Path(__file__).resolve() == CANDIDATE / 'reopen_feature_lighting002.py', 'Unexpected QA script location')
    args.run_id = args.run_id or ('reopen002_snapshot' if args.stage == 'snapshot' else 'reopen002_geometry')
    require(all(value and all(c.isalnum() or c in '_-' for c in value) for value in (args.run_id, args.snapshot_run_id)), 'Invalid QA run directory')
    require(args.stage != 'geometry' or args.run_id != args.snapshot_run_id, 'Geometry output must not replace snapshot evidence')
    output = CANDIDATE / 'qa' / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    REPORT.update({'schema': 2, 'stage': args.stage, 'source_only': True, 'status': 'RUNNING', 'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'script_sha256': sha(Path(__file__)), 'contact_tolerance_m': TOL,
                   'native_acceptance': 'NOT_RUN', 'export_created': False, 'render_performed': False,
                   'future_derivative_policy': {'force_disable_compression': True, 'raw_render_arrays_required': True,
                                                'independently_predicted_native_snapped_collision_contacts_required': True},
                   'limitations': [
                       'No candidate export exists or is tested here. Blender float32 equivalence is not native import equivalence.',
                       'No Godot, renderer, active-eight selection, energy/illuminance, reflection, performance or live A/B test is run.',
                       'Retained optical inputs are source-verified pool GLB triangles, not a newly compiled whole-ship physics world.',
                       'Clear receiver fans apply only to the currently installed sparse planting. Uninstalled fuller-middle crowns require a separate combined-adoption first-hit gate, especially for secondary timber rays.',
                       'Retained general-solid contact predicates use surface SAT and strict interior witnesses; full-area backplate support is separately measured.',
                       'Receiver fans and continuous 60 mm exits are geometric checks; source trial energy/range remain unaccepted until actual native A/B.',
                   ]})
    try:
        run(args, output)
    except Exception as exc:
        ISSUES.append({'category': 'qa_exception', 'message': str(exc), 'traceback': traceback.format_exc()})
    changed = []
    for path, expected in PINNED.items():
        try:
            if sha(path) != expected:
                changed.append(path)
        except OSError:
            changed.append(path)
    if changed:
        ISSUES.append({'category': 'input_changed_during_reopen', 'paths': changed})
    REPORT.update({'status': ('PASS_SNAPSHOT_ONLY' if args.stage == 'snapshot' else 'PASS_SOURCE_ONLY') if not ISSUES else 'FAIL', 'issues': ISSUES,
                   'inputs_unchanged_at_finish': not changed, 'input_sha256': PINNED,
                   'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    REPORT['evidence_sha256'] = {p.name: sha(p) for p in output.glob('*.json')}
    write_new(output / 'REOPEN_RECEIPT.json', REPORT)
    print(json.dumps({'status': REPORT['status'], 'receipt': str(output / 'REOPEN_RECEIPT.json'),
                      'source_sha256': REPORT.get('source_sha256'), 'issue_count': len(ISSUES)}, indent=2), flush=True)
    if ISSUES:
        raise RuntimeError('Independent feature-lighting source reopen QA failed; see preserved receipt')


if __name__ == '__main__':
    main()
