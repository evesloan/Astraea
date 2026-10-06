"""One new scratch-only 24-mesh additive source; never opens or overwrites originals."""
import bpy,sys,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from fixture_recipe import *
sys.path.insert(0,str(P/'source/firstpass_001'))
from firstpass_common import material_record,mesh_record,image_nodes,bvec,wvec
OUT=R/'AST-CUL-005_inward_stair_channels_020.blend'
contract=read(R/'SOURCE_CONTRACT.json')
for path,expected in contract['input_pins'].items():assert sha(Path(path))==expected,('Changed input',path)
assert not OUT.exists() and not(R/'BUILD_RECEIPT.json').exists() and not(R/'ACTUAL_SOURCE_RECIPE.json').exists()
# Start empty. Append only four actual retained guard/tread groups and the two exact materials.
# This does not open the original for editing and does not save any source library.
bpy.ops.wm.read_factory_settings(use_empty=True)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
for im in list(bpy.data.images):bpy.data.images.remove(im)
groups=['D11__champagne_metal__guard_proposal','D11__ivory_enamel__stair_flight','D12__champagne_metal__guard_proposal','D12__ivory_enamel__stair_flight']
material_names=[m['datablock']for m in contract['materials'].values()]
with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):
 assert all(n in src.objects for n in groups)and all(n in src.materials for n in material_names)
 dst.objects=groups;dst.materials=material_names
mats={role:bpy.data.materials[m['datablock']]for role,m in contract['materials'].items()}
materials=[]
for role,m in contract['materials'].items():
 mat=mats[role];record_sha=digest(material_record(mat));assert record_sha==m['retained_material_record_sha256'],('Retained graph changed',mat.name,record_sha,m['retained_material_record_sha256'])
 nodes=image_nodes(mat.node_tree);assert nodes,('Missing actual texture',mat.name)
 for n in nodes:assert n.image.packed_file and hashlib.sha256(n.image.packed_file.data).hexdigest()==m['texture_sha256']
 materials.append({'role':role,'datablock':mat.name,'retained_graph_sha256':record_sha,'meters_per_tile_uv':m['meters_per_tile_uv'],'packed_texture_sha256':m['texture_sha256'],'graph_changed':False})
source_snapshot=read(P/'source/firstpass_003/source_repair003/BUILD_REPORT.json')['preserved_snapshot'];wanted=set(contract['actual_source_references']);references={};proof=[]
def worldmatrix(ob):
 chain=[]
 while ob:chain.append(ob);ob=ob.parent
 matrix=Matrix.Identity(4)
 for item in reversed(chain):matrix=matrix@item.matrix_basis
 return matrix
for ob in list(dst.objects):
 me=ob.data;matrix=worldmatrix(ob)
 for part in json.loads(ob['pure_part_ranges']):
  name=part['name']
  if name not in wanted:continue
  partdigest=digest(mesh_record(me,part['face_start'],part['face_count'],part['vertex_start'],part['vertex_count']))
  assert partdigest==source_snapshot['parts'][name],('Actual retained part fingerprint changed',name)
  start,count=part['vertex_start'],part['vertex_count'];verts=[list(wvec(matrix@v.co))for v in list(me.vertices)[start:start+count]]
  faces=[[i-start for i in p.vertices]for p in list(me.polygons)[part['face_start']:part['face_start']+part['face_count']]]
  original=contract['actual_source_references'][name];error=max(abs(verts[i][k]-v[k])for i,v in enumerate(original['vertices_world'])for k in range(3));assert error<.00003,(name,error)
  references[name]={**original,'vertices_world':verts,'faces':faces};proof.append({'name':name,'source_group':ob.name,'actual_source_part_sha256':partdigest,'maximum_difference_from_contract_m':error})
assert set(references)==wanted and len(references)==98
# Discard temporary appended geometry. The output has only the 24 requested new meshes.
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
for me in list(bpy.data.meshes):bpy.data.meshes.remove(me)
for col in list(bpy.data.collections):bpy.data.collections.remove(col)
for mat in list(bpy.data.materials):
 if mat not in mats.values():bpy.data.materials.remove(mat)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
