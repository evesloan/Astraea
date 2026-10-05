"""Rebuild only the upper-link derivative in isolated source staging and verify it.

Run with python3 from the catalogue workspace. The base source/export is never
rebuilt. Blender container hashes may differ across staging paths; geometry,
UVs and the complete exported GLB must match the delivered derivative.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
FAMILY = Path('assets/primary_atrium_core')
AID = 'AST-CIR-005_upper_link'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [Path('catalogue_manifest.json'),
          FAMILY/'source/build_primary_atrium_core.py',
          FAMILY/'source/upper_link_section_contract.json']
inputs += [Path('materials')/(role+'.png')
           for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal']]
verifier = FAMILY/'qa/verify_upper_link.py'
base = [FAMILY/'source/AST-CIR-005.blend', FAMILY/'exports/AST-CIR-005.glb']
protected = {str(p): sha(ROOT/p) for p in base+[FAMILY/'source'/(AID+'.blend'), FAMILY/'exports'/(AID+'.glb')]}
with tempfile.TemporaryDirectory(prefix='astraea-upper-link-source-only-') as directory:
    stage = Path(directory)
    for p in inputs:
        (stage/p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, stage/p)
    (stage/FAMILY/'exports').mkdir()
    # No derivative blend, GLB or base binary exists at generation time.
    command = ['blender','--background','--threads','4','--python',
               str(stage/FAMILY/'source/build_primary_atrium_core.py'),'--','--variant','upper_link']
    build = subprocess.run(command, check=True, capture_output=True, text=True)
    assert (stage/FAMILY/'exports'/(AID+'.glb')).read_bytes() == (ROOT/FAMILY/'exports'/(AID+'.glb')).read_bytes()
    # Validator-only base inputs establish unchanged historical masters; the
    # generator above has already completed without these files present.
    for p in base+[verifier]:
        (stage/p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, stage/p)
    check = subprocess.run(['blender','--background','--threads','4','--python',str(stage/verifier)],
                           check=True, capture_output=True, text=True)
    fresh = json.loads((stage/FAMILY/'qa/upper_link_validation.json').read_text())
    original = json.loads((ROOT/FAMILY/'qa/upper_link_validation.json').read_text())
    for field in ['editable_source_meshes','export_meshes','export_triangles','source_bounds_blender_xyz_m',
                  'import_bounds_blender_xyz_m','required_source_and_import_markers','guard_assemblies_measured',
                  'source_uv_area_per_square_metre_range','import_uv_area_per_square_metre_range']:
        assert fresh[field] == original[field], field
    assert fresh['passed']
    report = {'passed': True, 'representation': AID,
              'source_only_generation_inputs': [{'path':str(p),'sha256':sha(ROOT/p)} for p in inputs],
              'base_assets_available_during_generation': False,
              'derivative_blend_or_glb_available_during_generation': False,
              'rebuilt_glb_byte_identical': True,
              'export_sha256': sha(stage/FAMILY/'exports'/(AID+'.glb')),
              'delivered_source_sha256': sha(ROOT/FAMILY/'source'/(AID+'.blend')),
              'staged_source_sha256': sha(stage/FAMILY/'source'/(AID+'.blend')),
              'container_hash_note': 'Blender source container bytes may vary with staging paths. Fresh per-mesh source/export geometry, UV, material and marker checks establish representation equivalence.',
              'fresh_staged_source_export_validation': fresh,
              'base_and_delivered_source_export_hashes_unchanged': protected,
              'scope': 'Fresh isolated upper-link source-only reproduction and source/export validation; not runtime or independent visual approval'}
    assert protected == {p:sha(ROOT/p) for p in protected}
    (ROOT/FAMILY/'qa/upper_link_reproducibility.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['passed','rebuilt_glb_byte_identical','export_sha256']},indent=2))
