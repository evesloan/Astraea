"""Coherent Orchard rail/station source plan. No selected-source mutation."""
from pathlib import Path
import importlib.util,json,math,hashlib,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r006'
spec=importlib.util.spec_from_file_location('retained_section',R/'recovery/tram_section_successor_20261023/author_section_r002.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=json.loads((R/'Game/orchard_tram_interior_20261025/r003/PLAN.json').read_text(encoding='utf-8'))
old=np.array(base['route_points_xz'])
# Retained R4 approach; keep dock straight and retain original constant rail Y.
north=m.screen.fillet([[-5.6,-315],[-5.6,-290],[11.5,-290],[11.5,-262]])
nr=4.5;nt=math.acos(1-5.8/(2*nr));ns=np.array([11.5,-262.]);nc=[]
for t in np.linspace(0,nt,33)[1:]:nc.append(ns+np.array([nr*(1-math.cos(t)),nr*math.sin(t)]))
nh=ns+np.array([nr*(1-math.cos(nt)),nr*math.sin(nt)])
for t in np.linspace(0,nt,33)[1:]:nc.append(nh+np.array([nr*(math.cos(nt-t)-math.cos(nt)),nr*(math.sin(nt)-math.sin(nt-t))]))
assert abs(nc[-1][0]-17.3)<1e-8
north=np.vstack([north,np.array(nc),np.array([[17.3,-233.5]])])
# A shallow R6 S offsets the exit away from the retained ThreadShell bearing.
r=4.5;shift=3.2;theta=math.acos(1-shift/(2*r));start=np.array([17.3,-233.5]);s=[]
for t in np.linspace(0,theta,25)[1:]:s.append(start+np.array([r*(1-math.cos(t)),r*math.sin(t)]))
half=start+np.array([r*(1-math.cos(theta)),r*math.sin(theta)])
for t in np.linspace(0,theta,25)[1:]:s.append(half+np.array([r*(math.cos(theta-t)-math.cos(theta)),r*(math.sin(theta)-math.sin(theta-t))]))
end=np.array(s[-1]);assert abs(end[0]-20.5)<1e-8
south=m.screen.fillet([end.tolist(),[20.5,-222],[-5.6,-222],[-5.6,-205]])
route=np.vstack([old[old[:,1]<-315],north,np.array(s),south[1:],old[old[:,1]>-205]])
fit=m.PathFit(route);stops=[]
for st in base['stops']:
 target=np.array([17.3,-236.1]) if st['station']=='FORE_MIDSHIP' else np.array(base['central']['path_point_xz'] if st['station']=='CENTRAL' else [st['world_xyz'][0],st['world_xyz'][2]])
 cursor=fit.nearest(target);pose=fit.fit(cursor)
 stops.append(dict(st,distance_m=cursor,world_xyz=[pose[1],56.1,pose[2]],body_yaw=pose[3]))
knots=sorted(set([4.,float(fit.s[-1]-4)]+list(np.arange(4,fit.s[-1]-4,.1))+[s['distance_m'] for s in stops]))
poses=[fit.fit(float(at))+[.25] for at in knots]
max_slide=max(abs(p[i]) for p in poses for i in [4,7]);assert max_slide<.20
assert abs(next(s for s in stops if s['station']=='FORE_MIDSHIP')['body_yaw'])<1e-8
old_central=base['central']['new_pose'];new_central=next(p for p in poses if p[0]==next(s['distance_m'] for s in stops if s['station']=='CENTRAL'))
assert np.linalg.norm(np.array(old_central[1:4])-np.array(new_central[1:4]))<1e-7
pins={}
for path in ['Game/tram_section_successor_20261024/section_plan_r002.json','Game/assets/models/AST-RTL-009.glb','Game/assets/models/AST-RTL-007.glb','Game/assets/models/AST-CIR-001.glb','Game/data/architecture/D09_thread_shell.json','Game/data/architecture/D09_D10_orchard_exchange.json','Game/scripts/commons_lift.gd','Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json','Game/source_derivatives/group4_boarding_safety_20261011/AST-TRM-G4-024_powered_portal_body_r001.glb']:
 pins[path]=hashlib.sha256((R/path).read_bytes()).hexdigest()
plan=dict(base,schema='astraea.orchard_interior_route.r006',active=False,status='UNSELECTED_COHERENT_CONSTRUCTION',route_points_xz=route.tolist(),stops=stops,safe_body_cursor_range_m=[4,float(fit.s[-1]-4)],maximum_cross_slide_m=max_slide,source_pins=pins)
plan['central']=dict(base['central'],new_pose=new_central[:-1])
plan['orchard_interval_m']=[fit.nearest(np.array([-5.6,-315])),fit.nearest(np.array([-5.6,-205]))]
plan['central_interval_m']=[fit.nearest(np.array(base['route_points_xz'][next(i for i,p in enumerate(base['route_points_xz']) if p==[-5.6,-85.3])])),fit.nearest(np.array([-5.6,92]))]
plan['foremid_receiving']={'station_id':'FORE_MIDSHIP','catchment_z':-216,'dock_xyz':[17.3,56.1,-236.1],'boarding_edge_x':15.1,'door_side':'port','bridge_reach_m':1.0925925925925926,'platform_xz':[9.7,-237.3,15.1,-228.0],'lift_root_xyz':[13,0,-231.8],'lift_yaw_rad':-math.pi/2,'lift_floor_heights':[52.5,56.1],'persistent_id':'group4_fore_midship_boarding_lift_001','stop_ids':['G4_FORE_MIDSHIP_LOWER','G4_FORE_MIDSHIP_BOARDING'],'original_station_sources_held':True}
unused_earlier_annotation={'orchard_north_transport_opening':{'lo':[15.1,55.4,-250.2],'hi':[19.5,60.1,-249.6]},'retail_shared_arrival_opening':{'lo':[8.3,52.5,-237.5],'hi':[23,60.15,-217.7]},'retail_front_transport_opening':{'lo':[4,55.4,-224.2],'hi':[10.3,60.1,-219.8]},'raised_canopy_y':[60.35,60.55],'protected_d10_underside_y':60.76,'unchanged_public_entry_xz':[8,-216],'unchanged_service_entry_xz':[40,-197]}
plan['remaining']=['Complete actual vehicle/door/cart/bogie swept envelope','Original station removal and all console/gate/bridge bindings must be reconciled before selection','Exact native geometry and source-equivalence checks','Rail/station/roof structural receiving, lower access and guest routes','Actual player-camera architectural/scenic acceptance','RID live-resource correction before moving full-ship validation','Performance and matching Windows delivery']
plan['architectural_changes']=base['architectural_changes']
plan['receiver_bindings']=[];plan['unresolved_receivers']=['New route supports must be authored and verified']
D.mkdir(exist_ok=False)
for name,data in [('PLAN.json',plan),('POSE_KNOTS.json',poses)]: (D/name).write_bytes((json.dumps(data,separators=(',',':'))+'\n').encode())
print(json.dumps({'poses':len(poses),'route_length_m':float(fit.s[-1]),'max_cross_slide_m':max_slide,'foremid':next(s for s in stops if s['station']=='FORE_MIDSHIP'),'central_pose_preserved':True}))
