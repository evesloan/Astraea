"""Create this owned batch's exact receipt only after all bounded checks pass."""
from pathlib import Path
import datetime, hashlib, json
HERE = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n')
plan = read(HERE / 'qa/BRIEFING_PLAN_CHECKS.json')
review = read(HERE / 'qa/BRIEFING_NATIVE_GEOMETRY.json')
cart = read(HERE / 'qa/BRIEFING_LOCAL_CART_PROXY_CHECKS.json')
compact = read(HERE / 'qa/COMPACT_RUNTIME_GEOMETRY.json')
repeat = read(HERE / 'qa/REPEAT_NATIVE_EXPORT.json')
visual = read(HERE / 'qa/SOURCE_VISUAL_REVIEW.json')
assert all(q['status'] == 'PASS' for q in [plan, review, cart, compact, repeat, visual])
receiver = read(HERE / 'source/BRIEFING_RECEIVER.json')
patch = read(HERE / 'source/CREW_STREET_BRIEFING_PATCH.json')
floor = read(HERE / 'source/BRIEFING_MISSING_SUPPORT_PROPOSAL.json')
support = read(HERE / 'qa/REVIEW_SUPPORT_AND_PATCH.json')
d = read(HERE / 'source/HANDOFF_TEMPLATE.json')
d['frozen_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
for q, spec in zip(d['assets'], [receiver, patch]):
    build = read(HERE / 'qa' / (q['asset'] + '_BUILD.json'))
    q['parts'] = len(spec['parts'])
    q['runtime_meshes'] = build['runtime_meshes']
    for key in ['source_spec', 'editable_source', 'runtime_export']:
        q[key + '_sha256'] = sha(HERE / q[key])
a = d['adoption']
a['actual_original_room_opening_preserved'] = receiver['actual_room_opening']
a['existing_room_root_preserved'] = receiver['preserved_original_root_name']
a['original_floor_owner_ids_preserved'] = receiver['preserved_floor_owner_ids']
a['existing_four_preparation_light_bindings_preserved'] = receiver['preserved_existing_preparation_light_bindings']
a['exact_native_frame_and_roof_bounds'] = receiver['existing_source_native_bounds']
a['existing_reserved_gate_pose'] = receiver['existing_gate_pose']
a['new_source_only_light_datum'] = receiver['fixtures'][0]
a['additional_missing_floor_m2'] = floor['new_missing_only_area_m2']
a['actual_floor_overlap_m2'] = floor['actual_compiled_overlap_m2']
a['prior_proposed_only_street_floor_overlap_m2'] = floor['frozen_first_street_proposed_overlap_only_m2']
a['native_first_street_meshes_to_omit'] = patch['native_mesh_batches_to_omit_only_during_root_adoption']
a['other_first_street_native_meshes_preserved'] = patch['preserved_other_native_meshes']
a['old_platform_briefing_branch_omitted_from_adoption'] = receiver['old_platform_briefing_branch_omitted_from_adoption']
q = d['qa']
q['material_height_cell_cross_sections'] = len(support['retained_street_cross_sections'])
q['derived_editable_component_bounds'] = len(review['derived_editable_component_bounds'])
q['stationary_native_capsules'] = len(review['capsule_stationary_witnesses'])
q['actual_native_contacts'] = len(review['actual_native_contacts'])
q['exact_rounded_roof_profile_points'] = len(review['exact_rounded_roof_profile_contacts'])
q['preserved_street_surface_points'] = len(review['preserved_street_surfaces'])
q['opening_points'] = len(review['bounded_opening_witnesses'])
q['supported_hanger_contacts'] = len(review['supported_hanger_ceiling_contacts'])
q['stationary_cart_contact_driver_poses'] = len(cart['bounded_cart_body_contact_driver_poses'])
q['minimum_cart_proxy_gap_m'] = min(c['proxy_gap_to_fixed_surfaces_m'] for c in cart['bounded_cart_body_contact_driver_poses'])
q['compact_runtime_triangles'] = compact['total_triangles']
q['runtime_mesh_batches'] = sum(c['runtime_meshes'] for c in compact['exports'])
q['native_repeat_exports_byte_identical'] = repeat['byte_identical']
q['source_views_reviewed'] = len(visual['views'])
d['dependency_manifest_sha256'] = sha(HERE / d['dependency_manifest'])
write(HERE / 'HANDOFF.json', d)
files = sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
assert all('__pycache__' not in p.parts and p.suffix != '.pyc' for p in files)
(HERE / 'SHA256SUMS.txt').write_text(''.join(sha(p) + '  ' + str(p.relative_to(HERE)) + '\n' for p in files))
files += [HERE / 'SHA256SUMS.txt']
size = sum(p.stat().st_size for p in files)
assert size <= 2_000_000, size
print(json.dumps({'status': 'FROZEN', 'files': len(files), 'bytes': size, 'manifest_sha256': sha(HERE / 'SHA256SUMS.txt'), 'handoff_sha256': sha(HERE / 'HANDOFF.json'), 'dependencies_sha256': sha(HERE / d['dependency_manifest'])}))
