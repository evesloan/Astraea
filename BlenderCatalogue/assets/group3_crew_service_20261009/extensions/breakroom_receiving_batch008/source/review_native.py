"""Fresh exact bounded source context; held floors are diagnostic only."""
from pathlib import Path
import bpy,bmesh,hashlib,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');CAT=ROOT/'BlenderCatalogue';FIRST=CAT/'assets/group3_crew_service_20261009';sys.path.insert(0,str(HERE/'source'));from native_glb_subset import GLB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gv=lambda p:Vector((p[0],-p[2],p[1]));write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
collar=json.loads((HERE/'source/BREAKROOM_COLLAR.json').read_text());branchspec=json.loads((HERE/'source/BREAKROOM_REUSED_BRANCH.json').read_text());patch=json.loads((HERE/'source/CREW_STREET_BREAKROOM_PATCH.json').read_text());support=json.loads((HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
materials={};defs=json.loads((CAT/'materials/staff/manifest.json').read_text())['materials']
def mat(role):
 if role in materials:return materials[role]
 q=defs[role];m=bpy.data.materials.new('CONTEXT_'+role);m.use_nodes=True;m.diffuse_color=tuple(v/255 for v in q['colour_srgb_8bit'])+(1,);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.interpolation='Closest';tx.image=bpy.data.images.load(str(CAT/'materials/staff'/q['file']),check_existing=True);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);materials[role]=m;return m

def bounded_load(reader,names,roles,prefix='Context_'):
 out=[]
 for name in names:
  vs,fs,uvs,extra=reader.geometry(name);me=bpy.data.meshes.new(prefix+name);me.from_pydata([gv(v)for v in vs],[],fs);me.update();uv=me.uv_layers.new(name='ExactNativeUV');
  for i,v in enumerate(uvs):uv.data[i].uv=v
  me.materials.append(mat(roles[name]));o=bpy.data.objects.new(prefix+name,me);bpy.context.collection.objects.link(o)
  for k,v in extra.items():o[k]=v
  out.append(o)
 return out

def load(p):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(p));return [o for o in bpy.context.scene.objects if o not in before]

def bvh_for(objects):
 vs,fs=[],[]
 for o in objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs,fs
oldbranch=GLB(ROOT/branchspec['retained_source_export']);assert sha(oldbranch.path)==branchspec['retained_source_export_sha256'];bounds=[]
for p in branchspec['parts']:
 actual=oldbranch.bounds(p['retained_source_semantic_name']);err=max(abs(a-b)for a,b in zip(actual,p['retained_original_world_aabb']));bounds.append({'retained_semantic_name':p['name'],'actual_native_original_aabb':actual,'selected_successor_aabb':p['aabb'],'explicit_clip':p['exact_clip'],'maximum_original_source_aabb_error_m':err,'pass':err<.00005})
assert all(q['pass']for q in bounds)
# Load the thirty-two editable derived components by name to independently
# verify every unchanged/clipped component, rather than just grouped GLB bounds.
with bpy.data.libraries.load(str(HERE/'source/AST-STF-G3-010.blend'),link=False)as(src,dst):dst.objects=[p['name']for p in branchspec['parts']]
editable=[]
for o in dst.objects:
 assert o is not None;bpy.context.collection.objects.link(o);editable.append(o)
bpy.context.view_layer.update();editable_checks=[]
for o in editable:
 p=next(p for p in branchspec['parts']if p['name']==o.name);v=[o.matrix_world@v.co for v in o.data.vertices];actual=[f(q[k]for q in v)for k in [0,2,1]for f in ([min,max]if k!=1 else[max,min])];actual[4:]=[-actual[4],-actual[5]];err=max(abs(a-b)for a,b in zip(actual,p['aabb']));editable_checks.append({'semantic_name':o.name,'native_editable_aabb':actual,'maximum_successor_aabb_error_m':err,'pass':err<.00005})
