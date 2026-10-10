from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.load(open(W/'RUNTIME_PLAN.json'));images=[];pins={}
for room in P['rooms']:
 idx=room['allocation']['source_envelope_index'];rests=[c for c in room['components']if c['catalogue_id']=='AST-RST-QC-001'];z=rests[0]['position'][2];native=W/f'StarAtlasSpecialty_{idx}.blend';pins[native.name]=sha(native)
 views=[('INTERIOR',(-88.9,90.15,z+.45),(-95.3,89.55,z),17)]if idx in (377,383)else[('INTERIOR',(-79.2,90.15,z+.45),(-72.8,89.55,z),17)]
 for n,rest in enumerate(rests):
  z=rest['position'][2];label='COCOON'+(f'_{n+1:02}'if len(rests)>1 else'')
  if idx not in (377,383):views.append((label,(rest['position'][0]-.8,89.7,z),(rest['position'][0]+1.25,89.4,z),14))
  else:views.append((label,(rest['position'][0]+.8,89.7,z),(rest['position'][0]-1.25,89.4,z),14))
 for label,pos,target,lens in views:
  bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
  scene.world=bpy.data.worlds.new('DiagnosticSourceWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.2,.22,.24,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
  for p in ([(-91,91.2,z),(-95,91.2,z),(-96,90.2,z)]if idx in (377,383) else[(-78,91.2,z),(-73,91.2,z),(-71,90.2,z)]):
   bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=90;bpy.context.object.data.size=2.5
  bpy.ops.object.camera_add(location=B(pos));camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name=f'SOURCE_{label}_{idx}.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for p,h in pins.items():assert sha(W/p)==h
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'diagnostic_fill_lighting':True,'unsaved_source_views':True,'native_pins_unchanged':pins},indent=2)+'\n')
