"""Retain r003; r004 seats loose equipment on exposed bench and clears bin dividers."""
from pathlib import Path
import bpy,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json';j=json.loads(d.read_text());assert j['native'].endswith('r003.blend')
old=ROOT/j['native'];oldglb=ROOT/j['model_path'].replace('res://','Game/');pins=[sha(old),sha(oldglb)]
native=P/'source/thread_stock/thread_stock_repair_r004.blend';export=P/'exports/thread_stock/thread_stock_repair_r004.glb';assert not native.exists() and not export.exists()
bpy.ops.wm.open_mainfile(filepath=str(old));changed=[]
for o in bpy.context.scene.objects:
    dz=0
    if o.name.startswith('Reserve_OpenNotionsBin_'):
        i=int(o.name.split('_')[2]);dz=[-.5625,-1.0375,.5625][i]
    elif o.name.startswith('Repair_Scissor'):dz=-.49
    elif o.name.startswith('Repair_MetricRule') or o.name.startswith('Repair_RuleGraduation'):dz=-.19
    elif o.name.startswith('Repair_TapeMeasure') or o.name.startswith('Repair_UnrolledMeasure'):dz=.38
    if dz:o.location.y-=dz;changed.append({'mesh':o.name,'world_delta_xyz':[0,0,dz]})
bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
native_sha=sha(native);export_sha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5_thread_r004_repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True);assert sha(repeat)==export_sha and sha(native)==native_sha and [sha(old),sha(oldglb)]==pins
target=ROOT/'Game/assets/models/group5/thread_stock'/export.name;assert not target.exists();shutil.copyfile(export,target)
j['equipment_contact_successor']={'revision':'r004','parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':pins[0],'parent_model':str(oldglb.relative_to(ROOT)),'parent_model_sha256':pins[1],'rigid_changes':changed,'reason':'r003 bench tools overlapped occupied trays and one reserve bin straddled a divider;move equipment onto exposed worktop and bins into existing shelf cells','geometry_material_uv_unchanged':True,'fresh_native_repeat_export_byte_identical':True}
j['native']=str(native.relative_to(ROOT));j['native_sha256']=native_sha;j['model_path']='res://assets/models/group5/thread_stock/'+export.name;j['model_sha256']=export_sha
d.write_text(json.dumps(j,indent=2)+'\n');print('THREAD_EQUIPMENT_R004',len(changed),export_sha)
