"""Fresh compact port2 exports in retained clinical context; bounded source QA."""
from pathlib import Path
import bpy, bmesh, hashlib, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parents[1]
ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
patch=json.loads((HERE/'source/CLINICAL_PORT2_RECEIVER_PATCH.json').read_text())
support=json.loads((HERE/'qa/REVIEW_SUPPORT.json').read_text())
binding=json.loads((HERE/'qa/CABIN_BINDING_AUDIT.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
def gv(p): return Vector((p[0],-p[2],p[1]))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.context.scene.objects if o not in before]
oldpath=Path(patch['predecessor']['export'])
assert sha(oldpath)==patch['predecessor']['export_sha256']
clinical=load(oldpath)
oldmeshcount=sum(o.type=='MESH' for o in clinical)
omitted=[]
for name in patch['native_mesh_batches_to_omit_only_during_root_adoption']:
    matches=[o for o in clinical if o.name==name and o.type=='MESH']
    assert len(matches)==1
    omitted.append(matches[0].name)
    clinical.remove(matches[0]); bpy.data.objects.remove(matches[0],do_unlink=True)
assert len(omitted)==2 and oldmeshcount==568
newpaths=[HERE/'exports'/n for n in ['AST-STF-G3-006.glb','AST-MED-G3-004.glb','AST-MED-G3-002_port2_receiver_patch.glb']]
newobjects=[]
for path in newpaths: newobjects.extend(load(path))
cabinpath=ROOT/binding['retained_cabin_export']
assert sha(cabinpath)==binding['retained_cabin_export_sha256']
cabin=load(cabinpath)
parent=bpy.data.objects.new('ExactRetained17Cabin_D05_CONTEXT_ONLY',None);bpy.context.collection.objects.link(parent)
for o in cabin:
    if o.parent not in cabin: o.parent=parent
parent.location=gv(binding['cabin_visual_origin_D05']); parent.rotation_euler.z=binding['cabin_visual_world_yaw']
bpy.context.view_layer.update()
def bvh_for(objects):
    vs,fs=[],[]
    for o in objects:
        if o.type!='MESH':continue
        o.data.calc_loop_triangles();base=len(vs)
        vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs,fs
bvh,vs,fs=bvh_for(bpy.context.scene.objects)
points=[q['floor_point'] for q in support['source_only_support_witnesses']]+[[-25,21,-283],[-21,12,-283],[-21,12,-289],[-21,102,-283],[-21,102,-289]]
checks=[]
for p in points:
    ds=[bvh.find_nearest(gv([p[0],p[1]+h,p[2]]))[3]for h in [.31,.8,1.3,1.65]]
    checks.append({'floor_point':p,'radius_m':.28,'minimum_native_surface_distance_m':min(ds),'pass':min(ds)>.28})
risermesh=[o for o in newobjects if o.type=='MESH' and o.get('source_asset')=='AST-STF-G3-006']
sillbvh,_,_=bvh_for([o for o in risermesh if o.get('category')=='landing_threshold'])
contacts=[]
for y in [12,21,102]:
    for z in [-284,-282]:
        p=[-23.1,y,z];d=sillbvh.find_nearest(gv(p))[3]
        contacts.append({'native_fixed_sill_surface':p,'distance_m':d,'pass':d<.002})
housingbvh,_,_=bvh_for([o for o in newobjects if o.type=='MESH' and o.get('source_asset')=='AST-MED-G3-004' and o.get('role')=='staff_zinc'])
roofbvh,_,_=bvh_for([o for o in newobjects+clinical if o.type=='MESH' and o.get('category')=='overhead'])
fixturechecks=[]
for x,z in [(-21,-291),(-21,-296),(-33,-293),(-45,-293),(-33,-297),(-45,-297),(-57,-297)]:
    p=[x,25.2,z];a=housingbvh.find_nearest(gv(p))[3];b=roofbvh.find_nearest(gv(p))[3]
    fixturechecks.append({'fixture_top_point':p,'housing_distance_m':a,'roof_distance_m':b,'pass':max(a,b)<.002})
allchecks=checks+contacts+fixturechecks
passed=all(q['pass'] for q in allchecks)
report={'status':'PASS' if passed else 'FAIL','new_export_hashes':{p.name:sha(p)for p in newpaths},'old_clinical_export_sha256':sha(oldpath),'retained_cabin_export_sha256':sha(cabinpath),'old_clinical_meshes':oldmeshcount,'exact_transient_omitted_native_nodes':omitted,'unmodified_other_clinical_meshes':oldmeshcount-2,'fresh_native_triangles':len(fs),'source_stationary_capsule_witnesses':checks,'actual_native_fixed_sill_surface_contacts':contacts,'actual_native_light_housing_roof_contacts':fixturechecks,'new_crossing_gates_instanced':False,'new_floor_installed':False,'scope':'Fresh native geometry in exact pinned context. The two held clinical replacement batches are substituted transiently for review only. Bounded stationary source witnesses and surface contacts, no dynamic gates, boarding, operational segregation, actual-main or route acceptance.'}
(HERE/'qa/PORT2_NATIVE_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'stationary_witnesses':len(checks),'sill_contacts':len(contacts),'fixture_roof_contacts':len(fixturechecks),'failed':[q for q in allchecks if not q['pass']]}))
assert passed
# Floors below are conspicuously diagnostic and never saved or exported.
verts=[];faces=[]
for t in support['diagnostic_floor_triangles']:
    k=len(verts);verts.extend(gv([x,21,z]) for x,z in t);faces.append((k,k+1,k+2))
me=bpy.data.meshes.new('HeldFloorComposite_QA_ONLY');me.from_pydata(verts,[],faces)
o=bpy.data.objects.new('HeldFloorComposite_QA_ONLY_NOT_INSTALLED',me);bpy.context.collection.objects.link(o)
m=bpy.data.materials.new('HeldFloorComposite_QA_ONLY');m.diffuse_color=(.26,.3,.32,1);me.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100
scene.world.color=(.15,.15,.15);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.lens=24;cam.data.clip_start=.04;cam.data.clip_end=70
views=[('Port2_D05_landing_to_header_native_eye.png',[-21,22.6,-286],[-21,22.4,-295]),('Port2_D05_clean_receiver_native_eye.png',[-54.6,22.6,-293],[-58,22.4,-294]),('Port2_D05_held_crossing_native_eye.png',[-52,22.6,-297],[-61,22.4,-297])]
for name,pos,target in views:
    cam.location=gv(pos);cam.rotation_euler=(gv(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
# Explicit transient D05 cutaway only. All saved native sources stay intact.
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    remove=[f for f in bm.faces if min((obj.matrix_world@v.co).z for v in f.verts)>22.2 or max((obj.matrix_world@v.co).z for v in f.verts)<20.7]
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(obj.data);bm.free()
cam.data.type='ORTHO';cam.data.ortho_scale=56;cam.data.clip_end=100
cam.location=gv([-41,70,-289]);cam.rotation_euler=(gv([-41,21,-289])-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa/Port2_D05_source_join_native_plan.png');bpy.ops.render.render(write_still=True)
