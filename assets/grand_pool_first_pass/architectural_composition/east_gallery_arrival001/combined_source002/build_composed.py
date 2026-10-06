"""Build one complete editable east-gallery source in a new scratch folder.
No exports, renders, Game/Catalogue writes or external processes.
"""
import sys, json, hashlib, gzip, importlib.util
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

def json_new(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')

def main():
    pins = json.loads((S/'JOB_PINS.json').read_text())
    for path, digest in pins['sha256'].items():
        assert sha(path) == digest, path
    assert not (S/'source').exists() and not (S/'qa/BUILD_RECEIPT.json').exists()
    core = module('combined_core_builder', P/'source_blockin001/build_core.py')
    programme = module('combined_programme_builder', P/'reference_programme001/append_retained_programme.py')
    plan, materials = core.build_core()
    programme_receipt = programme.append_retained_programme(P/'source_blockin001/CORE_PLAN.json')
    bpy.context.view_layer.update()
    core_snapshot = dict(plan, parts=core.snapshot(bpy.context.scene, plan))
    programme_snapshot = programme.snapshot_retained_programme()
    assert not [o for o in bpy.context.scene.objects if o.type not in {'MESH', 'EMPTY'}]
    inventory = sorted((o.name, o.type, o.parent.name if o.parent else None) for o in bpy.context.scene.objects)
    assert len(inventory) == len(set(x[0] for x in inventory))
    bpy.context.scene['status'] = 'Complete editable source candidate; source reopen, physical fitting and visual review pending'
    (S/'source').mkdir()
    (S/'qa').mkdir(exist_ok=True)
    path = S/'source/AST-AQU-016_east_gallery_composed.blend'
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    json_new(S/'qa/BUILD_EVALUATED_CORE.json', core_snapshot)
    with gzip.open(S/'qa/BUILD_EVALUATED_PROGRAMME.json.gz', 'xt') as handle:
        json.dump(programme_snapshot, handle, sort_keys=True, separators=(',', ':'), allow_nan=False)
    receipt = {
        'status': 'COMPOSED_SOURCE_SAVED_PENDING_INDEPENDENT_REOPEN',
        'source': str(path), 'source_sha256': sha(path),
        'core_plan_sha256': sha(P/'source_blockin001/CORE_PLAN.json'),
        'core_snapshot_sha256': sha(S/'qa/BUILD_EVALUATED_CORE.json'),
        'programme_snapshot_sha256': sha(S/'qa/BUILD_EVALUATED_PROGRAMME.json.gz'),
        'material_provenance': materials, 'programme': programme_receipt,
        'object_inventory': inventory, 'job_pins_sha256': sha(S/'JOB_PINS.json'),
        'exports': [], 'renders': [], 'game_writes': [], 'catalogue_writes': []
    }
    for input_path, digest in pins['sha256'].items():
        assert sha(input_path) == digest, input_path
    json_new(S/'qa/BUILD_RECEIPT.json', receipt)
    print('COMPOSED_SOURCE_SAVED', str(path), sha(path), flush=True)

if __name__ == '__main__':
    main()
