from pathlib import Path
import sys,json,hashlib,collections
import numpy as np
from scipy.spatial import cKDTree
from geometry_review import glb
source=Path(sys.argv[1]);export=Path(sys.argv[2]);out=Path(sys.argv[3]);assert not out.exists()
s=np.load(source,allow_pickle=False);st=s['triangles'];sv=st.reshape(-1,3);points,source_ids=np.unique(sv,axis=0,return_inverse=True);tree=cKDTree(points);g=glb(export);et=np.concatenate([m['triangles'] for m in g['meshes']]);dist,export_ids=tree.query(et.reshape(-1,3),workers=1)
source_labels=[str(s['material_names'][i]) for i in s['material_ids']];export_labels=[str(m['material']) for m in g['meshes'] for _ in m['triangles']]
def key(t,label):
 a,b,c=map(int,t);return (label,*min((a,b,c),(b,c,a),(c,a,b)))
sk=[key(t,label) for t,label in zip(source_ids.reshape(-1,3),source_labels)];ek=[key(t,label) for t,label in zip(export_ids.reshape(-1,3),export_labels)];sc=collections.Counter(sk);ec=collections.Counter(ek);missing=sc-ec;extra=ec-sc
back_dist=cKDTree(et.reshape(-1,3)).query(points,workers=1)[0]
report={'scope':'Independent reopened-source versus actual exported oriented triangle/material multiset; no engine or visual acceptance','source_npz_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'editable_source_sha256':str(s['source_sha256']),'export_sha256':g['sha256'],'source_triangles':len(st),'export_triangles':len(et),'source_unique_geometric_vertices':len(points),'maximum_export_to_source_vertex_error_m':float(dist.max()),'maximum_source_to_export_vertex_error_m':float(back_dist.max()),'oriented_material_triangles_missing':sum(missing.values()),'oriented_material_triangles_extra':sum(extra.values()),'missing_examples':[{'triangle_key':k,'count':v} for k,v in list(missing.items())[:30]],'extra_examples':[{'triangle_key':k,'count':v} for k,v in list(extra.items())[:30]],'source_material_names':sorted(set(source_labels)),'export_material_names':sorted(set(export_labels)),'passed':bool(len(st)==len(et) and dist.max()<.0001 and back_dist.max()<.0001 and not missing and not extra)}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['missing_examples','extra_examples']},indent=2))
