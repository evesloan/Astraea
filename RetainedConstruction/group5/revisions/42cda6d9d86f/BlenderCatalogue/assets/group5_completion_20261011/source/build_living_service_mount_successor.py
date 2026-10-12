"""Longer supports for the aft surface cassette;original stock screen/plinth immutable."""
from pathlib import Path
import bpy,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=P/'docs/LIVING_GIFTS_DOOR_COMPONENTS.json';j=json.loads(definition.read_text());row=next(r for r in j['variants'] if r['kind']=='service_left');old=ROOT/row['native'];oldsha=hashlib.sha256(old.read_bytes()).hexdigest();assert oldsha==row['native_sha256']
native=P/'source/living_gifts_doors/living_service_left_r002.blend';export=P/'exports/living_gifts_doors/living_service_left_r002.glb';assert not native.exists() and not export.exists()
bpy.ops.wm.open_mainfile(filepath=str(old))
for o in bpy.context.scene.objects:
    if o.name.startswith('track_wall_mount_'):
        for v in o.data.vertices:
            if v.co.y>.274:v.co.y=.535
bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-living-service-r002-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==esha and sha(native)==nsha and sha(old)==oldsha
target=ROOT/'Game/assets/models/group5/living_gifts_doors'/export.name;assert not target.exists();shutil.copyfile(export,target)
row.update({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/living_gifts_doors/'+export.name,'model_sha256':esha,'mount_reach_m':.535,'selected_successor':{'parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':oldsha,'reason':'Actual original back-wall plinth contacts at first candidate242.65m plane;242.90m aft surface clears it with all four120mm-spaced leaves.Frame interface remains Group6/integration held'}})
definition.write_text(json.dumps(j,indent=2)+'\n');print('LIVING_SERVICE_SUCCESSOR_PASS',esha)
