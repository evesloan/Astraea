"""Fresh bounded source geometry; the support cutaway is never saved/exported."""
from pathlib import Path
import bpy,bmesh,hashlib,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');CAT=ROOT/'BlenderCatalogue';sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE/'source'));from native_glb_subset import GLB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gv=lambda p:Vector((p[0],-p[2],p[1]));write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
receiver=json.loads((HERE/'source/RECREATION_RECEIVER.json').read_text());patch=json.loads((HERE/'source/CREW_STREET_RECREATION_PATCH.json').read_text());support=json.loads((HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
materials={};defs=json.loads((CAT/'materials/staff/manifest.json').read_text())['materials']
def mat(role):
 if role in materials:return materials[role]
 q=defs[role];m=bpy.data.materials.new('CONTEXT_'+role);m.use_nodes=True;m.diffuse_color=tuple(v/255 for v in q['colour_srgb_8bit'])+(1,);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.interpolation='Closest';tx.image=bpy.data.images.load(str(CAT/'materials/staff'/q['file']),check_existing=True);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);materials[role]=m;return m

def bounded_load(reader,names,roles,prefix='Context_'):
 out=[]
 for name in names:
  vs,fs,uvs,extra=reader.geometry(name);me=bpy.data.meshes.new(prefix+name);me.from_pydata([gv(v)for v in vs],[],fs);me.update();uv=me.uv_layers.new(name='ExactNativeUV')
  for i,v in enumerate(uvs):uv.data[i].uv=v
  me.materials.append(mat(roles[name]));o=bpy.data.objects.new(prefix+name,me);bpy.context.collection.objects.link(o)
  for k,v in extra.items():o[k]=v
  out.append(o)
 return out

def load(p):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(p));return[o for o in bpy.context.scene.objects if o not in before]

def bvh_for(objects):
 vs,fs=[],[]
 for o in objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs,fs
# Independently inspect all twenty editable components before fresh GLB import.
editable_checks=[]
for aid,spec in [('AST-STF-G3-018',receiver),('AST-STF-G3-019',patch)]:
 with bpy.data.libraries.load(str(HERE/'source'/f'{aid}.blend'),link=False)as(src,dst):dst.objects=[p['name']for p in spec['parts']]
 for o in dst.objects:
  assert o is not None;bpy.context.collection.objects.link(o)
 bpy.context.view_layer.update()
 for o in dst.objects:
  p=next(p for p in spec['parts']if p['name']==o.name)
  if'aabb'in p:expected=p['aabb']
  elif'vertices_godot'in p:expected=[f(v[k]for v in p['vertices_godot'])for k in range(3)for f in [min,max]]
  else:expected=[min(v[0]for v in p['boundary']),max(v[0]for v in p['boundary']),*p['y'],min(v[1]for v in p['boundary']),max(v[1]for v in p['boundary'])]
  vs=[o.matrix_world@v.co for v in o.data.vertices];actual=[min(v.x for v in vs),max(v.x for v in vs),min(v.z for v in vs),max(v.z for v in vs),-max(v.y for v in vs),-min(v.y for v in vs)];err=max(abs(a-b)for a,b in zip(expected,actual));editable_checks.append({'asset':aid,'semantic_name':o.name,'declared_aabb':expected,'actual_editable_aabb':actual,'maximum_error_m':err,'pass':err<.00005})
 for o in dst.objects:bpy.data.objects.remove(o,do_unlink=True)
