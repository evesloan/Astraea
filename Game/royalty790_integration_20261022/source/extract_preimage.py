from pathlib import Path
import bpy, hashlib, json
P=Path(__file__).resolve().parents[1]; R=P.parents[1]
pins=json.loads((P/'evidence/INPUT_PINS.json').read_text())
for path,digest in pins.items(): assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
out=P/'source/EXACT_FOUR_PREDECESSOR_MESHES.glb'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'))
bpy.ops.object.select_all(action='DESELECT')
names=['CR_RoyaltyLowerRoof','CR_LampHousing_CourtView','CR_LampLens_CourtView','CR_LampStem_CourtView']
for name in names: bpy.data.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
print('EXACT_PREIMAGE_EXTRACTED',names)
