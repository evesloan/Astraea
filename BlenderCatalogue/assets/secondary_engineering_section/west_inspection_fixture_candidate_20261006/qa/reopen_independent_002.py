"""Independent read-only Blender reopening. Never saves a blend or exports a GLB.
Run once, after the serial source build, with Blender --background --threads 2.
"""
from pathlib import Path
import bpy, json, hashlib, math, resource
import numpy as np
from mathutils import Matrix, Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa'
S=R/'source/AST-ENG-008_west_inspection_fixture.blend'
G=R/'exports/AST-ENG-008_west_inspection_fixture.glb'
ORIGINAL=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/source/AST-ENG-008.blend')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def xyz(v):return [float(v.x),float(v.z),float(-v.y)]
def cv(v):return Vector((v[0],-v[2],v[1]))
def basic(v):
 if isinstance(v,(str,bool,int,float)) or v is None:return v
 if hasattr(v,'to_list'):return [basic(x) for x in v.to_list()]
 if hasattr(v,'items'):return {k:basic(x) for k,x in v.items()}
 try:return [basic(x) for x in v]
 except TypeError:return str(v)
def image_record(im):
 return {'file_basename':Path(im.filepath).name,'size':list(im.size),'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode,'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None}
def mat_record(m):
 nodes=[]
 for n in m.node_tree.nodes:
  row={'name':n.name,'type':n.bl_idname,'inputs':[(s.name,basic(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]}
  if n.type=='TEX_IMAGE':row.update(image=image_record(n.image),extension=n.extension,interpolation=n.interpolation,projection=n.projection)
  nodes.append(row)
 return {'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'custom':{k:basic(v) for k,v in m.items()},'nodes':nodes,'links':sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)}
def mesh_record(me):
 return {'vertices':[list(v.co) for v in me.vertices],'edges':[list(e.vertices) for e in me.edges],'polygons':[{'vertices':list(p.vertices),'material':p.material_index,'smooth':p.use_smooth} for p in me.polygons],'uv_layers':{uv.name:[list(v.uv) for v in uv.data] for uv in me.uv_layers},'materials':[mat_record(m) for m in me.materials]}
for p in [Q/'INDEPENDENT_REOPEN.json',Q/'reopened_source.npz',Q/'SOURCE_MATERIALS.json']:
 assert not p.exists(),f'Preserve prior evidence: {p}'
pins=json.loads((R/'INPUT_PINS.json').read_text());input_before={p:sha(p) for p in pins}
assert input_before==pins
candidate_before={str(p):sha(p) for p in (S,G)}
bpy.ops.wm.open_mainfile(filepath=str(S));bpy.context.view_layer.update()
scene=list(bpy.context.scene.objects);expected={'WEST_mount','WEST_housing','WEST_opal','WEST_CapStem','DATUM_plant_west_front'}
assert {o.name for o in scene}==expected
assert len([o for o in scene if o.type=='MESH'])==4
assert not bpy.data.lights and not any(o.type=='LIGHT' for o in scene)
assert all(not o.hide_render and not o.modifiers for o in scene)
marker=bpy.data.objects['DATUM_plant_west_front'];assert marker.type=='EMPTY' and marker.parent is None
marker_xyz=xyz(marker.matrix_world.translation);assert np.max(np.abs(np.array(marker_xyz)-[25.55,9.5,-432]))<2e-5
assert abs(marker['emitter_offset_y_m']+.08)<1e-8 and not marker['energy_approved']
parts={o.name:o for o in scene if o.type=='MESH'};captured={n:mesh_record(o.data) for n,o in parts.items()}
all_tri=[];all_uv=[];all_mat=[];all_obj=[];groups=[];source_materials={}
for n,o in parts.items():
 me=o.data;me.calc_loop_triangles();assert len(me.uv_layers)==1 and me.uv_layers.active is not None
 assert o.parent is None and len(me.materials)==1
 v=np.array([xyz(o.matrix_world@p.co) for p in me.vertices]);groups.append({'name':n,'bounds_xyz':v.min(0).tolist()+v.max(0).tolist(),'triangles':len(me.loop_triangles),'material_names':[m.name for m in me.materials]})
 for t in me.loop_triangles:
  tri=v[list(t.vertices)];uv=np.array([list(me.uv_layers.active.data[i].uv) for i in t.loops]);uv[:,1]=1-uv[:,1]
  assert np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-9
  assert abs(float(np.linalg.det(np.array([uv[1]-uv[0],uv[2]-uv[0]]))))>1e-9
  all_tri.append(tri);all_uv.append(uv);all_mat.append(me.materials[t.material_index].name);all_obj.append(n)
 for m in me.materials:
  if m.name in source_materials:continue
  graph=mat_record(m);bs=next(a for a in m.node_tree.nodes if a.type=='BSDF_PRINCIPLED');base_links=list(bs.inputs['Base Color'].links)
  assert len(base_links)==1 and base_links[0].from_node.type=='TEX_IMAGE'
  im=base_links[0].from_node.image;assert im.packed_file
  image_path=Q/('image_'+image_record(im)['packed_sha256']+'.png')
  if not image_path.exists():image_path.write_bytes(bytes(im.packed_file.data))
  else:assert sha(image_path)==image_record(im)['packed_sha256']
  source_materials[m.name]={'graph_hash':digest(graph),'graph':graph,'base_color_texture':str(image_path),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'alpha':float(bs.inputs['Alpha'].default_value),'tile_m':list(m['meters_per_tile_uv'])}
# Metre-scaled UVs on every authored stem edge, not merely a layer name.
stem=parts['WEST_CapStem'];tile=np.array(stem.data.materials[0]['meters_per_tile_uv']);stem_uv_error=[]
for face in stem.data.polygons:
 ls=list(face.loop_indices)
 for i,j in zip(ls,ls[1:]+ls[:1]):
  a=stem.data.vertices[stem.data.loops[i].vertex_index].co;b=stem.data.vertices[stem.data.loops[j].vertex_index].co
  duv=np.array(stem.data.uv_layers.active.data[j].uv)-np.array(stem.data.uv_layers.active.data[i].uv)
  stem_uv_error.append(abs(float(np.linalg.norm(duv*tile))-(b-a).length))
# World-mapped float32 UVs at Z=-432 retain only ~0.05 mm precision.
assert max(stem_uv_error)<1e-4
# Re-read original donor objects after candidate capture; no candidate data edits.
donor_names=['plant_inspection_n_'+x for x in ['mount','housing','opal','ceiling_stem']]
with bpy.data.libraries.load(str(ORIGINAL),link=False) as (available,loaded):
 assert all(n in available.objects for n in donor_names);loaded.objects=donor_names.copy()
rotation=Matrix.Translation(cv((25.55,9.5,-432)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-cv((31,10.225,-437)))
donor_checks=[]
for original_name,donor in zip(donor_names[:3],loaded.objects[:3]):
 new_name='WEST_'+original_name.removeprefix('plant_inspection_n_');got=captured[new_name];want=mesh_record(donor.data)
 assert got==want,f'Local donor geometry/UV/material changed: {new_name}'
 error=max(abs(a-b) for row1,row2 in zip(parts[new_name].matrix_world,rotation@donor.matrix_world) for a,b in zip(row1,row2));assert error<2e-5
 donor_checks.append({'original':original_name,'candidate':new_name,'local_mesh_uv_material_exact':True,'content_sha256':digest(got),'maximum_world_matrix_error':error})
assert mat_record(stem.data.materials[0])==mat_record(loaded.objects[3].data.materials[0])
np.savez_compressed(Q/'reopened_source.npz',triangles=np.array(all_tri),uv=np.array(all_uv),materials=np.array(all_mat),objects=np.array(all_obj),source_sha256=np.array(candidate_before[str(S)]))
(Q/'SOURCE_MATERIALS.json').write_text(json.dumps(source_materials,indent=2)+'\n')
assert {p:sha(p) for p in pins}==pins
assert {str(p):sha(p) for p in (S,G)}==candidate_before
report={'status':'PASS','scope':'Independent saved-source reopening; no render, Game import or adoption','source_sha256':sha(S),'export_sha256':sha(G),'object_names':sorted(expected),'meshes':4,'markers':1,'lights':0,'triangle_count':len(all_tri),'groups':groups,'marker_xyz':marker_xyz,'emitter_xyz':(np.array(marker_xyz)+[0,-.08,0]).tolist(),'donor_preservation':donor_checks,'stem_material_donor_exact':True,'stem_max_uv_metric_edge_error_m':max(stem_uv_error),'retained_inputs_unchanged':True,'candidate_files_unchanged':True,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limits':['Source/export equivalence and contacts/rays in separate independent Python report','Energy, native 8/32 selection and complete visual quality remain unapproved']}
(Q/'INDEPENDENT_REOPEN.json').write_text(json.dumps(report,indent=2)+'\n');print('WEST_FIXTURE_INDEPENDENT_REOPEN_PASS',len(all_tri),flush=True)
