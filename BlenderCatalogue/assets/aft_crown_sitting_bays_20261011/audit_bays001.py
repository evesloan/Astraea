from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();expected={};checks=0

def mat(m):
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None);images=[]
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:
   assert n.image.packed_file;images.append((hashlib.sha256(n.image.packed_file.data).hexdigest(),n.interpolation,n.image.colorspace_settings.name))
 return {'roughness':bs.inputs['Roughness'].default_value if bs else None,'images':images,'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links]}
def mesh(o):return {'verts':[list(v.co)for v in o.data.vertices],'faces':[list(q.vertices)for q in o.data.polygons],'uvs':[[list(u.uv)for u in q.data]for q in o.data.uv_layers],'materials':[mat(m)for m in o.data.materials]}
for f in sorted({q['material_native']for q in P['parts']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/f))
 for q in P['parts']:expected[q['name']]=[mat(m)for m in bpy.data.objects[q['material_source']].data.materials]
furniture={}
for f in sorted({q['source_native']for q in P['furniture_meshes']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/f))
 for q in P['furniture_meshes']:
  if q['source_native']==f:furniture[q['name']]=mesh(bpy.data.objects[q['source_name']])
bpy.ops.wm.open_mainfile(filepath=str(W/P['structure']['native']))
for q in P['parts']:assert [mat(m)for m in bpy.data.objects[q['name']].data.materials]==expected[q['name']];checks+=1
for q in P['furniture_meshes']:
 o=bpy.data.objects[q['name']];assert mesh(o)==furniture[q['name']],q['name'];s=q['placement'];T=Matrix.Translation(Vector((s['at'][0],-s['at'][2],s['at'][1])))@Matrix.Rotation(s['yaw'],4,'Z')@Matrix(q['source_world_matrix']);assert max(abs(o.matrix_world[i][j]-T[i][j])for i in range(4)for j in range(4))<.0001;checks+=2
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','checks':checks,'exact_rigid_furniture_meshes':len(P['furniture_meshes']),'source_vertices_faces_UVs_packed_textures_roughness_links_exact':True,'all_source_pins_and_prior_native_exports_unchanged':True,'selected_native':P['structure']['native'],'fresh_saved_native_repeat_identical':P['structure']['fresh_native_repeat_identical']},indent=2)+'\n');print('PASS source audit',checks)
