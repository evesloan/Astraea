from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'SHAFT_INTERFACE_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);bpy.ops.wm.open_mainfile(filepath=str(W/N['envelope']['native']))
for spec in P['sill_gate_interfaces']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-DOR-003.glb'));objects=[o for o in bpy.data.objects if o not in before];parents=[o for o in objects if o.parent not in objects];anchor=bpy.data.objects.new('UNSAVED_HeldGate_D'+str(spec['deck']),None);bpy.context.collection.objects.link(anchor)
 for o in parents:o.parent=anchor
 anchor.location=B(spec['gate_center']);anchor.rotation_euler.z=spec['gate_yaw']
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.world.color=(.05,.05,.05)
bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';s.camera=c
bpy.ops.object.light_add(type='AREA');l=bpy.context.object;l.location=B((-13,108,-499));l.data.energy=4500;l.data.size=25;l.rotation_euler=(Vector(B((-25,83,-490)))-l.location).to_track_quat('-Z','Y').to_euler()
views=[]
for name,eye,target,scale,res in [('SOURCE_UPPER_SHAFT_OVERVIEW',(-6,94,-512),(-25,80,-490),58,(480,640)),('SOURCE_D17_HELD_GATE_SILL_CUTAWAY',(-15,109,-503),(-24,102,-490),13,(640,480))]:
 if 'CUTAWAY'in name:
  bpy.data.objects['ForwardStaffUpperMissingOnlyTopCap'].hide_render=True
  bpy.data.objects['PortUpperFore_6'].hide_render=True
  d=json.load(open(R/'Game/data/architecture/TIDAL_D17_SERVICE_RECEIVING.json'));mat=next(o.data.materials[0]for o in bpy.data.objects if o.type=='MESH')
  for q in d['floor_regions']:
   vs=[];fs=[]
   for tri in q['triangles']:
    p=[B((x,102,z))for x,z in tri];k=len(vs);vs.extend(p);fs.append((k,k+1,k+2))
   me=bpy.data.meshes.new('UNSAVED_D17_Floor');me.from_pydata(vs,[],fs);me.materials.append(mat);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
 c.location=B(eye);c.rotation_euler=(Vector(B(target))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(W/(name+'.png'));bpy.ops.render.render(write_still=True);views.append(name+'.png')
assert all(sha(W/N[k][t])==N[k][t+'_sha256']for k in ['envelope','cap_patch']for t in ['native','export']);(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'rendered_for_review','views':views,'native_and_exports_unchanged':True,'temporary_geometry':'Five unchanged AST-DOR-003 gate instances and exact D17 floor triangles; not saved','cutaway_hidden':['new top cap','upper fore wall segment6'],'runtime_visual_acceptance':False},indent=2)+'\n')
