from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.load(open(W/'D14_SHARED_RECEIVER_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);pin={f:sha(W/f)for f in[N['receiving_native'],N['receiving_export'],N['named_patch_native'],N['named_patch_export']]}
bpy.ops.wm.open_mainfile(filepath=str(W/N['receiving_native']));assert sum(o.type=='MESH'for o in bpy.context.scene.objects)==22
native_context_count=0
def ref(path,at=(0,0,0),yaw=0,keep=None):
 global native_context_count
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.data.objects)-before;bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in obs}
 if keep is not None:
  for o in list(obs):
   if o.type!='MESH'or not keep(o):bpy.data.objects.remove(o,do_unlink=True);obs.remove(o)
  for o in obs:o.parent=None;o.matrix_world=worlds[o]
 wrap=bpy.data.objects.new('UNSAVED_REF_'+Path(path).stem,None);bpy.context.collection.objects.link(wrap)
 for o in obs:
  if o.parent not in obs:m=o.matrix_world.copy();o.parent=wrap;o.matrix_world=m
 wrap.location=B(at);wrap.rotation_euler.z=yaw;native_context_count+=len(obs);return obs,wrap
patchnames={x['mesh']for x in P['named_source_replacements']};F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';ref(F/'exports/AST-STF-G3-003.glb',keep=lambda o:'_D14_'in o.name and o.name not in patchnames)
street=json.load(open(R/'Game/data/architecture/TIDAL_AQUATIC_DOUBLE.json'));ref(R/'Game/assets/models'/street['street_model'],keep=lambda o:o.name not in patchnames);ref(W/N['named_patch_export'])
# Actual adopted D13 module below; no shaft extension context is fabricated.
ref(R/'Game/assets/models/AST-RES-TIDAL_D13_service_receiving_r001.glb')
units=[]
for cfg in ['TIDAL_AQUATIC_SINGLES.json','TIDAL_AQUATIC_DOUBLE.json']:
 for q in json.load(open(R/'Game/data/architecture'/cfg))['units']:
  if q['allocation']['source_envelope_index']in[382,394]:
   units.append(q);ref(R/'Game/assets/models'/q['model_file'])
   for d in q['doors']:
    if d['name']=='EntryDoor':ref(R/'Game/assets/models/AST-DOR-002.glb',d['world_origin'],d['godot_yaw'])
obs,wrap=ref(R/'Game/assets/models/AST-STF-008.glb',P['door_binding']['position'],P['door_binding']['yaw']);service=(obs,wrap)
m=next(o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH'and o.name=='D14_SharedReceiverMissingFloor')
def floor(q,name):
 vs=[];fs=[]
 for tri in q['triangles']:
  k=len(vs);pts=[B((x,q['floor_y'],z))for x,z in tri]
  if (Vector(pts[1])-Vector(pts[0])).cross(Vector(pts[2])-Vector(pts[0])).z<0:pts.reverse()
  vs.extend(pts);fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(m);uv=me.uv_layers.new(name='MetricUV')
 for p in me.polygons:
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.3,-v.y*.3)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
for q in json.load(open(R/'Game/data/architecture/TIDAL_D13_SERVICE_RECEIVING.json'))['floor_regions']:floor(q,'UNSAVED_D13_'+q['id'])
# Retained uninstalled D14 approach reference: triangulate it from its original source polygon using its native already-authored plan.
a=json.load(open(F/'source/TIDAL_STAFF_INTERFACE.json'));fp=next(q for q in a['floor_proposals']if q['deck']=='D14')
# The rectangle crossbar at this local junction is wholly inside the retained approach; context only, no floor successor exported.
q={'floor_y':88.5,'triangles':[[[-59.06,-501.94],[-19.06,-501.94],[-19.06,-498.06]],[[-59.06,-501.94],[-19.06,-498.06],[-59.06,-498.06]]]};floor(q,'UNSAVED_D14_LOCAL_APPROACH')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=480;s.render.resolution_y=320;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.045,.05,.06);s.view_settings.view_transform='AgX';bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=22;s.camera=camera
for at in[P['fixture']['position'],[-44,91.495,-500],[-44,86.995,-500]]:
 data=bpy.data.lights.new('UNSAVED_FIXTURE_QA','POINT');data.energy=110;data.shadow_soft_size=.08;o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=B(at)
bpy.ops.object.light_add(type='AREA');fill=bpy.context.object;fill.data.energy=900;fill.data.size=9;fill.location=B((-49,92,-490));fill.rotation_euler=(Vector(B((-44,87,-496)))-fill.location).to_track_quat('-Z','Y').to_euler()
def capture(name,eye,target):
 camera.location=B(eye);camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
capture('SOURCE_D14_closed_street_portal.png',[-44,90.15,-488],[-44,89.7,-495.4])
for side,angle in [('LEFT',math.pi/2),('RIGHT',-math.pi/2)]:
 hinge=next(o for o in obs if o.name.startswith('HINGE_'+side));bpy.context.view_layer.update();m0=hinge.matrix_world.copy();pivot=m0.translation.copy();hinge.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)@m0
capture('SOURCE_D14_open_link_portal.png',[-44,90.15,-497],[-44,89.7,-491])
capture('SOURCE_D14_under_link_receivers.png',[-48,86,-495],[-44,86.5,-497.3])
assert all(sha(W/f)==h for f,h in pin.items());assert all(sha(R/p)==h for p,h in P['source_pins'].items())
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'schema':1,'fresh_native_source_opened':N['receiving_native'],'three_views':['SOURCE_D14_closed_street_portal.png','SOURCE_D14_open_link_portal.png','SOURCE_D14_under_link_receivers.png'],'actual_source_contexts':native_context_count,'source_and_exports_unchanged':True,'qa_light_context':'one proposed real fixture plus two existing source fixture positions, unsaved area inspection fill','resolution':[480,320],'cycles_samples':12,'engine_view':False,'runtime_installed':False},indent=2)+'\n');print('D14_NATIVE_SOURCE_VIEWS_PASS',flush=True)