for o in editable:bpy.data.objects.remove(o,do_unlink=True)
assert all(q['pass']for q in editable_checks)
# Exact received section in its independently retained translation.
breakpath=ROOT/'Game/assets/models/SOL_D03_directory_02_source001.glb';assert sha(breakpath)==collar['source_pins'][str(breakpath.relative_to(ROOT))];received=load(breakpath);parent=bpy.data.objects.new('ReceivedBreakroom_ExactPlacement_CONTEXT_ONLY',None);bpy.context.collection.objects.link(parent)
for o in received:
 if o.parent not in received:o.parent=parent
parent.location=gv([8,12,-466]);bpy.context.view_layer.update();receivedbvh,_,_=bvh_for(received)
oldstreet=GLB(ROOT/patch['original_export_path']);assert sha(oldstreet.path)==patch['original_export_sha256'];contextnames=[q['name']for q in oldstreet.doc['nodes']if'mesh'in q and(q['name'].endswith('_6_-53')or q['name'].endswith('_7_-53'))];rolemap={n:oldstreet.named(n)['extras']['role']for n in contextnames};before=bounded_load(oldstreet,patch['native_mesh_batches_to_omit_only_during_root_adoption'],rolemap,'OriginalBlocking_');beforebvh,_,_=bvh_for(before)
for o in before:bpy.data.objects.remove(o,do_unlink=True)
contextnames=[n for n in contextnames if n not in patch['native_mesh_batches_to_omit_only_during_root_adoption']];context=bounded_load(oldstreet,contextnames,rolemap)
exports=[HERE/'exports'/f'AST-STF-G3-{i:03}.glb'for i in [9,10,11]];newcollar=load(exports[0]);newbranch=load(exports[1]);newpatch=load(exports[2]);assert {o.name for o in newpatch if o.type=='MESH'}==set(patch['native_mesh_batches_to_omit_only_during_root_adoption'])
bpy.context.view_layer.update();bvh,vs,fs=bvh_for(bpy.context.scene.objects);cbvh,_,_=bvh_for(newcollar);bbvh,_,_=bvh_for(newbranch);pbvh,_,_=bvh_for(newpatch)
checks=[]
for q in support['bounded_floor_footprints']:
 p=q['floor_point'];ds=[bvh.find_nearest(gv([p[0],p[1]+h,p[2]]))[3]for h in [.31,.8,1.3,1.65]];checks.append({'floor_point':p,'radius_m':.28,'minimum_native_surface_distance_m':min(ds),'pass':min(ds)>.28})
joins=[]
def contact(group,p,a,b):
 da=a.find_nearest(gv(p))[3];db=b.find_nearest(gv(p))[3];joins.append({'interface':group,'world_point':p,'first_native_distance_m':da,'second_native_distance_m':db,'pass':max(da,db)<.0001})
for z in [-421.9,-418.1]:
 for y in [12.5,14.2]:
  contact('Actual received wall to missing collar',[48.1,y,z],receivedbvh,cbvh);contact('Missing collar to retained branch jamb',[50.02,y,z],cbvh,bbvh)
contact('Folded roof actual edge to roof nib',[48,15.25,-420],receivedbvh,cbvh);contact('Missing roof to retained platform cap',[50.02,15.2,-420],cbvh,bbvh)
for z in [-422.6,-417.4]:
 for y in [12.5,14.2]:contact('Retained branch to precise crew street successor',[55.06,y,z],bbvh,pbvh)
for z in [-422.515,-417.485]:contact('Retained bumper to street successor',[55.06,12.78,z],bbvh,pbvh)
retained=[]
for z in [-423,-416.8]:
 for y in [12.5,14.2]:
  p=[55.2,y,z];a=beforebvh.find_nearest(gv(p))[3];b=pbvh.find_nearest(gv(p))[3];retained.append({'preserved_wall_point':p,'old_native_distance_m':a,'successor_native_distance_m':b,'pass':max(a,b)<.0001})
opening=[]
for p in [[55.1,13.2,-420],[55.2,14.2,-421],[55.06,12.8,-418.8]]:
 a=beforebvh.find_nearest(gv(p))[3];b=pbvh.find_nearest(gv(p))[3];opening.append({'bounded_opening_point':p,'original_native_distance_m':a,'successor_native_distance_m':b,'pass':a<.06 and b>.28})
