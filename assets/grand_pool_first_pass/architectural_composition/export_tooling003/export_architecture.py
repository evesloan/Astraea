"""New-only precise-normal batched exports, after independently retained source QA."""
import bpy,json,hashlib,sys,math
from pathlib import Path
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S));from precise_normal_export import precise_normals
A=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/architectural_composition');R=A/'revisions/blockin003';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();approval=json.loads((S/'SOURCE_RETENTION.json').read_text());assert approval['status']=='PASS_INDEPENDENT_SOURCE_RETENTION'and approval['remote_metadata_verified'];build=json.loads((R/'qa/BUILD_RECEIPT.json').read_text());gate=json.loads((A/'qa/SOURCE_JOB_003.json').read_text());assert gate['status']=='BLOCKIN003_REOPEN_RETAINED_CONTACT_AND_ROOTED_SUPPORT_PASS';assert json.loads((S/'NEW_SEAT_ACCESS_003b.json').read_text())['status']=='PASS_NEW_SEAT_ACCESS_AND_PURPOSEFUL_POOL_VIEWS';assert not (R/'exports').exists();out=R/'exports';out.mkdir();reports=[]
with precise_normals()as precision:
 for source in build['sources']:
  path=Path(source['source']);assert sha(path)==source['source_sha256']==approval['sources'][str(path)]['current_sha256']==approval['sources'][str(path)]['retained_blob_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);contract=json.loads((S/(source['group']+'_contract.json')).read_text());records={p['name']:p for p in contract['parts']};assert set(records)=={o.name for o in bpy.context.scene.objects};groups={};batches=[]
  for ob in bpy.context.scene.objects:
   assert ob.type=='MESH'and ob.location.length<1e-10 and abs(ob.rotation_euler.to_quaternion().angle)<1e-8 and all(abs(x-1)<1e-10 for x in ob.scale);row=records[ob.name];center=[(a+b)*.5 for a,b in zip(row['bounds_min_xyz'],row['bounds_max_xyz'])];key=(math.floor(center[0]/16),math.floor(center[1]/8),math.floor(center[2]/16),row['material_role'],row['collision_contract'],row['cast_shadow']);groups.setdefault(key,[]).append(ob)
  for index,(key,objects)in enumerate(sorted(groups.items())):
   names=[o.name for o in objects];bpy.ops.object.select_all(action='DESELECT')
   for ob in objects:ob.select_set(True)
   bpy.context.view_layer.objects.active=objects[0]
   if len(objects)>1:bpy.ops.object.join()
   ob=bpy.context.object;ob.name='GPA_'+source['group']+'_BATCH_%03d_%s'%(index,key[3]);ob['source_part_names']=json.dumps(names);ob['collision_contract']=key[4];ob['cast_shadow']=key[5];batches.append({'name':ob.name,'source_parts':names,'material_role':key[3],'collision_contract':key[4],'cast_shadow':key[5]})
  glb=out/(path.stem+'.glb');assert not glb.exists();bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(path)==source['source_sha256'];receipt=dict(source_sha256=sha(path),export_sha256=sha(glb),batches=batches);rp=R/'qa'/(source['group']+'_EXPORT_BATCHES.json');assert not rp.exists();rp.write_text(json.dumps(receipt,indent=2)+'\n');reports.append(dict(group=source['group'],source_sha256=sha(path),export=str(glb),export_sha256=sha(glb),source_meshes=source['meshes'],runtime_batches=len(batches)))
p=R/'qa/EXPORT_001.json';assert not p.exists();p.write_text(json.dumps(dict(status='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE',components=reports,normal_precision=precision,approval_sha256=sha(S/'SOURCE_RETENTION.json'),source_saved=False,runtime_changed=False),indent=2)+'\n');print(json.dumps(reports))
