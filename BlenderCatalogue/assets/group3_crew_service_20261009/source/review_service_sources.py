"""Bounded fresh-native source review of streets, riser and clinical collars."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def gv(p):return Vector((p[0],-p[2],p[1]))
def import_asset(asset):
    bpy.ops.import_scene.gltf(filepath=str(HERE/'exports'/f'{asset}.glb'));bpy.context.view_layer.update()
def bvh_actual():
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name.startswith('QA_'):continue
        o.data.calc_loop_triangles();base=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(verts,faces,all_triangles=True),len(verts),len(faces)
def screen(bvh,points):
    result=[]
    for p in points:
        distances=[bvh.find_nearest(gv([p[0],p[1]+h,p[2]]))[3]for h in [.31,.8,1.3,1.65]]
        result.append({'floor_point':p,'minimum_sampled_surface_distance_m':min(distances),'radius_m':.28,'pass':min(distances)>.28})
    return result
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100
scene.world.color=(.16,.16,.16);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
def setup_camera():
    bpy.ops.object.camera_add();o=bpy.context.object;scene.camera=o;return o
def capture(name,pos,target,ortho=None,hide_overhead=False):
    camera=scene.camera;camera.location=gv(pos);camera.rotation_euler=(gv(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'if ortho else'PERSP';camera.data.ortho_scale=ortho or 20;camera.data.lens=26;camera.data.clip_start=.04;camera.data.clip_end=1500
    for o in scene.objects:
        if o.type=='MESH' and o.name.startswith('overhead_'):o.hide_render=hide_overhead
    scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
def floor(b):
    x0,x1,y,z0,z1=b;bpy.ops.mesh.primitive_cube_add(size=1,location=gv([(x0+x1)/2,y-.04,(z0+z1)/2]));o=bpy.context.object;o.name='QA_CONTEXT_PROPOSED_FLOOR_NOT_EXPORTED';o.dimensions=(x1-x0,z1-z0,.08)
    m=bpy.data.materials.new('QA_floor');m.diffuse_color=(.24,.28,.28,1);o.data.materials.append(m)
reports=[]
import_asset('AST-STF-G3-001');bvh,nv,nt=bvh_actual()
points=[[86,12,-136],[82,12,-136],[90,12,-136],[-86,12,172],[-90,12,172],[57,12,-216],[-103,12,0],[103,12,0],[86,12,328],[-86,12,-328]]
checks=screen(bvh,points);reports.append({'asset':'AST-STF-G3-001','source_vertices':nv,'source_triangles':nt,'bounded_stationary_points':checks,'pass':all(q['pass']for q in checks)})
# Crop only after the full-native source geometry audit. All retained source remains unchanged.
for o in list(scene.objects):
    if o.type!='MESH':continue
    world=[o.matrix_world@Vector(c)for c in o.bound_box]
    if max(v.x for v in world)<75 or min(v.x for v in world)>97 or max(-v.y for v in world)<-152 or min(-v.y for v in world)>-119:bpy.data.objects.remove(o,do_unlink=True)
floor([78,94,12,-152,-119]);setup_camera()
capture('STREET_native_eye.png',[86,13.6,-149],[86,13.5,-128])
capture('STREET_native_porch_plan.png',[86,30,-136],[86,12,-136],28,True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
import_asset('AST-STF-G3-002');bvh,nv,nt=bvh_actual()
spec=json.loads((HERE/'source/STARBOARD_FORWARD_STAFF_RISER.json').read_text());points=[]
for q in spec['floor_proposals']:
    points.extend([[21,q['floor_y'],-490],[21,q['floor_y'],-495.5],[22.7,q['floor_y'],-490]])
checks=screen(bvh,points);reports.append({'asset':'AST-STF-G3-002','source_vertices':nv,'source_triangles':nt,'bounded_stationary_points':checks,'pass':all(q['pass']for q in checks),'moving_cabin_or_gate_checked':False})
for o in list(scene.objects):
    if o.type=='MESH' and min((o.matrix_world@Vector(c)).z for c in o.bound_box)>17:bpy.data.objects.remove(o,do_unlink=True)
floor([18.8,23.18,12,-496,-484]);setup_camera()
capture('RISER_D03_native_eye.png',[21,13.6,-496.5],[24,13.6,-490])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
import_asset('AST-MED-G3-001');bvh,nv,nt=bvh_actual()
spec=json.loads((HERE/'source/CLINICAL_TERMINALS.json').read_text());points=[]
for q in spec['terminal_interfaces']:
    a,b,c,d=q['external_collar_rect'];points.append([(a+b)/2,21,(c+d)/2])
checks=screen(bvh,points);reports.append({'asset':'AST-MED-G3-001','source_vertices':nv,'source_triangles':nt,'bounded_stationary_points':checks,'pass':all(q['pass']for q in checks),'retained_receiver_opened':False})
for o in list(scene.objects):
    if o.type!='MESH':continue
    world=[o.matrix_world@Vector(c)for c in o.bound_box]
    if max(v.x for v in world)<-58 or min(v.x for v in world)>-53 or max(-v.y for v in world)<-465 or min(-v.y for v in world)>-459:bpy.data.objects.remove(o,do_unlink=True)
floor([-58,-54,21,-465,-459]);setup_camera()
capture('CLINICAL_clean_collar_native_eye.png',[-59,22.6,-461.5],[-54,22.5,-462])
for report in reports:report['glb_sha256']=hashlib.sha256((HERE/'exports'/f'{report["asset"]}.glb').read_bytes()).hexdigest()
out={'status':'PASS'if all(r['pass']for r in reports)else'FAIL','reports':reports,'scope':'Actual imported native source mesh-distance screens and neutral source images. QA floors are proposed context only. No actual-main runtime, moving cart/cabin/gate, species, sterile-flow or final-art acceptance.'}
(HERE/'qa/SERVICE_NATIVE_GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['status']=='PASS'
