from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'native/SYNTHESIS_EXTERNAL_LINKS_r001.blend'));bpy.data.collections['SYNTHESIS_EXTERNAL_RECEIVING_RUNTIME_R001'].hide_render=True;col=bpy.data.collections['SYNTHESIS_EXTERNAL_RECEIVING_AUTHORING_R001'];col.hide_render=False
for o in col.objects:
 if 'SourceJoinedRoof'in o.name:o.hide_render=True
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(G/'assets/models/G8_SYNTHESIS_PLANT_r002.glb'));source=json.loads((G/'data/architecture/group8/synthesis_plant.json').read_text());omit={b['name']for b in source['runtime_batches']if any('LocalRoof'in s for s in b['source_members'])}|{w['source_name']for w in r['walls']}
for o in set(bpy.data.objects)-before:
 if o.name in omit:bpy.data.objects.remove(o,do_unlink=True)
B=lambda p:Vector((p[0],-p[2],p[1]));floor=json.loads((G/'data/architecture/GROUP1_SYNTHESIS_SUPPORTING_FLOOR.json').read_text());tris=[t for region in floor['regions']for chunk in region['render_chunks']for t in chunk['triangles']];tris+=floor['actual_original_collider_triangles'];vs=[];fs=[]
for t in tris:
 ix=[]
 for x,z in t:ix.append(len(vs));vs.append(B((x,0,z)))
 fs.append(ix)
# Exact existing spine is a rectangle in the source region, with its central opening preserved.
regions=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions'];spine=next(r for r in regions if r['id']=='D01_port_service_spine')
for ring in spine['rings']:
 i=len(vs);vs.extend(B((x,0,z))for x,z in ring);fs.append(tuple(range(i,len(vs))))
mesh=bpy.data.meshes.new('ActualRetainedSourceFloorContext');mesh.from_pydata(vs,[],fs);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(obj);material=bpy.data.materials.new('RetainedFloorReview');material.diffuse_color=(.28,.31,.32,1);mesh.materials.append(material)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world=scene.world or bpy.data.worlds.new('ReviewWorld');scene.world.color=(.30,.33,.36);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';data=bpy.data.cameras.new('SynthesisReceivingReview');data.type='ORTHO';data.ortho_scale=90;camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);camera.location=B((-7,40,55));camera.rotation_euler=(B((-70,1,0))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;out=D/'visual_review';out.mkdir(exist_ok=True);path=out/'SYNTHESIS_SEPARATE_RECEIVING_NATIVE_CONTEXT.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);(out/'RECEIPT.json').write_text(json.dumps({'status':'NATIVE_CONTEXT_CUTAWAY_PENDING_PIXEL_REVIEW','file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_sha256':r['native_sha256'],'scope':'Two new links, exact wall successors, retained plant geometry and actual current supporting floor/spine. Source roof and new link roofs hidden; original bay/doors and wider ship omitted. Neutral BlenderWorkbench, no Game/CRT or final acceptance.'},indent=2)+'\n');print('PASS_SYNTHESIS_NATIVE_CONTEXT_VIEW')
