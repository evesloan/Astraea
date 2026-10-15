from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';S=R/'BlenderCatalogue/assets/group8_destinations_20261011';p=json.loads((G/'data/architecture/group8/crown_interiors.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();src=S/p['native'];runtime=G/'assets/models'/p['model_file'];assert bpy.app.version[:3]==(4,3,2)and sha(src)==p['native_sha256']and sha(runtime)==p['model_sha256'];assert not(G/'assets/fitted_upper_horizon_20261015').exists();bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.preferences.filepaths.save_version=0
key='D18_directory_09';records={x['name']:x for x in p['meshes']if x['programme_key']==key};source_lights=[x for x in p['lights']if x['programme_key']==key];batches=[x for x in p['runtime_batches']if x['programme_key']==key];assert len(records)==320 and len(batches)==70 and len(source_lights)==2
B=lambda v:Vector((v[0],-v[2],v[1]));authors=bpy.data.collections.new('FITTED_HORIZON_INDIVIDUAL_AUTHORING_R001');bpy.context.scene.collection.children.link(authors);poses=[]
for o in list(bpy.data.objects):
 if o.name not in records and o.name not in[x['name']for x in source_lights]:bpy.data.objects.remove(o,do_unlink=True);continue
 before=o.matrix_world.copy();dz=14 if'HorizonCounter'in o.name else 22;o.parent=None;o.matrix_world=Matrix.Translation(B((0,0,dz)))@before
 for c in list(o.users_collection):c.objects.unlink(o)
 authors.objects.link(o);poses.append({'name':o.name,'translation_z':dz,'before_matrix_blender':[list(x)for x in before],'after_matrix_blender':[list(x)for x in o.matrix_world]});o['fitted_upper_horizon_translation_z']=dz
# Export individual editable authoring evidence separately;runtime keeps theoriginal70 batchgroups.
bpy.ops.object.select_all(action='DESELECT')
for o in authors.objects:o.select_set(True)
unbatched=D/'FITTED_UPPER_HORIZON_r001_authoring.glb';bpy.ops.export_scene.gltf(filepath=str(unbatched),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
authors.hide_render=True;before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(runtime));imported=set(bpy.data.objects)-before;wanted={x['name']:x for x in batches};col=bpy.data.collections.new('FITTED_HORIZON_RUNTIME_R001');bpy.context.scene.collection.children.link(col);fit_batches=[]
for o in imported:
 if o.type!='MESH'or o.name not in wanted:bpy.data.objects.remove(o,do_unlink=True);continue
 row=wanted[o.name];is_counter=[('HorizonCounter'in name)for name in row['source_members']];assert all(is_counter)or not any(is_counter),'Mixed transformation batch';dz=14 if all(is_counter)else 22;old=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation(B((0,0,dz)))@old
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);row=dict(row);row.update(translation_z=dz,source_name=row['name']);row['world_aabb']=list(row['world_aabb']);row['world_aabb'][4]+=dz;row['world_aabb'][5]+=dz;fit_batches.append(row)
assert len(fit_batches)==70;lights=[]
for i,row in enumerate(source_lights):
 row=dict(row);row['source_name']=row['name'];row['name']='FittedHorizonLightDatum'+str(i);row['at']=list(row['at']);row['at'][2]+=22;o=bpy.data.objects.new(row['name'],None);col.objects.link(o);o.matrix_world=Matrix.Translation(B(row['at']));lights.append(row)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
policy={'programme_key':key,'original_foyer_z':[113,134],'original_sitting_bays_z':[153,169],'field_records_z':137,'study_consoles_z':142,'study_chairs_z':145,'task_lights_z':143,'counter_z':149,'floor_y':106.5,'new_floor_or_room_ids_or_capacity':0,'source_variants_retained':True,'operator_species_stock_pressure_or_final_art_accepted':False};bpy.data.texts.new('FITTING_POLICY.json').write(json.dumps(policy,indent=2));I=D/'import/Game/assets/fitted_upper_horizon_20261015';I.mkdir(parents=True,exist_ok=True);out=I/'FITTED_UPPER_HORIZON_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);N=D/'native';N.mkdir(exist_ok=True);native=N/'FITTED_UPPER_HORIZON_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['FITTED_HORIZON_RUNTIME_R001'].objects:o.select_set(True)
fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(fresh)==sha(out)and sha(src)==p['native_sha256']and sha(runtime)==p['model_sha256'];r={'status':'PASS_NATIVE_FRESH_EXPORT_EXACT_CURRENT_FITTING_PENDING','native_sha256':sha(native),'model_sha256':sha(out),'file':out.name,'source_native_sha256':p['native_sha256'],'source_model_sha256':p['model_sha256'],'authoring_meshes':320,'runtime_meshes':70,'policy':policy,'batches':sorted(fit_batches,key=lambda x:x['name']),'lights':lights,'individual_authoring_poses':poses};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_FITTED_HORIZON_NATIVE',320,70)
