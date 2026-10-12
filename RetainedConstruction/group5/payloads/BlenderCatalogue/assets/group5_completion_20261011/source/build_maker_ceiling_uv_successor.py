"""Retain r001;correct only eight wood-cove UVs to the actual shared metre-tile contract."""
from pathlib import Path
import bpy,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=P/'docs/MAKER_CEILING_ENCLOSURE.json';j=json.loads(definition.read_text());old=ROOT/j['native'];oldsha=hashlib.sha256(old.read_bytes()).hexdigest();assert oldsha==j['native_sha256'] and old.name.endswith('_r001.blend')
native=P/'source/maker_foyer/maker_ceiling_enclosure_r002.blend';export=P/'exports/maker_foyer/maker_ceiling_enclosure_r002.glb';assert not native.exists() and not export.exists()
bpy.ops.wm.open_mainfile(filepath=str(old));selected=[];values=0
contract=json.loads((ROOT/'BlenderCatalogue/materials/material_manifest.json').read_text())['materials']['warm_walnut']['meters_per_tile_uv'];assert contract==[.65,1.3]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith('MakerMiteredCove_'):continue
    assert o.data.materials[0].get('astraea_material_role')=='warm_walnut';selected.append(o.name)
    for uv in o.data.uv_layers.active.data:uv.uv=(uv.uv.x/contract[0],uv.uv.y/contract[1]);values+=1
assert len(selected)==8
bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-maker-ceiling-r002-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==esha and sha(native)==nsha and sha(old)==oldsha
target=ROOT/'Game/assets/models/group5/maker_foyer'/export.name;assert not target.exists();shutil.copyfile(export,target)
j.update({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/maker_foyer/'+export.name,'model_sha256':esha,'selected_uv_successor':{'parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':oldsha,'parent_export':'BlenderCatalogue/assets/group5_completion_20261011/exports/maker_foyer/maker_ceiling_enclosure_r001.glb','changed_wood_coves':selected,'source_uv_loops_scaled':values,'actual_metres_per_tile_uv':contract,'geometry_pose_material_changes':0,'reason':'Custom cove mesh UVs originally used1m tiles;actual shared warm-walnut contract is650mm/1300mm'}})
definition.write_text(json.dumps(j,indent=2)+'\n');print('MAKER_CEILING_UV_SOURCE_PASS',values,esha)
