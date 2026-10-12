"""New dimensioned clinical fitting, using retained staff materials and door lifecycle."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];CAT=ROOT/'BlenderCatalogue'
p=json.load(open(HERE/'source/COMPLETE_CLINICAL_CONTRACT.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():assert sha(ROOT/f)==h,f
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
materials=json.load(open(CAT/'materials/staff/manifest.json'));defs=materials['materials'];mats={}
def mat(role):
 if role in mats:return mats[role]
 row=defs[role];m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];bs.inputs['Base Color'].default_value=tuple(v/255 for v in row['colour_srgb_8bit'])+(1,)
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.image=bpy.data.images.load(str(CAT/'materials/staff'/row['file']),check_existing=True);tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.diffuse_color=tuple(v/255 for v in row['colour_srgb_8bit'])+(1,)
 m['astraea_material_role']=role;m['meters_per_tile_uv']=row['meters_per_tile_uv'];m['material_revision']=materials['revision'];m['intended_context']='staff_only';mats[role]=m;return m
def gv(x,y,z):return(x,-z,y)
rows=[]
def cube(name,a,role,parent=None):
 x0,x1,y0,y1,z0,z1=a;v=[gv(x,y,z)for y in[y0,y1]for z in[z0,z1]for x in[x0,x1]];faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.update();me.materials.append(mat(role));uv=me.uv_layers.new(name='MetricUV');tile=defs[role]['meters_per_tile_uv']
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();w=n.cross(u)
  for i in f.loop_indices:q=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=(q.dot(u)/tile[0],q.dot(w)/tile[1])
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o['role']=role;o['source_asset']='AST-MED-G3-009';o['new_dimensioned_clinical_fitting']=True;rows.append(dict(name=name,aabb=a,role=role));return o
for side,lo,hi in [('LEFT',-1.8,.02),('RIGHT',-.02,1.8)]:
 e=bpy.data.objects.new('LEAF_'+side,None);bpy.context.collection.objects.link(e);e['travel_m']=1.9;e['clinical_moving_leaf']=True
 cube(side+'_Panel',[lo,hi,.04,2.36,-.025,.025],'staff_white_paint',e)
 for name,y0,y1 in [('Base',0,.04),('Top',2.36,2.4)]:cube(side+'_'+name,[lo,hi,y0,y1,-.0275,.0275],'staff_zinc',e)
 for name,x0,x1 in ([('Outer',lo,lo+.025),('Meeting',hi-.025,hi)]if side=='LEFT'else[('Outer',hi-.025,hi),('Meeting',lo,lo+.025)]):cube(side+'_'+name,[x0,x1,.04,2.36,-.0275,.0275],'staff_rubber'if name=='Meeting'else'staff_bluegrey_paint',e)
for side,lo,hi in [('Left',-1.94,-1.8),('Right',1.8,1.94)]:
 for face,z0,z1 in [('Front',-.14,-.035),('Back',.035,.14)]:cube('Frame'+side+face,[lo,hi,0,2.55,z0,z1],'staff_white_paint')
# Closed casework supports the dimensioned 1.9m side pockets, leaving the full
# leaf channel open. The header and outer end caps close their source housing.
for side,lo,hi in [('Left',-3.72,-1.94),('Right',1.94,3.72)]:
 for face,z0,z1 in [('Front',-.14,-.035),('Back',.035,.14)]:cube('Pocket'+side+face,[lo,hi,0,2.4,z0,z1],'staff_bluegrey_paint')
 cube('Pocket'+side+'End',[lo,lo+.02,0,2.4,-.14,.14]if side=='Left'else[hi-.02,hi,0,2.4,-.14,.14],'staff_zinc')
cube('FullFrameHeader',[-3.72,3.72,2.4,2.55,-.14,.14],'staff_white_paint')
bpy.context.scene['source_asset']='AST-MED-G3-009';bpy.context.scene['no_persistent_identity_created']=True
native=HERE/'source/AST-MED-G3-009.blend';export=HERE/'exports/AST-MED-G3-009.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
originals=list(bpy.context.scene.objects);bindings=[]
for q in p['door_bindings']:
 copies={o:o.copy()for o in originals};at=q['position'];pose=Matrix.Translation(Vector(gv(*at)))@Matrix.Rotation(q['yaw'],4,'Z')
 for old,new in copies.items():
  bpy.context.collection.objects.link(new);new.name=q['name']+'__'+old.name;new.parent=copies.get(old.parent);new.matrix_parent_inverse=old.matrix_parent_inverse.copy();new.matrix_basis=old.matrix_basis.copy()
  if old.parent not in copies:new.matrix_world=pose@old.matrix_world
  if old.type=='MESH':assert new.data==old.data;bindings.append(dict(name=new.name,template_mesh_payload_shared=True,unscaled=True))
for o in originals:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene['source_asset']='AST-MED-G3-010'
assembly_native=HERE/'source/AST-MED-G3-010.blend';assembly_export=HERE/'exports/AST-MED-G3-010.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(assembly_native),compress=True);bpy.ops.export_scene.gltf(filepath=str(assembly_export),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
q=dict(status='SOURCE_BOUND_SLIDING_FITTINGS_BUILT',template_new_parts=rows,clear_aperture_m=[3.6,2.4],travel_m=1.9,max_linear_speed_m_s=1.0,instances=len(p['door_bindings']),mesh_bindings=len(bindings),no_original_asset_rescaled_or_replaced=True,no_registry_or_persistent_ids_created=True,template_sha256=sha(export),template_blend_sha256=sha(native),assembly_sha256=sha(assembly_export),assembly_blend_sha256=sha(assembly_native),source_poses=p['door_bindings'])
(HERE/'qa/SLIDING_NATIVE_ASSEMBLY.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['status','instances','mesh_bindings','template_sha256','assembly_sha256']}))
