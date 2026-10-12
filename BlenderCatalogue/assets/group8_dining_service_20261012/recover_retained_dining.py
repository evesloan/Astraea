from pathlib import Path,PurePosixPath
import json,hashlib,zipfile,stat,subprocess
W=Path(__file__).resolve().parent;R=W.parents[2];RR=Path('/workspace/group8-independent-readback-002');base='affc5c807087ff87da29f3642c2d6e418241b896';OUT=Path('/workspace/group8-dining-retained-native-001');assert not OUT.exists();OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();results=[]
for number in ['01','02','03']:
 key='D10_directory_'+number;rel='external_packages/remaining_sections_20261009/C/deliveries/'+key+'_BatchC_receiving_20261009.zip';raw=(R/rel).read_bytes();remote=subprocess.check_output(['git','-C',str(RR),'show',base+':'+rel]);assert remote==raw
 out=OUT/key;out.mkdir();rows={}
 with zipfile.ZipFile(R/rel)as z:
  assert z.testzip()is None
  for info in z.infolist():
   p=PurePosixPath(info.filename);assert not p.is_absolute()and'..'not in p.parts and'\\'not in info.filename and not stat.S_ISLNK(info.external_attr>>16);data=z.read(info);target=out/p
   if info.is_dir():target.mkdir(parents=True,exist_ok=True);continue
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb')as f:f.write(data)
   rows[info.filename]={'bytes':len(data),'sha256':sha(data)}
 root=out/'BatchC_rebuild_root';family=root/key;m=json.load(open(family/'MANIFEST.json'));native=family/'source/section.blend';runtime=family/'exports/section.glb';assert sha(native.read_bytes())==m['native_sha256'];assert sha(runtime.read_bytes())==m['GLB_sha256'];assert runtime.read_bytes()==(R/'Game/assets/models'/('SOL_'+key+'_remaining_batch.glb')).read_bytes()
 for item in m['pinned_rebuild_closure']:
  file=root/item['path'];assert file.stat().st_size==item['bytes']and sha(file.read_bytes())==item['sha256'],item['path']
 results.append({'programme_key':key,'archive':rel,'archive_sha256':sha(raw),'archive_bytes':len(raw),'archive_entries':len(rows),'all_crc_path_symlink_and_pinned_closure_checks':'PASS','remote_baseline_bytes_exact':True,'native':str(native),'native_sha256':m['native_sha256'],'runtime':str(runtime),'runtime_sha256':m['GLB_sha256'],'retained_documents':str(family/'docs'),'all_members':rows})
(W/'EXACT_RETAINED_DINING_RECOVERY.json').write_text(json.dumps({'status':'PASS','baseline_commit':base,'new_empty_recovery_root':str(OUT),'families':results,'original_mutations':0,'historical_fabrication':False},indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items()if k!='all_members'}for r in results]))
