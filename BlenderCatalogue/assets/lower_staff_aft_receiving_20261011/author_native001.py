from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
def material(role):
 if role in materials:return materials[role]
 m=bpy.data.materials.new('LSA_'+role);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.78
 im=bpy.data.images.load(str(R/'BlenderCatalogue/materials/staff'/(role+'.png')));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Closest';m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 if role=='staff_opal':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m;return m
for p in P['parts']:
 me=bpy.data.meshes.new(p['name']);me.from_pydata([(x,-z,y)for x,y,z in p['verts']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),p['name'];bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(material(p['role']));uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(v))
 for key in ['category','role','runtime_collision']:ob[key]=p[key]
 ob['source_input_sha256']=sha(W/'NATIVE_AUTHORING_INPUT_PLAN.json')
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
rec=export_native(bpy,W,R,'LowerSharedAftStaffRoute_r001.blend',P['structure_file']);P['structure']=rec;P['native_export_records']=[rec];P['model_pins']={rec['export']:rec['export_sha256']}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/LOWER_SHARED_AFT_STAFF_ROUTE.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':[rec],'old_native_exports_byte_identical':len(P['source_protected_native_exports']),'original_meshes_or_sources_modified':0,'own_solids_manifold':len(P['parts']),'packed_original_material_texture_family':list(materials),'scope':'New original editable corridor authoring;not a recovered concourse native or a changed old source'},indent=2)+'\n');print('New shared lower staff route saved and freshly re-exported identically')
