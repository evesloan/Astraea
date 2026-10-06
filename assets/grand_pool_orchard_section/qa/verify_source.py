"""Exact source/GLB triangles, UVs, textures, markers and unchanged derivative objects."""
from pathlib import Path
from collections import Counter,deque
import bpy,bmesh,json,hashlib,struct,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def clean(v):
 if isinstance(v,(str,int,float,bool,type(None))):return v
 if hasattr(v,'to_dict'):return {k:clean(x)for k,x in v.to_dict().items()}
 try:return[clean(x)for x in v]
 except:return str(v)
def fp(o):
 row={'type':o.type,'matrix':[list(v)for v in o.matrix_world],'parent':o.parent.name if o.parent else None,'properties':{k:clean(o[k])for k in o.keys()}}
 if o.type=='MESH':row.update(vertices=[list(v.co)for v in o.data.vertices],faces=[list(p.vertices)for p in o.data.polygons],uv=[list(v.uv)for v in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
 return row
def material_fingerprints():
 out={}
 used={m.name for o in bpy.context.scene.objects if o.type=='MESH'for m in o.data.materials}
 for m in bpy.data.materials:
  if m.name not in used or not m.use_nodes:continue
  rows=[]
  for n in m.node_tree.nodes:
   row={'type':n.bl_idname,'inputs':{i.name:clean(i.default_value)for i in n.inputs if hasattr(i,'default_value')}}
   if n.type=='TEX_IMAGE':row.update(image_sha256=hashlib.sha256(n.image.packed_file.data).hexdigest(),interpolation=n.interpolation,extension=n.extension)
   rows.append(row)
  out[m.name]={'nodes':rows,'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links],'properties':{k:clean(m[k])for k in m.keys()}}
 return out
def snap(path):bpy.ops.wm.open_mainfile(filepath=str(path));return{o.name:fp(o)for o in bpy.context.scene.objects}
preserved=[]
for p,h in D['preserved_catalogue_inputs'].items():assert sha(C/p)==h,p;preserved.append(p)
derivatives=[]
for parent,stem,removed in[('primary_atrium_core/source/AST-CIR-005_forward_core.blend','AST-CIR-005_forward_pool_market',D['derivatives']['forward_core']['changed_original_objects']),('lower_staff_network/source/AST-STF-009.blend','AST-STF-009_pool_market',['STF_ShaftTopCap'])]:
 A=snap(C/'assets'/parent);AM=material_fingerprints();B=snap(R/'source'/(stem+'.blend'));BM=material_fingerprints();assert AM==BM,(stem,'material graphs changed');assert set(A)-set(B)==set(removed),(stem,set(A)-set(B));changed=[n for n in A if n in B and A[n]!=B[n]];assert not changed,(stem,changed)
 derivatives.append({'stem':stem,'removed_original_objects':removed,'unchanged_original_objects':len(set(A)&set(B)),'added_objects':len(set(B)-set(A)),'material_graphs_and_packed_images_exact':True,'preservation':'Exact matrices, vertices, face order, UVs, material names, parents and properties'})
def sig(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
 for t in o.data.loop_triangles:
  p=[]
  for vi,li in zip(t.vertices,t.loops):
   q=o.matrix_world@o.data.vertices[vi].co;u=uv[li].uv;p.append((float(q.x),float(q.z),float(-q.y),float(u.x),struct.unpack('<f',struct.pack('<f',1-u.y))[0]))
  assert abs((p[1][3]-p[0][3])*(p[2][4]-p[0][4])-(p[1][4]-p[0][4])*(p[2][3]-p[0][3]))>1e-10,(o.name,'zero-area UV triangle')
  yield(o.data.materials[t.material_index].name,min(tuple(p[k:]+p[:k])for k in range(3)))
roundtrips=[]
for stem in['AST-AQU-016','AST-CIR-005_forward_pool_market','AST-STF-009_pool_market']:
 src=R/'source'/(stem+'.blend');ex=R/'exports'/(stem+'.glb');bpy.ops.wm.open_mainfile(filepath=str(src));S=Counter();count=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.get('export_excluded',False)or o.name.startswith('PREVIEW_ONLY_'):continue
  count+=1;assert all(math.isfinite(x)for v in o.data.vertices for x in v.co),o.name;bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.free();S.update(sig(o))
 marks={o.name:[o.location.x,o.location.z,-o.location.y]for o in bpy.context.scene.objects if o.type=='EMPTY'and not(o.get('export_excluded',False)or o.name.startswith('PREVIEW_ONLY_'))}
 raw=ex.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);data=raw[28+n:];E=Counter();batches=0
 def acc(ai):
  a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];cnt={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];sz=struct.calcsize('<'+fmt*cnt);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz);return[struct.unpack_from('<'+fmt*cnt,data,off+i*stride)for i in range(a['count'])]
 for node in g['nodes']:
  assert not node.get('name','').startswith('PREVIEW_ONLY_'),'preview leaked'
  if 'mesh'not in node:continue
  assert not any(k in node for k in['matrix','translation','rotation','scale']),node['name'];batches+=1
  for prim in g['meshes'][node['mesh']]['primitives']:
   p=acc(prim['attributes']['POSITION']);u=acc(prim['attributes']['TEXCOORD_0']);ix=[v[0]for v in acc(prim['indices'])];mat=g['materials'][prim['material']]['name']
   for i in range(0,len(ix),3):
    pts=[tuple((*p[k],*u[k]))for k in ix[i:i+3]];E[(mat,min(tuple(pts[k:]+pts[:k])for k in range(3)))]+=1
 assert S==E,(stem,'source/export mismatch',sum((S-E).values()),sum((E-S).values()))
 em={n['name']:n.get('translation',[0,0,0])for n in g['nodes']if'mesh'not in n};assert set(em)==set(marks),(stem,set(em)^set(marks));assert all(max(abs(a-b)for a,b in zip(em[n],p))<1e-5 for n,p in marks.items())
 images={hashlib.sha256(n.image.packed_file.data).hexdigest()for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file}
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];h=hashlib.sha256(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest();assert h in images,(stem,im['name'])
 roundtrips.append({'asset':stem,'source_sha256':sha(src),'export_sha256':sha(ex),'editable_exported_meshes':count,'export_batches':batches,'oriented_triangles':sum(S.values()),'exact_triangle_UV_material_equality':True,'finite_closed_positive_volume':True,'all_exported_UV_triangles_nondegenerate':True,'marker_count':len(marks),'exact_markers':True,'embedded_texture_bytes_preserved':True})
report={'pass':True,'scope':'Source/export equality and bounded derivative preservation only; not runtime or source contact/capsule proof','retained_inputs':preserved,'derivatives':derivatives,'roundtrips':roundtrips,'horizontal_common_floor_meshes_exported':0,'floor_preview_mesh_count':8,'contract_sha256':sha(R/'source/connected_contract.json')}
(R/'qa/source_export_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
