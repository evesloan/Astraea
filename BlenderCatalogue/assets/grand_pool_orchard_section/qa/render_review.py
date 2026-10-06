"""Labelled Blender source-only architecture review. No in-game or final-lighting claim."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-AQU-016.blend'))
# Replace wire compiler previews with temporary solid floor triangle prisms solely for source review.
mat=bpy.data.materials.get('ASTRAEA_warm_stone')
for o in list(bpy.context.scene.objects):
 if o.name.startswith('PREVIEW_ONLY_'):
  if 'DoorFitting' in o.name or 'service_'in o.name or 'wet_market_'in o.name:o.hide_render=False
  elif o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
for f in D['floor_regions']:
 vv=[];ff=[]
 for t in f['triangles']:
  k=len(vv);vv += [(x,-z,y)for y in[f['floor_y']-f['thickness'],f['floor_y']]for x,z in t];ff += [[k+i for i in face]for face in[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]]
 me=bpy.data.meshes.new('ReviewFloor');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new('REVIEW_'+f['id'],me);bpy.context.collection.objects.link(o);me.materials.append(mat)
# Modest matte trial water plane, explicitly a review-only datum; basin/source/export has no water mesh.
water=bpy.data.materials.new('REVIEW_water_datum');water.diffuse_color=(.05,.21,.23,1);water.use_nodes=True;bs=water.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.045,.22,.24,1);bs.inputs['Roughness'].default_value=.35
me=bpy.data.meshes.new('ReviewWater');me.from_pydata([(-40,457,46.05),(-22,457,46.05),(-22,407,46.05),(-40,407,46.05)],[],[(3,2,1,0)]);me.update();o=bpy.data.objects.new('REVIEW_ONLY_Water_Datum',me);bpy.context.collection.objects.link(o);me.materials.append(water)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.15,.15,.15);scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.46,.51,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.20
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.8
# Review illumination sits at actual fixture datums, plus broad neutral ceiling fill for architectural legibility.
for f in D['fixtures']:
 data=bpy.data.lights.new(f['name'],'AREA');data.energy=1000 if f['profile']=='pool_vault'else 350;data.color=(1,.90,.76);data.shape='DISK';data.size=2.0 if f['profile']=='pool_vault'else.6
 o=bpy.data.objects.new(f['name']+'_REVIEW_LIGHT',data);bpy.context.collection.objects.link(o);x,y,z=f['position_xyz'];o.location=(x,-z,y)
for x,z in[(-31,-456),(-31,-420),(-46,-437),(-12,-436)]:
 data=bpy.data.lights.new('REVIEW_neutral_fill','AREA');data.energy=700;data.size=10;o=bpy.data.objects.new('REVIEW_neutral_fill',data);bpy.context.collection.objects.link(o);o.location=(x,-z,59.0)
camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.lens=25;camdata.clip_end=1000
scene.render.use_stamp=True;scene.render.use_stamp_date=False;scene.render.use_stamp_time=False;scene.render.use_stamp_render_time=False;scene.render.use_stamp_frame=False;scene.render.use_stamp_filename=False;scene.render.use_stamp_scene=False;scene.render.use_stamp_camera=False;scene.render.use_stamp_note=True;scene.render.stamp_font_size=15
views=[('source_arrival',[-7.4,45.65,-432],[-31,49.8,-433],25),('source_market',[-10.0,54.15,-432],[-39,54.5,-446],27),('source_wet_long_view',[-20,47.85,-449],[-34,51.0,-423],25),('source_market_west',[-46.1,54.15,-440],[-51,55,-450],25),('source_ramp_arrival',[-9.4,45.65,-442],[-13.5,45.8,-456],25),('source_cutaway',[16,83,-376],[-30,49,-432],36)]
for name,pos,target,lens in views:
 cut=name=='source_cutaway'
 for o in scene.objects:
  if o.name.startswith(('REVIEW_D10','GP_RoofRib','GP_LongCeilingReturn','GP_EndEnclosure','GP_EastWall','GP_PublicPortalHeader')):o.hide_render=cut
  if o.type=='MESH'and o.name.startswith(('GP_KeelSeat','GP_Bearing')):o.hide_render=True
 x,y,z=pos;cam.location=(x,-z,y);x,y,z=target;direction=Vector((x,-z,y))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camdata.lens=lens
 scene.render.stamp_note_text='BLENDER SOURCE REVIEW | '+name.replace('source_','').replace('_',' ')+' | trial water datum / neutral review fill | NOT IN-GAME'
 scene.render.filepath=str(R/'qa'/(name+'.png'));bpy.ops.render.render(write_still=True)
report={'status':'Source-only CPU Cycles views; not in-game or final lighting','source_sha256':hashlib.sha256((R/'source/AST-AQU-016.blend').read_bytes()).hexdigest(),'contract_sha256':hashlib.sha256((R/'source/connected_contract.json').read_bytes()).hexdigest(),'samples':128,'denoising':False,'neutral_fill_energy_w':700,'exposure':-.8,'images':[{'path':'qa/'+name+'.png','camera_xyz':pos,'target_xyz':target,'lens_mm':lens,'sha256':hashlib.sha256((R/'qa'/(name+'.png')).read_bytes()).hexdigest()}for name,pos,target,lens in views],'exclusions_for_cutaway':['roof sheets','roof ribs','east/end walls','all lower bearing stems'],'preview_only':['all compiler-floor solids','flat trial water datum','existing-family door fitting instances','neutral review area lights']}
(R/'qa/reference_source_visual_review.json').write_text(json.dumps(report,indent=2)+'\n')
print('Source-only review images saved; no source .blend changes saved')
