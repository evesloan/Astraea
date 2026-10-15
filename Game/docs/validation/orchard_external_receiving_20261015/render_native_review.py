from pathlib import Path
import bpy,json,hashlib,os
from mathutils import Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'native/ORCHARD_SERVICE_GATEWAY_r001.blend'));bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_RUNTIME_R001'].hide_render=True;col=bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_AUTHORING_R001'];col.hide_render=False
for o in col.objects:
 if 'SourceJoinedRoof'in o.name:o.hide_render=True
B=lambda p:Vector((p[0],-p[2],p[1]));before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(G/'assets/models/AST-DIN-008.glb'))
for o in set(bpy.data.objects)-before:
 if o.type!='MESH':continue
 if o.name in ['ORCH_PerimeterDado_1','ORCH_PerimeterWall_1']or'Ceiling'in o.name:bpy.data.objects.remove(o,do_unlink=True);continue
 o.matrix_world.translation+=B((8,61,-250))
# Original three receiving fixtures show the preserved clean/dry/used destinations inside the wall.
s=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());names=[m['name']for m in s['meshes']if m['unit']in ['CleanDelivery','DryDelivery','UsedReturn']]
with bpy.data.libraries.load(str(R/'BlenderCatalogue/assets/group8_orchard_service_20261011/OrchardService_r003.blend'),link=False)as(df,dt):dt.objects=names
for o in dt.objects:bpy.context.scene.collection.objects.link(o)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world=scene.world or bpy.data.worlds.new('ReviewWorld');scene.world.color=(.30,.33,.36);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';camdata=bpy.data.cameras.new('OrchardReceivingReview');camdata.type='ORTHO';camdata.ortho_scale=78;cam=bpy.data.objects.new('OrchardReceivingReview',camdata);scene.collection.objects.link(cam);cam.location=B((98,101,-155));cam.rotation_euler=(B((36,62,-200))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;out=D/'visual_review';out.mkdir(exist_ok=True);path=out/'ORCHARD_SERVICE_GATEWAY_NATIVE_CONTEXT.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);(out/'RECEIPT.json').write_text(json.dumps({'status':'NATIVE_CONTEXT_CUTAWAY_REVIEW_PENDING_PIXEL_INSPECTION','file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_sha256':r['native_sha256'],'source_geometry_originals_unchanged':True,'scope':'New receiving approach, exact wall successors and original Orchard architecture/three receiving fixtures. Roof and source ceilings hidden for cutaway. Other furnishings, runtime staff-door leaves and compiled axial floor outside native context omitted. Neutral BlenderWorkbench; no Game/CRT or final art admission.'},indent=2)+'\n');print('PASS_ORCHARD_NATIVE_CONTEXT_VIEW')
