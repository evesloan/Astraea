from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));spec=next(x for x in N['receiving_successors']if x['deck']==17);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);bpy.ops.wm.open_mainfile(filepath=str(W/spec['native']))
assert 'D17_UnfinishedShaftPhysicalClosure'not in bpy.data.objects
bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-STF-009_upper_tidal_envelope_r001.glb'))
for o in bpy.context.scene.objects:
 if o.type=='MESH'and('Roof'in o.name or 'TopCap'in o.name or o.name=='PortUpperFore_6'):o.hide_render=True
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-DOR-003.glb'));objects=[o for o in bpy.data.objects if o not in before];anchor=bpy.data.objects.new('UNSAVED_D17_INTERLOCKED_GATE',None);bpy.context.collection.objects.link(anchor)
for o in objects:
 if o.parent not in objects:o.parent=anchor
anchor.location=B((-23.08,102,-490));anchor.rotation_euler.z=-1.57079632679
d=json.load(open(R/'Game/data/architecture/TIDAL_D17_SERVICE_RECEIVING.json'));mat=next(o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH')
for q in d['floor_regions']:
 vs=[];fs=[]
 for tri in q['triangles']:
  k=len(vs);vs.extend(B((x,102,z))for x,z in tri);fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new('UNSAVED_D17_EXACT_FLOOR');me.from_pydata(vs,[],fs);me.materials.append(mat);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.world.color=(.05,.05,.05)
bpy.ops.object.camera_add(location=B((-15,109,-503)));c=bpy.context.object;c.rotation_euler=(Vector(B((-24,102,-490)))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=13;s.camera=c
bpy.ops.object.light_add(type='AREA',location=B((-12,113,-500)));l=bpy.context.object;l.data.energy=3500;l.data.size=20;l.rotation_euler=(Vector(B((-24,102,-490)))-l.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(W/'SOURCE_D17_INTERLOCKED_RECEIVING.png');bpy.ops.render.render(write_still=True);assert sha(W/spec['native'])==spec['native_sha256'];assert sha(W/spec['export'])==spec['export_sha256'];(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'rendered_for_review','native_and_export_unchanged':True,'view':'SOURCE_D17_INTERLOCKED_RECEIVING.png','temporary_source_context':'Exact retained upper envelope, D17 floor triangles and AST-DOR-003 closed gate; not saved','hidden_roofs_cap_fore_segment':'diagnostic cutaway only','runtime_visual_acceptance':False},indent=2)+'\n')
