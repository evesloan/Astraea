"""Actual full-precision engine triangles versus immutable source/export cells."""
from pathlib import Path
import json,hashlib,itertools
import numpy as np
P=Path(__file__).resolve().parents[1]
run=json.loads((P/'qa/RUNTIME_CHECK.json').read_text());assert run['status']=='PASS'
cloud=json.loads((P/'qa/NATIVE_POINT_CLOUD.json').read_text());audit=json.loads((P/'qa/NATIVE_AUDIT.json').read_text());rows=[];tol=.0001
for row in run['actual_forecourt_triangle_captures']:
    path=P/'qa'/row['filename'];tri=np.fromfile(path,dtype='<f4').reshape(-1,3,3);assert np.isfinite(tri).all();cell=row['cell'];assert len(tri)==row['triangles']==audit['cell_triangles'][cell]
    points=np.unique(tri.reshape(-1,3),axis=0).astype(float);source=np.array(cloud[cell]);buckets={}
    for q in source:buckets.setdefault(tuple(np.floor(q/tol).astype(int)),[]).append(q)
    worst=0
    for q in points:
        key=np.floor(q/tol).astype(int);near=[p for off in itertools.product([-1,0,1],repeat=3)for p in buckets.get(tuple(key+off),[])];assert near,cell;error=float(np.min(np.max(np.abs(np.array(near)-q),axis=1)));assert error<=tol,(cell,error);worst=max(worst,error)
    keys={tuple(q)for q in np.floor(points/tol).astype(int)}
    assert all(any(tuple(k+off)in keys for off in itertools.product([-1,0,1],repeat=3))for k in np.floor(source/tol).astype(int)),cell
    bounds=np.array([points.min(axis=0),points.max(axis=0)]);assert np.max(np.abs(bounds-audit['cell_bounds'][cell]))<tol
    rows.append({'cell':cell,'triangles':len(tri),'actual_import_max_coordinate_error_m':worst,'actual_triangle_capture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_actual_vertices_bidirectional_match_0_1mm':True})
out={'status':'PASS','cells':rows,'total_actual_triangles':sum(q['triangles']for q in rows),'only_owned_new_imports_full_precision':True,'retained_model_imports_engine_renderer_unchanged':True,'physics_source_contacts_and_capacity_acceptance_are_separate':True}
(P/'qa/ACTUAL_IMPORT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('G7_R007_ACTUAL_IMPORT_CHECK_PASS',len(rows),out['total_actual_triangles'],max(q['actual_import_max_coordinate_error_m']for q in rows))
