"""Run only in the parent's reserved Blender serial slot.
Author editable geometry with retained materials and the original instanced chair.
No export, registry, runtime, shared source edits, rendering or overwrite of an
existing source file. The scene remains an unfinished source candidate.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

R=Path(__file__).resolve().parents[1]
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
p=argparse.ArgumentParser();p.add_argument('--output-name',default='AST-CUL-005.blend');p.add_argument('--report-name',default='editable_source_internal_report.json');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[])
assert Path(a.output_name).name==a.output_name and a.output_name.endswith('.blend')
out=R/'source'/a.output_name
assert Path(a.report_name).name==a.report_name and a.report_name.endswith('.json')
report_path=R/'qa'/a.report_name
if report_path.exists():raise RuntimeError('Preserve existing source QA report: choose a new explicit --report-name')
if out.exists():raise RuntimeError('Preserve existing editable source: choose a new explicit --output-name; do not overwrite')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(R/'qa/SOURCE_BUILD_INPUT_PINS.json')
for rel,expected in pins['owned_inputs_sha256'].items():
 assert sha(R/rel)==expected,('Changed owned input',rel)
for path,expected in pins['retained_inputs_sha256'].items():
 assert sha(Path(path))==expected,('Changed retained input',path)
registered=[x for x in read(CAT/'catalogue_manifest.json')['assets']if x['catalogue_id']=='AST-CUL-005']
assert not registered or all(x['family']=='grand_lantern_theater_section'for x in registered), 'Catalogue identity belongs to another family'
g=read(R/'source/geometry.json');mc=read(R/'contracts/material_reuse_contract.json');pc=read(R/'contracts/place_instances.json');surface=read(R/'contracts/surface_manifest.json')
assert len(surface['surfaces'])==8 and len(pc['places'])==2200
chair_path=CAT/'assets/auditorium_use/source/AST-CUL-003.blend';chair_hash=sha(chair_path);assert chair_hash==pc['source_sha256']
# A new local scene; loading or changing appended datablocks never modifies inputs.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
material_specs={}
for manifest_path in ['materials/material_manifest.json','materials/auditorium/manifest.json','materials/staff/manifest.json']:
 for role,spec in read(CAT/manifest_path)['materials'].items():
  assert role not in material_specs,('Duplicate material authority',role)
  material_specs[role]={**spec,'manifest':manifest_path}
mats={};material_load_records=[];tile_scales={};tile_scale_basis={}
for rel,names in mc['sources'].items():
 with bpy.data.libraries.load(str(CAT/'assets'/rel),link=False)as(src,dst):
  selected=[]
  for role in names:
   candidates=[name for name in [role,'ASTRAEA_'+role]if name in src.materials]
   assert len(candidates)==1,('Ambiguous or missing retained material datablock',rel,role,candidates)
   selected.append(candidates[0])
  selected_source_names=tuple(selected)  # Blender mutates the list assigned to dst.materials.
  dst.materials=list(selected_source_names)
 for role,source_name,mat in zip(names,selected_source_names,dst.materials):
  assert isinstance(source_name,str),('Source material name must stay a string',type(source_name).__name__)
  assert mat is not None,('Could not append retained material',source_name)
  mats[role]=mat
  if role=='gallery_glass':
   assert not any(n.type=='TEX_IMAGE'and n.image for n in mat.node_tree.nodes), 'Textured glass needs its own metric scale authority'
   scale=[1.0,1.0];basis='Untextured retained gallery glass: UVs unused by shader'
  else:
   assert role in material_specs,('Missing tile-scale authority',role)
   contract_scale=[float(x)for x in material_specs[role]['meters_per_tile_uv']]
   if 'meters_per_tile_uv'in mat:
    scale=[float(x)for x in mat['meters_per_tile_uv']]
    assert len(scale)==2 and max(abs(scale[i]-contract_scale[i])for i in range(2))<1e-7,('Source/manifest material-scale conflict',role)
    basis='Retained material meters_per_tile_uv, checked against '+material_specs[role]['manifest']
   else:
    scale=contract_scale;basis='Retained ARC material omits scale metadata; exact pinned '+material_specs[role]['manifest']+' supplies metric UV scale'
  assert len(scale)==2 and all(math.isfinite(x)and x>0 for x in scale)
  tile_scales[role]=scale;tile_scale_basis[role]=basis
  material_load_records.append({'role':role,'source':rel,'source_datablock':source_name,'appended_datablock':mat.name,'meters_per_tile_uv':scale,'scale_basis':basis})
root=bpy.data.objects.new('AST-CUL-005',None);bpy.context.collection.objects.link(root)
root['programme_keys']=json.dumps(['D11_directory_01','D12_directory_11','D13_directory_01'])
root['source_geometry_sha256']=sha(R/'source/geometry.json');root['source_only']=True;root['runtime_accepted']=False
root['floor_ownership']='D11 flat and non-walkable foundation remain compiler proposals; excluded from this source. Eight upper authored surfaces remain exact.'
root['first_pass_complete']=False
parts=[o for o in g['objects']if o['role']!='preview_only'];groups={}
for o in parts:
 key=(o.get('surface_region')or o['name'].split('_')[0],o['material_family'],o['role'])
 vs,fs,names,fm,ranges=groups.setdefault(key,([],[],[],[],[]));base=len(vs);fbase=len(fs)
 vs.extend((x,-z,y)for x,y,z in o['vertices_world']);fs.extend([base+i for i in f]for f in o['faces']);names.append(o['name']);fm.extend(o.get('face_material_families',[o['material_family']]*len(o['faces'])))
 ranges.append({'name':o['name'],'vertex_start':base,'vertex_count':len(o['vertices_world']),'face_start':fbase,'face_count':len(o['faces'])})
mesh_reports=[];all_world=[]
for(owner,material,role),(vs,fs,names,fm,ranges)in groups.items():
 me=bpy.data.meshes.new(owner);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 assert len(me.vertices)==len(vs)and len(me.polygons)==len(fs)
 obj=bpy.data.objects.new(owner+'__'+material+'__'+role,me);bpy.context.collection.objects.link(obj);obj.parent=root
 material_names=list(dict.fromkeys(fm))
 for name in material_names:me.materials.append(mats[name])
 for face,mat_name in zip(me.polygons,fm):face.material_index=material_names.index(mat_name)
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 for face in me.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
  face_role=material_names[face.material_index];sx,sy=tile_scales[face_role]
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/sx,v[axes[1]]/sy)
 # Independent read-back check per face uses its assigned material, including
 # mixed ivory/walnut groups. Raw metre UVs cannot pass non-unit tile scales.
 max_uv_error=0.0;face_role_counts={}
 for face in me.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
  face_role=material_names[face.material_index];sx,sy=tile_scales[face_role];face_role_counts[face_role]=face_role_counts.get(face_role,0)+1
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;actual=uv.data[li].uv
   max_uv_error=max(max_uv_error,abs(actual[0]-v[axes[0]]/sx),abs(actual[1]-v[axes[1]]/sy))
 assert max_uv_error<.00006,('Material-scaled UV error',obj.name,max_uv_error)
 assert len(uv.data)==len(me.loops)
 maxerr=max((Vector(v)-me.vertices[i].co).length for i,v in enumerate(vs))
 assert maxerr<.00003,(obj.name,maxerr)
 assert all(math.isfinite(float(c))for item in uv.data for c in item.uv)
 obj['catalogue_id']='AST-CUL-005';obj['ownership_region']=owner;obj['material_family']=material;obj['collision_role']=role;obj['pure_part_names']=json.dumps(names);obj['pure_part_ranges']=json.dumps(ranges)
 me.calc_loop_triangles()
 mesh_reports.append({'object':obj.name,'parts':len(names),'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(me.loop_triangles),'material_slots':material_names,'uv_loops':len(uv.data),'maximum_vertex_float_storage_error_m':maxerr,'maximum_material_scaled_uv_error':max_uv_error,'face_count_by_material_role':face_role_counts})
 all_world.extend([(v.co.x,v.co.z,-v.co.y)for v in me.vertices])
# Append untouched chair hierarchy once, instance it2200times; no new design or controller.
with bpy.data.libraries.load(str(chair_path),link=False)as(src,dst):dst.objects=list(src.objects)
loaded=[o for o in dst.objects if o];chair_root=next((o for o in loaded if o.name=='AST-CUL-003'),None)
if chair_root is None:raise RuntimeError('Exact retained chair root absent')
col=bpy.data.collections.new('Retained_AST-CUL-003_source')
chair_members=[]
for obj in loaded:
 ancestor=obj
 while ancestor and ancestor!=chair_root:ancestor=ancestor.parent
 if ancestor==chair_root:col.objects.link(obj);chair_members.append(obj.name)
assert chair_members
chair_objects=list(col.objects)
def chair_fingerprint():
 records=[]
 for ob in sorted(chair_objects,key=lambda o:o.name):
  row={'name':ob.name,'parent':ob.parent.name if ob.parent else None,'matrix_basis':[[float(v)for v in r]for r in ob.matrix_basis]}
  if ob.type=='MESH':
   me=ob.data;row.update(vertices=[list(v.co)for v in me.vertices],faces=[list(f.vertices)for f in me.polygons],face_materials=[f.material_index for f in me.polygons],materials=[m.name if m else None for m in me.materials],uvs={layer.name:[list(uv.uv)for uv in layer.data]for layer in me.uv_layers})
  records.append(row)
 return hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
chair_appended_fingerprint=chair_fingerprint()
for s in pc['places']:
 obj=bpy.data.objects.new(s['id'],None);bpy.context.collection.objects.link(obj);obj.parent=root;obj.instance_type='COLLECTION';obj.instance_collection=col
 x,y,z=s['position'];obj.location=(x,-z,y);obj.rotation_euler.z=s['orientation_yaw_radians'];obj['existing_family']='AST-CUL-003';obj['capacity_preview_only']=True;obj['seat_controller_authored']=False
# These datums preserve mounts/worklight placement. They do not create emitters.
fixture_records=read(R/'contracts/fixture_markers.json')['fixtures']
for f in fixture_records:
 obj=bpy.data.objects.new('DATUM_'+f['id'],None);bpy.context.collection.objects.link(obj);obj.parent=root
 x,y,z=f['position_world'];obj.location=(x,-z,y);obj['source_support']=f['source_support'];obj['source_family']=f['family'];obj['direction_world']=f['aim_world'];obj['runtime_light_installed']=False;obj['fixture_geometry_complete']=False
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['status']='Unfinished source candidate. Actual emitting fixtures, fitted doors/lift, furnishings/details, compiler adoption, source/export and runtime/visual acceptance remain gated.'
scene['foundation_proposal_sha256']=sha(R/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json')
scene['rendering_accepted']=False
used_images={};all_used_materials={mat.name:mat for mat in mats.values()}
for ob in chair_objects:
 if ob.type=='MESH':
  for mat in ob.data.materials:
   assert mat is not None,('Retained chair empty material slot',ob.name)
   all_used_materials[mat.name]=mat

def image_nodes(tree,seen=None):
 seen=set()if seen is None else seen
 if tree.as_pointer()in seen:return []
 seen.add(tree.as_pointer());out=[]
 for node in tree.nodes:
  if node.type=='TEX_IMAGE'and node.image:out.append(node)
  elif node.type=='GROUP'and node.node_tree:out.extend(image_nodes(node.node_tree,seen))
 return out
chair_material_names={mat.name for ob in chair_objects if ob.type=='MESH'for mat in ob.data.materials}
material_texture_checks=[]
for mat in all_used_materials.values():
 role=str(mat.get('astraea_material_role',''))
 if not role:
  role=next((r for r,m in mats.items()if m==mat),'')
 assert role,('Unidentified material role; refuse unchecked texture',mat.name)
 nodes=image_nodes(mat.node_tree)if mat.use_nodes else[]
 if role!='gallery_glass':
  assert role in material_specs and nodes,('Missing expected texture role',mat.name,role)
  expected_texture_sha=material_specs[role]['sha256']
 else:
  assert not nodes;expected_texture_sha=None
 image_records=[]
 for node in nodes:
  image=node.image
  if not image.packed_file:image.pack()
  assert image.packed_file is not None,('Source texture not portable',image.name)
  actual_sha=hashlib.sha256(image.packed_file.data).hexdigest()
  assert actual_sha==expected_texture_sha,('Retained texture bytes mismatch',mat.name,image.name,actual_sha,expected_texture_sha)
  item={'packed_bytes':len(image.packed_file.data),'sha256':actual_sha,'size':list(image.size)}
  used_images[image.name]=item;image_records.append({'image':image.name,**item})
 material_texture_checks.append({'material':mat.name,'role':role,'is_retained_chair_material':mat.name in chair_material_names,'expected_texture_sha256':expected_texture_sha,'images':image_records})
assert chair_fingerprint()==chair_appended_fingerprint,'Retained chair mesh/UV/transform/material slots changed'
assert all(sha(Path(path))==expected for path,expected in pins['retained_inputs_sha256'].items()),'Retained input changed during Blender authoring'
assert sha(chair_path)==chair_hash
assert chair_fingerprint()==chair_appended_fingerprint
report={'status':'Editable source internal construction verification only; not export/runtime/art acceptance','source_blend':str(out),'source_blend_sha256':None,'geometry_sha256':sha(R/'source/geometry.json'),'source_parts_preserved':len(parts),'authored_mesh_groups':len(groups),'mesh_reports':mesh_reports,'vertices':sum(x['vertices']for x in mesh_reports),'triangles':sum(x['triangles']for x in mesh_reports),'world_bounds':{'min':[min(v[k]for v in all_world)for k in range(3)],'max':[max(v[k]for v in all_world)for k in range(3)]},'chair_collection_members':chair_members,'unchanged_retained_chair_sha256':chair_hash,'chair_instances':2200,'chair_controller_created':False,'source_mount_markers':len(fixture_records),'packed_material_images':used_images,'material_load_and_tile_scales':material_load_records,'all_used_material_texture_checks':material_texture_checks,'retained_chair_appended_mesh_uv_transform_fingerprint':chair_appended_fingerprint,'retained_chair_materials_checked':sorted(chair_material_names),'maximum_material_scaled_uv_error':max(m['maximum_material_scaled_uv_error']for m in mesh_reports),'compiler_flat_or_foundation_meshes_authored':False,'new_runtime_lights':0,'new_export':False,'first_pass_complete':False,'not_accepted':['Source export equivalence','Full retained runtime-neighbour census','Runtime/capsule/loaded-cart/door/lift behavior','Normal-height visual review','First-pass furnishings and actual light coverage','Structural/pressure certification']}
# Prove the complete report is JSON-safe BEFORE creating an irreversible build output.
json.dumps(report,indent=2,allow_nan=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
assert sha(chair_path)==chair_hash
assert chair_fingerprint()==chair_appended_fingerprint
report['source_blend_sha256']=sha(out)
with report_path.open('x')as file:file.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:report[k]for k in ['status','source_parts_preserved','authored_mesh_groups','vertices','triangles','chair_instances','source_mount_markers','first_pass_complete']}))
