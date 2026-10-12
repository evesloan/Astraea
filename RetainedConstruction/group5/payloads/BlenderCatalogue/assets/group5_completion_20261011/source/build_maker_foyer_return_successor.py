"""Two foyer sources onto inward return walls;original r001 and venue immutable."""
from pathlib import Path
import bpy,json,hashlib,shutil,math
from mathutils import Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=P/'docs/MAKER_FOYER_SOURCES.json';j=json.loads(definition.read_text())
old=ROOT/j['native'];old_sha=hashlib.sha256(old.read_bytes()).hexdigest();assert old_sha==j['native_sha256']
native=P/'source/maker_foyer/maker_foyer_returns_r002.blend';export=P/'exports/maker_foyer/maker_foyer_returns_r002.glb'
assert not native.exists() and not export.exists(),'Saved revisions immutable'
bpy.ops.wm.open_mainfile(filepath=str(old));bpy.context.view_layer.update()
for z in [-7,7]:
    sign=1 if z>0 else -1;angle=-sign*math.pi/2
    transform=Matrix.Translation((-4.5,-sign*3.98,3.245))@Matrix.Rotation(angle,4,'Z')@Matrix.Translation((2.75,z,-3.245))
    for o in bpy.context.scene.objects:
        if o.name.startswith('MakerFoyer_'+str(z)+'_'):o.matrix_world=transform@o.matrix_world
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-maker-foyer-returns-r002-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True)
assert sha(repeat)==esha and sha(native)==nsha and sha(old)==old_sha
target=ROOT/'Game/assets/models/group5/maker_foyer'/export.name;assert not target.exists();shutil.copyfile(export,target)
j.update({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/maker_foyer/'+export.name,'model_sha256':esha,'origin_world_xyz':[-54,52.5,0],'selected_return_revision':{'parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':old_sha,'six_rigid_fixture_members':True,'reason':'Public foyer sources mount to actual inward threshold returns at Z+/-4.25 rather than shine from beyond those retained walls','fixture_source_indices':[-7,7],'actual_source_centers_world_xz':[[-58.5,-3.98],[-58.5,3.98]]}})
definition.write_text(json.dumps(j,indent=2)+'\n');print('MAKER_RETURN_SOURCE_PASS',esha)