assert all(q['pass']for q in editable_checks)
roompath=ROOT/'BlenderCatalogue/assets/crew_batch_receiving_preparation_20261008/incoming/D03_directory_07.glb';assert sha(roompath)==receiver['source_pins'][str(roompath.relative_to(ROOT))];room=load(roompath);bpy.context.view_layer.update();assert sum(o.type=='MESH'for o in room)==403;rbvh,_,_=bvh_for(room)
oldstreet=GLB(ROOT/patch['original_export_path']);assert sha(oldstreet.path)==patch['original_export_sha256'];contextnames=[q['name']for q in oldstreet.doc['nodes']if'mesh'in q and any(q['name'].endswith('_'+c)for c in ['-8_26','-8_27','-7_26','-7_27'])];rolemap={n:oldstreet.named(n)['extras']['role']for n in contextnames};before=bounded_load(oldstreet,patch['native_mesh_batches_to_omit_only_during_root_adoption'],rolemap,'OriginalBlocking_');beforebvh,_,_=bvh_for(before)
for o in before:bpy.data.objects.remove(o,do_unlink=True)
contextnames=[n for n in contextnames if n not in patch['native_mesh_batches_to_omit_only_during_root_adoption']];context=bounded_load(oldstreet,contextnames,rolemap)
exports=[HERE/'exports'/f'AST-STF-G3-{i:03}.glb'for i in [18,19]];new=load(exports[0]);newpatch=load(exports[1]);assert {o.name for o in newpatch if o.type=='MESH'}==set(patch['native_mesh_batches_to_omit_only_during_root_adoption']);bpy.context.view_layer.update();bvh,vs,fs=bvh_for(bpy.context.scene.objects);nbvh,_,_=bvh_for(new);pbvh,_,_=bvh_for(newpatch);roofbvh,_,_=bvh_for([o for o in new if o.type=='MESH'and o.get('category')=='overhead']);trimbvh,_,_=bvh_for([o for o in new if o.type=='MESH'and o.get('category')=='receiver_trim']);zincbvh,_,_=bvh_for([o for o in new if o.type=='MESH'and o.get('role')=='staff_zinc'])
checks=[]
for q in support['bounded_floor_footprints']:
 p=q['floor_point'];ds=[bvh.find_nearest(gv([p[0],p[1]+h,p[2]]))[3]for h in [.31,.8,1.3,1.65]];checks.append({'floor_point':p,'radius_m':.28,'minimum_native_surface_distance_m':min(ds),'pass':min(ds)>.28})
joins=[]
def contact(group,p,a,b):
 da=a.find_nearest(gv(p))[3];db=b.find_nearest(gv(p))[3];joins.append({'interface':group,'world_point':p,'first_native_distance_m':da,'second_native_distance_m':db,'pass':max(da,db)<.0001})
x=receiver['actual_room_opening']['native_outer_pier_face_x'];roofedge=receiver['actual_room_opening']['roof_edge_x'];header=receiver['existing_source_native_bounds']['E_outer_west_openingheader']
for z in [213.82,218.18]:
 for y in [12.5,14.2]:contact('Missing flared receiver to original fitted pier west face',[x,y,z],nbvh,rbvh)
for z in [214.12,217.88]:
 for y in [12.5,14.2]:contact('Missing receiver to exact first-street successor',[-55.06,y,z],nbvh,pbvh)
for z in [214.2,217.8]:contact('Missing bumper terminal to preserved street mouth corner',[-55.06,12.78,z],nbvh,pbvh)
contact('Receiver roof to original rounded roof straight edge',[roofedge,15.27,216],roofbvh,rbvh)
contact('Missing upper slot closure to original header top',[-53.81,header[3],216],trimbvh,rbvh)
contact('Missing upper slot closure to missing receiver roof',[-53.83,15.2,216],trimbvh,roofbvh)
# Exact native-profile points and their midpoints independently test the shaped
# nib, rather than relying on a contact to the original roof's bounding box.
source=GLB(roompath);roofverts=source.geometry('E_ceiling')[0];profile=json.loads((HERE/'qa/NATIVE_ROOF_EDGE_PROFILE.json').read_text());profilechecks=[]
for piece in profile['new_profile_complements']:
 pts=[p for p in piece['profile_boundary_xy']if any(abs(p[0]-v[0])+abs(p[1]-v[1])<1e-7 for v in roofverts)]
 for p in pts:
  point=[p[0],p[1],216];a=roofbvh.find_nearest(gv(point))[3];b=rbvh.find_nearest(gv(point))[3];profilechecks.append({'native_matched_nib':piece['part'],'point':point,'new_native_distance_m':a,'original_native_distance_m':b,'pass':max(a,b)<.0001})
retained=[]
for z in [210,221]:
 for y in [12.5,14.2]:
  point=[-55.2,y,z];a=beforebvh.find_nearest(gv(point))[3];b=pbvh.find_nearest(gv(point))[3];retained.append({'preserved_street_point':point,'original_native_distance_m':a,'successor_native_distance_m':b,'pass':max(a,b)<.0001})
