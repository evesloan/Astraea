"""Fresh source branch with precisely substituted retained spine cells."""
from pathlib import Path
import bpy,bmesh,hashlib,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
FIRST=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009'
patch=json.loads((HERE/'source/D03_SPINE_RECEIVER_PATCH.json').read_text());support=json.loads((HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json').read_text())
binding=json.loads((FIRST/'extensions/port2_clinical_batch006/qa/CABIN_BINDING_AUDIT.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
def gv(p):return Vector((p[0],-p[2],p[1]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(p));return [o for o in bpy.context.scene.objects if o not in before]
def bvh_for(objects):
    vs,fs=[],[]
    for o in objects:
        if o.type!='MESH':continue
        o.data.calc_loop_triangles();base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs,fs
oldpath=ROOT/'BlenderCatalogue'/patch['predecessor']['runtime_export_path'];assert sha(oldpath)==patch['predecessor']['runtime_export_sha256']
old=load(oldpath);oldcount=sum(o.type=='MESH'for o in old);assert oldcount==281
selected=[]
for name in patch['native_mesh_batches_to_omit_only_during_root_adoption']:
    matches=[o for o in old if o.name==name];assert len(matches)==1;selected.extend(matches)
bpy.context.view_layer.update();beforebvh,_,_=bvh_for(selected)
omitted=[o.name for o in selected]
for o in selected:old.remove(o);bpy.data.objects.remove(o,do_unlink=True)
portpath=FIRST/'extensions/port2_clinical_batch006/exports/AST-STF-G3-006.glb';riser=load(portpath)
branchpath=HERE/'exports/AST-STF-G3-007.glb';branch=load(branchpath)
patchpath=HERE/'exports/AST-STF-G3-008.glb';replacement=load(patchpath)
assert {o.name for o in replacement if o.type=='MESH'}==set(omitted)
assert {o.data.materials[0].name.split('.')[0]for o in replacement if o.type=='MESH'}=={'ASTRAEA_'+q for q in patch['runtime_batch_name_by_role']}
cabinpath=ROOT/binding['retained_cabin_export'];assert sha(cabinpath)==binding['retained_cabin_export_sha256'];cabin=load(cabinpath)
parent=bpy.data.objects.new('Exact17Cabin_D03_CONTEXT_ONLY',None);bpy.context.collection.objects.link(parent)
for o in cabin:
    if o.parent not in cabin:o.parent=parent
parent.location=gv([-23.2,12,-283]);parent.rotation_euler.z=math.pi/2
bpy.context.view_layer.update();bvh,vs,fs=bvh_for(bpy.context.scene.objects);afterbvh,_,_=bvh_for(replacement)
checks=[]
for q in support['bounded_floor_footprints']:
    p=q['floor_point'];ds=[bvh.find_nearest(gv([p[0],p[1]+h,p[2]]))[3]for h in [.31,.8,1.3,1.65]]
    checks.append({'floor_point':p,'radius_m':.28,'minimum_native_surface_distance_m':min(ds),'pass':min(ds)>.28})
retained=[]
for x in [-58.8,-55.2]:
    for z in [-297,-290,-282]:
        for y in [12.4,13.8]:
            p=[x,y,z];a=beforebvh.find_nearest(gv(p))[3];b=afterbvh.find_nearest(gv(p))[3];retained.append({'retained_wall_face_point':p,'old_native_distance_m':a,'successor_native_distance_m':b,'pass':max(a,b)<.002})
for p in [[-55.2,14.9,-293],[-55.326,15.0,-292]]:
    a=beforebvh.find_nearest(gv(p))[3];b=afterbvh.find_nearest(gv(p))[3];retained.append({'retained_lintel_or_joint_point':p,'old_native_distance_m':a,'successor_native_distance_m':b,'pass':max(a,b)<.002})
mouth=[]
for p in [[-55.26,13.3,-293],[-55.345,12.8,-293],[-55.323,13.8,-292]]:
    a=beforebvh.find_nearest(gv(p))[3];b=afterbvh.find_nearest(gv(p))[3];mouth.append({'bounded_opening_point':p,'before_native_surface_distance_m':a,'after_native_surface_distance_m':b,'pass':a<.07 and b>.28})
join=[];branchbvh,_,_=bvh_for(branch)
for z in [-294.8,-291.2]:
    for y in [12.5,14.0]:
        p=[-55.2,y,z];a=branchbvh.find_nearest(gv(p))[3];b=afterbvh.find_nearest(gv(p))[3];join.append({'receiver_shared_edge_point':p,'new_branch_distance_m':a,'retained_patch_distance_m':b,'pass':max(a,b)<.002})
roofbvh,_,_=bvh_for([o for o in branch if o.type=='MESH'and o.get('category')=='overhead']);housingbvh,_,_=bvh_for([o for o in branch if o.type=='MESH'and o.get('role')=='staff_zinc'])
fixtures=[]
for x,z in [(-21,-291),(-31,-293),(-41,-293),(-51,-293)]:
    p=[x,15.2,z];a=roofbvh.find_nearest(gv(p))[3];b=housingbvh.find_nearest(gv(p))[3];fixtures.append({'housing_roof_point':p,'roof_distance_m':a,'housing_distance_m':b,'pass':max(a,b)<.002})
allchecks=checks+retained+mouth+join+fixtures;passed=all(q['pass']for q in allchecks)
report={'status':'PASS'if passed else'FAIL','new_export_sha256':{p.name:sha(p)for p in [branchpath,patchpath]},'retained_context_export_sha256':{p.name:sha(p)for p in [oldpath,portpath,cabinpath]},'exact_transient_original_nodes_omitted':omitted,'other_retained_native_spine_meshes_unchanged':277,'source_stationary_clearance_witnesses':checks,'unchanged_native_wall_lintel_joint_surfaces':retained,'bounded_receiver_opening_witnesses':mouth,'native_new_branch_to_retained_patch_edge_contacts':join,'native_fixture_roof_contacts':fixtures,'fitted_triangles':len(fs),'existing_cart_stop_or_save_identities_modified':False,'scope':'Fresh source geometry in pinned lower spine and port2 context. Exactly four retained cell-role nodes substituted transiently. Stationary witnesses and contacts only; no working integration, floor, dynamic gate, boarding or full route acceptance.'}
(HERE/'qa/D03_BRANCH_NATIVE_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'stationary_witnesses':len(checks),'preserved_native_surfaces':len(retained),'opening_witnesses':len(mouth),'join_edge_contacts':len(join),'fixture_roof_contacts':len(fixtures),'failed':[q for q in allchecks if not q['pass']]}));assert passed
# Diagnostic floors exist only for source images, never saved or exported.
verts=[];faces=[]
for t in support['diagnostic_floor_triangles']:
    k=len(verts);verts.extend(gv([x,12,z])for x,z in t);faces.append((k,k+1,k+2))
me=bpy.data.meshes.new('HeldFloorComposite_QA_ONLY');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('HeldFloorComposite_QA_ONLY',me);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('HeldFloorComposite_QA_ONLY');m.diffuse_color=(.26,.3,.32,1);me.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100;scene.world.color=(.15,.15,.15);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.lens=24;cam.data.clip_start=.04;cam.data.clip_end=70
views=[('D03_port2_branch_from_lobby_native_eye.png',[-21,13.6,-286],[-21,13.4,-294]),('D03_port2_spine_receiver_native_eye.png',[-52,13.6,-293],[-58.5,13.4,-293]),('D03_retained_spine_to_branch_native_eye.png',[-57,13.6,-296.5],[-52,13.4,-293])]
for name,p,target in views:
    cam.location=gv(p);cam.rotation_euler=(gv(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data);remove=[f for f in bm.faces if min((obj.matrix_world@v.co).z for v in f.verts)>13.2 or max((obj.matrix_world@v.co).z for v in f.verts)<11.7];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(obj.data);bm.free()
cam.data.type='ORTHO';cam.data.ortho_scale=51;cam.data.clip_end=100;cam.location=gv([-40,60,-289]);cam.rotation_euler=(gv([-40,12,-289])-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa/D03_port2_branch_native_plan.png');bpy.ops.render.render(write_still=True)
