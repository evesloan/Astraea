"""Portable read-only full source-snapshot versus compact GLB verification."""
from pathlib import Path
import sys,json,hashlib,gzip
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def require(v,m):
 if not v:raise AssertionError(m)
def main():
 from verify_asset import verify_asset
 selection=read(B/'qa/ASSET_SELECTIONS.json');sr=read(B/'qa/SNAPSHOT_RECEIPT.json');er=read(B/'qa/EXPORT_RECEIPT.json');compact=read(B/'qa/COMPACT_EQUIVALENCE.json');source=B.parent/'source_build001/source/AST-AQU-016_connected_gallery_finish_r04.blend'
 if '--source' in sys.argv:source=Path(sys.argv[sys.argv.index('--source')+1])
 require(sha(source)==compact['source_sha256'],'Retained native source identity differs')
 g={'source_sha256':compact['source_sha256'],'light_proposal':source.parents[2]/'ACTUAL_RECEIVERS.json'}
 for a in selection:
  with gzip.open(B/'snapshots'/(a['name']+'.json.gz'),'rt')as f:s=json.load(f)
  row=next(x for x in sr['assets']if x['asset']==a['name']);s['_snapshot_sha256']=row['snapshot_sha256'];p=B/'snapshots'/(a['name']+'.json.gz')
  with gzip.open(p,'rb')as f:require(hashlib.sha256(f.read()).hexdigest()==row['snapshot_sha256'],'Snapshot changed')
  r=next(x for x in er['assets']if x['asset']==a['name']).copy();r['export']=str(B/'exports'/a['file']);r['export_sha256']=next(x for x in compact['assets']if x['file']==a['file'])['compact_sha256']
  out=verify_asset(g,a,s,r);print(out['status'],a['name'],out['source_meshes'],out['source_triangles'])
 print('PASS_TWO_COMPACT_GLB_SOURCE_EQUIVALENCE; source unchanged; native acceptance not run')
if __name__=='__main__':main()
