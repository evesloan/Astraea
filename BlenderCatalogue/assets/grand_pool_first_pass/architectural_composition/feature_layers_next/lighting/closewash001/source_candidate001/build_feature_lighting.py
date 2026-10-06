"""Parent-coordinated, two-thread Blender source authoring ONLY.
New scratch candidate: 12 exact hardware parts + 3 source markers.
No render, export, Godot process, existing source replacement or repository write.
Run only after parent assigns the source slot; independent reopen is a separate run.
"""
import bpy, bmesh, json, hashlib, struct, sys, math, datetime
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
EXPECTED=Path('/workspace/scratch/375c2e438292/pool-architectural-composition/fixture_layer_proposal001/source_candidate001')
assert HERE==EXPECTED
PROPOSAL_DIR=HERE.parent
PROPOSAL=PROPOSAL_DIR/'PROPOSED_FIXTURE_LAYER.json'
PROPOSAL_SHA256='230df56e7149bba6b4a089a99ed0ad3f09774d1e42c51be35a0fe17ab727c106'
GEOMETRY_GATE_SHA256='297b2b9c995458c01a5ca9314c17c97bb31135ba23668c1acee72d017bfb0703'
MATERIAL_SOURCE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/finish_envelope/source/grand_pool_finish_envelope.blend')
SOURCE=HERE/'source/AST-AQU-016_pool_feature_lighting.blend'
QA=HERE/'qa';RECEIPT=QA/'BUILD_RECEIPT.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not SOURCE.exists() and not RECEIPT.exists(),'Never overwrite a surviving source candidate or build receipt.'
assert sha(PROPOSAL)==PROPOSAL_SHA256 and sha(PROPOSAL_DIR/'GEOMETRY_CHECKS.json')==GEOMETRY_GATE_SHA256
D=json.loads(PROPOSAL.read_text());gate=json.loads((PROPOSAL_DIR/'GEOMETRY_CHECKS.json').read_text());retained=json.loads((PROPOSAL_DIR/'INPUT_PINS.json').read_text())
assert D['status']=='PROPOSAL_SOURCE_NUMERICAL_PASS' and gate['status']=='PASS' and not gate['issues']
assert len(D['proposed_parts'])==12 and len(D['fixtures'])==3
assert D['parent_design_id']=='AST-AQU-016' and D['preserved']==dict(original_source_fixtures=39,architectural_parts=451,architectural_plants=12,original_programme_furnishings=126,active_source_budget=8)
protected=dict(retained['sha256'])
for p in PROPOSAL_DIR.iterdir():
 if p.is_file():protected[str(p)]=sha(p)
for p in PROPOSAL_DIR.glob('rejected*/*'):
 if p.is_file():protected[str(p)]=sha(p)
for path,h in protected.items():assert sha(path)==h,('Protected read input changed',path)
assert str(MATERIAL_SOURCE)in protected
assert all(p['parent_design_id']=='AST-AQU-016'for p in D['proposed_parts'])
assert {p['material_role']for p in D['proposed_parts']}=={'warm_walnut','champagne_metal','lens'}
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
assert not args,'This bounded builder accepts no export/render or other runtime arguments.'

# Capture shader graphs without reauthoring, reducing nodes, baking, or changing images.
def value(v):
 if v is None or isinstance(v,(str,bool,int,float)):return v
 if hasattr(v,'to_dict'):return {str(k):value(x)for k,x in v.to_dict().items()}
 if isinstance(v,dict):return {str(k):value(x)for k,x in v.items()}
 try:return [value(x)for x in v]
 except TypeError:return str(v)
