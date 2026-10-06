"""Fresh-process exact saved-source verification, read-only source."""
import sys, json, gzip, hashlib, importlib.util
from pathlib import Path
import bpy
sys.dont_write_bytecode = True
S = Path(__file__).resolve().parent
P = S.parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    receipt = json.loads((S/'qa/BUILD_RECEIPT.json').read_text())
    pins = json.loads((S/'JOB_PINS.json').read_text())
    assert sha(S/'JOB_PINS.json') == receipt['job_pins_sha256']
    for path, digest in pins['sha256'].items():
        assert sha(path) == digest, path
    source = Path(receipt['source'])
    assert sha(source) == receipt['source_sha256']
    assert sha(S/'qa/BUILD_EVALUATED_CORE.json') == receipt['core_snapshot_sha256']
    assert sha(S/'qa/BUILD_EVALUATED_PROGRAMME.json.gz') == receipt['programme_snapshot_sha256']
    built_core = json.loads((S/'qa/BUILD_EVALUATED_CORE.json').read_text())
    with gzip.open(S/'qa/BUILD_EVALUATED_PROGRAMME.json.gz', 'rt') as handle:
        built_programme = json.load(handle)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.context.view_layer.update()
    plan = json.loads((P/'source_blockin001/CORE_PLAN.json').read_text())
    verifier = module('combined_core_reopen', P/'source_blockin001/reopen_core.py')
    core, exact, prediction = verifier.verify_core_subset(bpy.context.scene, plan, built_core, receipt['material_provenance'])
    programme = module('combined_programme_reopen', P/'reference_programme001/append_retained_programme.py')
    actual_programme = programme.snapshot_retained_programme()
    assert actual_programme == built_programme, 'Saved/reopened retained programme geometry, UV, material, properties or frames differ'
    inventory = sorted([o.name, o.type, o.parent.name if o.parent else None] for o in bpy.context.scene.objects)
    assert inventory == receipt['object_inventory'], 'Unexpected or missing scene object'
    assert sha(source) == receipt['source_sha256']
    for path, digest in pins['sha256'].items():
        assert sha(path) == digest, path
    output = S/'qa/INDEPENDENT_REOPEN.json'
    assert not output.exists()
    output.write_text(json.dumps({
        'status': 'PASS_EXACT_COMPOSED_SOURCE_REOPEN',
        'source_sha256': sha(source), 'source_unchanged': True,
        'core_exact_saved_checks': exact, 'core_exact_float32_prediction': prediction,
        'retained_programme_exact': True, 'retained_programme_objects': len(actual_programme['objects']),
        'scene_object_inventory_exact': True,
        'pending': ['Actual evaluated programme fitting gate', 'Composed source pixels', 'Independent retention/export', 'Native adoption and local lighting']
    }, indent=2) + '\n')
    print('PASS_EXACT_COMPOSED_SOURCE_REOPEN', len(inventory), flush=True)

if __name__ == '__main__':
    main()
