from pathlib import Path
import bpy,json,hashlib,struct
D=Path(__file__).resolve().parent
exec((D.parent/'thread_successor_receiving_20261015/verify_native_r005.py').read_text().split('old,oi=read')[0].split("r=json.loads((D/'NATIVE_SUCCESSOR_r005.json').read_text())",1)[-1])
old,oi=read(D/'native/PORT_FORE404_RECEIVER_r001.blend');new,ni=read(D/'native/PORT_FORE404_RECEIVER_r002.blend');print('OBJECT_ONLY_OLD',sorted(old.keys()-new.keys()),'ONLY_NEW',sorted(new.keys()-old.keys()));print('IMAGE_ONLY_OLD',sorted(oi.keys()-ni.keys()),'ONLY_NEW',sorted(ni.keys()-oi.keys()),'DIFFERENT',[k for k in oi.keys()&ni.keys()if oi[k]!=ni[k]]);assert old.keys()==new.keys();r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());batch=next(x['name']for x in r['batches']if'PFR_StaffEmbeddedTie2'in x['members']);same=0
for name,a in old.items():
 b=new[name];assert a['materials']==b['materials']
 if name=='PFR_StaffEmbeddedTie2':
  assert a['mesh']==b['mesh'];m=[x[:]for x in a['pose']];m[1][3]+=2.1;assert max(abs(m[i][j]-b['pose'][i][j])for i in range(4)for j in range(4))<.0001
 elif name==batch:assert a['pose']==b['pose']
 else:assert a==b,name;same+=1
report={'status':'PASS_ONE_NEW_ROOT_RIGID_RELOCATION_AND_ONE_FAITHFUL_REBAKED_BATCH_ONLY','unchanged_native_meshes_and_poses':same,'changed_new_root':'PFR_StaffEmbeddedTie2','source_mesh_geometry_and_UV_unchanged':True,'rigid_new_root_delta_Godot_xyz':[0,0,-2.1],'rebaked_batch':batch,'all_packed_image_payloads_identical':oi==ni,'old_only_packed_image_names':sorted(oi.keys()-ni.keys()),'new_only_packed_image_names':sorted(ni.keys()-oi.keys()),'differing_common_packed_image_names':[k for k in oi.keys()&ni.keys()if oi[k]!=ni[k]],'packed_images':len(oi),'r001_native_sha256':hashlib.sha256((D/'native/PORT_FORE404_RECEIVER_r001.blend').read_bytes()).hexdigest(),'r002_native_sha256':hashlib.sha256((D/'native/PORT_FORE404_RECEIVER_r002.blend').read_bytes()).hexdigest()};(D/'SINGLE_ROOT_NATIVE_DELTA_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],same)
