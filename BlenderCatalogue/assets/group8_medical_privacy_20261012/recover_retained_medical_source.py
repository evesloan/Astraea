from pathlib import Path,PurePosixPath
import subprocess,json,hashlib,stat,zipfile
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent;RR=Path('/workspace/group8-independent-readback-002');base='affc5c807087ff87da29f3642c2d6e418241b896';rel='external_packages/remaining_sections_20261009/receivers/medical_triage_remaining_receiver_20261009';manifest=json.loads((R/(rel+'.manifest.json')).read_text());data=(R/(rel+'.zip')).read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert len(data)==manifest['archive_bytes']and sha(data)==manifest['archive_sha256'];remote=subprocess.check_output(['git','-C',str(RR),'show',base+':'+rel+'.zip']);assert remote==data
out=Path('/workspace/group8-medical-retained-native-001');assert not out.exists(),'Never overwrite surviving native work';out.mkdir();rows={}
with zipfile.ZipFile(R/(rel+'.zip'))as z:
 assert z.testzip()is None and len(z.infolist())==manifest['archive_files']
 expected={r['path']:r for r in manifest['entries']}
 for info in z.infolist():
  p=PurePosixPath(info.filename);assert not p.is_absolute()and '..'not in p.parts and '\\'not in info.filename and not stat.S_ISLNK(info.external_attr>>16);b=z.read(info);assert len(b)==expected[info.filename]['bytes']and sha(b)==expected[info.filename]['sha256'];target=out/p;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(b)
  rows[info.filename]={'bytes':len(b),'sha256':sha(b)}
root=out/manifest['receiver_root'];native=root/'source/D05_medical_remaining_architecture.blend';glb=root/'exports/D05_medical_remaining_architecture.glb';assert glb.read_bytes()==(R/'Game/assets/models'/glb.name).read_bytes()
receipt={'status':'PASS_EXACT_ARCHIVE_REMOTE_BYTES_CRC_ENTRIES_NATIVE_RUNTIME_IDENTITY','baseline':base,'archive':rel+'.zip','archive_sha256':sha(data),'archive_bytes':len(data),'entries':rows,'native':str(native),'native_sha256':sha(native.read_bytes()),'runtime':str(glb),'runtime_sha256':sha(glb.read_bytes()),'historical_failed_modifiers_variant_retained':True,'original_mutations':0,'historical_reconstruction':False}
(W/'EXACT_RETAINED_SOURCE_RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='entries'}))
