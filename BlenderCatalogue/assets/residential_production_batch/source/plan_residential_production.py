"""One scalable standard/family production ledger, using the verified atlas crosswalk."""
from pathlib import Path
import json,hashlib,math,collections
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'inputs/REGULAR_500_SOURCE_CROSSWALK.json'
raw=SOURCE.read_bytes();cross=json.loads(raw)
old=json.loads((ROOT/'NEIGHBORHOOD_PLAN.json').read_text());known={r['census_source_index']:r for r in old['rooms']}
contract=json.loads((ROOT/'inputs/design_contract.json').read_text());floors={d['deck']:d['floor_elevation_m'] for d in contract['deck_datums']} if 'deck' in contract['deck_datums'][0] else {}
if not floors:
    for d in contract['deck_datums']:floors[d.get('id',d.get('deck_id'))]=d['floor_elevation_m']
def stable(key,v):return hashlib.sha256(('astraea-residential-production-v1|'+key+'|'+v).encode()).hexdigest()
rooms=[]
for r in cross['records']:
    index=r['source_envelope_index'];x0,x1=r['allocation_x'];z0,z1=r['allocation_z'];cx=(x0+x1)/2;cz=(z0+z1)/2
    door=r['historical_door_marker_xz'];entry_left=abs(door[0]-x0)<abs(door[0]-x1)
    origin=x0 if entry_left else x1;yaw=-math.pi/2 if entry_left else math.pi/2
    floor=floors.get(r['deck'],{'D13':84,'D14':88.5,'D16':97.5}[r['deck']])
    historical=r.get('historical_address');identity=r.get('existing_rebuild_identity') or ('D13-'+historical if historical in ['13017','13041'] else r['proposed_runtime_id'])
    address=historical or identity
    cls='family' if r['historical_class']=='family_triple' else 'standard'
    proposed_positions=[(-1.65,10.25,0),(1.65,10.25,0),(1.80,6.45,0)] if cls=='family' else [(-1.65,10.25,0),(1.65,10.25,0)]
    markers=r.get('historical_bed_anchor_markers',[]);anchors=[]
    if markers:
        for i,m in enumerate(markers):
            u=(m['z']-cz) if entry_left else -(m['z']-cz);v=(m['x']-origin) if entry_left else origin-m['x']
            anchors.append({'historical_anchor_index':i,'source_xyz':[round(u,4),round(v,4),0],'world_xyz':[m['x'],floor,m['z']],'evidence':'exact recovered atlas inset marker'})
    else:
        for i,(u,v,w) in enumerate(proposed_positions):
            anchors.append({'historical_anchor_index':i,'source_xyz':[u,v,w],'world_xyz':[origin+v if entry_left else origin-v,floor,cz+u if entry_left else cz-u],
                'evidence':'explicit proposed rest placement; count and allocation are historical, original coordinate unknown'})
    assert len(anchors)==r['rest_place_count']
    inward=(cx>0 and not entry_left) or (cx<0 and entry_left)
    view='real_atrium_candidate' if inward and 68<abs(cx)<85 and max(abs(z0),abs(z1))<64 else 'opaque_rear_no_verified_view'
    row={'address':address,'rebuild_identity':identity,'identity_status':'preserved installed rebuild ID' if historical in ['13017','13041'] else 'explicit new deterministic proposal; not recovered original save ID',
      'historical_address':historical,'deck':r['deck'],'house':r['house'],'census_source_index':index,'allocation_sha256':r['allocation_sha256'],
      'allocation_x':r['allocation_x'],'allocation_z':r['allocation_z'],'floor_y':floor,'source_origin_world_xyz':[origin,floor,cz],'source_yaw_godot':yaw,
      'historical_class':cls,'bed_anchors':anchors,'preserve_installed':historical in ['13017','13041'],'view_policy':view,
      'historical_door_marker_xz':door,'source_evidence':r['source_evidence'],'tier':'regular historical class; non-D17 production lane',
      'entry_persistent_id':('D13_'+historical+'_entry_door_A') if historical in ['13017','13041'] else identity+'__entry_A',
      'bath_persistent_id':('D13_'+historical+'_bath_door_A') if historical in ['13017','13041'] else identity+'__bath_A',
      'occupant_props_variant':int(stable(identity,'objects')[:8],16)%3,'handing':1,'finished':False}
    if index in known:
        k=known[index];row['layout']=k['layout'];row['palette']=k['palette'];row['occupant_props_variant']=k['occupant_props_variant']
    rooms.append(row)
byid={r['address']:r for r in rooms};assert len(byid)==500
neighbors={k:set() for k in byid};edges=[]
for i,a in enumerate(rooms):
    for b in rooms[i+1:]:
        if a['deck']!=b['deck']:continue
        ax,az=a['historical_door_marker_xz'];bx,bz=b['historical_door_marker_xz']
        if (abs(ax-bx)<.02 and abs(abs(az-bz)-7.4)<.02) or (abs(abs(ax-bx)-4)<.02 and abs(az-bz)<.02):
            edges.append([a['address'],b['address']]);neighbors[a['address']].add(b['address']);neighbors[b['address']].add(a['address'])
