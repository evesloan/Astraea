"""Three bounded source derivatives, after independent71-file source retention."""
import sys,re,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;HERE=Path(__file__).parent;INPUTS=HERE/'INPUTS.json';SOURCE_SHA='20671c745e83c92e56c1415211772a786825cc7baf6fe111bd2581236942ab83'
def require(v,m):
 if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,v):
 p=Path(p);require(p.resolve().is_relative_to(HERE/'runs'),'Outside new export output')
 with p.open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def run_path(label):
 require(re.fullmatch(r'[a-z][a-z0-9_]{0,60}',label),'Invalid run label');p=HERE/'runs'/label;require(p.resolve()==p and not p.is_symlink(),'Output redirection');return p
def gate():
 require(__debug__,'No optimized execution')
 for p,h in read(HERE/'TOOL_HASHES.json')['files'].items():require(sha(HERE/p)==h,'Changed frozen export tool/input: '+p)
 g=read(INPUTS);require(g['status']=='READY_AFTER_INDEPENDENT_SOURCE_RETENTION','Source retention pending');require(g['source_sha256']==SOURCE_SHA and sha(g['source'])==SOURCE_SHA,'Source changed')
 require(g['position_limit_m']==50e-6 and g['local_coordinate_limit_m']==1e-10 and g['normal_limit']==2e-6 and g['attribute_compression']is False,'Precision policy changed')
 for p,h in g['input_hashes'].items():require(sha(p)==h,'Source evidence changed: '+p)
 require(sha(g['retention_record'])==g['retention_sha256'],'Independent retention proof changed');r=read(g['retention_record']);require(r['status']=='PASS_71_CURVED_GALLERY_SOURCE_FILES_INDEPENDENTLY_RETAINED'and r['remote_commit']==g['retained_commit']and r['remote_main_compact_matches'],'Independent checkpoint not verified');require(len(r['files'])==len({x['path']for x in r['files']})==71,'Wrong retained scope')
 for row in r['files']:require(sha(Path(g['catalogue_root'])/row['path'])==row['sha256'],'Retained source drift')
 base=Path(g['source_evidence_root']);reopen=read(base/'lighting_revision002/source_build002/qa/INDEPENDENT_REOPEN.json');require(reopen['status']=='PASS_EXACT_PAIRED_LIGHT_SOURCE_REOPEN'and reopen['source_sha256']==SOURCE_SHA,'Reopen failed')
 for file,status in [('PURE_GEOMETRY_REVIEW.json','PASS_PURE_CONNECTED_GALLERY_GEOMETRY'),('ACTUAL_NEW_PROGRAMME_FIT.json','PASS_ACTUAL_NEW_PROGRAMME_FIT'),('lighting_revision002/RECEIVER_PROOF.json','PASS_PAIRED_PHYSICAL_FIXTURE_RECEIVER_PLAN'),('lighting_revision002/ANALYTIC_APERTURE_PROOF.json','PASS_ACTUAL_SOURCE_CONTINUOUS_APERTURE_CONES')]:
  q=read(base/file);require(q['status']==status and not q['issues'],'Source fitting failed: '+file)
 specs={'AST-AQU-016_east_gallery_rest_bay_r03':(27,2,3064,'AST-AQU-016'),'AST-AQU-016_connected_gallery_surroundings':(174,4,4080,'AST-AQU-016'),'AST-RES-001_pool_gallery_directory':(3,0,56,'AST-RES-001')};require({a['name']for a in g['assets']}==set(specs),'Wrong derivative scope')
 inv=read(g['source_inventory'])['object_names'];require(len(inv)==len(set(inv))==1976,'Whole source object set changed');selected=[]
 for a in g['assets']:
  n,e,t,family=specs[a['name']];require((len(a['mesh_parts']),len(a['empty_objects']),a['triangles'],a['parent_design_id'])==(n,e,t,family),'Wrong exact derivative census');names=a['mesh_parts']+a['empty_objects'];require(len(names)==len(set(names))and set(names)<=set(inv),'Selection identities changed');selected+=names
 require(len(selected)==len(set(selected))==210,'Repeated source selection');return g
