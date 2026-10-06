"""Independent pure-Python actual accessor/material/corner equivalence.
No bpy, authoring contracts, source regeneration, engine process or native import.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'vendor'))
import argparse, json, traceback
import numpy as np
from gate import gate, sha, read, require, run_path, write_new, INPUTS
from check_glb import decode, concat, material_check, compare_matrix
from provenance_match import match_with_provenance

def verify_asset(a, s, er, out):
    path = Path(er['export']); require(sha(path) == er['export_sha256'], 'GLB pin changed')
    require(er['source_sha256'] == s['source_sha256'] == a['source_sha256'], 'Source pin mismatch')
    require(s['source_bytes_unchanged'] and s['inputs_sha256'] == sha(INPUTS), 'Invalid snapshot gate')
    d = decode(path); nodes = d['nodes']; objects = {o['name']: o for o in s['objects']}
    meshes = {n: o for n, o in objects.items() if o['type'] == 'MESH'}
    empties = {n: o for n, o in objects.items() if o['type'] == 'EMPTY'}
    require(set(meshes) == set(a['mesh_parts']) and set(empties) == set(a['empty_objects']), 'Snapshot inventory mismatch')
    require(sum(o['triangles'] for o in meshes.values()) == a['triangles'], 'Snapshot triangle inventory mismatch')
    require(set(d['doc'].get('extensionsUsed', [])) <= {'KHR_materials_emissive_strength'}, 'Unverified GLB extension')
    # Recompute batch membership from actual saved-source material/collision/
    # shadow/parent/UV semantics, independently of exporter batch receipts.
    groups = {}
    for name, o in sorted(meshes.items()):
        e = o['extras']; key = (o['material'], e.get('material_role'), e.get('collision_contract'), e.get('collision'), e.get('cast_shadow', True), o['parent'], o['uv_layer'])
        require(np.array_equal(o['world_matrix_godot'], np.eye(4)), 'Source batch requires identity transform')
        groups.setdefault(key, []).append(name)
    expected_names = set(empties); reports = []; triangle_map = []; seen_materials = set(); material_reports = []
    require(len(er['batches']) == len(groups), 'Batch receipt count mismatch')
    if a['family'] == 'plant': require(len(groups) == 5, 'Plant was not batched to five material meshes')
    for index, (key, names) in enumerate(sorted(groups.items(), key=lambda x: json.dumps(x[0]))):
        name = a['name'] + '__batch_%02d' % index; expected_names.add(name)
        require(name in nodes, 'Missing GLB batch ' + name); node = nodes[name]
        require(node['mesh'] is not None and np.array_equal(node['matrix'], np.eye(4)), 'Batch mesh/transform mismatch')
        require(node['parent'] == key[5], 'Batch parent changed')
        e = node['extras']; require(json.loads(e['source_part_names']) == names, 'Actual GLB part membership changed')
        provenance = {n: {k: meshes[n][k] for k in ['extras', 'parent', 'material', 'uv_layer', 'triangles', 'world_matrix_godot']} for n in names}
        require(json.loads(e['source_part_provenance_json']) == provenance, 'Support/semantic source properties lost')
        require(json.loads(e['source_scene_properties_json']) == s['scene_extras'], 'Scene provenance lost')
        require(e['source_blend_sha256'] == a['source_sha256'] and e['source_snapshot_sha256'] == er['snapshot_sha256'], 'Embedded provenance pin mismatch')
        require(e['parent_design_id'] == a['parent_design_id'] and e['unique_catalogue_design'] is False, 'Lineage/design count changed')
        require(e.get('material_role') == key[1] and e.get('collision_contract') == key[2] and e.get('collision') == key[3] and e.get('cast_shadow') == key[4], 'Runtime collision/material/shadow semantics changed')
        rr = next(b for b in er['batches'] if b['name'] == name)
        require(rr['source_parts'] == names and rr['material'] == key[0] and rr['triangles'] == sum(meshes[n]['triangles'] for n in names), 'Receipt differs from actual source')
        mi = {p['material'] for p in node['primitives']}; require(len(mi) == 1, 'Mixed runtime material primitive'); mi = next(iter(mi))
        require(d['doc']['materials'][mi]['name'] == key[0], 'Wrong material assigned to source batch')
        if mi not in seen_materials:
            material_reports.append(material_check(s['materials'][key[0]], mi, d)); seen_materials.add(mi)
        expected = concat([meshes[n] for n in names]); actual = concat(node['primitives'])
        result = match_with_provenance(expected, actual, check_local=True)
        source_indices = [(n, ti) for n in names for ti in range(meshes[n]['triangles'])]
        actual_indices = [(p['primitive'], ti) for p in node['primitives'] for ti in range(p['triangles'])]
        part_counts = {n: 0 for n in names}
        for match in result.pop('triangle_correspondence'):
            part, ti = source_indices[match['source_triangle']]; primitive, export_ti = actual_indices[match['export_triangle']]
            part_counts[part] += 1
            triangle_map.append(dict(node=name, primitive=primitive, export_triangle=export_ti, source_part=part,
                source_triangle=ti, source_polygon=meshes[part]['triangle_provenance'][ti]['polygon'],
                source_vertices=meshes[part]['triangle_provenance'][ti]['vertices'], source_loops=meshes[part]['triangle_provenance'][ti]['loops'], corner_cyclic_shift=match['corner_cyclic_shift']))
        require(part_counts == {n: meshes[n]['triangles'] for n in names}, 'Source-part triangle provenance incomplete')
        reports.append(dict(node=name, source_parts=names, material=key[0], per_part_triangles=part_counts, **result))
    marker_reports = []; part_to_node = {n: r['node'] for r in reports for n in r['source_parts']}
    for name, o in empties.items():
        require(name in nodes, 'Missing source marker/root'); n = nodes[name]
        require(n['mesh'] is None and n['parent'] == o['parent'] and n['extras'] == o['extras'], 'Marker/root semantics or parent changed')
        deviation = compare_matrix(o, n)
        references = {}
        for key in ['physical_part', 'physical_housing', 'physical_lens']:
            if key in o['extras']:
                part = o['extras'][key]; require(part in part_to_node, 'Marker physical source part missing')
                references[key] = dict(source_part=part, runtime_batch=part_to_node[part])
        marker_reports.append(dict(name=name, max_matrix_deviation=deviation, physical_references=references))
    require(set(nodes) == expected_names, 'Extra/missing exported nodes')
    require(seen_materials == set(range(len(d['doc'].get('materials', [])))), 'Unexpected unused GLB materials')
    require({m['name'] for m in d['doc']['materials']} == set(s['materials']), 'Source material names changed')
    used_images = {image['image_index'] for r in material_reports for image in r['images']}
    require(used_images == set(range(len(d['images']))), 'Unreferenced or unchecked packed export image')
    require(len(triangle_map) == a['triangles'], 'Total exact provenance count mismatch')
    pp = out / (a['name'] + '_TRIANGLE_PROVENANCE.json')
    write_new(pp, dict(source_sha256=a['source_sha256'], export_sha256=er['export_sha256'], snapshot_sha256=er['snapshot_sha256'], triangles=triangle_map))
    return dict(asset=a['name'], status='PASS_ACTUAL_SOURCE_GLB_EQUIVALENCE', source_sha256=a['source_sha256'],
        export_sha256=er['export_sha256'], source_meshes=len(meshes), exported_mesh_batches=len(groups), source_empty_objects=len(empties),
        triangles=len(triangle_map), batches=reports, materials=material_reports, markers_and_roots=marker_reports, triangle_provenance=str(pp), triangle_provenance_sha256=sha(pp),
        full_source_semantic_metadata_preserved=True, source_material_graphs_and_packed_images_unchanged=True,
        native_raw_render_arrays='NOT_RUN', native_contact_and_snapped_collision='NOT_RUN', native_visual_AB='NOT_RUN')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run', required=True); args = ap.parse_args()
    g = gate(); out = run_path(args.run); destination = out / 'equivalence'
    require(not destination.exists(), 'Preserve prior verification outputs'); destination.mkdir()
    er = read(out / 'EXPORT_RECEIPT.json'); sr = read(out / 'SNAPSHOT_RECEIPT.json'); completed = []
    require(er['status'] == 'EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE' and er['inputs_sha256'] == sr['inputs_sha256'] == sha(INPUTS), 'Wrong export gate')
    require(sha(out / 'SNAPSHOT_RECEIPT.json') == er['snapshot_receipt_sha256'], 'Snapshot receipt changed')
    require(len(er['assets']) == len(sr['assets']) == 7, 'Incomplete stage receipts')
    try:
        for a in g['assets']:
            e = next(x for x in er['assets'] if x['asset'] == a['name']); r = next(x for x in sr['assets'] if x['asset'] == a['name'])
            require(sha(r['snapshot']) == r['snapshot_sha256'] == e['snapshot_sha256'], 'Source snapshot changed')
            completed.append(verify_asset(a, read(r['snapshot']), e, destination))
            print('PASS_ACTUAL_SOURCE_GLB_EQUIVALENCE', a['name'], flush=True)
        gate(); write_new(destination / 'GLB_EQUIVALENCE.json', dict(status='PASS_SEVEN_ACTUAL_SOURCE_GLB_EQUIVALENCE', assets=completed,
            inputs_sha256=sha(INPUTS), source_retention_sha256=g['retention_sha256'], source_retained_commit=g['retained_commit'],
            export_receipt_sha256=sha(out / 'EXPORT_RECEIPT.json'), source_triangles=sum(a['triangles'] for a in g['assets']),
            native_acceptance='NOT_RUN_SEPARATE_REQUIRED_GATE'))
    except Exception:
        write_new(destination / 'EQUIVALENCE_FAILURE.json', dict(status='FAILED_PRESERVE_ALL_OUTPUTS', completed=completed, traceback=traceback.format_exc())); raise
if __name__ == '__main__': main()
