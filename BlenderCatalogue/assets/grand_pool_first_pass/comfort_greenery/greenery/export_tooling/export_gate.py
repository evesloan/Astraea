"""Read-only preconditions shared by export and independent GLB verification."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
APPROVED_PACKAGE=CAT/'assets/grand_pool_first_pass/comfort_greenery/greenery'
APPROVED_CANDIDATE=APPROVED_PACKAGE/'candidate_v001'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_gate(inputs_path=None):
    ip=Path(inputs_path or HERE/'EXPORT_INPUTS.json').resolve();g=json.loads(ip.read_text());package=Path(g['package']).resolve();candidate=Path(g['candidate']).resolve();assert package==APPROVED_PACKAGE.resolve() and candidate==APPROVED_CANDIDATE.resolve(),'Outside explicitly checked source candidate'
    assert g['source_geometry_tolerance_m']==g['corner_uv_tolerance']==g['normal_tolerance']==2e-6,'No tolerance widening'
    for path,h in g['guard_file_hashes'].items():assert sha(path)==h,'Changed gate input '+path
    plan=json.loads((package/'greenery_contract.json').read_text());qa=json.loads((candidate/'qa/SOURCE_QA_all.json').read_text());ret=json.loads(Path(g['retention_record']).read_text());assert qa['status']=='PASS_SOURCE_QA_ONLY' and qa['source_count']==23 and qa['all_original_hashes_unchanged'];assert ret['independently_retained'] and ret['all_match'] and ret['all_committed_source_blobs_match'];assert ret['remote_commit_verified']==ret['committed_mirror_head']==g['retained_commit']
    assert qa['contract_sha256']==sha(package/'greenery_contract.json')==g['contract_sha256'];assert len(plan['assets'])==23;source_qa={s['name']:s for s in qa['sources']};retained={str(Path(s['source']).resolve()):s for s in ret['sources']}
    original_pins=json.loads((package/'INPUT_PINS.json').read_text())
    for p,h in original_pins['immutable_inputs'].items():
        p=Path(p);p=p if p.is_absolute() else (package/p).resolve();assert sha(p)==h,'Original input changed '+str(p)
    for a in plan['assets']:
        source=(candidate/a['source']).resolve();assert source.is_relative_to(candidate/'source');q=source_qa[a['name']];r=retained[str(source)];h=sha(source);assert h==q['source_sha256']==r['sha256']==r['mirror_sha256']==r['committed_blob_sha256'];assert r['match'] and sha(r['mirror'])==h,'Separate retained source bytes differ';assert a['parent_design_id'] in {'AST-BOT-002','AST-BOT-003','AST-BOT-007'}
    return g,plan,qa,source_qa,package,candidate
def source_unchanged(g,qa):
    for s in qa['sources']:assert sha(s['source'])==s['source_sha256'],'Editable source changed '+s['name']
    for p,h in g['guard_file_hashes'].items():assert sha(p)==h,'Gate input changed '+p
