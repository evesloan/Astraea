from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector, Matrix
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.loads((W/'D13_RECEIVING_PLAN.json').read_text());N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text());B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(W/N['derivative_native']));native_hash=sha(W/N['derivative_native']);asset_hash=sha(W/N['derivative_export'])
def import_ref(path,at=(0,0,0),yaw=0):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.data.objects)-before;wrap=bpy.data.objects.new('UNSAVED_CONTEXT_'+Path(path).stem,None);bpy.context.collection.objects.link(wrap)
 for o in obs:
  if o.parent not in obs:m=o.matrix_world.copy();o.parent=wrap;o.matrix_world=m
 wrap.location=B(at);wrap.rotation_euler.z=yaw
 return obs,wrap
house,_=import_ref(R/'Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb')
for o in list(house):
 if o.type=='MESH' and o.name in P['named_guard_replacement_map']:bpy.data.objects.remove(o,do_unlink=True)
import_ref(W/N['guard_patch_export']);doors=[]
for d in P['doors']:
 obs,wrap=import_ref(R/'Game/assets/models/AST-STF-008.glb',d['position'],d['yaw']);doors.append((obs,wrap))
# Exact runtime compiled missing-only floor proposal as unsaved source-review context.
m=bpy.data.materials.new('UNSAVED_RuntimeStaffFloor');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.image=bpy.data.images.load(str(R/'Game/assets/textures/staff_floor.png'));m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for q in P['floor_regions']:
 vs=[];fs=[]
 for tri in q['triangles']:
  k=len(vs);vs.extend(B((x,84,z))for x,z in tri);fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new('UNSAVED_FLOOR_'+q['id']);me.from_pydata(vs,[],fs);me.materials.append(m);uv=me.uv_layers.new(name='MetricUV')
 for poly in me.polygons:
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.3,-v.y*.3)
 ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.05,.06,.07);s.view_settings.view_transform='AgX';bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=24;s.camera=camera
for item in P['fixtures']:
 data=bpy.data.lights.new('UNSAVED_PhysicalFixture_'+item['name'],'POINT');data.energy=95;data.color=tuple(item['color']);data.shadow_soft_size=.05;o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=B(item['position'])
bpy.ops.object.light_add(type='AREA');fill=bpy.context.object;fill.data.energy=1400;fill.data.size=12;fill.location=B((-68,90,-493));fill.rotation_euler=(Vector(B((-63,84,-490)))-fill.location).to_track_quat('-Z','Y').to_euler()
def capture(n,eye,target):
 camera.location=B(eye);camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(W/n);bpy.ops.render.render(write_still=True)
if '--open-only' not in sys.argv:capture('SOURCE_REVIEW_D13_closed_receiver_court.png',(-68.2,85.65,-490),(-62.8,85.25,-490))
# Uninstalled display-only hinge pose matches existing service_door fully-open signs.
for obs,wrap in doors:
 for side,angle in [('LEFT',math.pi/2),('RIGHT',-math.pi/2)]:
  hinge=next(o for o in obs if o.name.startswith('HINGE_'+side));bpy.context.view_layer.update();m=hinge.matrix_world.copy();pivot=m.translation.copy();hinge.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)@m
capture('SOURCE_REVIEW_D13_open_clean_threshold.png',(-61,85.65,-496.5),(-64.5,85,-493))
assert sha(W/N['derivative_native'])==native_hash and sha(W/N['derivative_export'])==asset_hash
print('D13_TWO_UNSAVED_NATIVE_SOURCE_CONTEXT_VIEWS_COMPLETE; no native/export mutation')
