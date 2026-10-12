from pathlib import Path,PurePosixPath
import subprocess,json,hashlib,stat,zipfile
W=Path(__file__).resolve().parent;R=W.parents[2];RR=Path('/workspace/group8-independent-readback-002');base='affc5c807087ff87da29f3642c2d6e418241b896';out=Path('/workspace/group8-dining-fixture-retained-native-001');assert not out.exists();out.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();results=[];entries=json.load(open(R/'Game/data/architecture/received_sections.json'))['sections']
for key,relative,folder in [('D10_directory_06','E/D10_directory_06/D10_directory_06_03_mineral_broth_hall_SOURCE_PACKAGE.zip','03_mineral_broth_hall'),('D10_directory_10','E/D10_directory_10/D10_directory_10_02_observation_cafe_SOURCE_PACKAGE.zip','02_observation_cafe')]:
 rel='external_packages/retained_sections_20261008/sol_expansion/payloads/'+relative;raw=(R/rel).read_bytes();assert subprocess.check_output(['git','-C',str(RR),'show',base+':'+rel])==raw;directory=out/key;directory.mkdir();rows={}
 with zipfile.ZipFile(R/rel)as z:
  assert z.testzip()is None
  for info in z.infolist():
   p=PurePosixPath(info.filename);assert not p.is_absolute()and'..'not in p.parts and'\\'not in info.filename and not stat.S_ISLNK(info.external_attr>>16);data=z.read(info);target=directory/p
   if info.is_dir():target.mkdir(parents=True,exist_ok=True);continue
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb')as f:f.write(data)
   rows[info.filename]={'bytes':len(data),'sha256':sha(data)}
 root=directory/folder;native=root/'source'/(key+'.blend');runtime=root/'exports'/(key+'.glb');row=next(r for r in entries if r['programme_key']==key);assert runtime.read_bytes()==(R/'Game/assets/models'/row['model_file']).read_bytes();qa=json.load(open(root/'qa/INDEPENDENT_NATIVE_EXPORT_QA.json'));assert sha(native.read_bytes())==qa['native_sha256'];assert sha(runtime.read_bytes())==qa['export_sha256'];fixtures=json.load(open(root/'qa/fixtures.json'))
 results.append({'programme_key':key,'archive':rel,'archive_sha256':sha(raw),'archive_bytes':len(raw),'native':str(native),'native_sha256':qa['native_sha256'],'runtime_file':row['model_file'],'runtime_sha256':row['source_sha256'],'root':str(root),'exact_old_fixture_intents':fixtures,'members':rows})
(W/'EXACT_RETAINED_DINING_FIXTURE_RECOVERY.json').write_text(json.dumps({'status':'PASS_REMOTE_BASELINE_ARCHIVE_CRC_MEMBERS_FINAL_NATIVE_ACTIVE_RUNTIME','baseline':base,'families':results,'original_mutations':0,'historical_reconstruction':False},indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items()if k not in['members','exact_old_fixture_intents']}for r in results]))