recipe=make_recipe(references);recipe['input_pins']=contract['input_pins'];recipe['materials']=contract['materials'];recipe['reference_basis']='Actual hash-verified dfb Blender source parts, extracted read-only before additive authoring.'
fixturemap={f['flight']:f for f in recipe['fixtures']};collections={};uv_checks=[]
for flight,f in fixturemap.items():
 col=bpy.data.collections.new('INWARD_'+flight);bpy.context.scene.collection.children.link(col);collections[flight]=col
for row in recipe['objects']:
 f=fixturemap[row['flight']];origin=(np.array(f['channel_centerline_endpoints'][0])+np.array(f['channel_centerline_endpoints'][1]))*.5
 me=bpy.data.meshes.new(row['name']);me.from_pydata([bvec(np.array(v)-origin)for v in row['vertices_world']],[],row['faces']);me.materials.append(mats[row['material_family']]);me.update()
 ob=bpy.data.objects.new(row['name'],me);collections[row['flight']].objects.link(ob);ob.location=bvec(origin)
 ob['source_only']=True;ob['catalogue_family']='AST-CUL-005';ob['fixture_flight']=row['flight'];ob['fixture_part']=row['part'];ob['mount_guard']=f['guard'];ob['material_family']=row['material_family'];ob['retained_source_sha256']=SOURCE_SHA;ob['runtime_installed']=False
 scale=contract['materials'][row['material_family']]['meters_per_tile_uv'];uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 # True per-face physical metric projection, not normalized UVs or world-axis shortening.
 for face in me.polygons:
  originface=me.vertices[face.vertices[0]].co;u=(me.vertices[face.vertices[1]].co-originface).normalized();v=face.normal.cross(u).normalized()
  for li in face.loop_indices:
   point=me.vertices[me.loops[li].vertex_index].co-originface;uv.data[li].uv=(point.dot(u)/scale[0],point.dot(v)/scale[1])
 ob['meters_per_tile_uv']=scale;ob['uv_method']='Per-face orthonormal physical metric projection divided by retained material tile scale'
for f in recipe['fixtures']:
 lens=bpy.data.objects[next(n for n in f['mesh_names']if n.endswith('_LENS'))];ob=bpy.data.objects.new(f['attachment_empty'],None);collections[f['flight']].objects.link(ob);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.06
 ob.parent=lens;ob.matrix_parent_inverse=Matrix.Identity(4);ob.location=Vector(bvec(f['attachment_world']))-lens.location
 ob['source_only']=True;ob['physical_fixture_lens']=lens.name;ob['mount_guard']=f['guard'];ob['source_fraction_from_lower_guard_end']=.75;ob['optical_exit_offset_m']=.004;ob['optical_exit_normal_world']=[-1.,0.,0.];ob['range_m_geometry_only']=f['range_m_geometric_only'];ob['energy_unset_until_native_trial']=True;ob['runtime_light_installed']=False
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2
scene['scope']='Source-only additive: eight inward stair guard channels; exactly 24 simple editable meshes, 8 non-light source attachment empties. Actual dfb guard/tread references retained in pinned contract.'
scene['new_runtime_lights']=0;scene['native_illumination_proven']=False;scene['original_outward_fixtures_unchanged']=True;scene['no_hidden_manufacturing_detail']=True
bpy.context.view_layer.update()
assert len(bpy.data.objects)==32 and len(bpy.data.meshes)==24 and len(bpy.data.lights)==0
for role,m in contract['materials'].items():assert digest(material_record(mats[role]))==m['retained_material_record_sha256']
for path,expected in contract['input_pins'].items():assert sha(Path(path))==expected,('Input changed during source build',path)
write_new(R/'ACTUAL_SOURCE_RECIPE.json',recipe)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
write_new(R/'BUILD_RECEIPT.json',{'status':'SOURCE_BUILT_REOPEN_PENDING','source_path':str(OUT),'source_sha256':sha(OUT),'actual_recipe_sha256':sha(R/'ACTUAL_SOURCE_RECIPE.json'),'retained_source_sha256':SOURCE_SHA,'mesh_count':24,'attachment_empties':8,'light_datablocks':0,'guard_tread_reference_proofs':proof,'exact_retained_materials':materials,'original_input_hashes_unchanged':True,'runtime_writes':False,'blender_threads':2})
print('BUILT',OUT,sha(OUT))
