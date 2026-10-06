"""One ordinary-eye composed source study, physical fixtures only, no hidden enclosure."""
from pathlib import Path
import bpy,json,hashlib,math,resource
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003');D=json.loads((R/'source/HOME_SPEC.json').read_text());Q=R/'qa/build_run001';OUT=Q/'home_dogleg_normal_eye.png';assert not OUT.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cv(v):return Vector((v[0],-v[2],v[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
inputs=[R/'exports/AST-STF-010_home_dogleg.glb',R/'exports/AST-STF-009_pool_market_home.glb'];pins={str(p):sha(p)for p in inputs}
for p in inputs:bpy.ops.import_scene.gltf(filepath=str(p))
# Explicit normal fully-open authored state. This previews the unchanged inherited
# two-leaf sequencing endpoint; no claim that runtime input has already been built.
left=bpy.data.objects['HOME_HINGE_LEFT'];right=bpy.data.objects['HOME_HINGE_RIGHT'];left.rotation_euler.z=math.pi/2;right.rotation_euler.z=-math.pi/2;bpy.context.view_layer.update()
# Preview the actual existing compiler owner triangles, not a room-sized new slab.
compiled=G/'data/generated/structural_meshes.json';pins[str(compiled)]=sha(compiled);data=json.loads(compiled.read_text());verts=[];faces=[];owners=[]
for rec in data['regions']:
 if abs(rec['floor_y']-12)>.001:continue
 included=False
 for tri in rec['triangles']:
  if max(p[0]for p in tri)<-59 or min(p[0]for p in tri)>-37 or max(p[1]for p in tri)<-437 or min(p[1]for p in tri)>-421:continue
  i=len(verts);verts.extend([cv((x,12,z))for x,z in tri]);faces.append((i,i+1,i+2));included=True
 if included:owners.append(rec['id'])
me=bpy.data.meshes.new('QA_EXISTING_COMPILER_D03');me.from_pydata(verts,[],faces);me.update();obj=bpy.data.objects.new('QA_EXISTING_COMPILER_D03',me);bpy.context.collection.objects.link(obj)
mat=bpy.data.materials.new('QA_retained_staff_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87;t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials/staff/staff_floor.png'));mat.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);me.materials.append(mat);uv=me.uv_layers.new(name='MetreScaled')
for li,l in enumerate(me.loops):
 p=me.vertices[l.vertex_index].co;uv.data[li].uv=(p.x/.8,p.y/.8)
# The adjacent route fixture is already sourced. The two new fixtures are exact
# translated housed derivatives; power is a source-view trial, not Godot energy.
light_rows=[{'name':'Retained_STF_D03_TaskFixture_034','xyz':[-51,15,-432],'watts':110,'source':'existing retained fixture'},*({'name':f['name'],'xyz':f['emitter_xyz'],'watts':110,'source':'new supported source fixture trial'}for f in D['fixtures'])]
for r in light_rows:
 d=bpy.data.lights.new(r['name']+'_VIEW','POINT');d.energy=r['watts'];d.color=(.82,.90,1);d.shadow_soft_size=.08;o=bpy.data.objects.new(r['name']+'_VIEW',d);bpy.context.collection.objects.link(o);o.location=cv(r['xyz'])
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0
cam=bpy.data.cameras.new('QA_NORMAL_EYE');co=bpy.data.objects.new('QA_NORMAL_EYE',cam);sc.collection.objects.link(co);sc.camera=co;cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=32/(2*math.tan(math.radians(65)/2));cam.clip_start=.05;cam.clip_end=70
# Supported receiving vestibule, ordinary1.65m eye, oblique enough to show the
# real jamb depth and the first leg of the private dogleg.
eye=[-51.9,13.65,-432.8];aim=[-44.4,13.7,-431.3];co.location=cv(eye);co.rotation_euler=(cv(aim)-co.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(OUT);bpy.ops.render.render(write_still=True)
assert all(sha(p)==h for p,h in pins.items())
receipt={'status':'SOURCE_COMPOSITION_REVIEW_PENDING','view':str(OUT),'sha256':sha(OUT),'eye_xyz':eye,'aim_xyz':aim,'eye_height_m':1.65,'vertical_fov_degrees':65,'door_state':'Fully open authored endpoint, unsaved source preview only','lights':light_rows,'world_strength':0,'hidden_walls_or_ceilings':False,'floor_owners_previewed':owners,'actual_existing_floor_triangles':len(faces),'inputs_unchanged':pins,'renderer':'Blender Cycles CPU24samples,2threads','exposure':0,'runtime_selection_or_energy_equivalence_claimed':False,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(Q/'SOURCE_VIEW_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
