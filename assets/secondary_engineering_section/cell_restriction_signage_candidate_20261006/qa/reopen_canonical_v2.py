from pathlib import Path
import bpy,json,hashlib,resource,numpy as np
R=Path(__file__).resolve().parents[1];S=R/'source/AST-ENG-008_cell_restriction_signage_v2.blend';B=json.loads((R/'qa/EXPORT_CORRECTION_004.json').read_text());P=json.loads((R/'source/sign_plan.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(p):return[p.x,p.z,-p.y]
assert sha(S)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(S));visible=[o for o in bpy.context.scene.objects if not o.hide_render];hidden=[o for o in bpy.context.scene.objects if o.hide_render];assert len(visible)==2 and {o.name for o in visible}=={'SIGN_FIXED_EAST_HEADER','SIGN_MOVING_GLASS_LEAF'};assert len(hidden)==5 and sum(o.type=='FONT'for o in hidden)==4
assert sorted(o.data.body for o in hidden if o.type=='FONT')==sorted([P['header']['text']]+P['leaf_print']['lines']);assert all(o.type=='MESH'and o['collision_contract']=='none'for o in visible)
tri=[];uvs=[];mids=[];mnames=[];groups=[]
for o in visible:
 me=o.data;me.calc_loop_triangles();vs=np.array([xyz(o.matrix_world@v.co)for v in me.vertices]);lo=vs.min(0);hi=vs.max(0)
 if o.name=='SIGN_MOVING_GLASS_LEAF':
  b=np.array(P['leaf_print']['canonical_rest_bounds_xyz']);assert np.all(lo>=b[:3])and np.all(hi<=b[3:])and 21.8675<lo[0]<hi[0]<21.868
 else:assert 27.14999<=lo[0]<hi[0]<27.157 and lo[1]>8.64299 and hi[1]<8.78701
 for t in me.loop_triangles:
  v=vs[t.vertices];assert np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))>1e-14;uv=np.array([list(me.uv_layers.active.data[i].uv)for i in t.loops]);ab=uv[1]-uv[0];ac=uv[2]-uv[0];assert abs(ab[0]*ac[1]-ab[1]*ac[0])>1e-12
  mat=me.materials[t.material_index].name
  if mat not in mnames:mnames.append(mat)
  tri.append(v);mids.append(mnames.index(mat));uv[:,1]=1-uv[:,1];uvs.append(uv.astype(np.float32))
 groups.append({'name':o.name,'bounds_xyz':lo.tolist()+hi.tolist(),'triangles':len(me.loop_triangles),'surfaces':[m.name for m in me.materials]})
assert len(tri)==6672 and all(sha(p)==h for p,h in P['immutable_inputs'].items());np.savez_compressed(R/'qa/reopened_canonical_v2.npz',triangles=np.array(tri),uv=np.array(uvs),material_ids=np.array(mids),material_names=np.array(mnames),source_sha256=np.array(sha(S)))
report={'status':'PASS','source_sha256':sha(S),'visible_meshes':2,'hidden_editable_fonts':4,'hidden_authoring_plate':1,'triangles':len(tri),'groups':groups,'all_triangle_area_and_uv_positive':True,'fixed_header_and_moving_ink_exact_bounds':True,'original_pins_unchanged':True,'correction':'Eight exactly zero-area font fill triangles omitted; face-local metre-scaled UVs repair degenerate default font UVs. Editable font originals and earlier failed exports remain preserved. Canonical visible source meshes now exactly carry those UVs.','peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/CANONICAL_V2_REOPEN.json').write_text(json.dumps(report,indent=2)+'\n');print('CANONICAL_SIGN_SOURCE_PASS',len(tri))
