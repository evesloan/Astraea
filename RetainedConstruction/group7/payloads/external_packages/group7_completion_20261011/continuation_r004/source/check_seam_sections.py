"""Independent horizontal finite-material contacts against pinned receivers."""
from pathlib import Path
import hashlib,json,itertools
import numpy as np
from shapely.geometry import Polygon,MultiPoint

P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
plan=json.loads((P/'docs/SEAM_PLAN.json').read_text());survey=json.loads((P/'qa/ACTUAL_RECEIVERS.json').read_text())
for name,want in plan['source_pins'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==want,name
receivers=survey['receiver_parts'];checks=[];errors=[]
receiver_lo=np.array([q['minimum']for q in receivers]);receiver_hi=np.array([q['maximum']for q in receivers]);receiver_body=np.array([q['source_mode']=='ACTUAL_NATIVE_R003'for q in receivers]);receiver_fore=np.array([q['terminal']=='Fore'for q in receivers])
def section(row,y):
    a=np.array(row['vertices_world_xyz']);low=float(a[:,1].min());high=float(a[:,1].max())
    if y<low-1e-7 or y>high+1e-7:return Polygon()
    if 'section_polygons_xz'in row:
        t=(y-low)/(high-low);p=np.array(row['section_polygons_xz'][0])*(1-t)+np.array(row['section_polygons_xz'][1])*t;return Polygon(p)
    if row['name'].endswith('_SteppedRoof'):
        return Polygon(a[:len(a)//2][:,[0,2]])
    points=[q[[0,2]]for q in a if abs(q[1]-y)<1e-7]
    for i,j in itertools.combinations(range(len(a)),2):
        q,r=a[i],a[j]
        if (q[1]-y)*(r[1]-y)<-1e-12:
            v=q+(r-q)*((y-q[1])/(r[1]-q[1]));points.append(v[[0,2]])
    return MultiPoint(points).convex_hull if len(points)>2 else Polygon()
cache={}
def contacts(part,y,mode):
    poly=section(part,y);mn=np.array(part['vertices_world_xyz']).min(axis=0);mx=np.array(part['vertices_world_xyz']).max(axis=0);result=[]
    mask=(receiver_lo[:,1]<=y)&(receiver_hi[:,1]>=y)&np.all(np.minimum(mx[[0,2]],receiver_hi[:,[0,2]])-np.maximum(mn[[0,2]],receiver_lo[:,[0,2]])>1e-7,axis=1)
    mask&=receiver_fore if 'Fore'in part['name']else ~receiver_fore
    if mode=='body':mask&=receiver_body
    elif mode=='terminal':mask&=~receiver_body
    for i in np.where(mask)[0]:
        row=receivers[int(i)]
        key=(i,round(y,6))
        if key not in cache:cache[key]=section(row,y)
        area=poly.intersection(cache[key]).area
        if area>1e-6:result.append({'receiver':row['name'],'source':row['native'],'category':row['category'],'horizontal_contact_area_m2':area})
    return result
for part in plan['parts']:
    ya,yb=part['y_interval'];eps=min(.001,(yb-ya)/5)
    if 'CornerSeal'in part['name'] and 'HeadLap'not in part['name']:
        critical=sorted({ya,yb}|{float(q[1])for row in receivers if row['terminal']in part['name']for q in row['vertices_world_xyz']if ya<float(q[1])<yb})
        samples={ya+eps,yb-eps,(ya+yb)/2}
        for y in critical[1:-1]:
            if ya+eps<y-eps<yb-eps:samples.add(y-eps)
            if ya+eps<y+eps<yb-eps:samples.add(y+eps)
        for a,b in zip(critical,critical[1:]):
            if b-a>2*eps:samples.add((a+b)/2)
        for y in sorted(samples):
            body=contacts(part,y,'body');terminal=contacts(part,y,'terminal')
            record={'part':part['name'],'y':y,'body_receivers':body,'terminal_receivers':terminal,'passes':bool(body and terminal)};checks.append(record)
            if not record['passes']:errors.append({'part':part['name'],'y':y,'body':len(body),'terminal':len(terminal)})
    else:
        y=(ya+yb)/2;found=contacts(part,y,'any');record={'part':part['name'],'y':y,'receivers':found,'passes':bool(found)};checks.append(record)
        if not found:errors.append({'part':part['name'],'y':y,'receivers':0})
# Exact meeting planes between every successive spine segment have a nonzero
# common material section, including the lower/headwall transition at Y69.5.
for term in ['Fore','Aft']:
    for side in [-1,1]:
        spines=[p for p in plan['parts']if f'{term}_CornerSeal_{side}_'in p['name']];spines.sort(key=lambda q:q['y_interval'][0])
        for a,b in zip(spines,spines[1:]):
            y=a['y_interval'][1];assert abs(y-b['y_interval'][0])<1e-8
            area=section(a,y).intersection(section(b,y)).area
            checks.append({'source_spine_plane':[a['name'],b['name']],'y':y,'contact_face_area_m2':area,'passes':area>1e-5})
            if area<=1e-5:errors.append({'disconnected_spine':[a['name'],b['name']]})
out={'status':'PASS'if not errors else'HOLD','checks':len(checks),'errors':errors,'section_contacts':checks,'scope':'Finite material contacts of additive weather joints and their exact pinned receivers; common planes for continuous spine sections. GLB-correlated retained terminal records and actual r003 native vertices. Not pressure/load/joint capacity or whole-enclosure acceptance.','pressure_or_capacity_accepted':False,'source_pins':plan['source_pins']}
(P/'qa/SEAM_SECTION_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('G7_R004_SECTION_CHECK',out['status'],out['checks'],'errors',errors)
raise SystemExit(0 if not errors else 1)
