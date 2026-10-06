from pathlib import Path
import numpy as np,sys,json,collections
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,'/workspace/scratch/375c2e438292/engineering-density-review');from geometry_review import glb
s=np.load(R/'qa/reopened_canonical_v2.npz');g=glb(R/'exports/AST-ENG-008_cell_restriction_signage_004.glb');v,idx=np.unique(s['triangles'].reshape(-1,3),axis=0,return_inverse=True);tree=cKDTree(v);src=idx.reshape(-1,3);ec=[];sc=[]
def key(ids,uv,mat):
 row=tuple((int(i),float(u[0]),float(u[1]))for i,u in zip(ids,uv));return(mat,*min(row,row[1:]+row[:1],row[2:]+row[:2]))
for ids,uv,mi in zip(src,s['uv'],s['material_ids']):sc.append(key(ids,uv,str(s['material_names'][mi])))
uv_min=1;norm_error=0
for m in g['meshes']:
 dist,ids=tree.query(m['triangles'].reshape(-1,3));assert dist.max()==0;uv=m['uv'][m['indices']];assert np.isfinite(uv).all();ab=uv[:,1]-uv[:,0];ac=uv[:,2]-uv[:,0];det=abs(ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0]);assert det.min()>1e-12;uv_min=min(uv_min,float(det.min()));norm_error=max(norm_error,float(abs(np.linalg.norm(m['normals'],axis=1)-1).max()))
 for i,u in zip(ids.reshape(-1,3),uv):ec.append(key(i,u,m['material']))
assert collections.Counter(sc)==collections.Counter(ec);assert norm_error<.000001
print(json.dumps({'status':'PASS','triangles':len(sc),'exact_oriented_material_position_uv':True,'minimum_uv_double_area':uv_min,'maximum_unit_normal_error':norm_error}))
