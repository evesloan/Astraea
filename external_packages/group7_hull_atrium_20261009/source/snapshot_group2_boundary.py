"""Stable read-only coordination snapshot; never change the other helper's files."""
import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P.parent/'group2_luxury_20261009/C';D=P/'dependencies/coordination_group2_9311';D.mkdir(exist_ok=True);rows=[]
for name in ['GROUP2_GROUP7_BOUNDARY_SHEET.json','GROUP2_STATUS.json','SOURCE_README.md','deliveries/Group2C_D17_876_Deluxe_source_r001.json']:
 raw=(S/name).read_bytes();h=hashlib.sha256(raw).hexdigest();target=D/name;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==raw,'Refuse overwrite of earlier snapshot'
 else:target.write_bytes(raw)
 assert hashlib.sha256((S/name).read_bytes()).hexdigest()==h;rows.append({'source':str(S/name),'retained_path':target.relative_to(P).as_posix(),'sha256':h,'bytes':len(raw)})
boundary=json.loads((D/'GROUP2_GROUP7_BOUNDARY_SHEET.json').read_text());plan=json.loads((P/'docs/UPPER_PERIMETER_AND_TERMINAL_PROPOSALS.json').read_text())
assert boundary['pavilion_enclosure_targets']==plan['private_pavilion_boundary_targets']
plan['later_coordination_snapshot']={'reported_root_checkpoint':boundary['current_root_checkpoint'],'source':'dependencies/coordination_group2_9311/GROUP2_GROUP7_BOUNDARY_SHEET.json','status':'Other helper boundary snapshot, not a silently changed Game baseline. Relevant pavilion targets equal pinned master contract; all81 private reservations remain source-owned. Group2 reports80 units and external window/lift addenda unfinished.'}
plan['all81_private_reservation_keepouts']=boundary['all81_private_reservations'];plan['private790_entry_lift_stair_service_keepouts']=boundary['private_790_entry_and_circulation'];plan['actual876_internal_court_glass']=boundary['actual_876'];plan['root_adoption_decisions'].append('Use new Group2 source construction addenda when available; current recorded boundary sheet still reports80 units unbuilt and private external windows/lifts unresolved')
(P/'docs/UPPER_PERIMETER_AND_TERMINAL_PROPOSALS.json').write_text(json.dumps(plan,indent=2)+'\n')
gallery=json.loads((P/'docs/GALLERY_PLACEMENT_AND_INTERFACES.json').read_text())['rooms']+json.loads((P/'docs/QUIETER_GALLERY_PLACEMENT_AND_INTERFACES.json').read_text())['rooms'];hits=[]
for r in gallery:
 lo,hi=r['bounds_world_xyz']
 for v in boundary['all81_private_reservations']:
  xs=[q[0] for q in v['occupied_floor_boundary_xz']];zs=[q[1] for q in v['occupied_floor_boundary_xz']];a=[min(xs),v['lower_floor_y'],min(zs)];b=[max(xs),v['source_roof_limit_y'],max(zs)]
  if all(min(hi[i],b[i])-max(lo[i],a[i])>1e-5 for i in range(3)):hits.append([r['id'],v['source_envelope_index']])
assert not hits,hits
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'pavilion_targets_equal_pinned_contract':True,'protected_private_reservations':81,'gallery_reservation_overlap_candidates':hits,'scope':'Read-only other-helper boundary snapshot. Its9311 root checkpoint report does not replace this delivery9d6f85 Game pin. Reservations/source-bounds protection is not final window/lift/pavilion mesh acceptance.'}
(P/'qa/group2_coordination_snapshot.json').write_text(json.dumps(out,indent=2)+'\n');print('GROUP2_BOUNDARY_SNAPSHOT',len(rows),'files',81,'private envelopes;0gallery overlaps')
