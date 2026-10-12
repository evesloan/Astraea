"""Restore editable geometry for the current maker model; not its lost original.

The archive predates the integrated entry correction. Preserve both originals,
and explicitly derive this new source counterpart from the hash-pinned current
runtime. Mesh text stays mesh text; original procedural/font authoring is held.
"""
from pathlib import Path
import bpy,json,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
row=next(r for r in json.loads((P/'qa/TEN_LARGE_VENUES.json').read_text())['venues'] if r['programme_key']=='D09_directory_05')
original=ROOT/row['current_runtime'];expected=row['current_runtime_sha256']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(original)==expected
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(original))
def points():
    return {o.name:sorted({tuple(round(float(c),5) for c in o.matrix_world@v.co) for v in o.data.vertices}) for o in bpy.context.scene.objects if o.type=='MESH'}
current_points=points()
for image in bpy.data.images:
    if image.source=='FILE' and image.has_data and not image.packed_file:image.pack()
native=P/'source/retained_venue_recovery/D09_directory_05/current_counterpart_r001.blend'
out=P/'exports/D09_directory_05_current_counterpart_r001.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
native_hash=h(native);export_hash=h(out)
bpy.ops.wm.open_mainfile(filepath=str(native))
assert points()==current_points
repeat=Path('/tmp/D09_directory_05_counterpart_repeat.glb')
bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
assert h(repeat)==export_hash and h(native)==native_hash
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out))
assert points()==current_points
assert h(original)==expected
r={'status':'PASS_EXPLICIT_DERIVED_EDITABLE_COUNTERPART','programme_key':'D09_directory_05','current_runtime':row['current_runtime'],'current_runtime_sha256':expected,'native':str(native.relative_to(P)),'native_sha256':native_hash,'export':str(out.relative_to(P)),'export_sha256':export_hash,'native_unchanged_after_read':True,'byte_identical_repeat_export':True,'current_and_derived_geometry_fingerprint':hashlib.sha256(json.dumps(current_points,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'geometry_quantization_m':.00001,'mesh_count':len(current_points),'original_current_runtime_unchanged':True,'origin':'Explicit new Blender4.3 editable counterpart derived from exact retained integrated entry-corrected GLB;earlier archive-native and current runtime remain immutable','held':'Original documented correction-native and its procedural/font authoring are not recovered. Mesh text and current geometry/materials are editable;not a substitute provenance claim,registry update or venue acceptance.'}
(P/'docs/CURRENT_MAKER_COUNTERPART.json').write_text(json.dumps(r,indent=2)+'\n');print('GROUP5_MAKER_COUNTERPART',r['status'],len(current_points))
