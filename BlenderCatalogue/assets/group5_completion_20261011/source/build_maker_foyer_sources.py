"""Two physically wall-mounted sources in the original Little Makers fore recess."""
from pathlib import Path
import ast,bpy,bmesh,json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
t=P/'source/build_components.py';tree=ast.parse(t.read_text());FACES=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FACES' for a in n.targets)))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(t),'exec'),globals())
native=P/'source/maker_foyer/maker_foyer_sources_r001.blend';export=P/'exports/maker_foyer/maker_foyer_sources_r001.glb'
assert not native.exists() and not export.exists(),'Saved revisions stay immutable'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);root=empty('GROUP5_MAKER_FOYER_SOURCES')
for z in [-7,7]:
    def block(name,a,b,role):return cube('MakerFoyer_'+str(z)+'_'+name,(a[0]+54,a[1]-52.5,a[2]),(b[0]+54,b[1]-52.5,b[2]),role,root)
    block('wall_mount',(-56.66,55.83,z-.035),(-56.465,55.90,z+.035),'champagne_metal')
    block('housing',(-56.85,55.65,z-.35),(-56.65,55.84,z+.35),'ivory_enamel')
    block('lens',(-56.80,55.625,z-.30),(-56.70,55.65,z+.30),'champagne_metal')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Two original foyer wall contacts and source housings;no original aperture/floor/room-ID/stock changes'
native.parent.mkdir(exist_ok=True);export.parent.mkdir(exist_ok=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-maker-foyer-sources-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True)
assert sha(repeat)==esha and sha(native)==nsha
target=ROOT/'Game/assets/models/group5/maker_foyer'/export.name;target.parent.mkdir(exist_ok=True);assert not target.exists();shutil.copyfile(export,target)
(P/'docs/MAKER_FOYER_SOURCES.json').write_text(json.dumps({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/maker_foyer/'+export.name,'model_sha256':esha,'mesh_count':6,'origin_world_xyz':[-54.06,52.5,0],'fresh_native_repeat_export_byte_identical':True},indent=2)+'\n');print('MAKER_FOYER_SOURCE_PASS',esha)
