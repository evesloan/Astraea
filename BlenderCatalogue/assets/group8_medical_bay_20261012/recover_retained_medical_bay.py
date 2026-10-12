from pathlib import Path,PurePosixPath
import json,subprocess,zipfile,hashlib,stat
W=Path(__file__).resolve().parent;R=W.parents[2];RR=Path('/workspace/group8-independent-readback-002');base='affc5c807087ff87da29f3642c2d6e418241b896';rel='external_packages/remaining_sections_20261009/A/D05_directory_02_r001_source.zip';data=(R/rel).read_bytes();assert subprocess.check_output(['git','-C',str(RR),'show',base+':'+rel])==data;out=Path('/workspace/group8-medical-bay-retained-native-001');assert not out.exists();out.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();rows={}
with zipfile.ZipFile(R/rel)as z:
 assert z.testzip()is None
 for info in z.infolist():
  p=PurePosixPath(info.filename);assert not p.is_absolute()and'..'not in p.parts and'\\'not in info.filename and not stat.S_ISLNK(info.external_attr>>16);b=z.read(info);target=out/p
  if info.is_dir():target.mkdir(parents=True,exist_ok=True);continue
  target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(b)
  rows[info.filename]={'bytes':len(b),'sha256':sha(b)}
root=out/'D05_directory_02';native=root/'source/native.blend';runtime=root/'exports/D05_directory_02.glb';assert runtime.read_bytes()==(R/'Game/assets/models/SOL_D05_directory_02_remaining_batch.glb').read_bytes()
receipt={'status':'PASS_REMOTE_BASELINE_ARCHIVE_BYTES_CRC_PATH_MEMBERS_ACTIVE_RUNTIME_IDENTITY','baseline':base,'archive':rel,'archive_sha256':sha(data),'archive_bytes':len(data),'archive_members':rows,'native':str(native),'native_sha256':sha(native.read_bytes()),'runtime':str(runtime),'runtime_sha256':sha(runtime.read_bytes()),'root':str(root),'original_mutations':0,'historical_reconstruction':False};(W/'EXACT_RETAINED_MEDICAL_BAY_RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='archive_members'}))
