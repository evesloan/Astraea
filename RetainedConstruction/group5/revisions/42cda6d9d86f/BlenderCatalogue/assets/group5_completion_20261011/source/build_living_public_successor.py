"""Public r002:clear preserved canopy with120mm leaf-plane pitch and105mm mounts."""
from pathlib import Path
import bpy,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=P/'docs/LIVING_GIFTS_DOOR_COMPONENTS.json';j=json.loads(definition.read_text());row=next(r for r in j['variants'] if r['kind']=='public')
old=ROOT/row['native'];oldsha=hashlib.sha256(old.read_bytes()).hexdigest();assert oldsha==row['native_sha256']
native=P/'source/living_gifts_doors/living_public_r002.blend';export=P/'exports/living_gifts_doors/living_public_r002.glb';assert not native.exists() and not export.exists()
bpy.ops.wm.open_mainfile(filepath=str(old))
for label in ['L1','R1']:
    o=bpy.data.objects['Panel_'+label];o.location.y+=.06;o['collision_depth']=-.12
for o in bpy.context.scene.objects:
    if not o.name.startswith('track_wall_mount_'):continue
    for v in o.data.vertices:
        # Source Blender-Y is negative runtime Z.
        if v.co.y<-.304:v.co.y=-.105
bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-living-public-r002-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==esha and sha(native)==nsha and sha(old)==oldsha
target=ROOT/'Game/assets/models/group5/living_gifts_doors'/export.name;assert not target.exists();shutil.copyfile(export,target)
row.update({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/living_gifts_doors/'+export.name,'model_sha256':esha,'public_depth_pitch_m':.12,'mount_reach_m':.105,'selected_successor':{'parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':oldsha,'reason':'Actual retained canopy contacts at deeper candidate planes;47.6m public plane clears it.Retain aperture andoriginal flora;120mm pitch prevents source handles entering adjacent panes'}})
definition.write_text(json.dumps(j,indent=2)+'\n');print('LIVING_PUBLIC_SUCCESSOR_PASS',esha)