def properties(block):return {str(k):value(v)for k,v in block.items()if k!='_RNA_UI'}
def material_fingerprint(mat):
 assert mat.use_nodes and mat.node_tree
 nodes=[]
 for n in mat.node_tree.nodes:
  row={'name':n.name,'type':n.type,'bl_idname':n.bl_idname,'label':n.label,'mute':n.mute,'custom_properties':properties(n),'inputs':[{'index':i,'name':s.name,'identifier':s.identifier,'default':value(s.default_value)}for i,s in enumerate(n.inputs)if hasattr(s,'default_value')]}
  for key in ['is_active_output','operation','blend_type','data_type','interpolation','extension','projection','projection_blend','distribution','subsurface_method']:
   if hasattr(n,key):row[key]=value(getattr(n,key))
  if n.type=='TEX_IMAGE':
   im=n.image;assert im and min(im.size)>0 and im.packed_file,'Retained source texture must be packed and readable.'
   row['image']={'name':im.name,'size':list(im.size),'channels':im.channels,'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode,'source':im.source,'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'packed_bytes':len(im.packed_file.data)}
  nodes.append(row)
 links=[]
 for l in mat.node_tree.links:
  links.append([l.from_node.name,next(i for i,s in enumerate(l.from_node.outputs)if s==l.from_socket),l.to_node.name,next(i for i,s in enumerate(l.to_node.inputs)if s==l.to_socket)])
 return {'name':mat.name,'custom_properties':properties(mat),'use_nodes':mat.use_nodes,'use_backface_culling':mat.use_backface_culling,'diffuse_color':list(mat.diffuse_color),'metallic':mat.metallic,'roughness':mat.roughness,'surface_render_method':getattr(mat,'surface_render_method',None),'nodes':sorted(nodes,key=lambda n:n['name']),'links':sorted(links)}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
scene.render.threads_mode='FIXED';scene.render.threads=2
exemplars={'champagne_metal':'WetRestWash_444_SourceBackplate','warm_walnut':'WetRestWash_444_RecessHousing','lens':'WetRestWash_444_OpalLens'}
with bpy.data.libraries.load(str(MATERIAL_SOURCE),link=False)as(src,dst):
 assert set(exemplars.values())<=set(src.objects);dst.objects=list(exemplars.values())
loaded={o.name:o for o in dst.objects};mats={};provenance={}
for role,name in exemplars.items():
 ob=loaded[name];assert ob.type=='MESH' and len(ob.data.materials)==1
 mat=ob.data.materials[0];mats[role]=mat
 provenance[role]={'source':str(MATERIAL_SOURCE),'source_sha256':sha(MATERIAL_SOURCE),'source_exemplar':name,'source_material':mat.name,'metric_tile_m':value(mat.get('meters_per_tile_uv',[1,1])),'material_state':material_fingerprint(mat)}
for ob in loaded.values():
 mesh=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
 if mesh.users==0:bpy.data.meshes.remove(mesh)
assert len(bpy.context.scene.objects)==0
collection=bpy.data.collections.new('AST-AQU-016_pool_feature_lighting');scene.collection.children.link(collection)
mesh_evidence=[]
for part in D['proposed_parts']:
 vertices=[];lookup={};remap=[]
 for x,y,z in part['world_vertices']:
  co=struct.unpack('<3f',struct.pack('<3f',x,-z,y))
  if co not in lookup:lookup[co]=len(vertices);vertices.append(co)
  remap.append(lookup[co])
 faces=[[remap[i]for i in f]for f in part['faces']]
 assert len(vertices)==8 and len(faces)==6 and all(len(set(f))==4 for f in faces)
 mesh=bpy.data.meshes.new(part['name']+'_editable_mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();mesh.calc_loop_triangles()
 assert len(mesh.vertices)==8 and len(mesh.polygons)==6 and len(mesh.loop_triangles)==12
 ob=bpy.data.objects.new(part['name'],mesh);collection.objects.link(ob);mesh.materials.append(mats[part['material_role']])
 ob['parent_design_id']='AST-AQU-016';ob['retained_host']=part['support'];ob['collision_contract']=part['collision_contract'];ob['material_role']=part['material_role'];ob['source_contract_sha256']=PROPOSAL_SHA256;ob['proposal_sha256']=PROPOSAL_SHA256;ob['source_group']='pool_feature_lighting';ob['new_floor_owner']=False
 if part.get('cast_shadow')is False:ob['cast_shadow']=False
 if part.get('contact_witnesses'):ob['contact_witnesses_json']=json.dumps(part['contact_witnesses'],sort_keys=True)
 uv=mesh.uv_layers.new(name='MetreScaled');scale=mats[part['material_role']].get('meters_per_tile_uv',[1,1]);assert min(scale)>0
 for poly in mesh.polygons:
  n=poly.normal.normalized()
  u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized()
  v=n.cross(u).normalized();assert u.length>.999 and v.length>.999
  for li in poly.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u)/scale[0],co.dot(v)/scale[1])
 mesh_evidence.append({'name':ob.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'triangles':len(mesh.loop_triangles),'material':mesh.materials[0].name,'uv_layer':uv.name,'support':part['support'],'collision_contract':part['collision_contract']})
