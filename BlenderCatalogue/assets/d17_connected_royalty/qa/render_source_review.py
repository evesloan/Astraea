"""Bounded editable-source review only; root owns in-ship runtime visual acceptance."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-RES-006.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='Standard'
# Source-only preview slabs are enabled in this diagnostic copy, never saved/exported.
for o in scene.objects:
 if o.type=='MESH':
  if o.name.startswith('PREVIEW_ONLY_'):o.hide_render=False
  if o.name.startswith('D17_'):o.hide_render=True # frame excluded from this local spatial review; retained separately with proof
  # Cutaway the roof sheet, keep room/perimeter frame, reveal and light fixtures visible.
  if o.name in ['CR_RoyaltyLowerRoof','CR_CourtCanopy','CR_LaneCanopy','CR_PrivateBayCanopy','CR_NestedBayOverhead']:o.hide_render=True
# Orthographic local cutaway presents the original plan and actual source edges, without furnishing polish.
ld=bpy.data.lights.new('ReviewArea','AREA');lo=bpy.data.objects.new('ReviewArea',ld);scene.collection.objects.link(lo);lo.location=(90,-32,133);ld.energy=9500;ld.shape='DISK';ld.size=30
ld=bpy.data.lights.new('ReviewFill','AREA');lo=bpy.data.objects.new('ReviewFill',ld);scene.collection.objects.link(lo);lo.location=(110,-18,115);ld.energy=5000;ld.size=20;lo.rotation_euler=(Vector((99,-34,102))-lo.location).to_track_quat('-Z','Y').to_euler()
ca=bpy.data.cameras.new('SourceReviewCamera');co=bpy.data.objects.new('SourceReviewCamera',ca);scene.collection.objects.link(co);scene.camera=co;co.location=(127,-5,139);target=Vector((96,-31,103));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();ca.type='ORTHO';ca.ortho_scale=52
scene.render.filepath=str(R/'qa/source_cutaway_review.png');bpy.ops.render.render(write_still=True)
# Human height approach toward the composed threshold; source-only image is not world acceptance.
ca.type='PERSP';ca.lens=22;co.location=(81,-22,103.65);target=Vector((96.8,-31.7,103.3));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/'qa/source_court_threshold_review.png');bpy.ops.render.render(write_still=True)
