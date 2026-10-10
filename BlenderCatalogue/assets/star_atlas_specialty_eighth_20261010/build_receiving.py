from pathlib import Path
import bpy,json,hashlib,math,shutil,sys
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'RECEIVING_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);bpy.ops.wm.read_factory_settings(use_empty=True);retained=[];base_rails=[]
mat=bpy.data.materials.new('SpecialtyStructuralFrame');mat.diffuse_color=(.46,.4,.27,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color
tex=R/'Game/assets/models/AST-LIB-011_champagne_metal.png'
if tex.exists():n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(tex),check_existing=True);n.image.pack();mat.node_tree.links.new(n.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
def mesh_obj(name,verts,faces,category):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat);uv=mesh.uv_layers.new(name='MetreScaled')
 for face in mesh.polygons:
  normal=face.normal;u=Vector((1,0,0))if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
  for li in face.loop_indices:co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob['runtime_collision']=True;ob['construction_role']=category;return ob
floor_mat=bpy.data.materials.new('SpecialtyEighthWarmStoneFloor');floor_mat.diffuse_color=(.58,.54,.45,1);floor_mat.use_nodes=True;floor_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=floor_mat.diffuse_color
path=R/'Game/assets/models/AST-LIB-011_warm_stone.png'
if path.exists():
 n=floor_mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path),check_existing=True);n.image.pack();floor_mat.node_tree.links.new(n.outputs['Color'],floor_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy
for part in P['parts']:
 ob=mesh_obj(part['name'],[B(v)for v in part['verts']],part['faces'],part['category'])
 if part['category']=='D15_street_extension_floor':ob.data.materials[0]=floor_mat
for lower in P['lower_structural_owners']:
 src=R/lower['native_source'];assert sha(src)==lower['native_sha256']
 with bpy.data.libraries.load(str(src),link=False)as(a,b):b.objects=[n for n in a.objects if any(n.startswith(prefix)for prefix in lower['selected_prefixes'])]
 source_objects=[o for o in b.objects if o];assert len(source_objects)==22,[(o.name)for o in source_objects]
 root=bpy.data.objects.new('RetainedStructure_'+str(lower['source_index']),None);bpy.context.collection.objects.link(root);root.location=B(lower['origin']);root.rotation_euler.z=lower['yaw'];root['retained_owner']=lower['owner']
 for o in source_objects:
  bpy.context.collection.objects.link(o);original=o.name;o.parent=root;o.name='Persistent_'+str(lower['source_index'])+'_'+original;o['runtime_collision']=True;o['persistent_structural_contact_only']=True;o['retained_owner']=lower['owner'];o['original_source_object']=original;o['original_native_sha256']=lower['native_sha256'];retained.append({'owner':lower['owner'],'source_object':original,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
  if original.startswith('SUI_Wall_'):
   # Exact source wall footprint base rail closes the retained0.24m floor gap.
   coords=[v.co.copy()for v in o.data.vertices];bottom=min(v.z for v in coords);ids=[i for i,v in enumerate(coords)if abs(v.z-bottom)<1e-5];assert len(ids)==4,(original,len(ids));points=[coords[i]for i in ids];cx=sum(v.x for v in points)/4;cy=sum(v.y for v in points)/4;points.sort(key=lambda v:math.atan2(v.y-cy,v.x-cx));verts=[(v.x,v.y,z)for z in [0,bottom]for v in points];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];rail=mesh_obj('SA'+str(lower['source_index'])+'_WallBase_'+original,verts,faces,'retained_wall_footprint_base_rail');rail.parent=root;rail['retained_owner']=lower['owner'];base_rails.append(rail.name)
 bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();native=W/'StarAtlasSpecialtyEighthReceiving.blend';out=W/P['model_file'];bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);first=sha(out);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);assert sha(out)==first
for rel,h in P['source_pins'].items():assert sha(R/rel)==h
for lower in P['lower_structural_owners']:assert sha(R/lower['native_source'])==lower['native_sha256'] and sha(R/'Game/assets/models'/lower['runtime_source'])==lower['runtime_sha256']
validate_and_copy(out,R/'Game/assets/models'/out.name);P.update(model_sha256=first,native_sha256=sha(native),retained_structure_objects=retained,base_rails=base_rails,mesh_count=sum(o.type=='MESH'for o in bpy.data.objects),native_repeat_export_identical=True)
(W/'RUNTIME_RECEIVING.json').write_text(json.dumps(P,indent=2)+'\n');(W/'RECEIVING_NATIVE_CHECK.json').write_text(json.dumps({'status':'PASS','native_sha256':sha(native),'export_sha256':first,'mesh_count':P['mesh_count'],'retained_source_objects':len(retained),'wall_base_rails':len(base_rails),'new_frame_members':len(P['parts']),'fresh_native_repeat_identical':True,'source_files_unchanged':True},indent=2)+'\n')
