"""Inspection helpers; Blender-only. No launch, export, render, or automatic writes."""
import hashlib,json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector

def world_to_source(p):return (p[0],-p[2],p[1])
def source_to_world(p):return (p[0],p[2],-p[1])
def root_matrix(c):
 cols=[world_to_source(p)for p in c['basis_world_columns']];t=world_to_source(c['origin_world_xyz'])
 return Matrix(tuple(tuple(cols[j][i]for j in range(3))+(t[i],)for i in range(3))+((0,0,0,1),))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def material_state(m):
 nodes=[];links=[]
 for n in m.node_tree.nodes:
  v={'name':n.name,'type':n.bl_idname}
  if n.type=='TEX_IMAGE':v.update(image_name=n.image.name if n.image else None,image_packed_sha256=hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest() if n.image and n.image.packed_file else None,extension=n.extension,interpolation=n.interpolation)
  values={}
  for s in n.inputs:
   if hasattr(s,'default_value'):
    q=s.default_value
    if isinstance(q,(str,bool,int,float)):values[s.identifier]=q
    elif hasattr(q,'__len__'):values[s.identifier]=list(q)
  v['default_inputs']=values;nodes.append(v)
 for l in m.node_tree.links:links.append([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier])
 return {'material_name':m.name,'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':nodes,'links':sorted(links),'astraea_material_role':m.get('astraea_material_role'),'meters_per_tile_uv':list(m.get('meters_per_tile_uv',[1,1]))}
def metric_uv(me,material,grain):
 uv=me.uv_layers.active or me.uv_layers.new(name='UV_Metric_Metres');uv.name='UV_Metric_Metres';uv.active_render=True;tile=material.get('meters_per_tile_uv',[1,1])
 for p in me.polygons:
  drop=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=drop]
  if grain in axes:axes.remove(grain);axes.append(grain)
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/tile[0],co[axes[1]]/tile[1])
def evaluated_geometry(ob):
 # Callers must link every object and update the view layer first.
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
 vs=[list(source_to_world(eo.matrix_world@v.co))for v in me.vertices];triangles=[[vs[i]for i in t.vertices]for t in me.loop_triangles]
 edges={}
 for p in me.polygons:
  ids=list(p.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
 result={'vertices_world':vs,'triangles_world':triangles,'triangle_count':len(triangles),'bounds_world':[list(map(min,zip(*vs))),list(map(max,zip(*vs)))],'closed_manifold':bool(edges)and set(edges.values())=={2},'matrix_positive':eo.matrix_world.determinant()>0,'uv_layers':[x.name for x in me.uv_layers]}
 eo.to_mesh_clear();return result
