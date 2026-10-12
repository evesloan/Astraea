"""Real retained source street review; temporary clipping/cameras, no saved source edits."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
pins={};imports=[]
def gv(p):return Vector((p[0],-p[2],p[1]))
def import_pose(path,position=(0,0,0),yaw=0):
 pins[str(path.relative_to(ROOT))]=sha(path);before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.context.scene.objects)-before
 pose=Matrix.Translation(gv(position))@Matrix.Rotation(yaw,4,'Z')
 for o in new:
  if o.parent not in new:o.matrix_world=pose@o.matrix_world
 bpy.context.view_layer.update();imports.append(dict(path=str(path.relative_to(ROOT)),position=position,yaw=yaw,meshes=sum(o.type=='MESH'for o in new)));return new
def camera(eye,target,ortho=None,lens=22):
 d=bpy.data.cameras.new('SourceReviewCamera');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=gv(eye);o.rotation_euler=(gv(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=2000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 bpy.context.scene.camera=o
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('NeutralSourceReviewWorld');scene.world.color=(.21,.23,.25)
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.45;scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.05;scene.display.shading.curvature_valley_factor=.5;scene.display.shading.background_type='WORLD';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=1.1;scene.view_settings.gamma=1
for namespace,descriptor in [('group3_completion_20261011','D03_PRECINCT.json'),('group3_completion_20261011','LABELLED_BANK.json'),('group3_d03_streets_20261011','STREETS.json')]:
 f=ROOT/'Game/data/architecture'/namespace/descriptor
 if not f.exists()and descriptor=='D03_PRECINCT.json':f=ROOT/'Game/data/architecture'/namespace/'PRECINCT.json'
 p=json.load(open(f));pins[str(f.relative_to(ROOT))]=sha(f)
 for model,h in p['model_pins'].items():
  path=ROOT/'Game/assets/models'/namespace/model;assert sha(path)==h;import_pose(path)
 for q in p.get('service_doors',[]):import_pose(ROOT/'Game/assets/models/AST-STF-008.glb',q['position'],q['yaw'])
manifest=ROOT/'Game/data/architecture/crew_batch/runtime_manifest.json';pins[str(manifest.relative_to(ROOT))]=sha(manifest)
for q in json.load(open(manifest))['sections']:
 if q['programme']not in['D03_directory_05','D03_directory_06']:continue
 path=ROOT/'Game/assets/models'/q['model_file'];assert sha(path)==q['runtime_sha256'];import_pose(path,q['placement'])
# Retained D04 piers/bearings are exact context, regionally clipped below D04.
for model in ['D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb','D04_STARBOARD_CENTRAL_COMBINEDSTRUCTURE_r001.glb','D04_PORT_CENTRAL_HOME_905_r001.glb','D04_STARBOARD_CENTRAL_HOME_914_r001.glb']:import_pose(ROOT/'Game/assets/models'/model)
# Original physical floor triangles provide neutral context; no invented slab.
f=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/extensions/d03_remaining_streets_physical_batch023/source/RETAINED_PHYSICAL_FLOOR_SURVEY.json';pins[str(f.relative_to(ROOT))]=sha(f);floor=json.load(open(f));vertices=[];faces=[]
for t in floor['triangles']:
 if max(v[0]for v in t)<-110 or min(v[0]for v in t)>110 or max(v[1]for v in t)<-160 or min(v[1]for v in t)>55:continue
 k=len(vertices);vertices.extend(tuple(gv((x,12,z)))for x,z in t);faces.append((k,k+1,k+2))
mesh=bpy.data.meshes.new('ExactRetainedPhysicalFloorContext');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('NeutralRetainedCollisionFloorContext');m.diffuse_color=(.52,.54,.55,1);mesh.materials.append(m)
# Restrict the depicted district. All modifications are in-memory diagnostics.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
 for point,norm in [((-110,0,0),(1,0,0)),((110,0,0),(-1,0,0)),((0,-55,0),(0,1,0)),((0,160,0),(0,-1,0)),((0,0,11.75),(0,0,1)),((0,0,15.4),(0,0,-1))]:
  normal=(o.matrix_world.to_3x3().transposed()@Vector(norm)).normalized();bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=inv@Vector(point),plane_no=normal,clear_inner=True,dist=.000001)
 bm.to_mesh(o.data);bm.free()
 if not o.data.polygons:o.hide_render=True
# Wide context uses a clearly declared roof/wall cutaway; ordinary-eye view
# first retains the complete street roof to inspect its actual proportions.
camera((87,13.65,-146),(87,13.6,-85),lens=22);scene.render.filepath=str(HERE/'qa/D03_NEW_STREET_ORDINARY_EYE002.png');bpy.ops.render.render(write_still=True)
for o in list(bpy.context.scene.objects):
 if o.type!='MESH'or o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data);normal=(o.matrix_world.to_3x3().transposed()@Vector((0,0,-1))).normalized();bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=o.matrix_world.inverted()@Vector((0,0,14.6)),plane_no=normal,clear_inner=True,dist=.000001);bm.to_mesh(o.data);bm.free()
 if not o.data.polygons:o.hide_render=True
camera((230,210,-290),(0,12,-54),ortho=330);scene.render.filepath=str(HERE/'qa/D03_NEW_STREETS_CENTRAL_CONTEXT002.png');bpy.ops.render.render(write_still=True)
for f,h in pins.items():assert sha(ROOT/f)==h,f
q=dict(status='REAL_SOURCE_VIEWS_RENDERED_AWAITING_INSPECTION',renderer='Blender4.3.2 Workbench, original packed texture payloads, neutral studio illumination',source_pins=pins,imports=imports,photos=['D03_NEW_STREET_ORDINARY_EYE002.png','D03_NEW_STREETS_CENTRAL_CONTEXT002.png'],depicted_region_xz=[-110,110,-160,55],ordinary_eye_height_above_floor_m=1.65,wide_context_transient_cutaway_top_y=14.6,exact_retained_physical_floor_triangles_with_neutral_review_surface=True,source_native_GLB_or_Game_files_saved_or_modified=False,new_geometry_or_capacity_or_IDs_added=False,original_13_failed_network_criteria_unchanged=True,full_ship_in_game_CRT_hardware_or_final_art_accepted=False)
(HERE/'qa/SOURCE_VIEW_METHOD.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['status','photos','source_native_GLB_or_Game_files_saved_or_modified']}))
