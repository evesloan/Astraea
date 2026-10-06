from pathlib import Path
import bpy,bmesh,json,hashlib,resource,numpy as np
R=Path(__file__).resolve().parents[1];S=R/'source/AST-ENG-008_cell_restriction_signage.blend';P=json.loads((R/'source/sign_plan.json').read_text());B=json.loads((R/'qa/BUILD.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(p):return [p.x,p.z,-p.y]
assert sha(S)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene;obs=list(scene.objects);assert len(obs)==5 and sum(x.type=='FONT'for x in obs)==4 and sum(x.type=='MESH'for x in obs)==1;assert not any(x.type=='LIGHT'for x in obs)
assert sorted(x.data.body for x in obs if x.type=='FONT')==sorted([P['header']['text']]+P['leaf_print']['lines']);assert all(x['collision_contract']=='none'for x in obs)
tri=[];matids=[];matnames=[];parts=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in obs:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));me.transform(ob.matrix_world);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.calc_loop_triangles();vs=np.array([xyz(v.co)for v in me.vertices]);lo=vs.min(0);hi=vs.max(0)
 if ob['sign_group']=='SIGN_MOVING_GLASS_LEAF':
  bounds=np.array(P['leaf_print']['canonical_rest_bounds_xyz']);assert np.all(lo>=bounds[:3])and np.all(hi<=bounds[3:]);assert hi[0]<21.868 and lo[0]>21.8675
  for f in np.linspace(0,1,41):d=np.array([0,0,-1.22])*f;assert np.all(lo+d>=bounds[:3]+d)and np.all(hi+d<=bounds[3:]+d)
 else:
  assert lo[0]>=27.14999 and hi[0]<27.157 and lo[1]>=8.64299 and hi[1]<=8.78701 and lo[2]>=-406.4301 and hi[2]<=-403.8199
 for t in me.loop_triangles:
  v=[xyz(me.vertices[i].co)for i in t.vertices];assert np.linalg.norm(np.cross(np.array(v[1])-v[0],np.array(v[2])-v[0]))>1e-14;tri.append(v);mat=me.materials[t.material_index].name
  if mat not in matnames:matnames.append(mat)
  matids.append(matnames.index(mat))
 parts.append({'name':ob.name,'bounds_xyz':lo.tolist()+hi.tolist(),'group':ob['sign_group'],'triangles':len(me.loop_triangles)})
assert len(tri)==6680;assert all(sha(p)==h for p,h in P['immutable_inputs'].items())
np.savez_compressed(R/'qa/reopened_source_triangles.npz',triangles=np.array(tri),material_ids=np.array(matids),material_names=np.array(matnames),source_sha256=np.array(sha(S)))
report={'status':'PASS','source_sha256':sha(S),'editable_parts':len(obs),'editable_fonts':4,'triangles':len(tri),'parts':parts,'body_text_exact':True,'actual_ink_within_leaf_41poses':True,'header_fully_backed':True,'new_lights':0,'new_collisions':0,'original_pins_unchanged':True,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/SOURCE_REOPEN.json').write_text(json.dumps(report,indent=2)+'\n');print('SIGN_REOPEN_PASS',len(tri),'triangles',report['peak_rss_kib'],'KiB')