fixture=[];roofbvh,_,_=bvh_for([o for o in newbranch if o.type=='MESH'and o.get('category')=='overhead']);zincbvh,_,_=bvh_for([o for o in newbranch if o.type=='MESH'and o.get('role')=='staff_zinc'])
for x in [52.175,53.175]:
 p=[x,15.2,-420];a=roofbvh.find_nearest(gv(p))[3];b=zincbvh.find_nearest(gv(p))[3];fixture.append({'retained_hanger_ceiling_point':p,'native_ceiling_distance_m':a,'native_hanger_distance_m':b,'pass':max(a,b)<.0001})
light=next(o for o in newbranch if o.name=='CRW_TASK_LIGHT_DATUM_150');assert (light.matrix_world.translation-gv([52.7,15.03,-420])).length<.00005 and light['datum_kind']=='supported_staff_task_light'
allchecks=checks+joins+retained+opening+fixture;passed=all(q['pass']for q in allchecks)
report={'status':'PASS'if passed else'FAIL','export_hashes':{p.name:sha(p)for p in exports},'retained_context_hashes':{str(p.relative_to(ROOT)):sha(p)for p in [breakpath,oldstreet.path,oldbranch.path]},'original_branch_native_bounds':bounds,'derived_branch_editable_native_bounds':editable_checks,'capsule_stationary_witnesses':checks,'actual_native_receiver_contacts':joins,'preserved_street_surfaces':retained,'bounded_street_opening_witnesses':opening,'retained_hanger_ceiling_contacts':fixture,'retained_light_datum_verified':'CRW_TASK_LIGHT_DATUM_150 [52.7,15.03,-420]','transient_original_street_meshes_omitted':patch['native_mesh_batches_to_omit_only_during_root_adoption'],'bounded_context_original_street_nodes_loaded':contextnames,'probe_correction':'First native review rejected contact probes at retained bevel corners, clear-gap wall offsets and inside hanger solids. Final probes lie on real shared face bands; no geometry or tolerances were changed to hide these failures. Rounded source edges remain retained.', 'fitted_triangles':len(fs),'scope':'Bounded fresh source geometry and exact received breakroom. No full platform, runtime adoption, door sweep, floor bearing, actual travel or capacity acceptance.'};write(HERE/'qa/BREAKROOM_NATIVE_GEOMETRY.json',report);print(json.dumps({'status':report['status'],'native_branch_bounds':len(bounds),'editable_branch_bounds':len(editable_checks),'capsules':len(checks),'joins':len(joins),'preserved_faces':len(retained),'opening_witnesses':len(opening),'hanger_contacts':len(fixture),'failed':[q for q in allchecks if not q['pass']]}));assert passed
# Diagnostic composite support remains unsaved and unexported.
v=[];f=[]
for t in support['diagnostic_floor_triangles']:
 k=len(v);v.extend(gv([x,12,z])for x,z in t);f.append((k,k+1,k+2))
me=bpy.data.meshes.new('ExplicitDiagnosticSupport_ONLY');me.from_pydata(v,[],f);o=bpy.data.objects.new('ExplicitDiagnosticSupport_ONLY',me);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('ExplicitDiagnosticSupport_ONLY');m.diffuse_color=(.26,.3,.32,1);me.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100;scene.world.color=(.15,.15,.15);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.lens=24;cam.data.clip_start=.04;cam.data.clip_end=60
for name,p,target in [('breakroom_actual_mouth_native_eye.png',[46.4,13.6,-420],[53.5,13.4,-420]),('retained_branch_to_breakroom_native_eye.png',[53.7,13.6,-420],[46.3,13.4,-420]),('crew_street_breakroom_receiver_native_eye.png',[57,13.6,-423],[52,13.4,-420])]:
 cam.location=gv(p);cam.rotation_euler=(gv(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);remove=[f for f in bm.faces if min((o.matrix_world@v.co).z for v in f.verts)>13.2 or max((o.matrix_world@v.co).z for v in f.verts)<11.7];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
cam.data.type='ORTHO';cam.data.ortho_scale=18;cam.location=gv([50,42,-420]);cam.rotation_euler=(gv([50,12,-420])-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa/breakroom_source_receiver_plan.png');bpy.ops.render.render(write_still=True)
