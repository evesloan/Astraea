"""One coherent retained-crossing correction; preserve every original receiver."""
from pathlib import Path
import json,math,hashlib,importlib.util,sys,copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r008'
assert not D.exists(),'Preserve authored revisions'
spec=importlib.util.spec_from_file_location('author',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
prior=json.loads((D.parent/'r002/PLAN.json').read_text());old=np.array(prior['route_points_xz'])
def shift(x0,x1,z,radius=4.5):
    direction=1 if x1>x0 else -1
    theta=math.acos(1-abs(x1-x0)/(2*radius))
    first=np.array([[x0+direction*radius*(1-math.cos(t)),z+radius*math.sin(t)] for t in np.linspace(0,theta,49)])
    middle=first[-1]
    second=np.array([[middle[0]+direction*radius*(math.cos(theta-t)-math.cos(theta)),middle[1]+radius*(math.sin(theta)-math.sin(theta-t))] for t in np.linspace(0,theta,49)[1:]])
    return np.vstack([first,second])
north=shift(-5.6,0,118)
entry=shift(0,7,160)
exit_route=a.screen.fillet([[7,180],[7,209],[18.5,209],[18.5,248],[-5.6,248],[-5.6,279]],4.5)
core_shift=shift(-5.6,-5.2,279,20)
inside=np.vstack([entry,exit_route,core_shift[1:],np.array([[-5.2,289.8]])])
south=shift(-5.2,0,289.8);returning=shift(0,-5.6,310)
route=np.vstack([old[old[:,1]<118],north,inside,south[1:],returning,old[old[:,1]>returning[-1,1]]])
assert np.all(np.linalg.norm(np.diff(route,axis=0),axis=1)>1e-8)
fit=a.PathFit(route);plan=copy.deepcopy(prior)
for stop in plan['stops']:
    if stop['station']=='AFT_MIDSHIP':stop['world_xyz']=[18.5,56.1,217]
    target=np.array([stop['world_xyz'][0],stop['world_xyz'][2]]) if stop['station']!='CENTRAL' else np.array(plan['central']['path_point_xz'])
    cursor=fit.nearest(target);pose=fit.fit(cursor)
    assert np.max(abs(np.array(pose[1:4])-np.array([stop['world_xyz'][0],stop['world_xyz'][2],stop['body_yaw']])))<1e-6,stop
    stop['distance_m']=cursor
knots=sorted(set([4.,float(fit.s[-1]-4)]+list(np.arange(4,fit.s[-1]-4,.1))+[s['distance_m'] for s in plan['stops']]))
poses=[fit.fit(float(at))+[.25] for at in knots]
assert max(abs(p[i]) for p in poses for i in [4,7])<.2
interval=[fit.nearest(np.array([-5.6,110])),fit.nearest(np.array([-5.6,325]))]
plan.update(route_points_xz=route.tolist(),aquatic_interval_m=interval,safe_body_cursor_range_m=[4.,float(fit.s[-1]-4)],maximum_cross_slide_m=max(abs(p[i]) for p in poses for i in [4,7]),status='UNSELECTED_COMPLETE_CROSSING_CORRECTION',predecessor='a743f5c850cc1e79352c5b00b6ea87fb8a498c4d')
plan['aftmid_receiving']['physical_docking_z']=217
plan['alignment_reason']='Pass both paired D09 corridor roofs through their retained central gap, keeping every shell/headroom intact. Preserve the original switchback and bearing column with X7 west approach, enter the grand volume at Z209 and dock at X18.5/Z217; preserve the protected Aft Midship core approach; short radius4.5 tangent S transfers are subject to exact component/source checks.'
catalogue=json.loads((R/'Game/data/architecture/SHOPPING_PROMENADE.json').read_text());crossings=[]
for row in catalogue['chunks']:
    if row['chunk_id'] not in ['LINK_D09_P145','LINK_D09_S145','LINK_D09_P301','LINK_D09_S301']:continue
    entry={'id':row['chunk_id'],'position':row['position'],'sources':[]}
    for layer in row['exports']:
        path='Game/assets/models/shopping_promenade_20261009/'+Path(row['exports'][layer]).name
        entry['sources'].append({'path':path,'sha256':hashlib.sha256((R/path).read_bytes()).hexdigest(),'layer':layer})
    crossings.append(entry)
assert len(crossings)==4
D.mkdir()
for name,data in [('PLAN.json',plan),('POSE_KNOTS.json',poses),('CROSSING_SOURCES.json',crossings)]:
    (D/name).write_bytes((json.dumps(data,separators=(',',':'))+'\n').encode())
selected=[p for p in poses if interval[0]<=p[0]<=interval[1]]
(D/'QUERY_ROUTE.json').write_bytes((json.dumps({'variants':[{'crossing_z':'coherent_r008','poses':selected}]},separators=(',',':'))+'\n').encode())
print(json.dumps({'poses':len(poses),'affected_poses':len(selected),'crossings':len(crossings),'s_shift_end':south[-1].tolist(),'other_stop_poses_preserved':True,'aft_dock_z':217,'max_slide_m':plan['maximum_cross_slide_m']}))
