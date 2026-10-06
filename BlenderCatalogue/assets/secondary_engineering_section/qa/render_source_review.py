"""Parent-scheduled Blender source-only normal-eye-height review. Never saves source.
Run only in allocated serial render slot. Output remains within this package.
"""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-ENG-008.blend'));S=bpy.context.scene
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=64;S.cycles.use_denoising=False;S.render.resolution_x=960;S.render.resolution_y=600;S.render.resolution_percentage=100
S.world.use_nodes=True;world_bs=S.world.node_tree.nodes.get('Background');world_bs.inputs['Color'].default_value=(.55,.55,.55,1);world_bs.inputs['Strength'].default_value=.25
# Diagnostic fill only: not production fixture or runtime-light evidence.
neutral_fills=[('hall_form',(34.5,10.9,-438),1600,8),('hall_reverse',(34.5,10.9,-425),1200,8),('visitor_fill',(12,9.4,-436),500,4),('control_fill',(27,9.1,-459),600,4),('workbay_fill',(27,9.4,-405),600,4),('cart_fill',(51,9.75,-428),800,4)]
def bp(p):return Vector((p[0],-p[2],p[1]))
K=json.loads((R/'source/section_contract.json').read_text())
for fixture in K['fixtures']:
    d=bpy.data.lights.new('SOURCE_REVIEW_'+fixture['name'],'AREA');d.energy=450;d.shape='DISK';d.size=1.25;o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o);p=fixture['position_xyz'];o.location=bp((p[0],p[1]-.08,p[2]));o.rotation_euler=(0,0,0)
for n,p,energy,size in neutral_fills:
    d=bpy.data.lights.new('DIAGNOSTIC_NEUTRAL_FILL_'+n,'AREA');d.energy=energy;d.size=size;o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o);o.location=bp(p)
views=[('visitor_eye_source_only',(12,7.65,-439),(34.5,8.2,-432)),('plant_maintenance_eye_source_only',(46,7.65,-439),(34.5,8.3,-432)),('control_eye_source_only',(30,7.65,-457),(25.5,7.3,-462.7)),('cart_street_eye_source_only',(51,7.65,-449),(51,7.65,-410)),('workbay_eye_source_only',(30,7.65,-407),(24,7.1,-401))]
cam=bpy.data.cameras.new('SOURCE_REVIEW_CAMERA');o=bpy.data.objects.new('SOURCE_REVIEW_CAMERA',cam);S.collection.objects.link(o);S.camera=o;cam.lens=20;cam.clip_start=.05;cam.clip_end=160
for name,eye,target in views:
    o.location=bp(eye);o.rotation_euler=(bp(target)-o.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(R/'qa'/('AST-ENG-008_'+name+'.png'));bpy.ops.render.render(write_still=True)
(R/'qa/source_render_views.json').write_text(json.dumps(dict(stage='source-only diagnostic Blender review; neutral temporary fill; normal eye Y7.65; not production lighting or in-game/reference acceptance',fixture_emitter_down_offset_m=.08,neutral_world_fill=dict(color=[.55,.55,.55],strength=.25),neutral_area_fills=[dict(name=n,position_xyz=p,energy_w=energy,size_m=size) for n,p,energy,size in neutral_fills],walls_hidden=False,source_glass_unchanged=True,views=[dict(name=n,eye_xyz=e,target_xyz=t,image='AST-ENG-008_'+n+'.png') for n,e,t in views]),indent=2)+'\n')
