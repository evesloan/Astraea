"""Independently decode the real GLB triangles and compare saved-native vertices."""
from pathlib import Path
import json,sys,hashlib,collections,itertools
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(P.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read,acc,nodes
e=json.load(open(P/'docs/EXPORTS.json'));audit=json.load(open(P/'qa/NATIVE_AUDIT.json'));cloud=json.load(open(P/'qa/NATIVE_POINT_CLOUD.json'));rows=[];tol=.0001
def matches(a,b):
    keys={tuple(q)for q in np.floor(np.array(b)/tol).astype(int)}
    return all(any(tuple(k+np.array(off))in keys for off in itertools.product([-1,0,1],repeat=3))for k in np.floor(np.array(a)/tol).astype(int))
for row in e['exports']:
    file=P/row['path'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
    d,b=read(file);points=[];triangles=0;mesh_nodes=0;glazing=0
    for im in d.get('images',[]):assert 'uri'not in im and'bufferView'in im
    for n,m in nodes(d):
        mesh_nodes+=1;category=n.get('extras',{}).get('contact_category');assert category in ['solid_skin','solid_frame','solid_roof','solid_furniture','visual_foliage','visual_lens'],(file,category)
        for q in d['meshes'][n['mesh']]['primitives']:
            a=acc(d,b,q['attributes']['POSITION']);assert np.isfinite(a).all();a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3];points.extend(a)
            idx=acc(d,b,q['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a);triangles+=len(idx)//3
            for key in ['NORMAL','TEXCOORD_0']:assert key in q['attributes']and np.isfinite(acc(d,b,q['attributes'][key])).all()
            t=a[idx].reshape(-1,3,3);area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;assert np.min(area)>1e-10
            material=d['materials'][q['material']]
            if material.get('alphaMode','OPAQUE')!='OPAQUE':glazing+=len(idx)//3
    a=np.array(points);cell=row['cell'];assert triangles==audit['cell_triangles'][cell],cell
    delta=float(np.max(np.abs(np.array([a.min(axis=0),a.max(axis=0)])-audit['cell_bounds'][cell])));assert delta<tol
    assert matches(a,cloud[cell])and matches(cloud[cell],a),cell
    rows.append({'cell':cell,'triangles':triangles,'mesh_nodes':mesh_nodes,'transparent_triangles':glazing,'bound_max_error_m':delta,'all_native_and_exported_vertices_bidirectionally_matched_0_1mm':True})
report={'status':'PASS','exports':rows,'native_sha256':e['native_sha256'],'geometry_triangles':sum(q['triangles']for q in rows),'native_source_export_vertex_tolerance_m':tol,'embedded_images_only':True,'finite_uv_normal_positions':True,'no_degenerate_triangles':True,'engine_physics_or_pressure_capacity_acceptance':False}
(P/'qa/EXPORT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print('GROUP7_EXPORT_CHECK_PASS',len(rows),report['geometry_triangles'])
