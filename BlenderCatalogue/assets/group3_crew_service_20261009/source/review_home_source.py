"""Fresh native-import source checks and bounded source visual review only."""
from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
spec=json.loads((HERE/'source/CREW_BANK_HOME.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def gv(p):return Vector((p[0],-p[2],p[1]))
def import_asset(path,position=(0,0,0),yaw=0,prefix=''):
    before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    added=set(bpy.context.scene.objects)-before
    transform=Matrix.Translation(gv(position))@Matrix.Rotation(yaw,4,'Z')
    for o in added:
        if o.parent not in added:o.matrix_world=transform@o.matrix_world
        o.name=prefix+o.name
    return added
import_asset(HERE/'exports/AST-CRW-G3-001.glb',prefix='Shell_')
for bed in spec['beds']:
    pos=bed['position'];yaw=bed['yaw'];prefix='Rest'+bed['local_place']+'_'
    import_asset(ROOT/'BlenderCatalogue/assets/crew_rest/exports/AST-CRW-001.glb',pos,yaw,prefix)
    import_asset(ROOT/'BlenderCatalogue/assets/crew_rest/exports/AST-CRW-002.glb',bed['curtain_position'],bed['curtain_yaw'],prefix+'Curtain_')
    # The reading module mounts to the existing frame, using its actual contract.
    t=Vector((-.26,.88,-2.14));c=math.cos(yaw);s=math.sin(yaw)
    mounted=[pos[0]+c*t.x+s*t.z,pos[1]+t.y,pos[2]-s*t.x+c*t.z]
    import_asset(ROOT/'BlenderCatalogue/assets/crew_personal/exports/AST-CRW-004.glb',mounted,yaw,prefix+'Reading_')
for i,s in enumerate(spec['storage']):import_asset(ROOT/'BlenderCatalogue/assets/crew_personal/exports/AST-CRW-003.glb',s['position'],s['yaw'],f'Storage{i}_')
bpy.context.view_layer.update()
# Construct actual imported mesh BVH. No proxy obstacles participate in checks.
verts=[];faces=[];mesh_count=0
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    mesh_count+=1;o.data.calc_loop_triangles();base=len(verts)
    verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    faces.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True)
points=[(5.5,0),(4.8,0),(3.5,0),(0,0),(-.8,0),(-1.45,-2.3),(-1.45,2.3),(3.5,-1.9),(2.8,-2.3),(4.2,-2.3),(3.2,2.0)]
clear=[]
for x,z in points:
    distances=[]
    for y in [.31,.8,1.3,1.65]:
        result=bvh.find_nearest(gv((x,y,z)))
        distances.append(result[3])
    clear.append({'xz':[x,z],'sampled_min_surface_distance_m':min(distances),'radius_m':.28,'pass':min(distances)>.28})
# Native foot/floor contacts for the retained frame and personal storage.
contacts=[]
for bed in spec['beds']:
    # Frame lowest vertices are physically on the proposed floor plane.
    vv=[(o.matrix_world@v.co).z for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Rest'+bed['local_place']+'_') and 'Curtain' not in o.name and 'Reading' not in o.name for v in o.data.vertices]
    contacts.append({'place':bed['local_place'],'lowest_actual_native_vertex_y':min(vv),'floor_contact_pass':abs(min(vv))<.0001})
for i in range(2):
    vv=[(o.matrix_world@v.co).z for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(f'Storage{i}_') for v in o.data.vertices]
    contacts.append({'place':f'storage{i}','lowest_actual_native_vertex_y':min(vv),'floor_contact_pass':abs(min(vv))<.0001})
report={'status':'PASS' if all(q['pass']for q in clear) and all(q['floor_contact_pass']for q in contacts)else'FAIL','native_meshes':mesh_count,'native_triangles':len(faces),'bounded_stationary_clearance_points':clear,'native_floor_contacts':contacts,'shell_and_fittings_bounds_godot':[min(v.x for v in verts),max(v.x for v in verts),min(v.z for v in verts),max(v.z for v in verts),min(-v.y for v in verts),max(-v.y for v in verts)],'input_glb_sha256':hashlib.sha256((HERE/'exports/AST-CRW-G3-001.glb').read_bytes()).hexdigest(),'scope':'Native source-only distance/contact screen against actual meshes. Floor is a proposal. No actual-main runtime, traversal, species or final visual acceptance.'}
(HERE/'qa/HOME_NATIVE_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
# QA floor and reviewer lamps are contextual only, never exported.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.04));floor=bpy.context.object;floor.name='QA_CONTEXT_PROPOSED_FLOOR_NOT_EXPORTED';floor.dimensions=(12,9.5,.08)
m=bpy.data.materials.new('QA_floor');m.diffuse_color=(.24,.28,.28,1);floor.data.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=768;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.world.color=(.16,.16,.16);scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.7;scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera
def capture(name,pos,target,ortho=None,hide_shell=False):
    camera.location=gv(pos);direction=gv(target)-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'if ortho else'PERSP';camera.data.ortho_scale=ortho or 12;camera.data.lens=26;camera.data.clip_start=.04;camera.data.clip_end=80
    for o in scene.objects:
        if o.type=='MESH' and o.name.startswith('Shell_overhead_'):o.hide_render=hide_shell
    scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
capture('HOME_fitted_plan.png',(0,11,0),(0,0,0),13,True)
capture('HOME_fitted_eye.png',(5.45,1.6,.7),(-2.3,1.2,-1.9),None,False)
capture('HOME_activity_eye.png',(.2,1.6,.4),(3.1,1.1,3.35),None,False)
print('SOURCE_REVIEW_OUTPUT_COMPLETE')
