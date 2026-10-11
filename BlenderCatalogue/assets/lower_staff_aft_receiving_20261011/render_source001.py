from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pins={f:sha(R/f)for f in P['source_pins']}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(W/P['structure']['native']),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
#Generate the selected context directly from unchanged runtime structural triangles and rings.
for region in json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions']:
 if region['id']not in ['D01_aft_apron','D01_port_service_spine','D01_central_service_axis','D02_aft_apron']:continue
 verts=[];faces=[];y=region['floor_y'];thickness=region['thickness']
 for tri in region['triangles']:
  at=len(verts);verts += [(x,-z,y)for x,z in tri]+[(x,-z,y-thickness)for x,z in tri];faces += [(at,at+1,at+2),(at+5,at+4,at+3)]
 for ring in region['rings']:
  for i,a in enumerate(ring):
   b=ring[(i+1)%len(ring)];at=len(verts);verts += [(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-thickness),(a[0],-a[1],y-thickness)];faces.append((at,at+1,at+2,at+3))
 me=bpy.data.meshes.new(region['id']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(region['id'],me);bpy.context.collection.objects.link(ob);m=bpy.data.materials.new(region['id']+'_SourceGrey');m.diffuse_color=(.55,.59,.58,1);me.materials.append(m)
for index,spec in enumerate(P['service_doors']):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-STF-008.glb'));new=set(bpy.data.objects)-before
 #Apply the same original-controller fully open hinge end pose,not a changed fitting.
 for ob in new:
  if ob.name.startswith('HINGE_LEFT'):ob.rotation_euler.z=1.5707963267948966
  if ob.name.startswith('HINGE_RIGHT'):ob.rotation_euler.z=-1.5707963267948966
 for ob in new:
  if ob.parent is None:ob.matrix_world=Matrix.Translation(Vector((spec['at'][0],-spec['at'][2],spec['at'][1])))@Matrix.Rotation(spec['yaw'],4,'Z')@ob.matrix_world
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral source context');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(-56.65,-77.45,1.72));o=bpy.context.object;o.data.lens=20;o.rotation_euler=(Vector((-48.5,-76,1.70))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_SHARED_LOWER_ROUTE_WIDE001.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN001.json').write_text(json.dumps({'status':'PASS_SOURCE_INPUTS_UNCHANGED','image':'SOURCE_SHARED_LOWER_ROUTE_WIDE001.png','mode':'Neutral Workbench actual source view','roofs_walls_floors_fixtures_and_original_threshold_fittings_retained':True,'door_pose':'Original controller fully open end pose for visibility;production connection ends closed','original_floor_context_from_unchanged_runtime_triangles_and_rings':True,'textures_game_lighting_full_ship_context_omitted':True,'ordinary_game_CRT_hardware_final_visual_acceptance':False},indent=2)+'\n')
