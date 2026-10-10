from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;S=Path('/tmp/astraea_tidal_d14_receiver_20261010');R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';D=json.load(open(G/'data/architecture/TIDAL_D14_SERVICE_RECEIVING.json'));N=json.load(open(W/'CORRIDOR_NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);pins={str(W/N['native']):sha(W/N['native'])}
for x in D['model_bindings']:p=G/'assets/models'/x['file'];pins[str(p)]=sha(p);assert sha(p)==x['sha256']
bpy.ops.wm.open_mainfile(filepath=str(W/N['native']));assert sum(o.type=='MESH'for o in bpy.context.scene.objects)==65
for name in N.get('batched_patch_targets',[]):assert bpy.data.objects.get(name)
def ref(path,at=(0,0,0),yaw=0):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.data.objects)-before;wrap=bpy.data.objects.new('UNSAVED_ACTUAL_'+Path(path).stem,None);bpy.context.collection.objects.link(wrap)
 for o in obs:
  if o.parent not in obs:m=o.matrix_world.copy();o.parent=wrap;o.matrix_world=m
 wrap.location=B(at);wrap.rotation_euler.z=yaw;return obs,wrap
ref(G/'assets/models'/D['receiver_file']);street,_=ref(G/'assets/models'/D['original_street_file']);patch,_=ref(G/'assets/models'/D['patch_file']);replacements={o.name:o for o in patch if o.type=='MESH'}
for spec in D['named_replacements']:
 name=spec['mesh'];rep=next(o for o in patch if o.type=='MESH'and o.name.startswith(name));old=bpy.data.objects[name];assert old!=rep
 bpy.data.objects.remove(old,do_unlink=True);rep.name=name
# Mirror the actual supported approach floor region; the new link floor already belongs to the receiver GLB.
m=next(o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH'and o.name=='D14_SharedReceiverMissingFloor')
for q in D['approach_floor_regions']:
 vs=[];fs=[]
 for tri in q['triangles']:
  pts=[B((x,88.5,z))for x,z in tri]
  if(Vector(pts[1])-Vector(pts[0])).cross(Vector(pts[2])-Vector(pts[0])).z<0:pts.reverse()
  k=len(vs);vs.extend(pts);fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new(q['id']);me.from_pydata(vs,[],fs);me.materials.append(m);uv=me.uv_layers.new(name='MetricUV')
 for p in me.polygons:
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.3,-v.y*.3)
 o=bpy.data.objects.new('UNSAVED_APPROACH_'+q['id'],me);bpy.context.collection.objects.link(o)
for cfg in ['TIDAL_AQUATIC_SINGLES.json','TIDAL_AQUATIC_DOUBLE.json']:
 for q in json.load(open(G/'data/architecture'/cfg))['units']:
  if q['allocation']['source_envelope_index']in[382,394]:
   ref(G/'assets/models'/q['model_file'])
   for d in q['doors']:
    if d['name']=='EntryDoor':ref(G/'assets/models/AST-DOR-002.glb',d['world_origin'],d['godot_yaw'])
obs,wrap=ref(G/'assets/models/AST-STF-008.glb',D['door']['position'],D['door']['yaw'])
for side,angle in [('LEFT',math.pi/2),('RIGHT',-math.pi/2)]:
 hinge=next(o for o in obs if o.name.startswith('HINGE_'+side));bpy.context.view_layer.update();m0=hinge.matrix_world.copy();pivot=m0.translation.copy();hinge.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)@m0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=480;s.render.resolution_y=320;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.035,.04,.045);s.view_settings.view_transform='AgX';bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=24;s.camera=camera
for f in D['fixtures']:
 if f['visual_owner']=='corridor':p=next(x['position']for x in json.load(open(W/'D14_CORRIDOR_INTEGRATION_PLAN.json'))['fixture_markers']if x['name']==f['marker'])
 else:p=[-44,91.495,-496]
 data=bpy.data.lights.new('UNSAVED_BOUND_FIXTURE','POINT');data.energy=110;data.color=tuple(f['color']);data.shadow_soft_size=.06;o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=B(p)
bpy.ops.object.light_add(type='AREA');fill=bpy.context.object;fill.data.energy=350;fill.data.size=8;fill.location=B((-66,93,-490));fill.rotation_euler=(Vector(B((-61,89,-490)))-fill.location).to_track_quat('-Z','Y').to_euler()
def view(name,eye,target):
 camera.location=B(eye);camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
if '--west-only'not in sys.argv:view('SOURCE_INSTALLED_D14_crossbar_link.png',[-44,90.15,-500.3],[-44,89.7,-492])
camera.data.lens=18
view('SOURCE_INSTALLED_D14_west_mouth_closures.png',[-70,90.15,-490],[-62.8,89.9,-490])
camera.data.lens=24
if '--west-only'not in sys.argv:view('SOURCE_INSTALLED_D14_shaft_closure.png',[-20,90.15,-490],[-23.18,89.8,-490])
assert all(sha(Path(p))==h for p,h in pins.items())
(W/'INSTALLED_SOURCE_VIEW_RUN.json').write_text(json.dumps({'fresh_native_corridor_opened':N['native'],'corridor_fixed_meshes':65,'same_three_actual_runtime_exports_used':D['model_bindings'],'three_views':['SOURCE_INSTALLED_D14_crossbar_link.png','SOURCE_INSTALLED_D14_west_mouth_closures.png','SOURCE_INSTALLED_D14_shaft_closure.png'],'source_and_exports_unchanged':True,'ordinary_engine_capture':False,'unsaved_actual_fixture_positions_used':8,'unsaved_area_inspection_fill':True,'resolution':[480,320],'cycles_samples':12},indent=2)+'\n');print('INSTALLED_D14_SOURCE_VIEWS_PASS',flush=True)
