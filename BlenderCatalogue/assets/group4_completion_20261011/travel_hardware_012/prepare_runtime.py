from pathlib import Path
import json,hashlib,shutil,math
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());P=json.loads((W/'TRAVEL_SOURCE_PLAN.json').read_text());I=json.loads((W/'HARDWARE_INTERFACE.json').read_text())
T=R/'Game/source_derivatives/group4_travel_hardware_20261011';T.mkdir(exist_ok=True)
models=[]
for item in I['exports']:
 src=W/item['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256'];shutil.copy2(src,T/item['file']);models.append(item)
poses=P.pop('pose_knots');caps=[.25 if abs(p[0]-P['central_exact_pose'][0])<1.0 else .65 if max(abs(p[5]),abs(p[8]))>.10 else 6.0 for p in poses]
for i in range(len(caps)-2,-1,-1):caps[i]=min(caps[i],math.sqrt(caps[i+1]**2+1.6*(poses[i+1][0]-poses[i][0])))
for i in range(1,len(caps)):caps[i]=min(caps[i],math.sqrt(caps[i-1]**2+1.6*(poses[i][0]-poses[i-1][0])))
for p,speed in zip(poses,caps):p.append(speed)
(T/'POSE_KNOTS.json').write_text(json.dumps(poses,separators=(',',':'))+'\n')
P.update(models=models,model_root='res://source_derivatives/group4_travel_hardware_20261011/',pose_file='res://source_derivatives/group4_travel_hardware_20261011/POSE_KNOTS.json',pose_sha256=hashlib.sha256((T/'POSE_KNOTS.json').read_bytes()).hexdigest(),acceleration_m_s2=.8,maximum_speed_m_s=6.0,curve_speed_cap_m_s=.65,central_alignment_speed_cap_m_s=.25,source_wheels_reused=True,wheel_rail_traction_or_dynamic_forces_tested=False)
if (W/'GATE_FRAME_CONVEX_COMPONENTS.json').exists():
 shutil.copy2(W/'GATE_FRAME_CONVEX_COMPONENTS.json',T/'GATE_FRAME_CONVEX_COMPONENTS.json')
 P.update(gate_contacts_file='res://source_derivatives/group4_travel_hardware_20261011/GATE_FRAME_CONVEX_COMPONENTS.json',gate_contacts_sha256=hashlib.sha256((T/'GATE_FRAME_CONVEX_COMPONENTS.json').read_bytes()).hexdigest())
P['pose_columns'].append('bidirectional_speed_cap_m_s')
(R/'Game/data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');print('TRAVEL_RUNTIME_PREPARED',len(poses),'source-bound poses;2 pinned source models;bidirectional braking profile')
