"""Reproduce forward core and seventeen-stop cabin from source-only inputs.

The staging directory is local to this catalogue and is removed after the check.
Original or delivered binaries are never build inputs. No publisher is started.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
CORE = Path('assets/primary_atrium_core')
CABIN = Path('assets/commons_lift_cabin')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [Path('catalogue_manifest.json'), CORE/'source/build_forward_atrium_core.py',
          CORE/'source/forward_core_section_contract.json', CABIN/'source/build_seventeen_stop_cabin.py',
          Path('materials/material_manifest.json')]
inputs += [Path('materials')/(role+'.png') for role in ['ivory_enamel', 'warm_stone', 'warm_walnut',
           'champagne_metal', 'teal_weave', 'oatmeal_weave', 'clay_weave', 'botanical/botanical_soil']]
verifier = CORE/'qa/verify_forward_source_export.py'
inventory = CORE/'qa/forward_core_protected_hashes.json'
assets = [(CORE, 'AST-CIR-005_forward_core', 'forward_core_validation.json'),
          (CABIN, 'AST-CIR-003_seventeen_stop', 'seventeen_stop_validation.json')]
protected = {str(family/sub/(aid+suffix)): sha(ROOT/family/sub/(aid+suffix))
             for family, aid, _ in assets for sub, suffix in [('source', '.blend'), ('exports', '.glb')]}
with tempfile.TemporaryDirectory(prefix='.forward-source-only-', dir=ROOT) as directory:
    stage = Path(directory)
    for p in inputs:
        (stage/p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, stage/p)
    for family, aid, _ in assets:
        (stage/family/'exports').mkdir()
    builds = [(CORE/'source/build_forward_atrium_core.py', CORE, 'AST-CIR-005_forward_core'),
              (CABIN/'source/build_seventeen_stop_cabin.py', CABIN, 'AST-CIR-003_seventeen_stop')]
    for builder, family, aid in builds:
        assert not list(stage.rglob('*.blend')), 'Build must begin without delivered source containers'
        # Remove each fresh Blender file only after exporting and saving its bytes
        # outside the next generation tree. Restore it before source/export checks.
        subprocess.run(['blender', '--background', '--threads', '4', '--python-exit-code', '1',
                        '--python', str(stage/builder)], check=True, capture_output=True, text=True)
        assert (stage/family/'exports'/(aid+'.glb')).read_bytes() == (ROOT/family/'exports'/(aid+'.glb')).read_bytes()
        path = stage/family/'source'/(aid+'.blend')
        path.rename(path.with_suffix('.staged_source'))
    for family, aid, _ in assets:
        path = stage/family/'source'/(aid+'.staged_source')
        path.rename(path.with_suffix('.blend'))
    for p in [verifier, inventory]:
        (stage/p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, stage/p)
    subprocess.run(['blender', '--background', '--threads', '4', '--python-exit-code', '1',
                    '--python', str(stage/verifier), '--', '--protected-root', str(ROOT)],
                   check=True, capture_output=True, text=True)
    results = []
    for family, aid, receipt in assets:
        fresh = json.loads((stage/family/'qa'/receipt).read_text())
        original = json.loads((ROOT/family/'qa'/receipt).read_text())
        assert fresh['passed']
        for key in ['editable_source_meshes', 'export_meshes', 'export_triangles', 'material_roles',
                    'source_bounds_blender_xyz_m', 'export_bounds_blender_xyz_m',
                    'required_source_and_export_markers_blender_xyz_m',
                    'source_uv_area_per_square_metre_range_by_role',
                    'export_uv_area_per_square_metre_range_by_role']:
            assert fresh[key] == original[key], (aid, key)
        results.append({'representation': aid, 'rebuilt_glb_byte_identical': True,
                        'delivered_source_sha256': sha(ROOT/family/'source'/(aid+'.blend')),
                        'staged_source_sha256': sha(stage/family/'source'/(aid+'.blend')),
                        'export_sha256': sha(stage/family/'exports'/(aid+'.glb')),
                        'fresh_staged_source_export_validation': fresh})
    assert protected == {p: sha(ROOT/p) for p in protected}
    report = {'passed': True, 'source_only_generation_inputs': [
        {'path': str(p), 'sha256': sha(ROOT/p)} for p in inputs],
        'existing_blend_or_glb_used_as_build_input': False,
        'protected_originals_validation_location': 'Read-only original catalogue, after generation',
        'container_hash_note': 'Blender containers may vary by staging path; fresh source/export geometry and UV validation establishes equivalence.',
        'results': results, 'delivered_source_export_hashes_unchanged': protected,
        'scope': 'Fresh source-only reproducibility and exchange validation, not game integration or visual acceptance'}
    (ROOT/CORE/'qa/forward_derivatives_reproducibility.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': True, 'byte_identical_exports': [row['representation'] for row in results]}, indent=2))
