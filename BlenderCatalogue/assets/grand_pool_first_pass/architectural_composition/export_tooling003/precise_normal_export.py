"""Process-local glTF normal precision correction, never a keeper relaxation.

Official Blender 4.3.2's primitive extractor rounds loop normals to four decimal
places before normalizing. Preserve eight decimal places in that export stage,
then restore the module immediately. No installed add-on or preference writes.
"""
import sys
sys.dont_write_bytecode=True
import importlib,hashlib
from pathlib import Path
from contextlib import contextmanager
@contextmanager
def precise_normals():
    module=importlib.import_module('io_scene_gltf2.blender.exp.primitive_extract');path=Path(module.__file__).resolve();record=json_record();assert str(path)==record['primitive_extractor_path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==record['primitive_extractor_sha256'],'Unreviewed exporter implementation';original=module.ROUNDING_DIGIT;assert original==4,'Unexpected baseline normal quantization'
    module.ROUNDING_DIGIT=8
    try:yield dict(exporter_file=str(path),exporter_sha256=record['primitive_extractor_sha256'],normal_rounding_decimal_digits=8,original_decimal_digits=original,scope='Temporary in this export process only; restored in finally; no source/checker/persistent setting edits')
    finally:module.ROUNDING_DIGIT=original
def json_record():
    import json
    return json.loads((Path(__file__).resolve().parent/'NORMAL_PRECISION_FIX_INPUTS.json').read_text())
