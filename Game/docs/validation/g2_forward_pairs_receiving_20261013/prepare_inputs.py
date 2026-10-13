from pathlib import Path
import json,hashlib,subprocess,zipfile,io
P=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';rev='ffaf177df8fa460e3b098819604977cad8fbbdd5';sha=lambda b:hashlib.sha256(b).hexdigest();m={x['source_path']:x for x in json.loads((R/'RetainedConstruction/group2/SOURCE_MAP.json').read_text())['files']};rows=[];T=P/'inputs/Game';N=P/'native';N.mkdir(exist_ok=True)
keys=['port_forward_upper_house','starboard_forward_upper_house','port_central_upper_house','port_aft_upper_house','starboard_aft_upper_house']
paths=['Game/data/group2_completion/FLOOR_INTERFACE.json','Game/data/group2_completion/LIGHTING_ADDENDUM.json','Game/data/group2_care_programmes/FITTINGS_r001.json','Game/scripts/group2_care_programmes/package.gd']
for key in keys:paths+=['Game/assets/group2_completion/'+key+'.glb','Game/assets/group2_care_programmes/CARE_'+key+'_r001.glb','Game/data/group2_completion/contracts/'+key+'.json']
for path in paths:
 row=m[path];b=(R/row['storage_path']).read_bytes();assert len(b)==row['bytes']and sha(b)==row['sha256'];assert subprocess.check_output(['git','-C',S,'show',rev+':'+path])==b;q=T/path[5:];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);rows.append({'path':path,'bytes':len(b),'sha256':sha(b),'independent_commit':rev})
archive_rows=[];care=json.loads((T/'data/group2_care_programmes/FITTINGS_r001.json').read_text())
for key in keys:
 rec_path='BlenderCatalogue/assets/group2_completion_20261011/evidence/recovery_'+key+'.json';rec=json.loads((R/m[rec_path]['storage_path']).read_text());q=P/(key+'_original.zip');b=q.read_bytes()if q.exists()else subprocess.check_output(['git','-C',S,'show',rec['source_ref']+':'+rec['archive_path']]);assert len(b)==rec['archive_bytes']and sha(b)==rec['archive_sha256'];q.write_bytes(b)
 with zipfile.ZipFile(io.BytesIO(b))as z:
  for name in z.namelist():assert not name.startswith(('/', '\\'))and '..'not in Path(name.replace('\\','/')).parts,name
  members=[name for name in z.namelist()if name==rec['native_member']or name.endswith('/'+rec['native_member'])];assert len(members)==1;native=z.read(members[0]);assert sha(native)==rec['native_sha256'];(N/(key+'.blend')).write_bytes(native)
 row=next(r for r in care['rows']if r['key']==key);assert sha(native)==row['source_native_sha256']and sha((T/'assets/group2_completion'/f'{key}.glb').read_bytes())==row['source_runtime_sha256']and sha((T/'data/group2_completion/contracts'/f'{key}.json').read_bytes())==row['contract_sha256'];archive_rows.append({'key':key,'archive_ref':rec['source_ref'],'archive_path':rec['archive_path'],'archive_bytes':len(b),'archive_sha256':sha(b),'native_member':members[0],'native_sha256':sha(native)})
(P/'INPUT_VERIFICATION.json').write_text(json.dumps({'status':'PASS_FIVE_EXACT_IMMUTABLE_ADJUNCT_CARE_PAIRS','baseline':'f64d79dcc9a2a1bf1fa1e9320a8f01294cc9c16c','files':rows,'original_archives':archive_rows,'adoption_or_import_not_performed':True},indent=2)+'\n');print('PASS fiveimmutable pairs/native originals;noimports oradoption')
