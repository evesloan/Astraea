"""Independent reopened-source QA, no save/export/build or original file edits.
Open surviving theater Blend, measure its actual meshes/UVs/instances/textures,
then open the original chair Blend to compare the retained hierarchy directly.
"""
import argparse,collections,hashlib,json,math,re,sys
from pathlib import Path
import bpy
from mathutils import Vector
P=argparse.ArgumentParser();P.add_argument('--package',type=Path,required=True);P.add_argument('--source',type=Path,required=True);P.add_argument('--expected-sha',required=True);P.add_argument('--report',type=Path,required=True);a=P.parse_args(sys.argv[sys.argv.index('--')+1:]);R=a.package;CAT=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert not a.report.exists(),'Preserve prior reopened-source QA output'
assert a.source.resolve().parent==(R/'source').resolve()
assert sha(a.source)==a.expected_sha,'Surviving source changed before independent QA'
source_hash=sha(a.source);chair_path=CAT/'assets/auditorium_use/source/AST-CUL-003.blend';chair_hash=sha(chair_path)
geometry=read(R/'source/geometry.json');places=read(R/'contracts/place_instances.json')['places'];fixtures=read(R/'contracts/fixture_markers.json')['fixtures'];specs={}
for rel in ['materials/material_manifest.json','materials/auditorium/manifest.json','materials/staff/manifest.json']:
 for role,s in read(CAT/rel)['materials'].items():assert role not in specs;specs[role]=s
failures=[]
def check(ok,message):
 if not ok:failures.append(message)
 return ok

def role_of(mat):
 assert mat is not None,'Missing material slot'
 role=str(mat.get('astraea_material_role',''))
 if role:return role
 name=re.sub(r'\.\d{3,}$','',mat.name);name=name.removeprefix('ASTRAEA_')
 assert name in specs or name=='gallery_glass',('Unknown material role',mat.name)
 return name

def scales(mat):
 role=role_of(mat)
 if role=='gallery_glass':return [1.,1.]
 expected=[float(x)for x in specs[role]['meters_per_tile_uv']]
 if 'meters_per_tile_uv'in mat:
  got=[float(x)for x in mat['meters_per_tile_uv']]
  check(len(got)==2 and max(abs(got[i]-expected[i])for i in range(2))<1e-7,'Source material scale mismatch: '+mat.name)
 return expected

def cycle(ids):
 ids=list(ids);rev=ids[::-1]
 return min(tuple(ids[i:]+ids[:i])for i in range(len(ids)))if not rev else min([tuple(ids[i:]+ids[:i])for i in range(len(ids))]+[tuple(rev[i:]+rev[:i])for i in range(len(ids))])

def image_nodes(tree,seen=None):
 seen=set()if seen is None else seen
 if tree.as_pointer()in seen:return []
 seen.add(tree.as_pointer());out=[]
 for node in tree.nodes:
  if node.type=='TEX_IMAGE'and node.image:out.append(node)
  elif node.type=='GROUP'and node.node_tree:out.extend(image_nodes(node.node_tree,seen))
 return out

def material_signature(mat):
 role=role_of(mat);images=[];bsdf=[]
 for node in image_nodes(mat.node_tree)if mat.use_nodes else[]:
  image=node.image;check(image.packed_file is not None,'Unpacked reopened texture: '+image.name)
  digest=hashlib.sha256(image.packed_file.data).hexdigest()if image.packed_file else None
  check(role in specs and digest==specs[role]['sha256'],'Packed reopened texture mismatch: '+mat.name+'/'+image.name)
  images.append({'sha256':digest,'size':list(image.size),'interpolation':node.interpolation,'extension':node.extension})
 if role!='gallery_glass':check(bool(images),'Missing reopened texture: '+mat.name)
 else:check(not images,'Unexpected textured gallery_glass')
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':
    inputs={}
    for key in ['Base Color','Metallic','Roughness','IOR','Alpha','Emission Color','Emission Strength']:
     if key in node.inputs:
      v=node.inputs[key].default_value;inputs[key]=float(v)if isinstance(v,(float,int))else list(v)
    bsdf.append(inputs)
 return {'role':role,'diffuse_color':list(mat.diffuse_color),'use_nodes':mat.use_nodes,'surface_render_method':mat.surface_render_method,'images':images,'principled':bsdf}

def descendants(root):
 return [root]+[o for o in bpy.data.objects if o!=root and is_descendant(o,root)]
def is_descendant(o,root):
 parent=o.parent
 while parent:
  if parent==root:return True
  parent=parent.parent
 return False

