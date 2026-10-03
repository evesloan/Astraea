"""Serialized ordinary-height imported-GLB QA; never changes exported assets."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];RENDER='--render'in sys.argv
records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.85;return m
def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.world.color=(.32,.32,.32);sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False;sc.view_settings.view_transform='AgX'
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));floor=bpy.context.object;floor.name='QA_neutral_floor';floor.data.materials.append(mat('QA_neutral_floor',(.20,.22,.23)))
 for name,loc,power,size in[('key',(-3,-4,5),850,5),('fill',(4,-1,3),550,4),('rear',(0,5,5),750,4)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='QA_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
 return sc
def imp(path,offset=(0,0,0)):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.context.scene.objects)-before
 for o in obs:
  if o.parent is None:o.location+=Vector(offset)
 return {'file':str(path.relative_to(CAT)),'sha256':sha(path),'placement_translation_source_m':list(offset)}
def capture(name,inputs,eye,target,lens,res,scope):
 sc=bpy.context.scene;bpy.ops.object.camera_add(location=eye);cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;sc.camera=cam;sc.render.resolution_x=res[0];sc.render.resolution_y=res[1];sc.render.resolution_percentage=100;sc.render.filepath=str(BASE/'qa'/(name+'.png'));bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get();count=0
 for o in sc.objects:
  if o.type=='MESH'and not o.name.startswith('QA_'):count+=1
 target_id='AST-CRW-003'if name.startswith('storage')else'AST-CRW-004';framed=[]
 for ob in sc.objects:
  if ob.type!='MESH' or ob.name.startswith('QA_'):continue
  ancestors=[];p=ob
  while p:ancestors.append(p.name);p=p.parent
  if not any(a.startswith(target_id)for a in ancestors):continue
  e=ob.evaluated_get(deps);me=e.to_mesh();framed.extend(world_to_camera_view(sc,cam,ob.matrix_world@v.co)for v in me.vertices);e.to_mesh_clear()
 frame={'target':target_id,'ndc_min':[min(v[k]for v in framed)for k in range(3)],'ndc_max':[max(v[k]for v in framed)for k in range(3)]};frame['whole_target_visible']=all(0<=frame['ndc_min'][k]and frame['ndc_max'][k]<=1 for k in(0,1))and frame['ndc_min'][2]>0
 row={'camera_preflight':frame,'image':name+'.png','inputs':inputs,'camera_eye_source_m':eye,'camera_target_source_m':target,'camera_lens_mm':lens,'resolution_px':res,'scope':scope,'imported_meshes':count,'render_engine':'Blender EEVEE 64 sample component QA, not game renderer','no_runtime_light_claim':'QA lamps illuminate all views; reading asset exports no light object or active emitter'}
 if RENDER:bpy.ops.render.render(write_still=True);row['image_sha256']=sha(BASE/'qa'/(name+'.png'))
 records.append(row)
for state in('closed','open'):
 reset();p=BASE/'exports'/('AST-CRW-003'+('_open'if state=='open'else'')+'.glb');inp=[imp(p)];capture('storage_'+state+'_standing_640',inp,[1.65,-2.7,1.55],[0,-.05,.72],38,[640,360],'Whole storage at declared ordinary standing camera height 1.55m; '+state+' drawer state, proposal only')
reset();inputs=[imp(CAT/'assets/crew_rest/exports/AST-CRW-001.glb'),imp(BASE/'exports/AST-CRW-004.glb',(-.26,2.14,.88))];capture('reading_mounted_seated_640',inputs,[.80,1.02,1.12],[-.23,2.04,.87],50,[640,360],'Actual proposed headboard placement at declared seated eye1.12m; crop includes shelf/light, pillow and host headboard but is not a room view')
reset();inputs=[imp(CAT/'assets/crew_rest/exports/AST-CRW-001.glb'),imp(BASE/'exports/AST-CRW-004.glb',(-.26,2.14,.88))];capture('reading_mount_detail_1280',inputs,[-.82,1.15,1.16],[-.26,2.01,.90],56,[1280,960],'Explicit component detail crop showing supported shelf side braces, shield, diffuser, real backplate and resting surface')
(BASE/'qa'/('render_evidence.json'if RENDER else'camera_preflight.json')).write_text(json.dumps({'views':records,'rendered':RENDER,'source_note':'Images bind actual GLBs at listed hashes; source-only QA and source hashes are separate records'},indent=2)+'\n')
print('CREW_PERSONAL_RENDER'if RENDER else'CREW_PERSONAL_CAMERA_PREFLIGHT',len(records))
