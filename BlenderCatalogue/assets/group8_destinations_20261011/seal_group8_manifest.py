"""Seal only owned additions; refuse changes to any baseline path."""
from pathlib import Path
import subprocess,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2]
baseline='affc5c807087ff87da29f3642c2d6e418241b896'
manifest_path=W/'GROUP8_MANIFEST.json'
relative_manifest=manifest_path.relative_to(R).as_posix()
prefixes=('BlenderCatalogue/assets/group8_destinations_20261011/','BlenderCatalogue/assets/group8_orchard_service_20261011/','BlenderCatalogue/assets/group8_arrivals_service_20261011/','BlenderCatalogue/assets/group8_library_service_20261011/','BlenderCatalogue/assets/group8_medical_privacy_20261012/','BlenderCatalogue/assets/group8_dining_service_20261012/','Game/data/architecture/group8/','Game/scripts/group8/','Game/tests/group8/','Game/docs/group8/','Game/assets/models/G8_CROWN_INTERIORS_r006','Game/assets/models/G8_ORCHARD_SERVICE_r004','Game/assets/models/G8_ARRIVALS_SERVICE_r003','Game/assets/models/G8_LIBRARY_SERVICE_r006','Game/assets/models/G8_MEDICAL_PRIVACY_r003','Game/assets/models/G8_DINING_SERVICE_r003')
def git(*args):return subprocess.check_output(['git','-C',str(R),*args]).decode()
changes=git('diff','--name-status',baseline).splitlines()
owned=set()
for row in changes:
    action,path=row.split('\t',1)
    assert action=='A',('Baseline mutation',row)
    assert path.startswith(prefixes),('Unowned addition',path)
    owned.add(path)
for path in git('ls-files','--others','--exclude-standard').splitlines():
    assert path.startswith(prefixes),('Unowned untracked addition',path)
    owned.add(path)
owned.discard(relative_manifest)
rows={}
for path in sorted(owned):
    data=(R/path).read_bytes()
    assert len(data)<95*1024*1024,('Oversized payload',path)
    rows[path]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
report={'schema':1,'baseline_commit':baseline,'baseline_tree':git('rev-parse',baseline+'^{tree}').strip(),'owned_branch':git('branch','--show-current').strip(),'status':'Source and focused full-main construction checks PASS; uninstalled candidate; broader Group8 unfinished','files':rows,'total_files':len(rows),'total_bytes':sum(row['bytes']for row in rows.values()),'excluded_self':relative_manifest,'original_tracked_file_mutations':0,'shared_main_or_checkpoint_ref_mutations':0,'new_capacity':0,'new_programmes':0,'new_floor_owners':0}
manifest_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'payload_files':report['total_files'],'payload_bytes':report['total_bytes']}))
