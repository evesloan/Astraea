"""One retained canopy derivative. No engine or shared writes from this gate."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,re
HERE=Path(__file__).resolve().parent;INPUTS=HERE/'INPUTS.json';SOURCE_SHA='7dfce55242a651af80b59199217424470ed8d951ecb81eee68ac83539ea5fe14'
def require(value,message):
 if not value:raise AssertionError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,value):
 p=Path(p);require(p.resolve().is_relative_to(HERE/'runs'),'Output outside fresh export run')
 with p.open('x')as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def run_path(label):
 require(re.fullmatch(r'[a-z][a-z0-9_]{0,60}',label),'Fresh simple run label required');p=HERE/'runs'/label;require(p.resolve()==p and not p.is_symlink(),'No output remapping');return p
def gate():
 require(__debug__,'No optimized execution')
 for p,h in read(HERE/'TOOL_HASHES.json')['files'].items():require(sha(HERE/p)==h,'Prepared export input/tool changed: '+p)
 g=read(INPUTS);require(g['status']=='READY_AFTER_INDEPENDENT_SOURCE_RETENTION','Source retention pending')
 require(g['source_sha256']==SOURCE_SHA and sha(g['source'])==SOURCE_SHA,'Source changed')
 require(g['position_limit_m']==50e-6 and g['local_coordinate_limit_m']==1e-10 and g['normal_limit']==2e-6 and g['attribute_compression']is False,'Precision policy changed')
 for p,h in g['input_hashes'].items():require(sha(p)==h,'Pinned source evidence changed: '+p)
 require(sha(g['retention_record'])==g['retention_sha256'],'Independent source proof changed');r=read(g['retention_record'])
 require(r['status']=='PASS_37_CORRECTIVE_SOURCE_FILES_INDEPENDENTLY_RETAINED'and r['remote_commit']==g['retained_commit']and r['remote_main_compact_matches'],'Independent checkpoint not verified')
 require(len(r['files'])==len({x['path']for x in r['files']})==37,'Wrong retained scope')
 for row in r['files']:require(sha(Path(g['catalogue_root'])/row['path'])==row['sha256'],'Retained source changed')
 base=Path(g['source_evidence_root']);q=read(base/'source001/qa/REOPEN_RECEIPT.json');require(q['status']=='PASS_INDEPENDENT_REOPEN_EXACT_SOURCE_OBJECTS_MATERIALS_UV'and q['source_sha256']==SOURCE_SHA,'Reopen proof failed')
 for file,status in [('ACTUAL_CORE_REVIEW.json','PASS_CORE_PURE_GEOMETRY'),('ACTUAL_PROGRAMME_REVIEW.json','PASS_PURE_RETAINED_PROGRAMME')]:
  q=read(base/file);require(q['status']==status and not q['issues'],'Source fit failed: '+file)
 require(len(g['assets'])==1 and g['assets'][0]['parent_design_id']=='AST-AQU-016','Only one same-family derivative allowed');a=g['assets'][0]
 require(len(a['mesh_parts'])==25 and a['triangles']==2836 and len(a['empty_objects'])==2,'Wrong corrected canopy scope')
 inv=read(g['source_inventory'])['object_inventory'];require(len(inv)==846 and sum(x[1]=='MESH'for x in inv)==802,'Source census changed');by={x[0]:x for x in inv};names=set(a['mesh_parts']+a['empty_objects']);require(len(names)==27,'Duplicate source selection')
 for n in names:
  require(n in by and by[n][1]==('MESH'if n in a['mesh_parts']else'EMPTY'),'Wrong source object: '+n);require(by[n][2]is None or by[n][2]in names,'Missing ancestor')
 return g
