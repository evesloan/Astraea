"""Wide real native source views; temporary cameras only, no exported-source modification."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];PRE=HERE
DOOR_ONLY='door_context_only'in sys.argv
def gv(p):return Vector((p[0],-p[2],p[1]))
def setup():
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH'
 s.render.resolution_x=1680;s.render.resolution_y=1050;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.film_transparent=False
 s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.45
 s.display.shading.color_type='TEXTURE';s.display.shading.show_shadows=False
 s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
 s.display.shading.curvature_ridge_factor=1.1;s.display.shading.curvature_valley_factor=.65
 s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD'
 s.world.color=(.18,.2,.23);s.view_settings.view_transform='Standard'
 s.view_settings.look='None';s.view_settings.exposure=1.35;s.view_settings.gamma=1
def camera(eye,target,lens=24,ortho=None):
 d=bpy.data.cameras.new('QA_WideSourceCamera');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o)
 o.location=gv(eye);o.rotation_euler=(gv(target)-o.location).to_track_quat('-Z','Y').to_euler()
 d.lens=lens;d.clip_start=.05;d.clip_end=1000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 bpy.context.scene.camera=o
def import_pose(path,position=(0,0,0),yaw=0,opened=False):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.context.scene.objects)-before
 pose=Matrix.Translation(gv(position))@Matrix.Rotation(yaw,4,'Z')
 for o in new:
  if o.parent not in new:o.matrix_world=pose@o.matrix_world
 if opened:
  for o in new:
   if 'HINGE_LEFT'in o.name:o.rotation_mode='XYZ';o.rotation_euler.z+=math.pi/2
   if 'HINGE_RIGHT'in o.name:o.rotation_mode='XYZ';o.rotation_euler.z-=math.pi/2
 bpy.context.view_layer.update()
 return new
def render(folder,name):
 bpy.context.scene.render.filepath=str(folder/'qa'/name);bpy.ops.render.render(write_still=True)


import bmesh,hashlib
pins={str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest()for f in (HERE/'exports').glob('*.glb')}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);setup()
for name in ['AST-MED-G3-007.glb','AST-MED-G3-008.glb','AST-MED-G3-010.glb']:import_pose(HERE/'exports'/name)
data=json.load(open(ROOT/'Game/data/architecture/received_sections.json'));room=next(q for q in data['sections']if q['programme_key']=='D05_directory_08')
asset=ROOT/'Game/assets/models'/room['model_file'];assert hashlib.sha256(asset.read_bytes()).hexdigest()==room['source_sha256']
import_pose(asset,room['translation_xyz'],room['rotation_y'])
# Exact retained quiet-care slab is contextual geometry, not a new floor.
region=next(q for q in json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))['regions']if q['id']=='D05_directory_08_authored_floor')
verts=[];faces=[];y=region['floor_y'];lo=y-region['thickness']
for tri in region['triangles']:
 t=list(tri);area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(t,t[1:]+t[:1]))
 if area>0:t.reverse()
 k=len(verts);verts.extend([tuple(gv((x,lo,z)))for x,z in t]+[tuple(gv((x,y,z)))for x,z in t]);faces.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
for ring in region['rings']:
 for a,b in zip(ring,ring[1:]+ring[:1]):
  k=len(verts);verts.extend([tuple(gv((a[0],lo,a[1]))),tuple(gv((b[0],lo,b[1]))),tuple(gv((b[0],y,b[1]))),tuple(gv((a[0],y,a[1])))]);faces.append((k,k+1,k+2,k+3))
me=bpy.data.meshes.new('ExactRetainedQuietCareSlabContext');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
m=bpy.data.materials.new('NeutralDiagnosticOriginalSlabContext');m.diffuse_color=(.52,.54,.54,1);me.materials.append(m)
# Transient regional source clip and overhead cutaway. No source is saved.
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
 for point,norm in [((37,0,0),(1,0,0)),((81,0,0),(-1,0,0)),((0,-269,0),(0,1,0)),((0,-219,0),(0,-1,0)),((0,0,20.76),(0,0,1)),((0,0,25.35),(0,0,-1))]:
  normal=(o.matrix_world.to_3x3().transposed()@Vector(norm)).normalized()
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=inv@Vector(point),plane_no=normal,clear_inner=True,dist=.000001)
 bm.to_mesh(o.data);bm.free()
 if not o.data.polygons:o.hide_render=True
 if str(o.name).startswith('overhead_'):o.hide_render=True
camera((84,64,215),(59,21,244),24,72)
render(HERE,'CLINICAL_DIRECTORY08_WIDE_SOURCE.png')
for f,h in pins.items():assert hashlib.sha256((HERE/f).read_bytes()).hexdigest()==h
(HERE/'qa/SOURCE_VIEW_METHOD.json').write_text(json.dumps(dict(renderer='Blender4.3.2 Workbench with original packed textures and neutral diagnostic illumination',photos=['CLINICAL_DIRECTORY08_WIDE_SOURCE.png'],real_native_geometry=True,original_medical_programme='D05_directory_08',original_medical_model_sha256=room['source_sha256'],source_or_export_files_saved_or_modified=False,transient_regional_clip_and_roof_cutaway=True,exact_retained_quiet_care_slab_context_with_neutral_material=True,final_game_CRT_hardware_species_or_medical_acceptance=False),indent=2)+'\n')