for f in D['fixtures']:
 ob=bpy.data.objects.new(f['name'],None);collection.objects.link(ob);x,y,z=f['position_xyz'];ob.location=(x,-z,y)
 ob.empty_display_type='ARROWS';ob.empty_display_size=.12
 for key,value_ in {'parent_design_id':'AST-AQU-016','proposal_sha256':PROPOSAL_SHA256,'source_contract_sha256':PROPOSAL_SHA256,'direction_godot_xyz':f['direction_xyz'],'receiver_godot_xyz':f['receiver_xyz'],'visibility_sample_godot_xyz':f['visibility_sample_xyz'],'physical_housing':f['physical_housing'],'physical_lens':f['physical_lens'],'retained_host':f['host'],'suggested_range_m':f['suggested_range_m'],'suggested_energy':f['suggested_energy'],'suggested_spot_angle_degrees':f['suggested_spot_angle_degrees'],'receiver_source_part':f['receiver_source_part'],'source_support_anchor_godot_xyz':f['source_support_anchor_xyz'],'source_support_normal_godot_xyz':f['source_support_normal_xyz'],'profile':f['profile'],'scope':'Source trial only; actual native selection and A/B required.'}.items():ob[key]=value_
bpy.context.view_layer.update()
assert len(scene.objects)==15 and sum(o.type=='MESH'for o in scene.objects)==12 and sum(o.type=='EMPTY'for o in scene.objects)==3
assert len(bpy.data.materials)==3 and all(o.type in {'MESH','EMPTY'}for o in scene.objects)
assert all(not o.modifiers and o.parent is None for o in scene.objects)
for role,mat in mats.items():assert material_fingerprint(mat)==provenance[role]['material_state'],'Material graph changed during authoring.'
expected_import_policy={'derivative':'AST-AQU-016_pool_feature_lighting.glb','force_disable_compression':True,'scope':'This new asset only; no global or existing asset import changes.','render_equivalence':'Raw imported render surface arrays independently compared to exact source/export geometry; not get_faces.','collision_equivalence':'Independently predict native snapped collision faces and compare actual native contact, source-exit and receiver rays.','old_finish_contract':'All old39 fixtures/source bytes and old14 finish-adapter/tests unchanged.','active_source_budget':8,'native_AB_required':True}
scene['parent_design_id']='AST-AQU-016';scene['source_contract_sha256']=PROPOSAL_SHA256;scene['scope']='Separately approved fourth, new-only feature-lighting editable source; 12 hardware parts + 3 markers. No export/runtime/native acceptance.';scene['physical_host_scope']='External retained architecture hosts are hash-pinned; no host geometry is copied or edited.';scene['expected_import_policy_json']=json.dumps(expected_import_policy,sort_keys=True)
SOURCE.parent.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
assert not SOURCE.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=False)
assert SOURCE.exists()
for path,h in protected.items():assert sha(path)==h,('Protected input changed during source authoring',path)
receipt={'status':'NEW_SOURCE_SAVED_PENDING_INDEPENDENT_REOPEN','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_path':str(SOURCE),'source_sha256':sha(SOURCE),'proposal_sha256':PROPOSAL_SHA256,'geometry_gate_sha256':GEOMETRY_GATE_SHA256,'blender_version':bpy.app.version_string,'requested_threads':2,'source_mesh_parts':12,'source_markers':3,'source_triangles':144,'physical_parts':9,'visual_lenses':3,'material_provenance':provenance,'meshes':mesh_evidence,'protected_input_sha256':protected,'protected_inputs_unchanged':True,'expected_import_policy':expected_import_policy,'exports':[],'renders':[],'game_or_catalogue_writes':[],'native_AB_or_selection':'NOT_RUN_REQUIRED_LATER'}
assert not RECEIPT.exists();RECEIPT.write_text(json.dumps(receipt,indent=2)+'\n')
print('SOURCE_ONLY_BUILD_SAVED',SOURCE,sha(SOURCE),'12 hardware parts, 3 markers; independent reopen remains.',flush=True)