def chair_records(objects):
 result={}
 for ob in objects:
  row={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_basis':[[float(v)for v in r]for r in ob.matrix_basis]}
  if ob.type=='MESH':
   me=ob.data;mods=[]
   for mod in ob.modifiers:
    item={'name':mod.name,'type':mod.type,'show_viewport':mod.show_viewport,'show_render':mod.show_render}
    for key in ['width','segments','limit_method','angle_limit','keep_sharp','weight']:
     if hasattr(mod,key):item[key]=getattr(mod,key)
    mods.append(item)
   row.update(vertices=[list(v.co)for v in me.vertices],faces=[list(f.vertices)for f in me.polygons],face_materials=[f.material_index for f in me.polygons],materials=[material_signature(m)for m in me.materials],uvs={layer.name:[list(uv.uv)for uv in layer.data]for layer in me.uv_layers},modifiers=mods)
  result[ob.name]=row
 return result

def fingerprint(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(a.source));bpy.context.view_layer.update()
root=bpy.data.objects.get('AST-CUL-005');assert root is not None
check(root.get('source_geometry_sha256')==sha(R/'source/geometry.json'),'Saved geometry provenance differs')
check(not bool(root.get('first_pass_complete',True)),'Saved source wrongly marked first-pass complete')
expected={};parts=[o for o in geometry['objects']if o['role']!='preview_only']
for o in parts:
 key=(o.get('surface_region')or o['name'].split('_')[0],o['material_family'],o['role']);g=expected.setdefault(key,{'vertices':[],'faces':[],'materials':[],'names':[],'ranges':[]});base=len(g['vertices']);fbase=len(g['faces'])
 g['vertices'].extend(o['vertices_world']);g['faces'].extend([[base+i for i in f]for f in o['faces']]);g['materials'].extend(o.get('face_material_families',[o['material_family']]*len(o['faces'])));g['names'].append(o['name']);g['ranges'].append({'name':o['name'],'vertex_start':base,'vertex_count':len(o['vertices_world']),'face_start':fbase,'face_count':len(o['faces'])})
actual=[o for o in descendants(root)if o.type=='MESH'];check(len(actual)==len(expected),'Authored mesh group count differs')
reports=[];max_coord=0.;max_uv=0.;seen=set();all_materials={};world=[];face_roles=collections.Counter();degenerate=[]
for ob in actual:
 key=(str(ob.get('ownership_region','')),str(ob.get('material_family','')),str(ob.get('collision_role','')))
 if not check(key in expected,'Unexpected authored group: '+ob.name):continue
 check(key not in seen,'Duplicate authored group: '+ob.name);seen.add(key);g=expected[key];me=ob.data
 check(json.loads(ob.get('pure_part_names','[]'))==g['names'],'Part names mismatch: '+ob.name)
 check(json.loads(ob.get('pure_part_ranges','[]'))==g['ranges'],'Part ranges mismatch: '+ob.name)
 if not check(len(me.vertices)==len(g['vertices'])and len(me.polygons)==len(g['faces']),'Vertex/face counts differ: '+ob.name):continue
 local_max=0.
 for v,expected_point in zip(me.vertices,g['vertices']):
  p=ob.matrix_world@v.co;actual_point=Vector((p.x,p.z,-p.y));local_max=max(local_max,(actual_point-Vector(expected_point)).length);world.append(list(actual_point))
 max_coord=max(max_coord,local_max);check(local_max<.00003,'Source coordinate drift: '+ob.name)
 uv=me.uv_layers.get('metric_material_uv');assert uv is not None
 local_uv=0.
 for face,f,role in zip(me.polygons,g['faces'],g['materials']):
  check(cycle(face.vertices)==cycle(f),'Source topology differs: '+ob.name+'/'+str(face.index))
  mat=me.materials[face.material_index];check(role_of(mat)==role,'Face material differs: '+ob.name+'/'+str(face.index));all_materials[mat.name]=mat;face_roles[role]+=1
  if face.area<=1e-12 or face.normal.length<.9:degenerate.append({'object':ob.name,'face':face.index,'area':float(face.area),'normal_length':float(face.normal.length)})
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis];sx,sy=scales(mat)
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;u=uv.data[li].uv
   check(all(math.isfinite(float(x))for x in u),'Nonfinite reopened UV: '+ob.name)
   local_uv=max(local_uv,abs(u[0]-v[axes[0]]/sx),abs(u[1]-v[axes[1]]/sy))
 max_uv=max(max_uv,local_uv);check(local_uv<.00006,'Per-face material UV scale error: '+ob.name)
 me.calc_loop_triangles();reports.append({'object':ob.name,'parts':len(g['names']),'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(me.loop_triangles),'maximum_coordinate_error_m':local_max,'maximum_material_scaled_uv_error':local_uv})
check(seen==set(expected),'Missing authored mesh groups')
check(not degenerate,'Degenerate reopened authored faces: '+str(len(degenerate)))
check(face_roles['warm_walnut']==9022,'Soffit material face count changed')

instances=[o for o in descendants(root)if o.instance_type=='COLLECTION'];check(len(instances)==2200,'Chair instance count differs');mapping={o.name:o for o in instances};collections_seen=set();instance_errors=[]
for place in places:
 ob=mapping.get(place['id'])
 if not check(ob is not None,'Missing chair instance: '+place['id']):continue
 p=ob.matrix_world.translation;x,y,z=place['position'];error=(Vector((p.x,p.z,-p.y))-Vector((x,y,z))).length
 yaw_error=abs(math.remainder(float(ob.rotation_euler.z)-place['orientation_yaw_radians'],2*math.pi));check(error<.00003 and yaw_error<.000002,'Chair placement transform differs: '+place['id'])
 check(list(ob.scale)==[1.,1.,1.],'Scaled retained chair: '+place['id'])
 check(ob.get('existing_family')=='AST-CUL-003'and not bool(ob.get('seat_controller_authored',True)),'Retained chair identity/behavior claim changed')
 if ob.instance_collection:collections_seen.add(ob.instance_collection.name)
 instance_errors.append({'id':place['id'],'position_error_m':error,'yaw_error_radians':yaw_error})
check(len(collections_seen)==1,'Chair instances do not share exactly one retained source collection')
col=bpy.data.collections.get(next(iter(collections_seen)));assert col is not None
candidate_chair=chair_records(list(col.objects));candidate_chair_fingerprint=fingerprint(candidate_chair)
chair_materials={m.name:m for o in col.objects if o.type=='MESH'for m in o.data.materials};all_materials.update(chair_materials)
texture_checks=[{'material':m.name,'is_retained_chair_material':m.name in chair_materials,'signature':material_signature(m)}for m in all_materials.values()]
marker_rows=[]
for f in fixtures:
 ob=bpy.data.objects.get('DATUM_'+f['id']);assert ob is not None;p=ob.matrix_world.translation;error=(Vector((p.x,p.z,-p.y))-Vector(f['position_world'])).length
 check(error<.00003,'Source mount marker position drift: '+f['id']);check(ob.get('source_support')==f['source_support'],'Mount provenance changed: '+f['id']);check(not bool(ob.get('runtime_light_installed',True)),'Mount incorrectly claims runtime light')
 marker_rows.append({'id':f['id'],'position_error_m':error,'source_support':str(ob.get('source_support'))})
source_lights=[o.name for o in bpy.context.scene.objects if o.type=='LIGHT'];check(not source_lights,'Unexpected source lights')
# Reopen the genuine retained chair source separately. Do not append from the
# candidate or compare against its own metadata. Neither Blend is saved.
bpy.ops.wm.open_mainfile(filepath=str(chair_path));bpy.context.view_layer.update()
original_root=bpy.data.objects.get('AST-CUL-003');assert original_root is not None
original_chair=chair_records(descendants(original_root));original_chair_fingerprint=fingerprint(original_chair)
check(set(candidate_chair)==set(original_chair),'Original chair object-name roster differs')
chair_differences=[name for name in sorted(set(candidate_chair)|set(original_chair))if candidate_chair.get(name)!=original_chair.get(name)]
check(not chair_differences,'Retained chair actual geometry/UV/transform/material/modifier differences: '+str(chair_differences[:12]))
check(sha(a.source)==source_hash,'QA modified surviving theater Blend')
check(sha(chair_path)==chair_hash,'QA modified original chair Blend')
report={'status':'REOPENED_EDITABLE_SOURCE_PASS'if not failures else'REOPENED_EDITABLE_SOURCE_FAIL','surviving_source_sha256':source_hash,'failed_build_adapter_sha256':'b8efa85fa5140b21f642e90eaf4c180d6e766abd4b05661003515c337d17b45a','source_geometry_sha256':sha(R/'source/geometry.json'),'source_parts_checked':len(parts),'authored_mesh_groups':len(actual),'mesh_reports':reports,'authored_vertices':sum(r['vertices']for r in reports),'authored_triangles':sum(r['triangles']for r in reports),'maximum_coordinate_error_m':max_coord,'maximum_material_scaled_uv_error':max_uv,'face_material_counts':dict(face_roles),'degenerate_faces':degenerate,'chair_instances_checked':len(instances),'maximum_chair_position_error_m':max(x['position_error_m']for x in instance_errors),'maximum_chair_yaw_error_radians':max(x['yaw_error_radians']for x in instance_errors),'retained_chair_original_sha256':chair_hash,'candidate_chair_fingerprint':candidate_chair_fingerprint,'original_chair_fingerprint':original_chair_fingerprint,'chair_object_differences':chair_differences,'packed_material_texture_checks':texture_checks,'retained_chair_materials_checked':sorted(chair_materials),'source_mount_marker_checks':marker_rows,'original_files_unchanged':True,'source_saved_or_exported_by_qa':False,'engine_runtime_or_render_run':False,'source_lights':source_lights,'first_pass_complete':False,'failures':failures,'not_accepted':['Source/export equivalence','Source-only normal-height visual review','Complete world/collision census','Actual fixture lighting and furnished first pass','Fitted doors/cabin and runtime traversal','Pressure enclosure/load certification']}
text=json.dumps(report,indent=2,allow_nan=False)+'\n'
with a.report.open('x')as file:file.write(text)
print(json.dumps({k:report[k]for k in ['status','surviving_source_sha256','source_parts_checked','authored_mesh_groups','authored_vertices','authored_triangles','maximum_coordinate_error_m','maximum_material_scaled_uv_error','chair_instances_checked','chair_object_differences','original_files_unchanged','failures']}))
if failures:raise RuntimeError('Independent reopened-source QA failed; inspect report and preserve surviving files')
