from pathlib import Path
import bpy,json,hashlib,os
P=Path(__file__).resolve().parent;ST=Path(os.environ.get('ASTRAEA_PORTABLE_CHECK_OUTPUT','/tmp/central-room-portability-check'));ST.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();port=json.loads((P/'RETENTION_PORTABILITY.json').read_text());checks=[]
for row in port['source_components']:
 root=P/'residential-neighborhood-courts-20261007'/row['folder'];rev=root/'outputs'/row['current_revision']
 for folder in sorted(p for p in rev.iterdir()if p.is_dir()):
  source=folder/'assembly.blend';before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();assert not bpy.data.libraries
  ref=json.loads((folder/'EVALUATED_GEOMETRY.json').read_text());obs={o['name']:o for o in ref};meshes=[o for o in bpy.context.scene.objects if o.type in ['MESH','CURVE']];assert set(o.name for o in meshes)==set(obs)
  error=0
  for ob in meshes:
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ob.matrix_world @ v.co for v in me.vertices];ev.to_mesh_clear();lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)];r=obs[ob.name]['bounds'];err=max(abs(a-b)for got,want in [(lo,r[0]),(hi,r[1])]for a,b in zip(got,want));error=max(error,err)
  assert error<.0001,(folder,error);assert sha(source)==before
  missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
  checks.append({'folder':str(folder.relative_to(P)),'source_sha256':before,'actual_mesh_parts':len(meshes),'max_saved_bounds_error_m':error,'external_libraries':0,'unresolved_images':missing})
assert len(checks)==16
report={'status':'PASS_NATIVE_BYTE_EXACT_16_SHARED_SOURCE_REOPEN','recipes':16,'mapped_new_units':165,'mapped_rest_slots':431,'checks':checks,'source_files_saved_or_changed':False,'Game_or_Catalogue_writes':False,'scope':'Saved native source parts/evaluated bounds and dependency resolution only. Prior source route/privacy checks not rerun.'};(ST/'NATIVE_PORTABILITY_PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(checks),flush=True)
