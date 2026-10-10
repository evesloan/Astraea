from pathlib import Path
import json,hashlib,numpy as np,math
W=Path(__file__).resolve().parent;G={'__file__':str(W/'north_receiving_geometry.py'),'__name__':'geometry'};exec((W/'north_receiving_geometry.py').read_text(),G);R=G['R'];P=G['P'];station=G['station'];recipes=G['recipes'];code=(P/'check_north_candidate.py').read_text();a=code.index('def intersects(');b=code.index('\nsources=',a);exec(code[a:b],globals());U=G['U'];rows=[];hits=[]
for floor in [52.5,56.1]:
 cabin=dict(U['triangles']('AST-CIR-003.glb',(-11.2,floor,-225),-math.pi));posehits=[]
 for name,t in cabin.items():
  lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
  for owner,shapes in [('Frozen_North_Station_Proposal',station),('New_Receiving_006',{q['name']:q['triangles'] for q in recipes})]:
   for n,v in shapes.items():
    aa=v.min(axis=1);bb=v.max(axis=1);mask=np.all((aa<hi-1e-5)&(bb>lo+1e-5),axis=1)
    if not mask.any():continue
    vv=v[mask];aa=aa[mask];bb=bb[mask];hit=False
    for nt in t:
     nl=nt.min(axis=0);nh=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=nh+1e-6)&(bb>=nl-1e-6),axis=1))
     if any(intersects(nt,vv[i]) for i in ids):hit=True;break
    if hit:posehits.append({'floor_y':floor,'cabin_mesh':name,'static_owner':owner,'static_mesh':n})
 hits.extend(posehits);rows.append({'floor_y':floor,'unexpected_contacts':posehits})
# Actual existing-script fixed sill mapped through proposed root−PI/2 and gate_origin_xz=(0,0).
sill={'min':np.array([-12.4,52.39,-225.10]),'max':np.array([-10,52.5,-225.01])};tongue=next(q for q in recipes if q['name']=='N006_LowerLiftThresholdTongue');v=np.maximum(0,np.minimum(tongue['max'],sill['max'])-np.maximum(tongue['min'],sill['min']));assert v.prod()>1e-6 and abs(v[2]-.02)<1e-6
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['Game/scripts/commons_lift.gd','Game/scripts/lift_gate.gd','Game/assets/models/AST-CIR-003.glb']}
rep={'status':'NORTH_LIFT_TWO_STATIONARY_POSES_SOURCE_PASS' if not hits else 'NORTH_LIFT_SOURCE_HOLD','source_only':True,'runtime_changed':False,'existing_controller':{'script':'commons_lift.gd','root_xyz':[-11.2,0,-225],'root_yaw_rad':-math.pi/2,'gate_origin_xz':[0,0],'script_relative_cabin_yaw_rad':-math.pi/2,'net_cabin_yaw_rad':-math.pi,'stop_ids':['G4_FORE_MIDSHIP_LOWER','G4_FORE_MIDSHIP_BOARDING'],'floor_heights':[52.5,56.1]},'actual_cabin_stationary_poses':rows,'unexpected_contacts':hits,'lower_threshold_fixed_sill_overlap_volume_m3':float(v.prod()),'lower_threshold_fixed_sill_bearing_area_m2':float(v[0]*v[2]),'lower_threshold_top_step_m':.001,'lower_floor_to_sill_gap_without_new_tongue_m':.10,'retained_pit_pan_to_actual_lower_cabin_floor_clearance_m':.04,'retained_housing_side_rear_to_actual_cabin_clearance_m':.04,'upper_cabin_roof_to_retained_top_cap_clearance_m':.26,'source_pins':pins,'limits':['Two stationary actual visual cabin poses only, not travel, live collision/carry, controls/rays, gate-leaf sweep or full boarding.','Threshold is separate fixed hardware crossing the front border of an unchanged uncut17.6m² floor-aperture proposal; no current floor is cut.','Root stop/route/lift/arrival adoption, normal-world receiving and capacity remain open.']};(W/'NORTH_LIFT_RECEIVING_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],len(hits),'contacts');print(json.dumps(hits,indent=2))
