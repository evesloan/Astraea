"""Bounded fresh-native Tidal service source review; house remains unchanged."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(HERE/'exports/AST-STF-G3-003.glb'));bpy.context.view_layer.update()
def gv(p):return Vector((p[0],-p[2],p[1]))
verts=[];faces=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    o.data.calc_loop_triangles();base=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True)
spec=json.loads((HERE/'source/TIDAL_STAFF_INTERFACE.json').read_text());checks=[]
for q in spec['floor_proposals']:
    y=q['floor_y']
    for x,z in [(-21,-490),(-21,-500),(-33,-500),(-45,-500),(-61,-500),(-61,-493),(-61,-487),(-62.5,-493),(-62.5,-487)]:
        distances=[bvh.find_nearest(gv([x,y+h,z]))[3]for h in [.31,.8,1.3,1.65]]
        checks.append({'deck':q['deck'],'floor_point':[x,y,z],'minimum_native_surface_distance_m':min(distances),'pass':min(distances)>.28})
report={'status':'PASS'if all(q['pass']for q in checks)else'FAIL','bounded_native_stationary_witnesses':checks,'source_triangles':len(faces),'glb_sha256':hashlib.sha256((HERE/'exports/AST-STF-G3-003.glb').read_bytes()).hexdigest(),'retained_cap_opened':False,'existing_lift_or_house_modified':False,'scope':'New native source only; proposed floors, exact existing cap derivative, actual-main lift/door movement and root-owned house receivers remain held.'}
(HERE/'qa/TIDAL_STAFF_NATIVE_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[q for q in checks if not q['pass']]}));assert report['status']=='PASS'
# Remove other levels only from the transient review scene, then inspect D13 edge.
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    world=[o.matrix_world@Vector(c)for c in o.bound_box]
    if max(v.z for v in world)<84 or min(v.z for v in world)>87.35:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1,location=gv([-61,83.96,-492]));o=bpy.context.object;o.name='QA_PROPOSED_FLOOR_NOT_EXPORTED';o.dimensions=(3.6,16,.08)
m=bpy.data.materials.new('QA_floor');m.diffuse_color=(.24,.28,.28,1);o.data.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100;scene.world.color=(.16,.16,.16);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.location=gv([-61,85.6,-497]);camera.rotation_euler=(gv([-62.8,85.3,-492.4])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=26;camera.data.clip_start=.04;camera.data.clip_end=200;scene.render.filepath=str(HERE/'qa/TIDAL_staff_receiver_native_eye.png');bpy.ops.render.render(write_still=True)
