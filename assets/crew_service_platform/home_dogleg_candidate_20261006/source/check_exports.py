"""Pure actual GLB source-member coverage, bounds, UV/normal and triangle accounting."""
from pathlib import Path
import json,sys,hashlib,collections
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'engineering-density-review'));from geometry_review import glb
out=[]
for stem in ['AST-STF-010_home_dogleg','AST-STF-009_pool_market_home']:
 src=json.loads((R/'qa'/(stem+'_REOPEN.json')).read_text());expected={r['name']:r for r in src['meshes']};g=glb(R/'exports'/(stem+'.glb'));nodes={n['name']:n for n in g['nodes']};by_node=collections.defaultdict(list)
 for m in g['meshes']:by_node[m['node']].append(m)
 seen=[];records=[]
 for name,ms in by_node.items():
  members=json.loads(ms[0]['extras']['source_members_json']);assert len(members)==len(set(members));assert all(n in expected for n in members);seen+=members;tri=np.concatenate([m['triangles']for m in ms]);flat=tri.reshape(-1,3);lo=np.min([expected[n]['bounds_min']for n in members],axis=0);hi=np.max([expected[n]['bounds_max']for n in members],axis=0);error=np.maximum(abs(flat.min(0)-lo),abs(flat.max(0)-hi));scale=np.maximum(abs(lo),abs(hi)).astype(np.float32);ulp=np.abs(np.spacing(scale)).astype(float);tolerance=np.maximum(ulp*4,2e-6)
  assert np.all(error<=tolerance),(name,error,tolerance);assert len(tri)==sum(expected[n]['triangles']for n in members),(name,len(tri))
  for m in ms:
   assert np.isfinite(m['triangles']).all()and m['uv']is not None and np.isfinite(m['uv']).all()and m['normals']is not None and np.isfinite(m['normals']).all();assert all(r['collision_contract']==m['extras'].get('collision_contract')for r in[expected[n]for n in members])
  records.append({'batch':name,'source_members':members,'triangles':len(tri),'bounds_error_xyz_m':error.tolist(),'float32_conversion_bound_xyz_m':tolerance.tolist()})
 assert collections.Counter(seen)==collections.Counter(expected.keys());assert sum(r['triangles']for r in records)==src['triangles']
 out.append({'stem':stem,'export_sha256':g['sha256'],'source_sha256':src['source_sha256'],'source_members':len(seen),'batches':len(records),'triangles':src['triangles'],'material_groups':len(g['doc'].get('materials',[])),'embedded_images':all('bufferView'in im for im in g['doc'].get('images',[])),'records':records})
report={'status':'PASS_EXPORTED_SOURCE_MEMBER_ACCOUNTING','representations':out,'limits':'Actual export checks coverage, per-batch bounds and triangle counts plus finite UV/normals. This is not full per-vertex equivalence, collision import or runtime traversal acceptance.'};(R/'qa/EXPORT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'representations':[{k:v for k,v in r.items()if k!='records'}for r in out]},indent=2))
