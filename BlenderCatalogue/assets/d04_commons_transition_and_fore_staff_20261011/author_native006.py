from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
def mat(role):
 if role in materials:return materials[role]
 m=bpy.data.materials.new('ShortService_'+role);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.75;im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/ (role+'.png')));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Closest';m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color']);materials[role]=m;return m
for q in P['commons_parts']:
 me=bpy.data.meshes.new(q['name']);me.from_pydata([(x,-z,y)for x,y,z in q['verts']],[],q['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(mat(q['role']));uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:at=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(at.dot(u),at.dot(v))
 for k in ['category','role','runtime_collision']:ob[k]=q[k]
short=P['commons_structure'];assert hashlib.sha256((W/short['native']).read_bytes()).hexdigest()==short['native_sha256'];assert hashlib.sha256((W/short['export']).read_bytes()).hexdigest()==short['export_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);mapping=[]
source_dir=R/'BlenderCatalogue/assets/d04_private_court_controls_and_staff_approach_20261011';phys_dir=R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'
specs=[(source_dir/'D04StaffCourtApproachSealed_r002.blend',set(P['fore_models']['structure']['collision_policy'])-{'D04SA_ServiceLaneScreen_0','D04SA_ServiceLaneScreen_2'}),(source_dir/'D04CourtGateControls_r003.blend',set(P['fore_models']['court']['collision_policy'])),(phys_dir/'D04BoundedPhysicalCuts_r010.blend',set(P['fore_patch_names'])),(phys_dir/'D04PhysicalFittings_r010.blend',set(P['fore_owned_names']))]
def payload(ob):return {'verts':[list(v.co)for v in ob.data.vertices],'faces':[list(q.vertices)for q in ob.data.polygons],'uvs':[[list(v.uv)for v in layer.data]for layer in ob.data.uv_layers],'materials':[m.name for m in ob.data.materials],'world_matrix':[list(v)for v in ob.matrix_world]}
for source,names in specs:
 with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
 matched=set()
 for ob in dst.objects:
  if not ob:continue
  key=ob.name.replace('.','_')
  if key in names:
   assert ob.type=='MESH';pose=ob.matrix_world.copy();before=payload(ob);ob.parent=None;ob.matrix_world=pose;bpy.context.collection.objects.link(ob);mapping.append({'name':ob.name,'normalized_name':key,'native_source':str(source.relative_to(R)),'native_sha256':sha(source),'payload_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'payload':before});matched.add(key)
 for ob in dst.objects:
  if ob and ob.name.replace('.','_')not in matched:bpy.data.objects.remove(ob,do_unlink=True)
 assert matched==names,(source,names-matched)
for name,d in P['fore_rigid_fixed_control_moves'].items():bpy.data.objects[name].location+=Vector((d[0],-d[2],d[1]))
for name,change in P['fore_screen_end_successors'].items():
 ob=bpy.data.objects[name];inv=ob.matrix_world.inverted()
 for vertex in ob.data.vertices:
  point=ob.matrix_world@vertex.co
  if point.x<change['world_x_min_after']:point.x=change['world_x_min_after'];vertex.co=inv@point
 ob.data.update()
fore=export_native(bpy,W,R,'D04PortForwardStaffCourtConnection_r004.blend','D04_PORT_FORWARD_STAFF_COURT_CONNECTION_r004.glb');P['fore_structure']=fore;P['native_export_records']=[short,fore];P['model_pins']={q['export']:q['export_sha256']for q in P['native_export_records']};P['fore_source_mesh_mappings']=[{k:v for k,v in q.items()if k!='payload'}for q in mapping];P['fore_selected_mesh_count']=len(mapping)
bpy.ops.wm.open_mainfile(filepath=str(W/fore['native']))
for q in mapping:
 now=payload(bpy.data.objects[q['name']]);old=q['payload'];assert all(now[k]==old[k]for k in (['faces','uvs','materials'] if q['name'] in P['fore_screen_end_successors']else ['verts','faces','uvs','materials'])),q['name']
 if q['name']not in P['fore_rigid_fixed_control_moves']:assert now['world_matrix']==old['world_matrix'],q['name']
 else:
  d=P['fore_rigid_fixed_control_moves'][q['name']];delta=Vector((d[0],-d[2],d[1]));assert (bpy.data.objects[q['name']].matrix_world.translation-Vector([old['world_matrix'][i][3]for i in range(3)])-delta).length<.00001

for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','fore_selected_meshes_exact_local_geometry_UVs_materials':201,'fore_selected_meshes_exact_world_pose':201,'fore_selected_meshes_entirely_exact':199,'bounded_lane_screen_successors':P['fore_screen_end_successors'],'new_short_profiles':3,'old_gate_geometry_scaled':False,'old4333_native_export_files_unchanged':True,'own_r001_native_exports_preserved':6,'own_r002_fore_native_exports_preserved':3,'own_r003_fore_native_exports_preserved':3,'rigid_fixed_staff_control_translations':P['fore_rigid_fixed_control_moves'],'private_gate_leaf_geometry_and_controllers_unchanged':True,'native_records':P['native_export_records']},indent=2)+'\n')
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('Distinct short profiles and exact selected fore native assembly saved',len(mapping))
