"""Clear real-source court photograph; supplemental review lights, no source edit."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
native=P/'source/natives/G7_Completion_r002.blend'
before=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath='/tmp/G7_Completion_review_context_20261011.blend')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False
s.cycles.sample_clamp_indirect=1.5;s.cycles.sample_clamp_direct=10
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100
def point(p):return Vector((p[0],-p[2],p[1]))
def area(name,at,target,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.location=point(at)
    ob.rotation_euler=(point(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('Supplemental_source_photo_key',(-30,83,27),(-44,78,22),120000,18)
area('Supplemental_source_photo_fill',(-34,80,35),(-44,79,22),35000,12)
data=bpy.data.cameras.new('D12 source court review');ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob)
eye=(-34,80.0,31);target=(-43.7,79.1,22)
ob.location=point(eye);ob.rotation_euler=(point(target)-ob.location).to_track_quat('-Z','Y').to_euler()
data.lens=22;data.clip_start=.02;data.clip_end=5000;s.camera=ob
out=P/'qa/views/SOURCE_D12_COURT_CLEAR_DIAGNOSTIC.png';assert not out.exists()
s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
report={'status':'SOURCE_PHOTO_CREATED_REVIEW_PENDING','view':'qa/views/'+out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'eye_world_xyz':eye,'target_world_xyz':target,'immutable_native_sha256':before,'native_not_resaved':True,'source_geometry_or_materials_changed':False,'lighting_limits':'Supplemental key/fill area lights for clear geometry photography, plus diagnostic retained context daylight. Not actual Godot lamp output, CRT, final lighting or target hardware acceptance. No concept generation or image manipulation.'}
(P/'qa/COURT_DIAGNOSTIC_VIEW_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
