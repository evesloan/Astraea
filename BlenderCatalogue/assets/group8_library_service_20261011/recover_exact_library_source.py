"""Recover exact original archive into a new empty directory; no rebuild/overwrite."""
from pathlib import Path,PurePosixPath
import json,hashlib,subprocess,zipfile,stat
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent;RR=Path('/workspace/group8-independent-readback-002');base='affc5c807087ff87da29f3642c2d6e418241b896'
rel='external_packages/remaining_sections_20261009/recovered_originals/WP06_D12_directory_02_FULL_CANDIDATE';src=R/rel
sha=lambda b:hashlib.sha256(b).hexdigest()
def remote(path):return subprocess.check_output(['git','-C',str(RR),'show',base+':'+path])
mb=(src/'PARTS_MANIFEST.json').read_bytes();assert remote(rel+'/PARTS_MANIFEST.json')==mb;m=json.loads(mb)
target=Path('/workspace/group8-library-retained-native-001');assert not target.exists(),'Never overwrite a surviving source workspace';target.mkdir();original=target/m['original_filename'];pins={}
with original.open('xb')as out:
 for p in m['parts']:
  local=(src/p['filename']).read_bytes();assert len(local)==p['bytes']and sha(local)==p['sha256'];rb=remote(rel+'/'+p['filename']);assert rb==local
  pins[p['filename']]={'bytes':len(local),'sha256':sha(local),'independent_remote_bytes_verified':True};out.write(local)
assert original.stat().st_size==m['original_bytes']and sha(original.read_bytes())==m['original_sha256']
extract=target/'extracted';extract.mkdir();files={}
with zipfile.ZipFile(original)as z:
 assert len(z.infolist())==m['original_zip_entry_count']and z.testzip()is None
 for info in z.infolist():
  path=PurePosixPath(info.filename);assert not path.is_absolute()and'..'not in path.parts and'\\'not in info.filename and not stat.S_ISLNK(info.external_attr>>16)
  destination=extract/path
  if info.is_dir():destination.mkdir(parents=True,exist_ok=True);continue
  destination.parent.mkdir(parents=True,exist_ok=True);data=z.read(info)
  with destination.open('xb')as out:out.write(data)
  files[info.filename]={'bytes':len(data),'sha256':sha(data)}
expected_native='5cb4388f45401fd2a8c9d5f1788d356dd7eb8f477a122a531bc5a7b29c250128';expected_runtime='432baa23a4aa7b9dc422f6d6ec5485cf9826bd252d749ec63039785c252e6c5a'
natives=[p for p in extract.rglob('*.blend')if sha(p.read_bytes())==expected_native];runtimes=[p for p in extract.rglob('*.glb')if sha(p.read_bytes())==expected_runtime];assert len(natives)==len(runtimes)==1
assert (R/'Game/assets/models/WP06_long_library.glb').read_bytes()==runtimes[0].read_bytes()
receipt={'status':'PASS_EXACT_ORIGINAL_RECOVERY_AND_INDEPENDENT_REMOTE_PARTS','retained_baseline':base,'retained_source_parts':rel,'original_archive_sha256':m['original_sha256'],'archive_bytes':m['original_bytes'],'parts':pins,'zip_crc_and_paths_pass':True,'extracted_files':files,'exact_native':str(natives[0]),'exact_native_sha256':expected_native,'exact_runtime':str(runtimes[0]),'exact_runtime_sha256':expected_runtime,'installed_runtime_identical':True,'no_historical_source_reconstruction':True,'original_files_modified':0}
(W/'EXACT_RETAINED_LIBRARY_RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['parts','extracted_files']}))
