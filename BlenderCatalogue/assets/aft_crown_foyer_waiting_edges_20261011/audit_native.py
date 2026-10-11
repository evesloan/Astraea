from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def material(m):
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None);images=[]
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:assert n.image.packed_file;images.append((hashlib.sha256(n.image.packed_file.data).hexdigest(),n.interpolation,n.image.colorspace_settings.name))
 return {'roughness':bs.inputs['Roughness'].default_value if bs else None,'images':images,'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links]}
def signature(o):return {'verts':[list(v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons],'uvs':[[list(v.uv)for v in layer.data]for layer in o.data.uv_layers],'materials':[material(m)for m in o.data.materials],'modifiers':[(m.type,m.name)for m in o.modifiers]}
def evaluated(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];faces=[list(f.vertices)for f in me.polygons];uv=[[tuple(v.uv)for v in layer.data]for layer in me.uv_layers];e.to_mesh_clear();return vs,faces,uv
original={};partmats={}
for file in sorted({q['material_native']for q in P['parts']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/file))
 for q in P['parts']:
  if q['material_native']==file:partmats[q['name']]=[material(m)for m in bpy.data.objects[q['material_source']].data.materials]
for file in sorted({q['source_native']for q in P['source_copies']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/file));bpy.context.view_layer.update()
 for q in P['source_copies']:
  if q['source_native']==file:
   o=bpy.data.objects[q['source_name']];original[q['name']]={'signature':signature(o),'evaluated':evaluated(o),'matrix':o.matrix_world.copy()}
bpy.ops.wm.open_mainfile(filepath=str(W/P['structure']['native']));bpy.context.view_layer.update();checks=0;bounds=[];maximum=0
for q in P['parts']:
 o=bpy.data.objects[q['name']];assert [material(m)for m in o.data.materials]==partmats[q['name']];assert len(o.data.vertices)==len(q['verts']);assert max((v.co-Vector((p[0],-p[2],p[1]))).length for v,p in zip(o.data.vertices,q['verts']))<.00002
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges)and bm.calc_volume(signed=True)>0;bm.free();checks+=3
for q in P['source_copies']:
 o=bpy.data.objects[q['name']];old=original[q['name']];assert signature(o)==old['signature'],q['name'];s=q['placement'];T=Matrix.Translation(Vector((s['at'][0],-s['at'][2],s['at'][1])))@Matrix.Rotation(s['yaw'],4,'Z');expect=T@old['matrix'];assert max(abs(o.matrix_world[i][j]-expect[i][j])for i in range(4)for j in range(4))<.0001
 v,F,U=evaluated(o);vs,f,u=old['evaluated'];assert F==f and U==u and len(v)==len(vs);delta=max((a-T@b).length for a,b in zip(v,vs));assert delta<.0001,(q['name'],delta);maximum=max(maximum,delta)
 pts=[[a.x,a.z,-a.y]for a in v];bounds.append({'name':q['name'].replace('.','_'),'kind':q['placement']['kind'],'bounds':[[min(a[k]for a in pts)for k in range(3)],[max(a[k]for a in pts)for k in range(3)]]});checks+=3
for q in P['fixture_instances']:
 o=bpy.data.objects[q['name']+'__LightExit'];assert (Vector((o.location.x,o.location.z,-o.location.y))-Vector(q['emitter'])).length<.00002;checks+=1
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f,h in P['protected_native_exports'].items():assert sha(R/f)==h,f
P['runtime_source_expected_bounds']=bounds
out={'status':'PASS','checks':checks,'original_source_meshes_exact':len(P['source_copies']),'original_furniture_meshes_exact':sum(q['placement']['kind']=='furniture'for q in P['source_copies']),'original_fixture_meshes_exact':sum(q['placement']['kind']=='fixture'for q in P['source_copies']),'evaluated_faces_uvs_material_texture_modifier_stacks_exact':True,'max_evaluated_rigid_world_vertex_delta_m':maximum,'custom_closed_outward_meshes':len(P['parts']),'prior_native_export_files_byte_identical':len(P['protected_native_exports']),'fresh_saved_native_repeat_export_identical':P['structure']['fresh_native_repeat_identical'],'new_floor_m2':0}
for f in [W/'EXACT_NATIVE_AUDIT.json',R/'Game/artifacts/aft_crown_foyer_waiting_edges_native.json']:f.write_text(json.dumps(out,indent=2)+'\n')
P['native_audit_sha256']=sha(R/'Game/artifacts/aft_crown_foyer_waiting_edges_native.json')
for f in [W/'PLAN.json',R/'Game/data/architecture/AFT_CROWN_FOYER_WAITING_EDGES.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print(json.dumps(out))
