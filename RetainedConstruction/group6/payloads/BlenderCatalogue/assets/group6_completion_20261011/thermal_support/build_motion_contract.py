"""Record source-part joint groups for owner adoption; no controller activation."""
import json,math,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[3];p=P/'THERMAL_SUPPORT_CONTRACT.json';data=json.loads(p.read_text())
for spec in data['rooms']:
 prefix='G6_SUPPORT_'+spec['programme_key'][-2:]+'__'
 for j,t in enumerate(spec['stations']):
  station_prefix=prefix+'station_'+str(j)+'_';names=[n for n in spec['new_meshes'] if n.startswith(station_prefix)]
  t['future_carrier_meshes']=[n for n in names if any(n.startswith(station_prefix+x) for x in ['seat_load_pan','seat_pad','seat_back_load','seat_back_pad','returned_grip','side_cradle','folded_towel','sling_seat_anchor'])]
  t['future_flexible_sling_meshes']=[n for n in names if '_sling_' in n and n not in t['future_carrier_meshes']]
  t['future_arm_meshes']=[n for n in names if any(n.startswith(station_prefix+x) for x in ['parked_lift_arm','arm_knee','parked_head','task_'])]
  t['fixed_pivot_connector_meshes']=[station_prefix+'mast_load_column',station_prefix+'swivel_collar']
  mast=t['mast_anchor_xyz'];end=t['proposed_water_seat_xyz'];park=t['seat_top_xyz'];direction=1 if park[2]>mast[2] else -1;t['proposed_yaw_radians']=math.atan2((end[0]-mast[0])*direction,(end[2]-mast[2])*direction);t['proposed_lower_from_parked_m']=44.48-park[1]
  t['moving_player_load_or_occupied_hoist_accepted']=False;t['initial_dock_release_gameplay_implemented']=False
 (P/('CONTRACT_'+spec['programme_key'][-2:]+'.json')).write_text(json.dumps(spec,indent=2)+'\n');shutil.copyfile(R/spec['export'],R/spec['runtime_addition'])
p.write_text(json.dumps(data,indent=2)+'\n');shutil.copyfile(p,R/'Game/data/architecture/group6_completion/THERMAL_SUPPORT_CONTRACT.json');print('THERMAL SOURCE MOTION INTERFACE ONLY; production inactive')
