"""Non-runtime interval proof for the offset fore-midship core and bounded study."""
from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parents[3]
read=lambda p:json.loads((R/p).read_text())
core=read('data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json')
assert core['origin']==[0,0,-272] and core['transport_catchment_z']==-216
stair=next(s for s in core['stairs']if s['base_y']==52.5)
assert stair['origin']==[3,52.5,-268] and stair['top_y']==61 and stair['file']=='AST-CIR-001.glb'
# Actual source vertex envelope, including rails; baked GLB coordinates.
def bounds(f):
 b=(R/f).read_bytes();ln=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+ln]);aa=[a for a in d['accessors']if 'min'in a and len(a['min'])==3]
 return [[min(a['min'][i]for a in aa)for i in range(3)],[max(a['max'][i]for a in aa)for i in range(3)]]
a,b=bounds('assets/models/AST-CIR-001.glb')
# pi yaw: x'=3-x,z'=-268-z
stair_world=[[3-b[0],52.5+a[1],-268-b[2]],[3-a[0],52.5+b[1],-268-a[2]]]
candidate={'x':[-2,2],'z':[-250,-182],'y':[55.55,60.1]}
# Source convex stair contact, .001 margin: midlanding at local z -10.5 is nearest.
contact_z=[-268.001,-257.499]
# Full floor-height translation, static XZ; any travel phase remains in these bounds.
cabin={'x':[-1.801,1.801],'z':[-280.001,-275.999],'y':[-.181,104.941]}
# Gate leaf closed centers ±.3/±.9; travel ±1.21/±.61; widest inner leaf full-open ±(1.51+.2975+.001).
gates={'x':[-1.954,-1.642],'z':[-279.8085,-276.1915],'y':[-.001,104.811]}
threshold={'x':[-2.12,-1.48],'z':[-279.91,-276.09],'y':[0,104.67]}
# Conservatively reserve entire core's open landing and player capsule radial clearance.
walking_core={'x':[-8.1,8.1],'z':[-285.3,-251.7],'y':[52.5,64]}
sources=['data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json','scripts/primary_atrium_core.gd','scripts/commons_lift.gd','scripts/lift_gate.gd','scripts/player.gd','assets/models/AST-CIR-001.glb','assets/models/AST-CIR-003_seventeen_stop.glb','assets/models/AST-DOR-003.glb']
report={'status':'source/controller interval proof only; no live runtime checks','actual_core_origin':core['origin'],'catchment_z':-216,'catchment_is_not_core_origin':True,'candidate':candidate,'d09_d10_stair_source_world_bounds':stair_world,'d09_d10_stair_convex_contact_z_with_margin':contact_z,'stair_source_z_gap_m':candidate['z'][0]-stair_world[1][2],'stair_contact_z_gap_m':candidate['z'][0]-contact_z[1],'stair_opening_reserved_z_gap_m':7.3,'walking_entire_core_and_landing_envelope':walking_core,'walking_landing_z_gap_m':1.7,'full_seventeen_stop_cabin_collider_sweep':cabin,'cabin_z_gap_m':candidate['z'][0]-cabin['z'][1],'full_moving_cabin_gate_and_all_landing_gate_union':gates,'gate_z_gap_m':candidate['z'][0]-gates['z'][1],'gate_interlock_threshold_union':threshold,'threshold_z_gap_m':candidate['z'][0]-threshold['z'][1],'shaft_reservation_z_gap_m':25.8,'existing_player_capsule_height_m':1.8,'under_structure_trial_ground_clearance_m':3.05,'under_structure_margin_above_player_capsule_m':1.25,'protected_circulation_cuts_required_for_bounded_volume':[],'station_access_and_structure_verified':False,'new_support_required':['Elevated guideway structure','Port boarding platform and landing support','Separate boarding lift floor/shaft/headroom','Separate stair','Preserve four-metre ground pedestrian axis without columns or lift intrusion'],'important_limitation':'The offset core sweeps do not intersect this bounded volume; that does not certify transit viability, accessibility or a complete route. Support columns and new lift landing are not authored or tested.','sources_sha256':{f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in sources}}
(R/'data/architecture/packages/tram/D09_BOUNDED_CORE_SWEEP_20261006.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:report[k]for k in ['stair_source_z_gap_m','stair_contact_z_gap_m','walking_landing_z_gap_m','cabin_z_gap_m','gate_z_gap_m']})
