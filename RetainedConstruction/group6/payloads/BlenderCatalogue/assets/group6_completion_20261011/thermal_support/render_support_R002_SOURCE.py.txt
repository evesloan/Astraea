"""Saved thermal source views, with original compiler floor context only."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[3]
def xyz(p):return Vector((p[0],-p[2],p[1]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=[];source=R/'Game/data/generated/received_structural_meshes.json';regions=json.loads(source.read_text())['regions']
for spec in json.loads((P/'THERMAL_SUPPORT_CONTRACT.json').read_text())['rooms']:
 native=R/spec['native'];assert sha(native)==spec['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1800;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('Neutral source review');s.world.color=(.35,.39,.42);s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.view_settings.view_transform='Standard'
 for m in bpy.data.materials:
  if m.use_nodes:
   b=m.node_tree.nodes.get('Principled BSDF')
   if b:m.diffuse_color=b.inputs['Base Color'].default_value
 hidden=[]
 for o in s.objects:
  if o.type=='MESH' and any(t in o.name.lower() for t in ['ceiling','roof']):o.hide_render=True;hidden.append(o.name)
 preview=[]
 for region in regions:
  if not region['id'].startswith(spec['programme_key']+'_'):continue
  vs=[];faces=[]
  for triangle in region['triangles']:
   j=len(vs);vs.extend([xyz((p[0],region['floor_y'],p[1])) for p in triangle]);faces.append((j,j+1,j+2))
  m=bpy.data.meshes.new('Render-only original '+region['id']);m.from_pydata(vs,[],faces);m.update();o=bpy.data.objects.new(m.name,m);s.collection.objects.link(o);o.data.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);preview.append(region['id'])
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=200
 i=spec['programme_key'][-2:]
 views=[('wide',(67,74,-474),(34,44.5,-432),49),('court',(43,52,-442),(34,45.1,-432),13)] if i=='02' else [('wide',(4,74,-250),(-29,44.5,-216),43),('court',(-25,52,-226),(-34,45.1,-216),12)]
 for key,eye,target,scale in views:
  cam.data.ortho_scale=scale;cam.location=xyz(eye);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();name=f'SOURCE_THERMAL_SUPPORT_{i}_{key}002.png';s.render.filepath=str(P/name);bpy.ops.render.render(write_still=True)
  receipts.append({'image':name,'image_sha256':sha(P/name),'native':spec['native'],'native_sha256':spec['native_sha256'],'eye_xyz':eye,'target_xyz':target,'orthographic_scale_m':scale,'render_only_original_floor_context':preview,'compiler_input_sha256':sha(source),'cutaway_original_roof_objects':hidden,'native_resaved':False,'presentation':'Actual saved thermal support/entry/original room source, neutral studio/base colors. Compiler floor context is render-only; occupied hoist/water, ordinary lights, engineering, species, final art and hardware unaccepted.'})
(P/'SOURCE_VIEW_RECEIPT002.json').write_text(json.dumps(receipts,indent=2)+'\n')
