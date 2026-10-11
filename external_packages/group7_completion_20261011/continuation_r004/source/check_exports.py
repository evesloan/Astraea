"""Decode fresh GLBs independently of Blender and match selected native points."""
from pathlib import Path
import json,sys,hashlib,itertools
import numpy as np
P=Path(__file__).resolve().parents[1];C=P.parent
sys.path.insert(0,str(C.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read,acc,nodes
e=json.loads((P/'docs/EXPORTS.json').read_text());audit=json.loads((P/'qa/NATIVE_AUDIT.json').read_text());cloud=json.loads((P/'qa/NATIVE_POINT_CLOUD.json').read_text());rows=[];tol=.0001
def matches(a,b):
    keys={tuple(q)for q in np.floor(np.array(b)/tol).astype(int)}
    return all(any(tuple(k+off)in keys for off in itertools.product([-1,0,1],repeat=3))for k in np.floor(np.array(a)/tol).astype(int))
for row in e['exports']:
    file=P/row['path'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];d,b=read(file);points=[];count=0
    for im in d.get('images',[]):assert 'uri'not in im and 'bufferView'in im
    for n,m in nodes(d):
        assert n.get('extras',{}).get('contact_category')in ['solid_frame','solid_roof']
        for prim in d['meshes'][n['mesh']]['primitives']:
            a=acc(d,b,prim['attributes']['POSITION']);assert np.isfinite(a).all();a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3];points.extend(a)
            idx=acc(d,b,prim['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a);count+=len(idx)//3
            for k in ['NORMAL','TEXCOORD_0']:assert k in prim['attributes']and np.isfinite(acc(d,b,prim['attributes'][k])).all()
            t=a[idx].reshape(-1,3,3);assert np.min(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1))>1e-9
    a=np.array(points);cell=row['cell'];assert count==audit['cell_triangles'][cell];assert np.max(np.abs(np.array([a.min(axis=0),a.max(axis=0)])-audit['cell_bounds'][cell]))<tol
    assert matches(a,cloud[cell])and matches(cloud[cell],a);rows.append({'cell':cell,'triangles':count,'positions_bidirectionally_match_native_0_1mm':True})
out={'status':'PASS','exports':rows,'native_sha256':e['native_sha256'],'total_triangles':sum(q['triangles']for q in rows),'embedded_images_only':True,'finite_uv_normal_positions':True,'no_degenerate_triangles':True,'pressure_or_capacity_accepted':False}
(P/'qa/EXPORT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('G7_R004_EXPORT_CHECK_PASS',len(rows),out['total_triangles'])
