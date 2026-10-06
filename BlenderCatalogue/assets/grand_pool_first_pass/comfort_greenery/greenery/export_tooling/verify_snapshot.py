"""Read-only portable snapshot verification. No Blender, git or runtime work."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
PACKAGE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/comfort_greenery/greenery')
TARGET=PACKAGE/'export_tooling'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check_hash(path,expected):
    actual=sha(path);assert actual==expected,'Hash mismatch: '+str(path);return actual
def local_evidence(path,root=HERE):
    """Remap only this packet's approved final location to its current copy."""
    root=Path(root).resolve();p=Path(path)
    if p.is_absolute():
        p=p.resolve();assert p.is_relative_to(TARGET.resolve()),'Not this approved tooling packet';p=root/p.relative_to(TARGET.resolve())
    else:p=(root/p).resolve()
    assert p.is_relative_to(root),'Evidence path escapes packet';return p
def verify():
    manifest=json.loads((HERE/'SNAPSHOT_MANIFEST.json').read_text());assert manifest['approved_install_target']==str(TARGET);verified=0
    for rel,row in manifest['files'].items():
        p=local_evidence(rel);assert p.is_file() and not p.is_symlink();check_hash(p,row['sha256']);assert p.stat().st_size==row['bytes'];verified+=1
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()};assert actual==set(manifest['files'])|{'SNAPSHOT_MANIFEST.json'},'Unlisted or missing packet file'
    g=json.loads((HERE/'EXPORT_INPUTS.json').read_text());assert g['package']==str(PACKAGE) and g['candidate']==str(PACKAGE/'candidate_v001');retention=TARGET/'evidence/INDEPENDENT_SOURCE_RETENTION.json';assert g['retention_record']==str(retention);allowed={str(PACKAGE/'greenery_contract.json'),str(PACKAGE/'INPUT_PINS.json'),str(PACKAGE/'candidate_v001/qa/SOURCE_QA_all.json'),str(retention)};assert set(g['guard_file_hashes'])==allowed
    for name,h in g['guard_file_hashes'].items():check_hash(local_evidence(name) if name==str(retention) else Path(name),h)
    originals=json.loads((HERE/'evidence/SOURCE_PACKAGE_INPUT_PINS.json').read_text())
    for name,h in originals['immutable_inputs'].items():
        p=Path(name);p=p if p.is_absolute() else (PACKAGE/p).resolve();check_hash(p,h)
    ret=json.loads(local_evidence(str(retention)).read_text());assert ret['independently_retained'] and ret['all_match'];assert ret['remote_commit_verified']==ret['committed_mirror_head']==g['retained_commit'];sources={row['source']:row for row in ret['sources']};qa=json.loads((HERE/'receipts/SOURCE_QA_all.json').read_text());assert qa['source_count']==23 and qa['status']=='PASS_SOURCE_QA_ONLY'
    for row in qa['sources']:
        p=Path(row['source']).resolve();assert p.is_relative_to(PACKAGE/'candidate_v001/source');r=sources[str(p)];check_hash(p,row['source_sha256']);assert row['source_sha256']==r['sha256']==r['committed_blob_sha256'];check_hash(r['mirror'],r['sha256'])
    eq=json.loads((HERE/'receipts/GLB_EQUIVALENCE_r002_all.json').read_text());assert eq['status']=='PASS_ACTUAL_GLB_SOURCE_EQUIVALENCE' and eq['asset_count']==23;assert eq['position_tolerance_m']==eq['corner_uv_tolerance']==eq['normal_tolerance']==2e-6
    for row in eq['assets']:
        p=Path(row['glb']).resolve();assert p.is_relative_to(PACKAGE/'candidate_v001/exports_r002');check_hash(p,row['glb_sha256'])
    er=json.loads((HERE/'receipts/EXPORT_RECEIPT_r002_all.json').read_text())
    for name,h in er['preserved_failed_exports'].items():
        p=Path(name).resolve();assert p.is_relative_to(PACKAGE/'candidate_v001/exports');check_hash(p,h)
    print(json.dumps(dict(status='PASS_READ_ONLY_REPRODUCIBILITY_SNAPSHOT',packet_files_verified=verified+1,checked_sources=23,checked_r002_glbs=23,preserved_first_exports=23,installed_target=str(TARGET),source_export_pass=True,game_candidate_and_visual_work='Parent-owned; not re-executed by this verification'),indent=2))
if __name__=='__main__':verify()
