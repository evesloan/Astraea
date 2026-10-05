"""Check retained old stub faces and UVs against original005 source, including the tiny fore stub."""
from pathlib import Path
import bpy,json,subprocess,tempfile,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];freeze=json.loads((R/'qa/preauthor_baseline.json').read_text());base=freeze['baseline_catalogue_commit'];p=Path(tempfile.gettempdir())/'upper_horizon_original_005.blend';p.write_bytes(subprocess.check_output(['git','-C',str(C),'show',base+':assets/aft_crown_platform/source/AST-CMD-005.blend']));bpy.ops.wm.open_mainfile(filepath=str(p))
old={}
for mapping in freeze['guard_migration']:
 ob=bpy.data.objects[mapping['old_name']];old[ob.name]={'verts':[v.co.copy()for v in ob.data.vertices],'faces':[list(f.vertices)for f in ob.data.polygons],'faceuv':[[ob.data.uv_layers.active.data[i].uv.copy()for i in f.loop_indices]for f in ob.data.polygons],'materials':[m.name for m in ob.data.materials]}
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/aft_crown_platform/source/AST-CMD-005.blend'));report=[]
for mapping in freeze['guard_migration']:
 src=old[mapping['old_name']]
 for spec in mapping['replacement']:
  ob=bpy.data.objects[spec['name']];assert [m.name for m in ob.data.materials]==src['materials'];errors=[];maxuv=0;closure=[]
  for f in ob.data.polygons:
   original_indices=src['faces'][f.index];p0,p1,p2=[src['verts'][i]for i in[original_indices[0],original_indices[1],original_indices[-1]]];u0,u1,u2=[src['faceuv'][f.index][i]for i in[0,1,-1]];e1=p1-p0;e2=p2-p0
   for j,li in enumerate(f.loop_indices):
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;expected=u0+(u1-u0)*(v-p0).dot(e1)/e1.length_squared+(u2-u0)*(v-p0).dot(e2)/e2.length_squared;actual=ob.data.uv_layers.active.data[li].uv;maxuv=max(maxuv,(actual-expected).length);assert(actual-expected).length<1e-6
   vs=[ob.data.vertices[i].co for i in f.vertices]
   if max(v.y for v in vs)-min(v.y for v in vs)<1e-8 and any(abs(-vs[0].y-z)<1e-7 for z in[160,164]):closure.append({'polygon':f.index,'plane_z':-vs[0].y,'normal_blender':list(f.normal),'material':ob.data.materials[f.material_index].name,'uv':[list(ob.data.uv_layers.active.data[i].uv)for i in f.loop_indices]})
  for q,v in zip(src['verts'],ob.data.vertices):
   if not spec['name'].endswith('__low_bay'):assert v.co.x==q.x and v.co.z==q.z
  zvals=sorted(set(-v.co.y for v in ob.data.vertices));expected_z=spec['z'];assert all(abs(a-b)<.00001 for a,b in zip(zvals,expected_z)),(zvals,expected_z)
  if spec['name'].endswith('__fore_stub'):assert zvals[1]-zvals[0]>.047 and zvals[1]-zvals[0]<.048
  assert len(closure)==(2 if spec['name'].endswith('__low_bay')else 1)
  report.append({'old':mapping['old_name'],'new':ob.name,'z_actual_float32':zvals,'z_contract':expected_z,'y_actual':[min(v.co.z for v in ob.data.vertices),max(v.co.z for v in ob.data.vertices)],'retained_x_and_y_exact':not spec['name'].endswith('__low_bay'),'source_face_interpolated_uv_max_error':maxuv,'added_cut_closure_faces':closure})
(R/'qa/005_exact_stub_audit.json').write_text(json.dumps({'pass':True,'baseline':base,'source_sha256':hashlib.sha256((C/'assets/aft_crown_platform/source/AST-CMD-005.blend').read_bytes()).hexdigest(),'parts':report,'note':'Retained exterior surfaces preserve exact old X/Y and affineUV mapping; float32Z follows originalsource encoding. Cut caps close the split solids and introduce no extra exterior seam volume.'},indent=2)+'\n');print('STUB_PRESERVATION_PASS',len(report))
