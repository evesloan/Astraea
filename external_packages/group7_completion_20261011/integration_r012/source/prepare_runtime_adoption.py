"""Project only selected runtime assets for the sole Group1 integration owner.

No Group1 workspace is changed, no engine import/build occurs, and no inactive
native/export generation is projected into Game. The source remains uninstalled
until the owner applies a reviewed boundary and completes current-scene checks.
"""
from pathlib import Path
import json, hashlib, copy, difflib

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
GROUP7 = '455e381c3bf9b89e661651f9e5508065554c075e'
PARENT = '47eb8359caa5531e04122b6e56292f8c44d4281a'
data_file = R/'Game/data/architecture/GROUP7_COMPLETION.json'
data = json.loads(data_file.read_text())
assert (len(data['models']), len(data['lights']), len(data['doors'])) == (88, 39, 8)
receipt = json.loads((P/'qa/PREVIOUS_R010_REMOTE_VERIFICATION.json').read_text())
assert receipt['status'] == 'PASS' and receipt['commit'] == GROUP7
source_map = json.loads((P/'qa/group1_current/RetainedConstruction/group7/SOURCE_MAP.json').read_text())
stored = {row['source_path']: row for row in source_map['files']}
cells = {row['cell']: row for row in data['models']}
foundation = {name for name in cells if name.startswith('Prior_')}
envelope = {name for name in cells if not ('_Court_' in name or name.startswith('G7C6_') or name.startswith('G7C7_'))}
assert len(foundation) == 34 and len(envelope) == 69

def physical_cell(feature):
    name = feature['id']
    if name.startswith('G7C2_'):
        return 'Prior_G7C2_'+('Fore' if '_Fore_' in name else 'Aft')
    if name.startswith('G7C3_Fore_Lamp_'): return 'G7C3_Fore_Closure'
    if name.startswith('G7C3_Aft_Lamp_'): return 'G7C3_Aft_Closure'
    for prefix, suffix in [('G7C6_', '_ComposedEdge'), ('G7C7_', '_ForeGardenCourt')]:
        if name.startswith(prefix): return prefix+name.split('_')[1]+suffix
    matches = [cell for cell in cells if name.startswith(cell+'_')]
    assert len(matches) == 1, (name, matches)
    return matches[0]

feature_cells = {kind: {row['id']: physical_cell(row) for row in data[kind]}
                 for kind in ['lights', 'doors']}
for mapping in feature_cells.values(): assert set(mapping.values()) <= cells.keys()
out = P/'runtime_boundaries'; out.mkdir(exist_ok=True)
boundaries = {}
for name, selected in [('foundation', foundation), ('envelope', envelope), ('all_built', set(cells))]:
    projected = copy.deepcopy(data)
    projected['models'] = [row for row in data['models'] if row['cell'] in selected]
    for kind in ['lights', 'doors']:
        projected[kind] = [row for row in data[kind] if feature_cells[kind][row['id']] in selected]
    projected['integration_boundary'] = {'name': name, 'source_commit': GROUP7, 'parent_source_commit': PARENT,
        'installed': False, 'current_scene_checked': False, 'capacity_delta': 0,
        'primary_capacity_accepted': False, 'physical_source_feature_cells': feature_cells}
    file = out/(name+'.json'); file.write_text(json.dumps(projected, indent=2)+'\n')
    boundaries[name] = {'manifest': file.relative_to(P).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
        'models': len(projected['models']), 'lights': len(projected['lights']), 'doors': len(projected['doors']),
        'original_definition_poses_and_hashes_exact': True}
assert (boundaries['foundation']['lights'], boundaries['foundation']['doors']) == (4, 4)
assert (boundaries['envelope']['lights'], boundaries['envelope']['doors']) == (8, 4)

paths = {'Game/scripts/group7_completion.gd', 'Game/data/architecture/GROUP7_COMPLETION.json'}
uid = R/'Game/scripts/group7_completion.gd.uid'
if uid.exists(): paths.add(uid.relative_to(R).as_posix())
for row in data['models']:
    file = R/'Game/assets/models'/row['file']; assert file.is_file()
    assert hashlib.sha256(file.read_bytes()).hexdigest() == row['sha256']
    paths.add(file.relative_to(R).as_posix())
    if file.with_suffix('.glb.import').exists(): paths.add(file.with_suffix('.glb.import').relative_to(R).as_posix())
    for texture in file.parent.glob(file.stem+'_*.png'):
        paths.add(texture.relative_to(R).as_posix())
        if Path(str(texture)+'.import').exists(): paths.add(Path(str(texture)+'.import').relative_to(R).as_posix())
