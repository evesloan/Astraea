# Single bounded local diagnostic; does not save or alter production source scenes.
from pathlib import Path
import bpy,json,hashlib,math,time
from mathutils import Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/Astraea');G=R/'Game';Q=D/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());native=D/'source/GAMES_SERVICE_RECEIVER_r001.blend';source=G/'assets/models/SOL_D11_directory_10_source001.glb'
assert sha(native)==r['native_sha256'] and sha(source)==r['source_pins']['assets/models/SOL_D11_directory_10_source001.glb']
bpy.ops.wm.open_mainfile(filepath=str(native));B=lambda p:Vector((p[0],-p[2],p[1]))
for c in bpy.data.collections:
 if 'AUTHORING'in c.name:c.hide_render=False
 if 'RUNTIME'in c.name:c.hide_render=True
bpy.ops.import_scene.gltf(filepath=str(source))
for wall in r['walls']:bpy.data.objects.remove(bpy.data.objects[wall['source_name']],do_unlink=True)
hidden=[]
for o in bpy.data.objects:
 if o.name=='E_ceiling' or o.name.startswith('E_roofbeam') or o.name in ['GCR_SourceJoinedRoof','GCR_SourceRoofJoin']:
  o.hide_render=True;hidden.append(o.name)
# Display existing production floor triangles; crop only the contextual aft route.
def clip(poly,axis,plane,less):
 out=[];s=poly[-1];ds=s[axis]-plane
 for e in poly:
  de=e[axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:out.append([s[k]+(e[k]-s[k])*ds/(ds-de)for k in range(2)])
  if ine:out.append(e)
  s=e;ds=de
 return out
material=bpy.data.materials.new('DIAGNOSTIC_existing_floor');material.diffuse_color=(.20,.24,.24,1)
floor_rows=[]
for file in ['data/generated/received_structural_meshes.json','data/generated/structural_meshes.json']:
 for row in json.loads((G/file).read_text())['regions']:
  if row['id']not in ['D11_directory_10_authored_floor','D11_directory_10_spine_connection','D11_aft_route']:continue
  vs=[];fs=[]
  for tri in row['triangles']:
   poly=tri
   if row['id']=='D11_aft_route':
    for axis,plane,less in [(1,180,False),(1,257,True)]:
     if poly:poly=clip(poly,axis,plane,less)
   if len(poly)<3:continue
   vertices=[B((x,row['floor_y'],z))for x,z in poly]
   if (vertices[1]-vertices[0]).cross(vertices[2]-vertices[0]).z<0:vertices.reverse()
   offset=len(vs);vs.extend(vertices);fs.append(tuple(range(offset,offset+len(vertices))))
  mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(vs,[],fs);mesh.materials.append(material);obj=bpy.data.objects.new(row['id'],mesh);bpy.context.scene.collection.objects.link(obj);floor_rows.append(row['id'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.cycles.max_bounces=3;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1024;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.07,.09,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for o in list(bpy.data.objects):
 if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
light=bpy.data.lights.new('DIAGNOSTIC_sun','SUN');light.energy=2;light.angle=.5;obj=bpy.data.objects.new('DIAGNOSTIC_sun',light);scene.collection.objects.link(obj);obj.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-30))
cam=bpy.data.cameras.new('LOCAL_progress_camera');obj=bpy.data.objects.new('LOCAL_progress_camera',cam);scene.collection.objects.link(obj);obj.location=B((14,125,277));target=B((-26,70,220));obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=90;cam.clip_end=1000;scene.camera=obj
font=bpy.data.curves.new('DiagnosticCaption','FONT');font.body='GAMES & COMPANIONSHIP | LOCAL CONSTRUCTION VIEW\nCeilings hidden for inspection / diagnostic lighting / not final game art';font.size=1.05;font.space_line=1.3;text=bpy.data.objects.new('DiagnosticCaption',font);scene.collection.objects.link(text);text.parent=obj;text.location=(-43,31,-80)
mat=bpy.data.materials.new('DiagnosticCaptionWhite');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.8,.85,.9,1);mat.node_tree.links.new(em.outputs[0],out.inputs[0]);font.materials.append(mat)
scene.view_settings.view_transform='AgX';scene.render.filepath=str(Q/'LOCAL_PROGRESS.png');start=time.time();bpy.ops.render.render(write_still=True)
receipt={'scope':'One local Blender cutaway diagnostic; actual source geometry and installed receiver with production floor triangles. No full game scene, game-lighting/CRT claim or final art acceptance.','render_engine':'Blender Cycles CPU','samples':8,'resolution':[1024,768],'elapsed_seconds':time.time()-start,'native_sha256':sha(native),'runtime_sha256':r['model_sha256'],'original_source_sha256':sha(source),'png_sha256':sha(Q/'LOCAL_PROGRESS.png'),'hidden_for_cutaway':hidden,'production_floor_records':floor_rows,'floor_material':'neutral diagnostic approximation','production_files_modified':False,'final_visual_accepted':False};(Q/'LOCAL_PROGRESS_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('LOCAL_PROGRESS_RENDER_COMPLETE',receipt['elapsed_seconds'])
