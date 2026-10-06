"""Read-only actual evaluated-source arrays. Run only after the parent releases a source slot."""
import sys,json
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from job_common import *
import bpy,numpy as np
sys.path.insert(0,str(R/'dependencies'));from proven_source_snapshot import material,props,C
verify_pins();assert OUT.is_dir()and not SNAPSHOT.exists();bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
recipe=read(S/'ACTUAL_SOURCE_RECIPE.json');specs={o['name']:o for o in recipe['objects']};fixtures=recipe['fixtures'];markers={f['attachment_empty']:f for f in fixtures}
assert set(bpy.context.scene.objects.keys())==set(specs)|set(markers)
assert len(bpy.data.lights)==0 and len(specs)==24 and len(markers)==8
objects=[];materials={};roots=[]
for ob in sorted(bpy.context.scene.objects,key=lambda ob:ob.name):
 assert ob.type in ['MESH','EMPTY']and not ob.modifiers and not ob.constraints and ob.animation_data is None
 eo=ob.evaluated_get(dg);mw=np.asarray(eo.matrix_world,dtype=np.float64)
 row={'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'extras':props(ob),'world_matrix_godot':(C@mw@C.T).tolist(),'local_matrix_godot':(C@np.asarray(ob.matrix_basis,dtype=np.float64)@C.T).tolist()}
 if ob.type=='MESH':
  assert ob.name in specs and len(ob.data.materials)==1 and ob.parent is None
  me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);me.calc_loop_triangles();assert me.uv_layers and len(me.uv_layers)==1 and me.uv_layers.active
  mat=me.materials[0];materials[mat.name]=material(mat);row['material']=mat.name;row['flight']=specs[ob.name]['flight'];row['part']=specs[ob.name]['part'];row['uv_layer']=me.uv_layers.active.name
  local=np.asarray([list(v.co)for v in me.vertices],dtype=np.float64);local_native=(C[:3,:3]@local.T).T;world=(C[:3,:3]@((mw[:3,:3]@local.T).T+mw[:3,3]).T).T
  nm=C[:3,:3]@np.linalg.inv(mw[:3,:3]).T;normals=np.asarray([list(n.vector)for n in me.corner_normals],dtype=np.float64);normals=(nm@normals.T).T;normals/=np.linalg.norm(normals,axis=1)[:,None]
  uv=np.asarray([list(v.uv)for v in me.uv_layers.active.data],dtype=np.float64);uv[:,1]=1.0-uv[:,1]
  row.update(positions=[],local_positions=[],normals=[],uvs=[])
  for tri in me.loop_triangles:
   assert tri.material_index==0
   row['positions'].append(world[list(tri.vertices)].tolist());row['local_positions'].append(local_native[list(tri.vertices)].tolist());row['normals'].append(normals[list(tri.loops)].tolist());row['uvs'].append(uv[list(tri.loops)].tolist())
  row['triangles']=len(me.loop_triangles);row['source_vertices']=len(me.vertices);row['max_local_coordinate_m']=float(abs(local_native).max());assert row['max_local_coordinate_m']<3
  eo.to_mesh_clear()
 else:
  assert ob.name in markers and ob.parent and ob.parent.name.endswith('_LENS')
 objects.append(row)
byname={o['name']:o for o in objects}
for f in fixtures:
 source=[byname[n]for n in f['mesh_names']];matrix=np.asarray(source[0]['world_matrix_godot']);assert all(np.array_equal(matrix,np.asarray(s['world_matrix_godot']))for s in source)
 assert np.array_equal(matrix[:3,:3],np.eye(3)),'Expected exact translation-only local source meshes'
 roots.append({'name':'INWARD_'+f['flight']+'_ROOT','flight':f['flight'],'world_matrix_godot':matrix.tolist(),'mesh_children':f['mesh_names'],'source_attachment':f['attachment_empty'],'extras':{'source_flight':f['flight'],'source_sha256':SOURCE_SHA,'source_only_grouping_root':True,'runtime_light_installed':False}})
assert sum(o.get('triangles',0)for o in objects)==416 and sum(o.get('source_vertices',0)for o in objects)==256
verify_pins();write_new(SNAPSHOT,{'status':'ACTUAL_READ_ONLY_SOURCE_SNAPSHOT','source':str(SOURCE),'source_sha256':SOURCE_SHA,'source_bytes_unchanged':True,'source_saved':False,'blender':bpy.app.version_string,'numeric_method':'Float64 transforms of actual evaluated float32 local source vertices; no world-coordinate vertex baking','uv_method':'Actual source loop UV, glTF V=1-Blender V; only output float32 representation accepted','mesh_count':24,'source_attachment_count':8,'triangle_count':416,'objects':objects,'materials':materials,'export_roots':roots,'corner_limit':read(S/'TREAD_CORNER_CLASSIFICATION.json')['classification_counts']});print('SNAPSHOT',sha(SNAPSHOT))
