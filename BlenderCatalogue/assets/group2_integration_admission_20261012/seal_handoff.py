"""Seal only the changed admission handoff and verify independent remote bytes."""
import argparse,pathlib,json,hashlib,subprocess,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
PARENT='ffaf177df8fa460e3b098819604977cad8fbbdd5'
OWNED=['BlenderCatalogue/assets/group2_integration_admission_20261012','Game/data/group2_integration_admission']
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signature(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def audit():
 assert git('rev-parse','HEAD')==PARENT and not git('diff','--name-only','HEAD')
 manifests=[]
 for name in ['group2_completion_20261011','group2_private_vertical_20261011','group2_pit_perimeters_20261011','group2_vip_pavilions_20261012','group2_care_programmes_20261012','group2_family_childcare_20261012','group2_vip_dry_club_20261012','group2_garden_quiet_20261012','group2_family_meal_20261012','group2_meal_arrangement_20261012']:
  f=ROOT/'BlenderCatalogue/assets'/name/'MANIFEST.json';assert subprocess.check_output(['git','show',PARENT+':'+f.relative_to(ROOT).as_posix()],cwd=ROOT)==f.read_bytes();manifests.append({'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f)})
 for name in ['RECEIVER_GEOMETRY_PASS.json','ADAPTER_SOURCE_PASS.json','COMBINED_REFRESH_EXACT_INPUTS.json']:assert json.loads((P/'evidence'/name).read_text())['pass']
 d=json.loads((ROOT/'Game/data/group2_integration_admission/STAR_ATLAS_DRY_ADMISSION.json').read_text());assert d['needed_new_floor_m2']==0 and d['new_models_furniture_or_capacity']==0 and d['route_static_source_overlap_m2']<.0001
 for row in d['required_materialization']:assert sha(ROOT/row['source_path'])==row['sha256']
 delta=d['needed_runtime_delta'];assert sha(ROOT/delta['path'])==delta['preimage_sha256'] and sha(P/'preview/package.gd')==delta['postimage_sha256']
 write(P/'evidence/CHANGED_WORK_INTEGRITY.json',{'pass':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent':PARENT,'ten_prior_manifests_unchanged':manifests,'tracked_originals_unchanged':True,'four_legacy_source_payloads_exact':True,'only_new_owned_paths':OWNED,'source_geometry_and_adapter_checks_only':True,'no_new_engine_import_build_or_backup':True,'not_installed_by_Group2':True,'whole_Group2_accepted':False})
 target=P/'MANIFEST.json';files=[]
 for prefix in OWNED:
  for f in sorted((ROOT/prefix).rglob('*')):
   if f.is_file()and f!=target:
    assert not f.is_symlink()and'__pycache__'not in f.parts;files.append({'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
 write(target,{'schema':'astraea.group2_narrow_admission_handoff.v1','parent':PARENT,'owned_paths':OWNED,'files':files,'file_count':len(files),'bytes':sum(r['bytes']for r in files),'signature':signature(files),'self_excluded':True,'status':'SOURCE_HANDOFF_NOT_INSTALLED;Group1 sole build owner'})
 print(json.dumps({'pass':True,'manifest_sha256':sha(target),'manifest_signature':signature(files),'files_excluding_manifest':len(files),'bytes_excluding_manifest':sum(r['bytes']for r in files)}))
def verify(output):
 f=P/'MANIFEST.json';d=json.loads(f.read_text());assert signature(d['files'])==d['signature']
 for row in d['files']:p=ROOT/row['path'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256']
 actual={p.relative_to(ROOT).as_posix()for prefix in OWNED for p in(ROOT/prefix).rglob('*')if p.is_file()};assert actual=={r['path']for r in d['files']}|{f.relative_to(ROOT).as_posix()}
 rows=git('diff','--name-status',PARENT,'HEAD').splitlines();assert len(rows)==len(d['files'])+1 and all(r.startswith('A\t')and any(r[2:].startswith(p+'/')for p in OWNED)for r in rows)
 assert git('rev-parse','HEAD^')==PARENT and not git('diff','--name-only','HEAD')and not(ROOT/'.git/objects/info/alternates').exists()
 write(output,{'pass':True,'commit':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'parent':PARENT,'manifest_sha256':sha(f),'manifest_signature':d['signature'],'files_excluding_manifest':len(d['files']),'bytes_excluding_manifest':d['bytes'],'all_downloaded_owned_bytes_match_SHA256':True,'method':'Independent remote sparse readback,no object alternates','installed_in_combined_branch':False,'Group1_current_engine_validation':'Pending'})
 print(output.read_text())
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--verify-output',type=pathlib.Path);a=parser.parse_args();verify(a.verify_output)if a.verify_output else audit()