openings=[]
for point in [[-55.1,13.2,215],[-55.1,13.2,217],[-55.2,14.2,216]]:
 a=beforebvh.find_nearest(gv(point))[3];b=pbvh.find_nearest(gv(point))[3];openings.append({'first_street_mouth_point':point,'original_native_distance_m':a,'successor_native_distance_m':b,'pass':a<.06 and b>.28})
for point in [[x,13.5,215],[x,13.5,217]]:
 a=rbvh.find_nearest(gv(point))[3];b=nbvh.find_nearest(gv(point))[3];openings.append({'original_room_opening_preserved_point':point,'original_native_distance_m':a,'new_native_distance_m':b,'pass':min(a,b)>.28})
fixtures=[]
for p in receiver['parts']:
 if not p['name'].endswith(('Hanger0','Hanger1')):continue
 a=p['aabb'];point=[a[0],15.2,(a[4]+a[5])/2];dr=roofbvh.find_nearest(gv(point))[3];dh=zincbvh.find_nearest(gv(point))[3];fixtures.append({'hanger':p['name'],'point':point,'native_roof_distance_m':dr,'native_hanger_distance_m':dh,'pass':max(dr,dh)<.0001})
f=receiver['fixtures'][0];light=next(o for o in new if o.name==f['name']);light_error=(light.matrix_world.translation-gv(f['position'])).length;assert light_error<.00005 and light['datum_kind']=='supported_staff_task_light'
allchecks=checks+joins+profilechecks+retained+openings+fixtures;passed=all(q['pass']for q in allchecks)
report={'status':'PASS'if passed else'FAIL','export_hashes':{p.name:sha(p)for p in exports},'unchanged_original_room_sha256':sha(roompath),'unchanged_received_mesh_count':403,'derived_editable_component_bounds':editable_checks,'capsule_stationary_witnesses':checks,'actual_native_contacts':joins,'exact_rounded_roof_profile_contacts':profilechecks,'preserved_street_surfaces':retained,'bounded_opening_witnesses':openings,'supported_hanger_ceiling_contacts':fixtures,'source_fixture_datum':{'name':f['name'],'position':f['position'],'native_error_m':light_error},'exact_original_street_nodes_transiently_omitted':patch['native_mesh_batches_to_omit_only_during_root_adoption'],'bounded_original_street_context_nodes':contextnames,'fitted_triangles':len(fs),'scope':'Fresh bounded source context, original room/frame and exact wall successors. No runtime, structure, moving door/cart, species or final-art acceptance.'};write(HERE/'qa/RECREATION_NATIVE_GEOMETRY.json',report);print(json.dumps({'status':report['status'],'editable_components':len(editable_checks),'capsules':len(checks),'contacts':len(joins),'matched_roof_profile_points':len(profilechecks),'preserved_faces':len(retained),'openings':len(openings),'hangers':len(fixtures),'failed':[q for q in allchecks if not q['pass']]}));assert passed
v=[];faces=[]
for t in support['diagnostic_floor_triangles']:
 k=len(v);v.extend(gv([x,12,z])for x,z in t);faces.append((k,k+1,k+2))
me=bpy.data.meshes.new('ExplicitDiagnosticSupport_ONLY');me.from_pydata(v,[],faces);o=bpy.data.objects.new('ExplicitDiagnosticSupport_ONLY',me);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('ExplicitDiagnosticSupport_ONLY');m.diffuse_color=(.26,.3,.32,1);me.materials.append(m)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=400;scene.render.resolution_percentage=100;scene.world.color=(.15,.15,.15);scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.display.shading.show_object_outline=False
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.lens=24;cam.data.clip_start=.04;cam.data.clip_end=30
for name,p,target in [('recreation_original_frame_inside_native_eye.png',[-50,13.6,216],[-57,13.4,216]),('recreation_street_receiver_native_eye.png',[-57,13.6,213],[-50,13.4,216])]:
 cam.location=gv(p);cam.rotation_euler=(gv(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa'/name);bpy.ops.render.render(write_still=True)
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);remove=[f for f in bm.faces if min((o.matrix_world@v.co).z for v in f.verts)>13.2 or max((o.matrix_world@v.co).z for v in f.verts)<11.7];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
cam.data.type='ORTHO';cam.data.ortho_scale=18;cam.location=gv([-53.2,40,216]);cam.rotation_euler=(gv([-53.2,12,216])-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/'qa/recreation_short_receiver_plan.png');bpy.ops.render.render(write_still=True)
