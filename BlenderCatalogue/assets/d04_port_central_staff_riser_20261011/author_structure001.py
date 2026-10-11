from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True)
def material(role):
 if role in materials:return materials[role]
 f={'staff_panel':'staff/staff_bluegrey_paint','rubber_floor':'staff/staff_floor','zinc':'staff/staff_zinc','opal_glow':'staff/staff_opal'}.get(role,role)
 m=bpy.data.materials.new('PCS_'+role);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.78
 im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/(f+'.png')));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Closest';m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 if role=='opal_glow':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m;return m
materials={}
for p in P['parts']:
 me=bpy.data.meshes.new(p['name']);me.from_pydata([(x,-z,y)for x,y,z in p['verts']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),p['name'];bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(material(p['role']));uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:
   q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(v))
 for key in ['category','role','runtime_collision']:ob[key]=p[key]
 ob['source_input_sha256']=sha(W/'NATIVE_AUTHORING_INPUT_PLAN.json')
# Keep the catalogue cupboard geometry/materials/transforms, translated only.
source=R/'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend'
with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
cabinet=[]
for ob in dst.objects:
 if ob.type not in ['MESH','EMPTY']:continue
 bpy.context.collection.objects.link(ob);ob.name='PCS_CleanCabinet_'+ob.name;cabinet.append(ob)
for ob in cabinet:
 if ob.parent is None:ob.location+=Vector((-60.4,38.2,16.5))
 if ob.type=='MESH':ob['role']='clean_stock_cabinet';ob['category']='cabinet';ob['runtime_collision']=True
P['cabinet_source_object_names']=[ob.name for ob in cabinet]
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
rec=export_native(bpy,W,R,'D04PortCentralStaffStructure_r001.blend',P['structure_file']);P['structure']=rec;P['native_export_records']=[P['wall_patch']['native_export'],rec];P['model_pins']={q['export']:q['export_sha256']for q in P['native_export_records']}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_CENTRAL_STAFF_RISER.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':P['native_export_records'],'original_cabinet_geometry_translated_only':True},indent=2)+'\n');print('Staff structure exported')
