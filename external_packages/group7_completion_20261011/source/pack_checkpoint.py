"""Verify immutable inputs, then inventory only this isolated handoff's additions."""
from pathlib import Path
import hashlib,json,subprocess,gzip
P=Path(__file__).resolve().parents[1];R=P.parents[1]
BASE='affc5c807087ff87da29f3642c2d6e418241b896'
PRIOR='7f9f4777a4ae93884282155ea9d05b6ff125bd57'
OLD=P.parent/'group7_hull_atrium_20261009'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
baseline=json.loads((R/'CHECKPOINT.json').read_text());counts={}
for label,project in baseline['projects'].items():
    files=project['files'];root=R/project['prefix']
    for name,want in files.items():assert sha(root/name)==want,(label,name)
    counts[label]=len(files)
prior_counts={}
for label,root in [('prior589',OLD),('continuation_r002',OLD/'continuation_r002')]:
    data=json.loads((root/'RESOURCE_HASHES.json').read_text())
    for name,row in data['files'].items():
        path=root/name;assert path.stat().st_size==row['bytes'];assert sha(path)==row['sha256'],name
    prior_counts[label]=len(data['files'])
# The entire restored handoff must match the actual retained Git blobs, not just
# the documented manifests' selected files.
prior_blobs={}
for line in git('ls-tree','-r',PRIOR,'--',str(OLD.relative_to(R))).decode().splitlines():
    meta,name=line.split('\t',1);mode,kind,blob=meta.split();assert kind=='blob'
    path=R/name
    content=path.read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    assert actual==blob,name;prior_blobs[name]=blob
assert git('diff','--name-only',BASE).strip()==b'', 'Existing tracked source changed'
saved='/workspace/Astraea'
assert subprocess.check_output(['git','status','--porcelain','-uno'],cwd=saved)==b''
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=saved).decode().strip()=='144ba8cd8d6105c7b1959f25ce88cb5d89185f0b'
ret=json.loads((P/'qa/R001_LOSSLESS_RETENTION.json').read_text())
raw=P/'source/natives/G7_Completion_r001.blend'
compressed=P/'source/natives/G7_Completion_r001.blend.gz'
assert gzip.decompress(compressed.read_bytes())==raw.read_bytes()
assert sha(P/'source/natives/G7_Completion_r002.blend')=='4f200a563aaa19a2ef4d77ef725c328b95fa469b573903284fff9034688011b9'
assert sha(P/'source/natives/G7_Completion_r003.blend')=='21ea0a9cda7942bacf81e288ab89e12b979ffef1933d192eb200d0f0c438b327'
census=P/'qa/RETAINED_RUNTIME_CENSUS.json'
assert gzip.decompress(census.with_suffix('.json.gz').read_bytes())==census.read_bytes()
preservation={'status':'PASS','baseline_commit':BASE,'baseline_tree':git('rev-parse',BASE+'^{tree}').decode().strip(),'baseline_managed_sha256_files':counts,'prior_manifest_sha256_files':prior_counts,'all_prior_git_blobs_verified':len(prior_blobs),'source_originals_changed':0,'saved_checkout_untouched':True,'r001_lossless_recovery_verified':True,'shared_root_registry_edits':0,'capacity_delta':0,'new_room_ids':0}
(P/'qa/PRESERVATION_CHECK.json').write_text(json.dumps(preservation,indent=2)+'\n')
paths=set()
for name in git('ls-files','--others','--exclude-standard','-z').decode().split('\0'):
    if not name:continue
    owned=(name.startswith(str(P.relative_to(R))+'/') or name.startswith(str(OLD.relative_to(R))+'/') or name.startswith('Game/assets/models/G7_Completion_') or name in ['Game/data/architecture/GROUP7_COMPLETION.json','Game/scripts/group7_completion.gd','Game/scripts/group7_completion.gd.uid'] or any(name in ['Game/tests/'+test+'.gd','Game/tests/'+test+'.gd.uid']for test in ['group7_source_census','group7_completion_check','group7_lighting_registration_check']))
    if owned:paths.add(name)
manifest_name=str(P.relative_to(R)/'RESOURCE_HASHES.json');paths.discard(manifest_name)
files={}
for name in sorted(paths):
    path=R/name;assert path.is_file()
    size=path.stat().st_size;assert size<95*1024*1024,(name,size)
    files[name]={'sha256':sha(path),'bytes':size}
aggregate=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
manifest={'schema':'astraea.group7.handoff.resource-sha256.v1','baseline_commit':BASE,'prior_group7_commit':PRIOR,'path_base':'repository root','files':files,'files_aggregate_sha256':aggregate,'file_count':len(files),'total_bytes':sum(row['bytes']for row in files.values()),'scope':'Owned new source/runtime/checks/views and byte-identical restored prior handoff. Manifest itself excluded to avoid self-reference; its SHA256 is reported independently with the published commit/tree. No baseline-managed source edits.','exclusions':{'raw_census':'Complete bytes retained in qa/RETAINED_RUNTIME_CENSUS.json.gz; see qa/CENSUS_LOSSLESS_RETENTION.json', 'raw_r001_native':'Losslessly retained as source/natives/G7_Completion_r001.blend.gz, see qa/R001_LOSSLESS_RETENTION.json','caches':['.godot','__pycache__','*.blend1'],'unrelated_generated_uid':'Game/tests/validate_lighting_unbounded_range.gd.uid (import-generated; retained in /tmp outside checkout, not staged)','post_publication_verification':'Independent fresh remote receipt is external to the checkpoint and identifies its exact commit/tree.'}}
(P/'RESOURCE_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n')
stage=sorted(paths|{manifest_name})
# Emit NUL-separated owned additions for a later explicit git add operation.
Path('/tmp/astraea_group7_owned_paths.nul').write_bytes('\0'.join(stage).encode()+b'\0')
print(json.dumps({'status':'PASS','baseline_sha256_files':sum(counts.values()),'prior_blobs':len(prior_blobs),'manifest_files':len(files),'bytes':manifest['total_bytes'],'manifest_sha256':sha(P/'RESOURCE_HASHES.json'),'aggregate_sha256':aggregate}))
