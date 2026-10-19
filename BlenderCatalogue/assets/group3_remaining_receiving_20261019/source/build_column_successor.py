import bpy,bmesh,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[4];W=pathlib.Path(__file__).resolve().parent/'receiving_inputs';P=R/'BlenderCatalogue/assets/group3_remaining_receiving_20261019';S=R/'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_crew_bank_source_batch015';native=S/'source/AST-CRW-G3-003.blend';assert hashlib.sha256(native.read_bytes()).hexdigest()=='f91517d43999d9da79222683147752740a62d6157ae4064b43e023d1372e6f13'
plans=json.load(open(W/'RIGID_FURNITURE_FIT_PLAN.json'))['plans'];hits=json.load(open(W/'SOURCE_COLUMN_TRIANGLE_SCREEN.json'))['hits'];bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.preferences.filepaths.save_version=0
source_objects=list(bpy.context.scene.objects);original={o.name:{'matrix':[list(row)for row in o.matrix_world],'vertices':len(o.data.vertices) if o.type=='MESH'else None,'data_pointer':o.data.as_pointer() if o.type=='MESH'else None}for o in source_objects};moved=[];edited=[]
for p in plans:
 key=p['allocation'];delta=p['world_translation'];native_delta=Vector((delta[0],-delta[2],delta[1]))
 if native_delta.length<1e-9:continue
 for o in source_objects:
  if o.get('source_allocation_key')!=key or o.name.split('__')[1]=='Shell':continue
  group=o.name.split('__')[1]
  if o.parent is not None and o.parent.get('source_allocation_key')==key and o.parent.name.split('__')[1]==group:continue
  o.location+=native_delta;o['receiving_rigid_translation_world']=delta;moved.append(o.name)
bpy.context.view_layer.update()
byalloc={}
for h in hits:
 if h['original_component']=='Shell':byalloc.setdefault(h['allocation'],{})[h['protected_path']]=h['protected_bounds']
for key,columns in byalloc.items():
 verts=[];faces=[]
 for a in columns.values():
  x0,y0,z0,x1,y1,z1=a;x0-=.005;x1+=.005;z0-=.005;z1+=.005;y0=11.7;y1=15.5;k=len(verts)
  verts.extend([(x,-z,y)for y in [y0,y1]for z in [z0,z1]for x in [x0,x1]])
  faces.extend([tuple(k+i for i in f)for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]])
 me=bpy.data.meshes.new('TemporaryProtectedColumns');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cutter=bpy.data.objects.new('TEMP_COLUMN_CLEARANCES',me);bpy.context.collection.objects.link(cutter)
 names=sorted({h['source_node']for h in hits if h['allocation']==key and h['original_component']=='Shell'})
 for name in names:
  o=bpy.data.objects.get(name);assert o is not None,name;assert o.type=='MESH';o.data=o.data.copy();before=len(o.data.polygons)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.to_mesh(o.data);bm.free()
  bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('ProtectedExistingColumnClearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False);assert len(o.data.polygons)>0,name
  o['bounded_column_successor']=True;o['original_native_sha256']='f91517d43999d9da79222683147752740a62d6157ae4064b43e023d1372e6f13'
  edited.append({'name':name,'allocation':key,'faces_before':before,'faces_after':len(o.data.polygons),'columns':list(columns)})
 bpy.data.objects.remove(cutter,do_unlink=True)
# Every untouched source object keeps its matrix and original mesh datablock.
modified_names=set(moved)|{r['name']for r in edited};moved_allocs={p['allocation']for p in plans if p['local_x_translation_m']>0};unchanged=0
for o in source_objects:
 if o.name in modified_names or (o.get('source_allocation_key')in moved_allocs and o.name.split('__')[1]!='Shell'):continue
 assert [list(row)for row in o.matrix_world]==original[o.name]['matrix'],o.name
 if o.type=='MESH':assert o.data.as_pointer()==original[o.name]['data_pointer'],o.name
 unchanged+=1
bpy.context.scene['receiving_derivative']='Protected column clearance only; bounded whole rest/storage arrangement translation in9 allocations.';bpy.context.scene['new_registered_berths']=0;bpy.context.scene['C036_migration_applied']=False
outnative=P/'source/AST-CRW-G3-003_current_columns_r001.blend';outglb=P/'exports/AST-CRW-G3-003_current_columns_r001.glb';assert not outnative.exists() and not outglb.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(outnative),compress=True);bpy.ops.export_scene.gltf(filepath=str(outglb),export_format='GLB',export_extras=True,export_yup=True,export_lights=False,export_cameras=False)
report={'status':'BOUNDED_SOURCE_SUCCESSOR_EXPORTED_RECEIVING_PENDING','original_native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(outnative.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(outglb.read_bytes()).hexdigest(),'objects_unchanged':unchanged,'rigid_root_objects_moved':moved,'edited_shell_meshes':edited,'furniture_plans':plans,'column_geometry_modified':False,'room_footprints_ids_or_capacity_modified':False,'remaining_validation':'Independent source column clearance, floor fit, current main integration and pixel review.'};(P/'qa/COLUMN_SUCCESSOR.json').write_text(json.dumps(report,indent=2)+'\n');print('COLUMN_SUCCESSOR',len(edited),'shell meshes;',len(moved),'rigid roots;',unchanged,'unchanged objects')
