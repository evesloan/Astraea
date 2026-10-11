"""Actual retained GLB head faces receiving the four new Y61 weather feet."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
sys.path.insert(0,str(C.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read,acc,nodes
plan=json.loads((P/'docs/SEAM_PLAN.json').read_text());prior=json.loads((P/'docs/PREIMAGE_GROUP7_COMPLETION.json').read_text());faces=[];pins={}
for row in prior['models'][40:56]:
    file=R/row['source'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];pins[row['source']]=row['sha256'];d,b=read(file)
    for n,m in nodes(d):
        for prim in d['meshes'][n['mesh']]['primitives']:
            a=acc(d,b,prim['attributes']['POSITION']);a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3];idx=acc(d,b,prim['indices']).ravel();tri=a[idx].reshape(-1,3,3)
            mask=np.all(np.abs(tri[:,:,1]-61)<.0001,axis=1)&(np.max(np.abs(tri[:,:,2]),axis=1)>509.2)
            for t in tri[mask]:
                poly=Polygon(t[:,[0,2]])
                if poly.area>1e-8:faces.append({'source':row['source'],'node':n.get('name',''),'poly':poly})
checks=[]
for row in plan['parts']:
    if not row['name'].endswith('_Lower')or '_CornerSeal_'not in row['name']:continue
    poly=Polygon(row['section_polygons_xz'][0]);contacts=[]
    for face in faces:
        area=poly.intersection(face['poly']).area
        if area>1e-8:contacts.append({'source':face['source'],'node':face['node'],'contact_face_area_m2':area})
    area=poly.intersection(unary_union([f['poly']for f in faces])).area
    checks.append({'new_foot':row['name'],'plane_y':61,'actual_middle_frame_contact_area_m2':area,'receivers':contacts,'passes':area>1e-5})
out={'status':'PASS'if len(checks)==4 and all(q['passes']for q in checks)else'HOLD','checks':checks,'source_pins':pins,'actual_binary_retained_frame_horizontal_faces':len(faces),'native_or_source_edited':False,'capacity_accepted':False,'scope':'Geometric receiving faces only. Four weather feet meet retained middle-frame top faces at Y61; downstream primary structure and loads/joints/receiver strength remain held.'}
(P/'qa/MIDDLE_FRAME_SEAT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('G7_R004_MIDDLE_FRAME_SEATS',out['status'],[(q['new_foot'],q['actual_middle_frame_contact_area_m2'])for q in checks])
raise SystemExit(0 if out['status']=='PASS'else 1)
