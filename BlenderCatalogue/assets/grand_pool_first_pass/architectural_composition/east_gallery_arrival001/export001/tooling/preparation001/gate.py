"""Fail-closed retained inputs and NEW scratch outputs; no engine invocation."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'INPUTS.json'
SOURCE_SHA = '9aa232ad30c515eabb128804b6d430ae2cfc3d76f93383a612165281620e6f05'
RETENTION_SHA = 'c3c5bdee6a28bb9074317f498fb167627ffc724812b77d5f43058b7bf58cb27e'
COMMIT = '15f68cec578f1c054917f0540ac4789821889160'
def require(value, message):
    if not value: raise AssertionError(message)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def write_new(p, value):
    p = Path(p)
    require(p.resolve().is_relative_to(HERE / 'runs'), 'Output outside new scratch runs')
    with p.open('x') as handle: json.dump(value, handle, indent=2, allow_nan=False); handle.write('\n')
def run_path(label):
    require(re.fullmatch(r'[a-z][a-z0-9_]{0,60}', label), 'Use a simple fresh run label')
    p = HERE / 'runs' / label
    require(p.resolve() == p and not p.is_symlink(), 'No symlink output remapping')
    return p

def gate():
    require(__debug__, 'Do not use Python -O')
    for p,h in read(HERE/'TOOL_HASHES.json')['files'].items(): require(sha(HERE/p)==h, 'Prepared tool/input changed: '+p)
    g = read(INPUTS)
    require(g['source_sha256']==SOURCE_SHA and g['retention_sha256']==RETENTION_SHA and g['retained_commit']==COMMIT, 'Wrong retained checkpoint')
    require(g['position_limit_m']==50e-6 and g['local_coordinate_limit_m']==1e-10 and g['normal_limit']==2e-6 and g['attribute_compression'] is False, 'No precision policy relaxation')
    for p,h in g['input_hashes'].items(): require(sha(p)==h, 'Pinned input changed: '+p)
    r = read(g['retention_record']); require(sha(g['retention_record'])==RETENTION_SHA, 'Retention hash changed')
    require(r['status']=='PASS_ALL127_SOURCE_FILES_INDEPENDENTLY_RETAINED' and r['remote_commit']==COMMIT and r['remote_main_compact_matches'], 'Independent retention not passed')
    require(len(r['files'])==len({x['path'] for x in r['files']})==127, 'Wrong retained file inventory')
    for row in r['files']: require(sha(Path(g['catalogue_root'])/row['path'])==row['sha256'], 'Retained file changed: '+row['path'])
    require(sha(g['source'])==SOURCE_SHA, 'Source bytes changed')
    base=Path(g['source_evidence_root'])
    q=read(base/'qa/INDEPENDENT_REOPEN.json'); require(q['status']=='PASS_EXACT_COMPOSED_SOURCE_REOPEN' and q['source_unchanged'] and q['source_sha256']==SOURCE_SHA, 'Source reopen not passed')
    for name,status in [('ACTUAL_CORE_FITTING.json','PASS_CORE_PURE_GEOMETRY'),('ACTUAL_PROGRAMME_FITTING.json','PASS_PURE_RETAINED_PROGRAMME')]:
        q=read(base/'qa'/name); require(q['status']==status and q['issues']==[], 'Fitting not passed: '+name)
    require(len(g['assets'])==4 and [len(a['mesh_parts']) for a in g['assets']]==[6,23,21,26] and [a['triangles'] for a in g['assets']]==[304,2752,3468,3466], 'Wrong four derivative scope')
    require(len({n for a in g['assets'] for n in a['mesh_parts']})==76, 'Repeated or wrong source selection')
    require([a['parent_design_id'] for a in g['assets']]==['AST-AQU-016','AST-AQU-016','AST-RES-001','AST-LIB-010'], 'Source family changed')
    require(len(g['existing_runtime_models_reused'])==4 and all(n.startswith('AST-BOT-') for n in g['existing_runtime_models_reused']), 'Plant reuse scope changed')
    inv=read(g['source_inventory'])['object_inventory']; require(len(inv)==844 and sum(x[1]=='MESH' for x in inv)==800, 'Wrong retained scene inventory')
    by={x[0]:x for x in inv}
    for a in g['assets']:
        names=set(a['mesh_parts']+a['empty_objects']); require(len(names)==len(a['mesh_parts'])+len(a['empty_objects']), 'Duplicate selection')
        for n in names:
            require(n in by and by[n][1]==('MESH' if n in a['mesh_parts'] else 'EMPTY'), 'Wrong source type: '+n)
            require(by[n][2] is None or by[n][2] in names, 'Selection omits retained ancestor: '+n)
        for root in a['selected_roots']:
            children={n for n,t,p in inv if p==root}; require(children<=names, 'Programme root selection is incomplete')
    return g
