"""Compare actual evaluated source and native role-consolidated position/UV/normal corners."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.spatial import cKDTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
for rp in sorted(OUT.glob('independent_source_corners_AST-*.json')):
 r=json.loads(rp.read_text());sp=ROOT/r['source'];assert sha(sp)==r['source_sha256'];cache=np.load(ROOT/r['corner_cache']);sc=cache['export_expected_corners'];sr=cache['roles'];gp=sp.parent.parent/'exports'/(sp.stem+'.glb');n=Native(gp);corners=[];roles=[]
 for i,node in enumerate(n.g.doc['nodes']):
  if 'mesh'not in node:continue
  w=n.world[i];nm=np.linalg.inv(w[:3,:3]).T
  for p in n.g.doc['meshes'][node['mesh']]['primitives']:
   ix=n.g.accessor(p['indices']).ravel();pos=n.g.accessor(p['attributes']['POSITION']);pos=(np.column_stack([pos,np.ones(len(pos))])@w.T)[:,:3]@C;normal=n.g.accessor(p['attributes']['NORMAL'])@nm.T;normal=normal/np.linalg.norm(normal,axis=1)[:,None];normal=normal@C;uv=n.g.accessor(p['attributes']['TEXCOORD_0']).copy();uv[:,1]=1-uv[:,1];a=np.column_stack([pos,normal,uv]);corners.extend(a[ix]);roles.extend([n.g.doc['materials'][p['material']]['name']]*len(ix))
 gc=np.asarray(corners);gr=np.asarray(roles);results=[]
 for role in sorted(set(sr)):
  a=np.unique(sc[sr==role],axis=0);b=np.unique(gc[gr==role],axis=0);ds,ia=cKDTree(b).query(a);dg,ib=cKDTree(a).query(b);err=float(max(ds.max(),dg.max()));delta=np.concatenate([abs(a-b[ia]),abs(b-a[ib])]);pe=float(delta[:,:3].max());ne=float(delta[:,3:6].max());ue=float(delta[:,6:8].max());results.append({'role':str(role),'source_unique_attribute_corners':len(a),'native_unique_attribute_corners':len(b),'symmetric_attribute_vector_error':err,'max_position_component_error_m':pe,'max_split_normal_component_error':ne,'max_uv_component_error':ue,'normal_tolerance':.0002,'pass':pe<1e-6 and ne<.0002 and ue<1e-6})
 rows.append({'catalogue_id':sp.stem,'source_sha256':sha(sp),'export_sha256':sha(gp),'export_only_uv_repairs':r['export_only_degenerate_uv_projection_repairs'],'source_corner_receipt_sha256':sha(rp),'source_corner_cache_sha256':sha(ROOT/r['corner_cache']),'role_checks':results,'pass':all(x['pass']for x in results)});print(sp.stem,rows[-1]['pass'],max(x['symmetric_attribute_vector_error']for x in results),flush=True)
(OUT/'independent_source_native_corner_comparison.json').write_text(json.dumps({'passed':all(x['pass']for x in rows),'assets':rows,'method':'Actual evaluated source corner world positions/split normals and UVs, with explicitly enumerated collapsed modifier UV polygons reprojected onto their dominant physical plane for expected export UVs versus actual native hierarchy/attributes, per material. Native V mapped once to Blender V=1-V. Symmetric unique8D attribute sets allow equivalent cap tessellation; triangle winding and material surface/volume equality remain separately checked. This does not infer engine batching or performance.','executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
