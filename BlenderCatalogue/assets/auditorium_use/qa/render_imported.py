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
 target_id='AST-CUL-003'if name.startswith('seat')else'AST-CUL-004';framed=[]
 for ob in sc.objects:
  if ob.type!='MESH' or ob.name.startswith('QA_'):continue
  ancestors=[];p=ob
  while p:ancestors.append(p.name);p=p.parent
  if not any(a.startswith(target_id)for a in ancestors):continue
  e=ob.evaluated_get(deps);me=e.to_mesh();framed.extend(world_to_camera_view(sc,cam,ob.matrix_world@v.co)for v in me.vertices);e.to_mesh_clear()
 frame={'target':target_id,'ndc_min':[min(v[k]for v in framed)for k in range(3)],'ndc_max':[max(v[k]for v in framed)for k in range(3)]};frame['whole_target_visible']=all(0<=frame['ndc_min'][k]and frame['ndc_max'][k]<=1 for k in(0,1))and frame['ndc_min'][2]>0
 row={'camera_preflight':frame,'image':name+'.png','inputs':inputs,'camera_eye_source_m':eye,'camera_target_source_m':target,'camera_lens_mm':lens,'resolution_px':res,'scope':scope,'imported_meshes':count,'render_engine':'Blender EEVEE 64 sample component QA, not game renderer','no_runtime_light_claim':'QA lamps illuminate all views; no asset exports light objects or active emitters','source_bindings':[{'source':str(p.relative_to(BASE)),'sha256':sha(p)}for p in sorted((BASE/'source').glob('AST-CUL-*.blend'))if p.stem==target_id],'generator_sha256':sha(BASE/'source/build_auditorium_use.py')}
 if RENDER:bpy.ops.render.render(write_still=True);row['image_sha256']=sha(BASE/'qa'/(name+'.png'))
 records.append(row)

reset();inputs=[imp(BASE/'exports/AST-CUL-003.glb')];capture('seat_closed_seated_640',inputs,[1.35,-2.55,1.18],[0,-.03,.55],36,[640,360],'Whole seat at declared seated eye1.18m. Original dry audience proposal; no species/row/host fit.')
reset();inputs=[imp(BASE/'exports/AST-CUL-003_folded.glb'),imp(BASE/'exports/AST-CUL-003.glb',(.74,0,0))];capture('seat_folded_adjacent_seated_640',inputs,[1.80,-2.95,1.20],[.35,-.02,.57],38,[640,360],'Folded module plus adjacent closed module at expressly proposed X0.74m centres, seated eye1.20m. Inspection pair only; no numbered seats, real row pitch or capacity added.')
reset();inputs=[imp(BASE/'exports/AST-CUL-004.glb')];capture('stand_work_standing_640',inputs,[1.10,-3.1,1.62],[0,-.02,.84],32,[640,360],'Whole backstage notes/work stand at ordinary standing eye1.62m. Cue face inactive; neutral QA lighting, no photometry.')
reset();inputs=[imp(BASE/'exports/AST-CUL-004_service_open.glb')];capture('stand_service_standing_640',inputs,[1.4,3.25,1.62],[0,.11,.85],34,[640,360],'Rear service view at ordinary standing eye1.62m. Complete detached cover in proposed handling pose; no floating/retained mechanism or user body asserted. Protected column channel and grip are inspectable.')
(BASE/'qa'/('render_evidence.json'if RENDER else'camera_preflight.json')).write_text(json.dumps({'views':records,'rendered':RENDER,'source_note':'Imported GLBs at listed hashes; exact source hashes bound per view. QA pair does not imply any room adjacency or installed row.'},indent=2)+'\n')
print('AUDITORIUM_USE_RENDER'if RENDER else'AUDITORIUM_USE_PREFLIGHT',len(records),all(r['camera_preflight']['whole_target_visible']for r in records))