choices=['A_open_salon','B_twin_retreat','C_gathering_gallery'];assigned={r['address']:r['layout'] for r in rooms if 'layout'in r}
pending=set(byid)-set(assigned)
while pending:
    key=min(pending,key=lambda k:(-len({assigned[n] for n in neighbors[k] if n in assigned}),-len(neighbors[k]),k))
    forbidden={assigned[n] for n in neighbors[key] if n in assigned};legal=[v for v in choices if v not in forbidden];assert legal,key
    assigned[key]=min(legal,key=lambda v:stable(key,v));pending.remove(key)
for r in rooms:
    r['layout']=assigned[r['address']];r['palette']={'A_open_salon':'clay','B_twin_retreat':'teal','C_gathering_gallery':'oatmeal'}[r['layout']]
    # Prototypes share static architecture; unit identities/anchors stay in the
    # per-instance contract. Additional props are an independent bounded layer.
    anchor_geometry=sorted([a['source_xyz'] for a in r['bed_anchors']])
    anchor_key=hashlib.sha256(json.dumps(anchor_geometry,sort_keys=True).encode()).hexdigest()[:8]
    r['prototype_key']=r['historical_class']+'__'+r['layout']+'__'+('atrium' if r['view_policy']=='real_atrium_candidate' else 'opaque')+'__'+anchor_key
assert all(assigned[a]!=assigned[b] for a,b in edges)
groups=collections.defaultdict(list)
for r in rooms:
    if not r['preserve_installed']:groups[r['prototype_key']].append(r)
prototypes=[]
for key,group in sorted(groups.items()):
    # Choose one representative with canonical proposed source anchor ordering.
    eligible=sorted(group,key=lambda r:(not any(a['evidence'].startswith('exact') for a in r['bed_anchors']),r['address']))
    rep=dict(eligible[0]);rep['address']='PROTO__'+key;rep['instance_representative']=eligible[0]['address'];rep['prototype_instance_count']=len(group)
    # Prototype geometry uses canonical local anchors; exact instance anchor IDs
    # bind by spatial coordinates, never incidental node enumeration order.
    coords=sorted(a['source_xyz'] for a in rep['bed_anchors'])
    rep['bed_anchors']=[{'historical_anchor_index':i,'source_xyz':p,'world_xyz':p,'evidence':'prototype local position, instance binding in production ledger'}for i,p in enumerate(coords)]
    prototypes.append(rep)
schedule={'status':'source production plan; no Game registry or geometry adoption','rooms':rooms,'representative_sample_addresses':[p['address']for p in prototypes],
 'count':500,'new_source_placements':498,'preserved_installed':2,'historical_rest_places':1300,'counts':dict(collections.Counter(r['historical_class']for r in rooms)),
 'adjacency_edges':edges,'source_crosswalk_path':str(SOURCE),'source_crosswalk_sha256':hashlib.sha256(raw).hexdigest(),
 'full_ship_scope':{'total_guest_units':1000,'luxury_replacements':81,'remaining_other_units':919,'luxury_tiers':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},
 'lane_covered_here':'500 source-classified standard/family units on D13,D14,D16, including2installed units',
 'additional_lanes':{'specialty_allocations_D04_D13_D14_D15':400,'upper_D17_envelopes_with_unresolved_final_luxury_mapping':100},
 'admission_cap':2000,'crew_separate':400,'luxury_geometry_never_scaled_standard':True},
 'prototype_count':len(prototypes),'unit_count_delta':0,
 'views':'Interior/space views are part of district architecture. Current prototypes only open proven inward atrium candidates; unverified hull/court outlooks remain explicit pending interfaces.',
 'limits':['No final original save IDs inferred','New rest coordinates explicitly proposed where original marker absent','No source material or class count implies finished rooms','D17 luxury assignment remains distinct from unapproved proposal']}
(ROOT/'RESIDENTIAL_500_PLAN.json').write_text(json.dumps(schedule,indent=2)+'\n')
(ROOT/'PROTOTYPE_PLAN.json').write_text(json.dumps({'status':'shared source family prototypes for the500-unit lane','rooms':prototypes,'representative_sample_addresses':[p['address']for p in prototypes]},indent=2)+'\n')
(ROOT/'inputs/REGULAR_500_SOURCE_CROSSWALK.json').write_bytes(raw)
print(json.dumps({'units':500,'new':498,'classes':schedule['counts'],'prototypes':len(prototypes),'adjacency_edges':len(edges),'decks':dict(collections.Counter(r['deck']for r in rooms))}))
