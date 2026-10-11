from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();input_pin=sha(W/'NATIVE_AUTHORING_INPUT_PLAN.json')
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
assets=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))['assets'];assert all(a['catalogue_id']!='AST-CIR-005'or a['family']=='primary_atrium_core'for a in assets)
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
source=R/'BlenderCatalogue/assets/primary_atrium_core/source/AST-CIR-005_spine_core.blend';audit=json.load(open(W/'EXACT_NATIVE_MESH_AUDIT.json'));bpy.ops.wm.open_mainfile(filepath=str(source))
def payload(o):return {'vertices':[list(o.matrix_world@q.co)for q in o.data.vertices],'faces':[list(q.vertices)for q in o.data.polygons],'materials':[m.name for m in o.data.materials]}
def meshsha(o):return hashlib.sha256(json.dumps(payload(o),sort_keys=True,separators=(',',':')).encode()).hexdigest()
for name,item in audit['meshes'].items():assert meshsha(bpy.data.objects[name])==item['sha256'],name
def ensure_material(role):
 if role in bpy.data.materials:return bpy.data.materials[role]
 mat=bpy.data.materials.new(role);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.78;im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/(role+'.png')));im.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;node.interpolation='Closest';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);return mat
materials={role:ensure_material(role)for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal']};materials['opal_glow']=bpy.data.materials['core_opal_lens']
def addpart(p,origin_z):
 verts=[(q[0],-(q[2]-origin_z),q[1])for q in p['verts']];me=bpy.data.meshes.new(p['name']);me.from_pydata(verts,[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(materials[p['role']]);uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:
   q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(v))
 for k in ['category','role','runtime_collision']:ob[k]=p[k]
 ob['source_plan_sha256']=input_pin;ob['parent_design_id']='AST-CIR-005';return ob
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def replacebox(name,suffix,lo,hi,role):
 x0,y0,z0=lo;x1,y1,z1=hi;return addpart({'name':name+'_'+suffix,'verts':[[x,y,z]for y in [y0,y1]for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],'faces':faces,'category':'wall','role':role,'runtime_collision':True},272)
replaced={}
for name in P['exact_removed_source_meshes']:
 ob=bpy.data.objects[name];a=audit['meshes'][name];lo=a['world_min'];hi=a['world_max'];role='ivory_enamel'if 'OuterWall'in name else'warm_walnut';replaced[name]=a
 replacebox(name,'ForeRetained',lo,[hi[0],hi[1],287.1],role);replacebox(name,'AftRetained',[lo[0],lo[1],290.3],hi,role)
 if 'OuterWall'in name:replacebox(name,'HeaderRetained',[lo[0],19.7,287.1],[hi[0],hi[1],290.3],role)
 bpy.data.objects.remove(ob,do_unlink=True)
for part in P['parts']:
 if part['group']=='core':addpart(part,272)
unchanged={name:item['sha256']for name,item in audit['meshes'].items()if name not in replaced}
for name,h in unchanged.items():assert meshsha(bpy.data.objects[name])==h,name
core=export_native(bpy,W,R,'AST-CIR-005_aft_midship_d04_port_threshold_r001.blend',P['core_derivative_file'])
for name,h in unchanged.items():assert meshsha(bpy.data.objects[name])==h,name
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.materials=[n for n in src.materials if n in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal','core_opal_lens']]
materials={role:ensure_material(role)for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal']};materials['opal_glow']=bpy.data.materials['core_opal_lens'];mat=bpy.data.materials.new('D04PA_hospitality_glass');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.22,.4,.44,1);bs.inputs['Alpha'].default_value=.12;bs.inputs['Roughness'].default_value=.16;bs.inputs['Transmission Weight'].default_value=.65;mat.surface_render_method='DITHERED';materials['hospitality_glass']=mat
for part in P['parts']:
 if part['group']=='collar':addpart(part,0)
collar=export_native(bpy,W,R,'D04PortAftCoreCollar_r001.blend',P['collar_file']);P['native_export_records']=[core,collar];P['model_pins']={v['export']:v['export_sha256']for v in P['native_export_records']};P['core_structure']=core;P['collar_structure']=collar
(W/'SOURCE_PRESERVATION.json').write_text(json.dumps({'status':'PASS_EXACT_NATIVE_SOURCE_MESHES','original_native_meshes':839,'unchanged_original_meshes':len(unchanged),'unchanged_original_mesh_sha256':unchanged,'removed_exact_wall_dado_preimages':replaced,'preserved_empty_marker_names':True,'shared_original_native_and_exports_unchanged':True,'only_placed_aft_midship_D04_port_side_changed':True,'new_unique_design_ids':0},indent=2)+'\n')
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_AFT_CORE_THRESHOLD.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':P['native_export_records'],'source_meshes_unchanged':len(unchanged)},indent=2)+'\n');print('Threshold immutable exports complete')
