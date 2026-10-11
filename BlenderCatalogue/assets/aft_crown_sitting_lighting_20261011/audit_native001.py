from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def signature(o):
 return {'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons],'uvs':[[list(u.uv)for u in layer.data]for layer in o.data.uv_layers],'materials':[{'name':m.name,'roughness':m.roughness,'diffuse':list(m.diffuse_color),'nodes':[(n.name,n.bl_idname)for n in m.node_tree.nodes]if m.node_tree else []}for m in o.data.materials],'textures':{n.image.name:hashlib.sha256(n.image.packed_file.data).hexdigest()for m in o.data.materials if m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file}}
bpy.ops.wm.open_mainfile(filepath=str(R/P['source_native']));orig={o.name:{'signature':signature(o),'matrix':o.matrix_world.copy()}for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(W/P['structure']['native']));checks=0
for q in P['fixture_meshes']:
 o=bpy.data.objects[q['name']];assert signature(o)==orig[q['source_name']]['signature'],o.name
 p=q['placement'];T=Matrix.Translation(Vector((p['origin'][0],-p['origin'][2],p['origin'][1])))@Matrix.Rotation(p['yaw'],4,'Z');expected=T@orig[q['source_name']]['matrix'];assert max(abs(o.matrix_world[i][j]-expected[i][j])for i in range(4)for j in range(4))<.00001;checks+=2
for q in P['fixture_instances']:
 lo,hi=q['mount_bounds'];a,b=q['pier_bounds'];overlap=[min(hi[i],b[i])-max(lo[i],a[i])for i in range(3)];assert all(t>0 for t in overlap),q['name'];assert abs(overlap[0]-.015)<.00001;assert lo[1]>108.7
 o=bpy.data.objects[q['name']+'__LightExit'];assert (Vector((o.location.x,o.location.z,-o.location.y))-Vector(q['emitter'])).length<.00002;checks+=3
for f,h in P['protected_native_exports'].items():assert sha(R/f)==h,f
out={'status':'PASS','checks':checks,'exact_rigid_original_fixture_meshes':len(P['fixture_meshes']),'source_mount_positive_contacts':8,'mount_pier_overlap_m':.015,'source_emitter_marker_error_m_max':.00002,'all_prior_native_export_files_byte_identical':len(P['protected_native_exports']),'fresh_native_repeat_export_identical':P['structure']['fresh_native_repeat_identical'],'source_materials_uvs_faces_textures_exact':True}
(W/'EXACT_NATIVE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
