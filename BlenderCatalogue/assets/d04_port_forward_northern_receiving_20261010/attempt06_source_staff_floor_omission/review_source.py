from pathlib import Path
import bpy,json,hashlib,bmesh
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'BUILD_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
native=W/P['native_file'];prior=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend';hull=R/'BlenderCatalogue/assets/lower_hull_body/source/AST-HUL-001.blend';staff=R/'BlenderCatalogue/assets/lower_staff_network/source/AST-STF-009.blend';pins={str(p.relative_to(R)):sha(p)for p in[native,prior,hull,staff]};bpy.ops.wm.open_mainfile(filepath=str(native));originals={o.name:o for o in bpy.data.objects};rigid=[]
for spec in P['source_fittings']:
 source=R/spec['source'];assert sha(source)==P['source_pins'][spec['source']]
 with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=a.objects
 obs=[o for o in b.objects if o]
 for o in obs:bpy.context.collection.objects.link(o)
 bpy.context.view_layer.update();T=Matrix.Translation(Vector(B(spec['origin'])))@Matrix.Rotation(spec['yaw'],4,'Z');count=0;worst=0.
 for o in obs:
  if o.type!='MESH':continue
  actual=originals.get(spec['prefix']+'__'+o.name)
  if actual is None:
   assert 'PreviewGround'in o.name or any(o.get(k,False)for k in['preview_only','presentation_only','exclude_from_production']),o.name;continue
  assert len(actual.data.vertices)==len(o.data.vertices),o.name
  for a,b in zip(actual.data.vertices,o.data.vertices):worst=max(worst,(actual.matrix_world@a.co-T@o.matrix_world@b.co).length)
  count+=1
 assert worst<.00005 and count>0,(spec['prefix'],worst,count);rigid.append({'prefix':spec['prefix'],'meshes':count,'max_world_vertex_error_m':worst,'original_native_sha256':sha(source),'rigid_no_rescaling':True})
 for o in obs:bpy.data.objects.remove(o,do_unlink=True)
owned=[]
for p in P['parts']:
 o=originals[p['name']];bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert bad==0 and volume>0,(p['name'],bad,volume);owned.append({'name':p['name'],'manifold':True,'positive_volume_m3':volume});bm.free()
(W/'SOURCE_RIGID_NATIVE_CHECK.json').write_text(json.dumps({'status':'PASS','native_sha256':sha(native),'owned_closed_manifold_parts':len(owned),'rigid_original_bindings':rigid,'parts':owned,'source_models_unchanged':True},indent=2)+'\n')
def append(path):
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
 return[o for o in b.objects if o]
old_objs=append(prior);hull_objs=append(hull);staff_objs=append(staff)
# Inspect genuine source at the current guarded phase. Hide hull side facets
# only in the unsaved diagnostic cutaway; originals stay unchanged.
for o in hull_objs:
 if o.name.startswith('HUL_LowerBand'):o.hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('D04NorthernDiagnosticWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for item in P['lights']:
 bpy.ops.object.light_add(type='AREA',location=B(item['at']));o=bpy.context.object;o.data.energy=220;o.data.size=2
images=[]
def view(name,at,target,lens=24,ortho=None):
 bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
view('SOURCE_NORTHERN_STREET.png',[-43.8,18.15,-364.8],[-44,18.0,-330],24)
view('SOURCE_NORTHERN_CARE_POCKET.png',[-47.2,18.15,-349.2],[-53.2,17.35,-348.7],24)
# Actual retained staff corridor remains opaque and uncut.
bpy.ops.object.light_add(type='AREA',location=B([-57,14.85,-338]));bpy.context.object.data.energy=180;bpy.context.object.data.size=2
view('SOURCE_RETAINED_STAFF_CORRIDOR.png',[-57,13.65,-340],[-57,13.65,-328],24)
# Unsaved section exposes support joints without pretending the roof is absent.
visibility={}
for o in originals.values():
 if o.type=='MESH'and o.get('category','')not in['keel_shoe','foundation_pier','lower_diagonal_brace','transfer_frame']:visibility[o]=o.hide_render;o.hide_render=True
for o in old_objs+staff_objs:visibility[o]=o.hide_render;o.hide_render=True
bpy.ops.object.light_add(type='AREA',location=B([-70,14,-325]));bpy.context.object.data.energy=2000;bpy.context.object.data.size=30
view('SOURCE_KEEL_TRANSFER_SECTION.png',[-85,17,-328],[-44,7,-328],24,48)
for o,v in visibility.items():o.hide_render=v
for p,h in pins.items():assert sha(R/p)==h,p
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'support_section_hides_surfaces_unsaved':True,'staff_original_unmodified':True,'ordinary_Godot_CRT_hardware_accepted':False},indent=2)+'\n');print('D04_NORTHERN_SOURCE_REVIEW_PASS')
