"""Only the corrected directory; passing architecture exports must stay unchanged."""
import sys,re,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;HERE=Path(__file__).parent;INPUTS=HERE/'INPUTS.json';SOURCE_SHA='cec736ae273f0403f823a6aa7f78007d1c88daf4f5236c2832fea17286778520'
def require(v,m):
 if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,v):
 p=Path(p);require(p.resolve().is_relative_to(HERE/'runs'),'Outside new directory export')
 with p.open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def run_path(label):
 require(re.fullmatch(r'[a-z][a-z0-9_]{0,60}',label),'Invalid run label');p=HERE/'runs'/label;require(p.resolve()==p and not p.is_symlink(),'Output redirection');return p
def gate():
 for p,h in read(HERE/'TOOL_HASHES.json')['files'].items():require(sha(HERE/p)==h,'Frozen directory tool/input changed')
 g=read(INPUTS);require(g['status']=='EXACT_SOURCE_COPY_READ_ONLY_EXPORT_AUTHORIZED_PUBLICATION_PENDING','Source-copy authorization pending');require(g['source_sha256']==SOURCE_SHA and sha(g['source'])==SOURCE_SHA,'Changed sampler source')
 require(sha(g['copy_receipt'])==g['copy_receipt_sha256'],'Changed exact copy receipt');r=read(g['copy_receipt']);require(r['status']=='PASS_EXACT_NEW_CURVED_GALLERY_SOURCE_RETENTION'and len(r['written'])==48 and not r['unexpected_changes'],'Source copy not verified')
 source_rel=str(Path(g['source']).relative_to(g['catalogue_root']));require(sum(row['path']==source_rel and row['sha256']==SOURCE_SHA for row in r['written'])==1,'Source successor not in exact copy')
 for row in r['written']:require(sha(Path(g['catalogue_root'])/row['path'])==row['sha256'],'Retained copied file drift')
 require(sha(g['independent_preimage_retention'])==g['independent_preimage_retention_sha256'],'Preimage protection proof changed');protection=read(g['independent_preimage_retention']);require(protection['status']=='PASS_71_CURVED_GALLERY_SOURCE_FILES_INDEPENDENTLY_RETAINED'and protection['live_mirror_immutable_commit_hashes_all_match'],'Original source not independently protected')
 base=Path(g['source']).parents[1];b=read(base/'BUILD_RECEIPT.json');q=read(base/'REOPEN_RECEIPT.json');require(q['status']=='PASS_EXACT_SAMPLER_SUCCESSOR_REOPEN'and q['source_sha256']==SOURCE_SHA,'Reopen failed');require(b['exact_change']['property']=='extension'and b['exact_change']['before']=='CLIP'and b['exact_change']['after']=='EXTEND'and b['all_geometry_uv_images_palette_unchanged'],'Unreviewed source setting change')
 require(g['position_limit_m']==50e-6 and g['local_coordinate_limit_m']==1e-10 and g['normal_limit']==2e-6 and g['attribute_compression']is False,'Precision policy changed')
 require(len(g['assets'])==1,'Do not re-export unchanged architecture');a=g['assets'][0];require(a['name']=='AST-RES-001_pool_gallery_directory'and a['parent_design_id']=='AST-RES-001'and len(a['mesh_parts'])==3 and a['triangles']==56 and not a['empty_objects'],'Only exact corrected directory permitted');return g
