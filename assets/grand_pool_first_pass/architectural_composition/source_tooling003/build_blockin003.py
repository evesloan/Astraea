"""Parent-coordinated two-thread source build. New blockin003 only, no export/render/Game."""
import bpy,bmesh,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');TARGET=C/'assets/grand_pool_first_pass/architectural_composition';OUT=TARGET/'revisions/blockin003';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((S/'BLOCKIN_PLAN_003.json').read_text());gate=json.loads((S/'BLOCKIN_PREFLIGHT_003.json').read_text());assert gate['status']=='PURE_PREFLIGHT_PASS' and gate['plan_sha256']==sha(S/'BLOCKIN_PLAN_003.json');assert not OUT.exists(),'Preserve every surviving source revision'
for path,h in plan['input_sha256'].items():assert sha(path)==h
assert len(plan['parts'])==451 and len(plan['plants'])==12 and not plan['fixtures'];assert plan['budget']['active_shadow_limit_unchanged']==8

def canonical(v):
 if isinstance(v,(str,int,float,bool))or v is None:return v
 try:return [canonical(x)for x in v]
 except TypeError:return str(v)
def mat_state(mat):
 nodes=[]
 for n in mat.node_tree.nodes:
  row={'name':n.name,'type':n.type,'inputs':{x.name:canonical(x.default_value)for x in n.inputs if hasattr(x,'default_value')}}
  if n.type=='TEX_IMAGE':
   im=n.image;assert im and im.packed_file;row['image']={'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'extension':n.extension,'interpolation':n.interpolation}
  nodes.append(row)
 return{'role':mat.get('astraea_material_role'),'nodes':nodes,'links':sorted([l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in mat.node_tree.links),'metric_tile_m':canonical(mat.get('meters_per_tile_uv',[1,1])),'backface_culling':mat.use_backface_culling}

def load_materials():
 materials={};provenance={}
 for path in [C/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend',C/'assets/aquatic_lounge/source/AST-AQU-001.blend']:
  with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.materials=list(src.materials)
  for mat in dst.materials:
   role=mat.get('astraea_material_role')
   if role in {p['material_role']for p in plan['parts']} and role not in materials:
    materials[role]=mat;provenance[role]={'source':str(path.relative_to(C)),'source_sha256':sha(path),'material_name':mat.name,'material_state':mat_state(mat)}
 assert set(materials)=={p['material_role']for p in plan['parts']},set(materials)
 return materials,provenance

names={'loggia':'AST-AQU-016_pool_loggia','focal_end':'AST-AQU-016_pool_focal_end','roof':'AST-AQU-016_pool_roof_composition'};OUT.mkdir(parents=True,exist_ok=False);(OUT/'source').mkdir();(OUT/'qa').mkdir();results=[]
for group,name in names.items():
 bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.;scene.render.threads_mode='FIXED';scene.render.threads=2;materials,provenance=load_materials();count=0;triangles=0
 for part in [p for p in plan['parts']if p['group']==group]:
  vertices=[];lookup={};remap=[]
  for x,y,z in part['vertices_xyz']:
   p=struct.unpack('<3f',struct.pack('<3f',x,-z,y))
   if p not in lookup:lookup[p]=len(vertices);vertices.append(p)
   remap.append(lookup[p])
  faces=[[remap[i]for i in f]for f in part['faces']];assert all(len(set(f))==len(f)for f in faces)
  mesh=bpy.data.meshes.new(part['name']+'_editable');mesh.from_pydata(vertices,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();mesh.calc_loop_triangles()
  ob=bpy.data.objects.new(part['name'],mesh);scene.collection.objects.link(ob);mat=materials[part['material_role']];mesh.materials.append(mat);ob['parent_design_id']='AST-AQU-016';ob['source_group']=group;ob['material_role']=part['material_role'];ob['support_json']=json.dumps(part['support']);ob['collision_contract']=part['collision'];ob['blockin_only']=True;ob['source_plan_sha256']=sha(S/'BLOCKIN_PLAN_003.json');ob['new_floor_owner']=False
  if part.get('intentional_anchor_through'):ob['named_finish_skin_anchor_penetrations']=json.dumps(part['intentional_anchor_through'])
  if part.get('intentional_new_mechanical_joint'):ob['intentional_new_mechanical_joint']=part['intentional_new_mechanical_joint']
  uv=mesh.uv_layers.new(name='MetreScaled_SourceRole');scale=mat.get('meters_per_tile_uv',[1,1]);desired=part.get('grain_axis_xyz',[1,0,0]);axis=Vector((desired[0],-desired[2],desired[1]))
  for face in mesh.polygons:
   normal=face.normal.normalized();u=axis-normal*axis.dot(normal)
   if u.length<.01:
    alternative=Vector((0,0,1))if abs(normal.z)<.9 else Vector((0,1,0));u=alternative-normal*alternative.dot(normal)
   u.normalize();v=normal.cross(u).normalized()
   for li in face.loop_indices:
    p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
  count+=1;triangles+=len(mesh.loop_triangles)
 scene['status']='Editable spatial block-in; no export or first-pass acceptance';scene['parent_design_id']='AST-AQU-016';scene['source_plan_sha256']=sha(S/'BLOCKIN_PLAN_003.json');scene['budget_json']=json.dumps(plan['budget']);scene['pending']='Independent reopen, rooted support, export equivalence and native runtime acceptance required; market threshold and lighting refinements are separate bounded work'
 path=OUT/'source'/(name+'.blend');assert not path.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);results.append({'group':group,'source':str(path),'source_sha256':sha(path),'meshes':count,'triangles':triangles,'material_provenance':{role:value for role,value in provenance.items()if role in {p['material_role']for p in plan['parts']if p['group']==group}}});print('BLOCKIN_SOURCE_SAVED',group,count,flush=True)
for path,h in plan['input_sha256'].items():assert sha(path)==h
(OUT/'qa/BUILD_RECEIPT.json').write_text(json.dumps({'status':'BLOCKIN_SAVED_PENDING_INDEPENDENT_REOPEN','plan_sha256':sha(S/'BLOCKIN_PLAN_003.json'),'sources':results,'original_inputs_unchanged':True,'exports':[],'runtime_writes':[]},indent=2)+'\n')
print('Three source block-ins saved, no export/render/runtime change.')
