from pathlib import Path
import bpy,json,hashlib,math,time
from mathutils import Vector
R=Path('/workspace/Astraea');E=Path(__file__).resolve().parent;B=lambda p:Vector((p[0],-p[2],p[1]));G=lambda p:Vector((p.x,p.z,-p.y));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;hidden=[];inputs=[]
def trim(o,lo=(18.5,83,-489),hi=(46.5,101,-477)):
 o.data.calc_loop_triangles();vs=[];uvs=[];faces=[];mats=[]
 for t in o.data.loop_triangles:
  poly=[(G(o.matrix_world@o.data.vertices[v].co),o.data.uv_layers.active.data[l].uv.copy() if o.data.uv_layers.active else Vector((0,0)))for v,l in zip(t.vertices,t.loops)]
  for axis in range(3):
   for plane,less in [(lo[axis],False),(hi[axis],True)]:
    if not poly:break
    out=[];s=poly[-1];ds=s[0][axis]-plane
    for e in poly:
     de=e[0][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
     if ins!=ine:
      a=ds/(ds-de);out.append((s[0].lerp(e[0],a),s[1].lerp(e[1],a)))
     if ine:out.append(e)
     s=e;ds=de
    poly=out
  if len(poly)<3:continue
  offset=len(vs);vs.extend([B(v)for v,u in poly]);uvs.extend([u for v,u in poly]);faces.append(tuple(range(offset,offset+len(poly))));mats.append(t.material_index)
 data=bpy.data.meshes.new(o.name+'_DIAGNOSTIC_CROP');data.from_pydata(vs,[],faces);data.update()
 for m in o.data.materials:data.materials.append(m)
 layer=data.uv_layers.new(name='SourceUV')
 for poly,mat in zip(data.polygons,mats):
  poly.material_index=mat
  for l in poly.loop_indices:layer.data[l].uv=uvs[data.loops[l].vertex_index]
 o.data=data;o.matrix_world.identity()
for deck,revision in [(13,'r001'),(14,'r002'),(15,'r004'),(16,'r001')]:
 p=json.loads((R/f'Game/data/quiet_d{deck}_receiving_20261016/RECEIPT.json').read_text());f=R/f'Game/assets/quiet_d{deck}_receiving_20261016'/p['file'];assert sha(f)==p['model_sha256'];inputs.append({'file':str(f.relative_to(R)),'sha256':sha(f)});before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(f))
 for o in set(bpy.data.objects)-before:
  if o.type!='MESH':continue
  if o.name.startswith('PATCH_'):
   if deck==15 and 'lobby_wall' in o.name:o.hide_render=True;hidden.append(o.name+' (superseded by D14)')
   else:trim(o)
  if f'Q{deck}_Canopy' in o.name or f'Q{deck}_Edge0_'in o.name or f'Q{deck}_Edge2_'in o.name:
   o.hide_render=True;hidden.append(o.name)
for f,names in [(R/'Game/assets/models/group3_fore_starboard_clinical_20261011/AST-STF-G3-041.glb',{f'floor_staff_floor_D{d}'for d in [13,14,15,16]}),(R/'Game/assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb',{'QG_Batch_3','QG_Batch_11','QG_Batch_52','QG_Batch_94'})]:
 inputs.append({'file':str(f.relative_to(R)),'sha256':sha(f)});before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(f))
 for o in set(bpy.data.objects)-before:
  if o.type=='MESH'and o.name in names:trim(o)
  elif o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.max_bounces=3;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('DiagnosticWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.07,.09,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
light=bpy.data.lights.new('DIAGNOSTIC_sun','SUN');light.energy=2;light.angle=.5;obj=bpy.data.objects.new('DIAGNOSTIC_sun',light);scene.collection.objects.link(obj);obj.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-30))
cam=bpy.data.cameras.new('LOCAL_cutaway_camera');camera=bpy.data.objects.new('LOCAL_cutaway_camera',cam);scene.collection.objects.link(camera);camera.location=B((57,108,-525));camera.rotation_euler=(B((32,92,-483))-camera.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=43;cam.clip_end=1000;scene.camera=camera
mat=bpy.data.materials.new('Diagnostic_caption');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.85,.9,.95,1);mat.node_tree.links.new(em.outputs[0],out.inputs[0])
def label(name,text,at,size,parent=False):
 f=bpy.data.curves.new(name,'FONT');f.body=text;f.size=size;f.space_line=1.3;o=bpy.data.objects.new(name,f);scene.collection.objects.link(o);f.materials.append(mat)
 if parent:o.parent=camera;o.location=at
 else:o.location=B(at);o.rotation_euler=camera.rotation_euler
label('Caption','QUIET GROVE | D13–D16 STAFF CONNECTIONS\nLocal construction cutaway / actual retained geometry',(-20.5,14.5,-80),.65,True)
label('Limits','Ceilings + near wall panels hidden / diagnostic lighting\n8365c7690 / not a game-lighting, engineering or final-art acceptance',(-20.5,-14.2,-80),.46,True)
for d,y in [(13,84),(14,88.5),(15,93),(16,97.5)]:label(f'Deck{d}',f'D{d}  Y{y:g}',(16.4,y+.2,-486.5),.63)
scene.view_settings.view_transform='AgX';scene.render.filepath=str(E/'QUIET_GROVE_D13_D16_DIAGNOSTIC.png');start=time.time();bpy.ops.render.render(write_still=True)
(E/'CAPTURE_RECEIPT.json').write_text(json.dumps({'source_revision':'8365c7690edad5f637587e62c687958633f34dde','scope':'One local Blender cutaway of exact installed receiver assets and cropped retained lobby/street floor triangles. No full-ship render; no production file edits.','engine':'Blender Cycles CPU','samples':8,'resolution':[1280,960],'elapsed_seconds':time.time()-start,'source_inputs':inputs,'hidden_for_cutaway':hidden,'context_crop_world':[[18.5,83,-489],[46.5,101,-477]],'lighting':'Diagnostic sun/world; not production lighting','png_sha256':sha(E/'QUIET_GROVE_D13_D16_DIAGNOSTIC.png'),'final_visual_accepted':False},indent=2)+'\n');print('ONE_LOCAL_CAPTURE_COMPLETE',time.time()-start)
