"""Resolve same-role coplanar advisory cases by actual flat normals and affine UV equality."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
for ident in ['AST-RTL-003','AST-RTL-004']:
 rp=OUT/f'independent_support_finish_{ident}.json';screen=json.loads(rp.read_text());sp=ROOT/screen['source'];assert sha(sp)==screen['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(sp),load_ui=False);dg=bpy.context.evaluated_depsgraph_get();cases=[]
 for rec in screen['suspected_same_facing_overlaps']:
  if not rec['exposed_candidate']:continue
  p=np.array(rec['sample_point_source_m']);n=np.array(rec['outward_normal_source']);fields=[]
  for name in rec['parts']:
   ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();nm=ob.matrix_world.to_3x3().inverted().transposed();found=[]
   for tr in me.loop_triangles:
    v=np.array([ob.matrix_world@me.vertices[i].co for i in tr.vertices]);no=np.cross(v[1]-v[0],v[2]-v[0]);no/=np.linalg.norm(no)
    if no@n<.999999 or max(abs((v-p)@n))>2e-6:continue
    b=np.linalg.lstsq(np.column_stack([v[1]-v[0],v[2]-v[0]]),p-v[0],rcond=None)[0]
    if min(b)<-1e-5 or sum(b)>1.00001:continue
    uv=np.array([me.uv_layers.active.data[i].uv for i in tr.loops]);coef=np.linalg.lstsq(np.column_stack([v,np.ones(3)]),uv,rcond=None)[0];norms=np.array([(nm@me.corner_normals[i].vector).normalized()for i in tr.loops]);found.append((coef,me.materials[tr.material_index].name,float(np.max(np.linalg.norm(norms-n,axis=1)))))
   assert found,(ident,name,p.tolist());coef,mat,normalerr=found[0];fields.append({'part':name,'material':mat,'uv_at_point':np.append(p,1)@coef,'tangent_uv_gradient':(np.eye(3)-np.outer(n,n))@coef[:3],'normal_error':normalerr});ev.to_mesh_clear()
  error=float(max(abs(fields[0]['uv_at_point']-fields[1]['uv_at_point']).max(),abs(fields[0]['tangent_uv_gradient']-fields[1]['tangent_uv_gradient']).max()));same=fields[0]['material']==fields[1]['material'];flat=max(x['normal_error']for x in fields)<2e-5;passed=rec['same_material']and same and flat and error<2e-5;cases.append({'parts':rec['parts'],'material':fields[0]['material'],'same_material':same,'affine_uv_value_and_tangent_gradient_error':error,'flat_normals_agree':flat,'accepted_as_same_visible_finish':passed,'decision':'Same opaque role, flat outward normal and affine metric texture field give identical visible finish across buried-overlap edge; retained duplicate triangles are disclosed small construction overlap, not a new material z-fighting defect.'})
 row={'catalogue_id':ident,'source_sha256':sha(sp),'advisory_screen_sha256':sha(rp),'all_parts_connected':screen['all_part_contact_graph']['passed'],'different_material_exposed_cases':sum(not x['same_material']for x in screen['suspected_same_facing_overlaps']if x['exposed_candidate']),'same_role_resolutions':cases,'passed':screen['all_part_contact_graph']['passed']and all(x['accepted_as_same_visible_finish']for x in cases)};rows.append(row);print(ident,row['passed'],len(cases),flush=True)
(OUT/'independent_finish_resolution.json').write_text(json.dumps({'passed':all(x['passed']for x in rows),'assets':rows,'scope':'Resolves only listed same-role exposed coplanar advisory candidates; distinct-role findings must be fixed. Actual final imported pixels are a separate gate. No extra remeshing required for an identical material/normal/UV field.','executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
