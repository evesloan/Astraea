"""Immutable r001 -> r002;only three entire task fixtures project in front of crowns."""
from pathlib import Path
import bpy,json,hashlib,shutil
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
definition=ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json';j=json.loads(definition.read_text())
original=P/'source/thread_stock/thread_stock_repair_r001.blend';old_export=P/'exports/thread_stock/thread_stock_repair_r001.glb'
before_native=sha(original);before_export=sha(old_export)
native=P/'source/thread_stock/thread_stock_repair_r002.blend';export=P/'exports/thread_stock/thread_stock_repair_r002.glb'
assert not native.exists() and not export.exists(),'Saved source revisions stay immutable'
bpy.ops.wm.open_mainfile(filepath=str(original))
selected=[];unchanged={}
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    if '_fixture_' in o.name:
        o.location.x-=.65;selected.append(o.name)
    else:unchanged[o.name]=list(o.matrix_world)
assert len(selected)==9
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
native_sha=sha(native);export_sha=sha(export)
bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5_thread_stock_r002_repeat.glb')
bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
assert sha(repeat)==export_sha and sha(native)==native_sha and sha(original)==before_native and sha(old_export)==before_export
for name,mat in unchanged.items():assert list(bpy.data.objects[name].matrix_world)==mat
target=ROOT/'Game/assets/models/group5/thread_stock'/export.name;assert not target.exists();shutil.copyfile(export,target)
j['selected_fixture_successor']={'parent_native':str(original.relative_to(ROOT)),'parent_native_sha256':before_native,'parent_export':str(old_export.relative_to(ROOT)),'parent_export_sha256':before_export,'changed_meshes':selected,'rigid_source_translation_xyz_m':[-.65,0,0],'unchanged_mesh_count':len(unchanged),'geometry_material_uv_unchanged':True,'fresh_native_repeat_export_byte_identical':True,'reason':'Project all three fixtures in front of stock crowns so they can reach useful work/inspection points;original mounts/room ceilings preserved'}
j['native']=str(native.relative_to(ROOT));j['native_sha256']=native_sha;j['model_path']='res://assets/models/group5/thread_stock/'+export.name;j['model_sha256']=export_sha
for f in j['fixtures']:f['world_xyz'][0]-=.65
definition.write_text(json.dumps(j,indent=2)+'\n');print('THREAD_STOCK_FIXTURE_SUCCESSOR_PASS',len(selected),len(unchanged),export_sha)
