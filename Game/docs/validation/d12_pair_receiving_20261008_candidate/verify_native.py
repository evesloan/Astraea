"""Allocated Blender lane only: source, resource and save/reload proof; no renders."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
O=Path(__file__).resolve().parent;B=O/'native_attempts/build002';A='AST-RCV-D12-PAIR-001'
def sha(b):return hashlib.sha256(b).hexdigest()
def clean(v):
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 return [clean(x) for x in v]
def snap():
 out={'objects':{},'materials':{},'images':{}}
 for ob in sorted(bpy.data.objects,key=lambda x:x.name):
  rec={'type':ob.type,'matrix':[list(v)for v in ob.matrix_world],'parent':ob.parent.name if ob.parent else None,'props':{k:clean(v)for k,v in ob.items()}}
  if ob.type=='MESH':
   me=ob.data;me.calc_loop_triangles();rec.update(vertices=[list(v.co)for v in me.vertices],polygons=[list(p.vertices)for p in me.polygons],normals=[list(n.vector)for n in me.corner_normals],uv=[list(v.uv)for v in me.uv_layers.active.data],triangles=[list(t.vertices)for t in me.loop_triangles],triangle_loops=[list(t.loops)for t in me.loop_triangles],materials=[m.name for m in me.materials])
  out['objects'][ob.name]=rec
 used={m for ob in bpy.data.objects if ob.type=='MESH' for m in ob.data.materials}
 for m in used:
  nodes=[]
  for n in m.node_tree.nodes:
   node={'name':n.name,'type':n.type,'inputs':{s.name:clean(s.default_value)for s in n.inputs if hasattr(s,'default_value') and (isinstance(s.default_value,(float,int,bool)) or hasattr(s.default_value,'__len__'))}}
   if n.type=='TEX_IMAGE':node.update(image=n.image.name,interpolation=n.interpolation,extension=n.extension)
   nodes.append(node)
  out['materials'][m.name]={'props':{k:clean(v)for k,v in m.items()},'diffuse_color':list(m.diffuse_color),'nodes':nodes,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in m.node_tree.links]}
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':
    img=n.image;assert img.packed_file;out['images'][img.name]={'size':list(img.size),'channels':img.channels,'packed_sha256':sha(bytes(img.packed_file.data)),'colorspace':img.colorspace_settings.name}
 return out
bpy.ops.wm.open_mainfile(filepath=str(B/(A+'.blend')));before=snap();spec=json.loads((O/'GUARD_SOLIDS.json').read_text());meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==116
checks=[]
for row in spec['solids']:
 ob=bpy.data.objects[row['name']];me=ob.data;assert len(me.vertices)==len(row['vertices']);deltas=[]
 for v,w in zip(me.vertices,row['vertices']):
  p=ob.matrix_world@v.co;got=(p.x,p.z,-p.y);deltas.append(max(abs(a-b)for a,b in zip(got,w)))
 assert max(deltas)<1.6e-5,(row['name'],max(deltas))
 bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
 role=ob['astraea_material_role'];mat=me.materials[0];assert mat['astraea_material_role']==role;tile=tuple(mat['meters_per_tile_uv']);uvmax=0
 for poly in me.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=([1,2],[0,2],[0,1])[axis]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;expected=(v[axes[0]]/tile[0],v[axes[1]]/tile[1]);uvmax=max(uvmax,max(abs(a-b)for a,b in zip(expected,me.uv_layers.active.data[li].uv)))
 assert uvmax<4e-5,(row['name'],uvmax)
 assert all(abs(n.vector.length-1)<1e-6 for n in me.corner_normals)
 checks.append({'name':row['name'],'source_vertex_max_delta_m':max(deltas),'manifold':True,'signed_volume_m3':volume,'unit_normals':True,'uv_scale_max_error':uvmax,'support':ob['support'],'role':role})
(B/'NATIVE_SNAPSHOT.json').write_text(json.dumps(before,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(B/(A+'_roundtrip.blend')));bpy.ops.wm.open_mainfile(filepath=str(B/(A+'_roundtrip.blend')));after=snap();assert before==after
(B/'NATIVE_VERIFICATION.json').write_text(json.dumps({'status':'PASS','source_meshes':116,'checks':checks,'saved_reloaded_semantic_snapshot_exact':True,'used_resources':{'materials':before['materials'],'images':before['images']},'native_sha256':sha((B/(A+'.blend')).read_bytes()),'roundtrip_sha256':sha((B/(A+'_roundtrip.blend')).read_bytes()),'snapshot_sha256':sha((B/'NATIVE_SNAPSHOT.json').read_bytes()),'rendered':False},indent=2)+'\n')
print('PASS116 source meshes, manifold positive solids, unit normals, material-scaled UV, packed resources and exact semantic save/reload')