files = {}; reused = 0; fresh = 0
for name in sorted(paths):
    file = R/name; digest = hashlib.sha256(file.read_bytes()).hexdigest(); previous = stored.get(name)
    reuse = previous is not None and previous['sha256'] == digest
    if reuse: reused += 1
    else: fresh += 1
    files[name] = {'sha256': digest, 'bytes': file.stat().st_size,
                  'reuse_exact_retained_payload': reuse,
                  'current_parent_storage_path': previous.get('storage_path') if reuse else None,
                  'source_commit': GROUP7}

parent_file = P/'qa/group1_current/Game/scripts/ship.gd'; original = parent_file.read_text()
anchor = '\tlighting_budget.configure(self,player)\n'
assert original.count(anchor) == 1
addition = ('\t# Sole-owner Group7 boundary: selected JSON and exact runtime files must be admitted first.\n'
            '\tif OS.get_environment("ASTRAEA_GROUP7_ENABLE") == "1":\n'
            '\t\tload("res://scripts/group7_completion.gd").build(self)\n')
successor = original.replace(anchor, addition+anchor)
assert successor.replace(addition, '') == original
patch = ''.join(difflib.unified_diff(original.splitlines(True), successor.splitlines(True),
                  fromfile='a/Game/scripts/ship.gd', tofile='b/Game/scripts/ship.gd', n=4))
(P/'docs/GROUP1_BOOTSTRAP_47eb8359.patch').write_text(patch)
assert hashlib.sha256(parent_file.read_bytes()).hexdigest() == json.loads((P/'docs/GROUP1_CURRENT_RETAINED_SOURCE_PINS.json').read_text())['files']['Game/scripts/ship.gd']['sha256']
manifest = {'schema': 'astraea.group7.narrow_runtime_adoption.r012', 'source_commit': GROUP7,
            'source_tree': receipt['tree'], 'source_manifest_sha256': receipt['manifest_sha256'],
            'parent_frozen_source_commit': PARENT, 'retained_source_is_not_installed': True,
            'boundaries': boundaries, 'files': files, 'runtime_file_count': len(files),
            'runtime_bytes': sum(row['bytes'] for row in files.values()),
            'exact_parent_retained_payloads_reusable': reused, 'new_or_changed_runtime_payloads': fresh,
            'inactive_native_or_export_history_projected_to_Game': 0,
            'parent_bootstrap_patch': 'docs/GROUP1_BOOTSTRAP_47eb8359.patch',
            'parent_bootstrap_preimage_sha256': hashlib.sha256(parent_file.read_bytes()).hexdigest(),
            'parent_workspace_shared_refs_engine_imports_or_builds_changed': False,
            'whole_group_or_primary_capacity_accepted': False}
(P/'docs/RUNTIME_ADOPTION_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
proof = {'status': 'PASS_OFFLINE_PROJECTION_AND_EXACT_PARENT_PATCH',
         'boundaries': boundaries, 'all88_model_file_hashes_exact': True,
         'all39_source_and8_door_definitions_preserved_in_all_built': True,
         'each_projected_feature_has_its_physical_model': True,
         'source_original_data_unchanged': hashlib.sha256(data_file.read_bytes()).hexdigest(),
         'runtime_files': len(files), 'bytes': manifest['runtime_bytes'], 'reusable': reused, 'new_or_changed': fresh,
         'only_parent_bootstrap_addition': addition, 'parent_patch_applied': False,
         'no_engine_build_or_import': True, 'no_installed_work_claim': True}
(P/'qa/RUNTIME_PROJECTION_CHECK.json').write_text(json.dumps(proof, indent=2)+'\n')
print('G7_RUNTIME_ADOPTION', len(files), manifest['runtime_bytes'], 'bytes', reused, 'reusable', fresh, 'new/changed', boundaries)
