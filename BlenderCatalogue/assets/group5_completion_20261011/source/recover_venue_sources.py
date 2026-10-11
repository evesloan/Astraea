"""Recover immutable canonical venue sources from independently verified archives."""
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,subprocess,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
checkpoint=json.loads((ROOT/'CHECKPOINT.json').read_text())
venues=json.loads((P/'qa/TEN_LARGE_VENUES.json').read_text())['venues']
store='/tmp/astraea-group5-independent-verification.git'
target=P/'source/retained_venue_recovery';target.mkdir(exist_ok=True)
archives=[]
for p in (ROOT/'external_packages/retained_sections_20261008').rglob('*.zip'):
    if any(x in p.name for x in ['02_copper_source','04_papermoon_source','05_parcels_source','01_starlight_source','03_companion_source']) or p.name=='D09_directory_05_reviewed_source.zip':archives.append(p)
assert len(archives)==6
rows=[]
for archive in sorted(archives):
    name=str(archive.relative_to(ROOT));data=archive.read_bytes()
    oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert oid==checkpoint['source_archives'][name]['sha']
    remote=subprocess.check_output(['git','-C',store,'cat-file','blob',oid])
    h=lambda b:hashlib.sha256(b).hexdigest()
    assert h(remote)==h(data)
    key=next(x for x in archive.parts if x.startswith('D09_directory_'))
    venue=next(x for x in venues if x['programme_key']==key)
    destination=target/key
    assert not destination.exists(),'Never overwrite a recovered source directory'
    destination.mkdir()
    members=[];native=None;export=None
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            n=item.filename;p=PurePosixPath(n)
            if item.is_dir() or '/failed/' in n or 'dependencies' in p.parts or 'inputs' in p.parts:continue
            if not(n.endswith('/source/native.blend') or n=='source/section.blend' or n.endswith('.json') or n.endswith('/exports/section.glb') or n=='exports/D09_directory_05.glb'):continue
            assert not p.is_absolute() and '..' not in p.parts
            b=z.read(item);out=destination/Path(*p.parts);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
            assert h(out.read_bytes())==h(b)
            row={'archive_member':n,'recovered_path':str(out.relative_to(P)),'bytes':len(b),'sha256':h(b)};members.append(row)
            if n.endswith('.blend'):native=row
            if n.endswith('.glb'):export=row
    assert native and export
    rows.append({'programme_key':key,'name':venue['name'],'retained_archive':name,'archive_git_blob':oid,'archive_sha256':h(data),'independent_remote_archive_sha256':h(remote),'native':native,'archived_export':export,'current_runtime':venue['current_runtime'],'current_runtime_sha256':venue['current_runtime_sha256'],'archived_export_matches_current_runtime':export['sha256']==venue['current_runtime_sha256'],'native_header':(P/native['recovered_path']).read_bytes()[:12].decode(),'members':members,'original_archive_and_runtime_unchanged':True,'registry_update':'Scoped provenance contract only;shared received-section metadata untouched','acceptance':'Exact original source recovery,not renewed venue/operation acceptance. D05 archive predates current entry-corrected runtime;do not bind its old source as the corrected authority.'})
r={'status':'PASS_IMMUTABLE_RECOVERY_WITH_D05_CORRECTION_HOLD','archives_verified_from_independent_remote_store':6,'canonical_natives_recovered':6,'canonical_exports_matching_current_runtime':sum(x['archived_export_matches_current_runtime'] for x in rows),'rows':rows,'whole_group_accepted':False,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(P/'qa/VENUE_SOURCE_RECOVERY.json').write_text(json.dumps(r,indent=2)+'\n')
print('GROUP5_VENUE_SOURCE_RECOVERY',len(rows),r['canonical_exports_matching_current_runtime'],'exact runtime matches')
