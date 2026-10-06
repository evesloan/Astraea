"""Deterministic, allocation-bound D13 candidate plan. No Game/Catalogue writes."""
from pathlib import Path
import json, hashlib, math
ROOT = Path(__file__).resolve().parents[1]
def write(name, obj):
    (ROOT/name).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
def rank(key, value):
    return hashlib.sha256(('astraea-d13-starboard-v1|'+key+'|'+value).encode()).hexdigest()
evidence = json.loads((ROOT/'inputs/D13_named_residential_evidence.json').read_text())
census = json.loads((ROOT/'inputs/historical_guest_census.json').read_text())['guest_envelopes']
rooms = []
for r in evidence['records']:
    address = r['historical_address']; inner = r['allocation_x'][0] < 80
    center_z = sum(r['allocation_z'])/2
    source_index = next(i for i,e in enumerate(census) if e['deck']==13 and e['x']==r['allocation_x'] and e['z']==r['allocation_z'])
    origin_x = r['allocation_x'][1] if inner else r['allocation_x'][0]
    yaw = math.pi/2 if inner else -math.pi/2
    local_beds=[]
    for k,m in enumerate(m for m in r['markers'] if m['kind']=='bed_anchor'):
        u = -(m['z']-center_z) if inner else m['z']-center_z
        v = origin_x-m['x'] if inner else m['x']-origin_x
        local_beds.append({'historical_anchor_index':k,'source_xyz':[round(u,4),round(v,4),0], 'world_xyz':[m['x'],84,m['z']]})
    rooms.append({'address':address,'rebuild_identity':'D13-'+address,'original_save_identity':None,
      'historical_class':r['historical_class'],'census_source_index':source_index,'allocation_x':r['allocation_x'],
      'allocation_z':r['allocation_z'],'floor_y':84,'source_origin_world_xyz':[origin_x,84,center_z],
      'source_yaw_godot':yaw,'bank':'inner' if inner else 'outer','branch':'north' if center_z<0 else 'south',
      'row':round((abs(center_z)-42)/7.4),'historical_markers':r['markers'],'bed_anchors':local_beds,
      'preserve_installed':address in ['13017','13041'],
      'view_policy':'real_atrium_candidate' if inner and max(abs(z) for z in r['allocation_z'])<64 else 'opaque_rear_no_verified_view',
      'tier':'historical_non_luxury_pending_global_reconciliation',
      'entry_persistent_id':'D13_'+address+'_entry_door_A','bath_persistent_id':'D13_'+address+'_bath_door_A'})
by_id={r['address']:r for r in rooms}
edges=[]
for i,a in enumerate(rooms):
    for b in rooms[i+1:]:
        if a['branch']==b['branch'] and ((a['row']==b['row'] and a['bank']!=b['bank']) or
           (a['bank']==b['bank'] and abs(a['row']-b['row'])==1)):
            edges.append([a['address'],b['address']])
neighbors={a:set() for a in by_id}
for a,b in edges:neighbors[a].add(b);neighbors[b].add(a)
fixed={'13017':'A_open_salon','13041':'B_twin_retreat'}
assigned=dict(fixed)
# Constrained graph coloring uses stable identities, never random() or array order.
def assign(group, choices):
    pending=set(group)-set(assigned)
    def visit():
        if not pending:return True
        key=min(pending,key=lambda k:(-len({assigned[n] for n in neighbors[k] if n in assigned}),-len(neighbors[k]),k))
        forbidden={assigned[n] for n in neighbors[key] if n in assigned}
        for v in sorted(choices,key=lambda v:rank(key,v)):
            if v in forbidden:continue
            assigned[key]=v;pending.remove(key)
            if visit():return True
            pending.add(key);del assigned[key]
        return False
    assert visit(), 'No legal assignment: keep constraints and author another compatible profile.'
assign([r['address'] for r in rooms if r['historical_class']=='standard'],['A_open_salon','B_twin_retreat','C_gathering_gallery'])
assign([r['address'] for r in rooms if r['historical_class']=='specialty'],['S_acoustic_cove','T_quiet_gallery'])
palette_map={'A_open_salon':'clay','B_twin_retreat':'teal','C_gathering_gallery':'oatmeal','S_acoustic_cove':'teal','T_quiet_gallery':'clay'}
for r in rooms:
    r['layout']=assigned[r['address']];r['palette']=palette_map[r['layout']]
    # Handing is constrained independently from the room's world-facing bank.
    r['handing']=1 if int(rank(r['address'],'handing')[:8],16)%2==0 else -1
    r['occupant_props_variant']=int(rank(r['address'],'objects')[:8],16)%3
    r['species_support']={'mandatory_canon':'quiet cocoon' if r['historical_class']=='specialty' else 'ordinary dry accommodation',
      'source':'v0.3 ch4 D13 quiet-cocoon neighborhoods; ch6 and ch8; current design_contract.species',
      'species_allocation':None,'final_body_fit_verified':False,'mindo_charging_invented':False,
      'aquatic_support_claimed':False,'limits':['No approved body dimensions or sleeping pose','No functional molt-care system'] if r['historical_class']=='specialty' else ['No universal species-fit claim']}
    if r['preserve_installed']:
        r['source_model']='AST-SUI-001.glb' if r['address']=='13017' else 'AST-SUI-002.glb'
        r['action']='preserve existing assembly and persistent IDs byte-for-byte'
    else:r['action']='scratch candidate; review before adoption'
samples=[]
for layout in ['A_open_salon','B_twin_retreat','C_gathering_gallery','S_acoustic_cove','T_quiet_gallery']:
    candidates=[r for r in rooms if r['layout']==layout and not r['preserve_installed']]
    # Prefer the verified atrium band for A and closed-back outboard examples for B/C.
    candidates.sort(key=lambda r:(r['branch']!='north',(r['bank']!='inner') if layout=='A_open_salon' else (r['bank']!='outer'),r['address']))
    samples.append(candidates[0]['address'])
assert len(rooms)==26 and len({r['census_source_index'] for r in rooms})==26
assert sum(len(r['bed_anchors']) for r in rooms)==42
assert all(assigned[a]!=assigned[b] for a,b in edges)
assert {r['layout'] for r in rooms if r['historical_class']=='standard'}=={'A_open_salon','B_twin_retreat','C_gathering_gallery'}
plan={'schema':'astraea.d13.neighborhood_candidate.v1','status':'source candidate, not installed or accepted',
 'room_count':26,'preserved_installed_count':2,'new_candidate_count':24,'historical_bed_anchor_count':42,
 'unit_count_delta':0,'admission_limit':2000,'ship_guest_unit_total':1000,'rooms':rooms,'adjacency_edges':edges,
 'representative_sample_addresses':samples,'fixed_existing':fixed,
 'circulation':{'existing_street_x':[81.95,86.05],'datum_y':84,'required_north_extent_z':[-90,-26],
 'required_south_extent_z':[14,90],'commons_programme':'D13_directory_05','existing_north_connection_z':[-26,-14],
 'policy':'Keep installed support/void geometry exact. New support only as additive authored regions after contact/ownership review. One shared corridor ceiling/runner per paired row; never instantiate one per facing room.',
 'unbuilt_dependencies':['Extend north street past z=-53','Author supported south street and commons threshold','Fit street ends and transitions without guest-envelope overlap','Reconcile all additions against current compiled floor/void ownership']},
 'global_protection':{'luxury_units':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'luxury_replaces_existing_units':True,
 'luxury_local_assignment_changed':False,'species':['Koblins','Mantelids','Humans','Baelins','Munkos','Mindos'],
 'original_persistent_ids_not_recovered':True,'engine':'Godot 4.6.3 Compatibility','new_engine_job':False},
 'recovery_evidence':{'implementation_source_recovered':False,'method_from_historical_reports':'Three authored standard/family layouts with neighbor anti-repetition, coordinated walls/ceilings/floor/entry/privacy; enclosed sliding pockets.',
 'historical_report_ids':['Sentinel_1926444a0e3c8191b709c064ed9d66f0','Sentinel_0ec7475de6dc8191b26563f09792bc29','Sentinel_88b93f878304819185fc35a3fdb9bfce'],
 'limit':'Reports establish the prior approach, not the old generator bytes or current acceptance.'}}
write('NEIGHBORHOOD_PLAN.json',plan)
write('qa/PLAN_CHECKS.json',{'status':'PASS_READ_ONLY_PLANNING','rooms':26,'anchors':42,'adjacency_edges':len(edges),
 'distinct_standard_layouts':3,'distinct_specialty_layouts':2,'existing_assemblies_pinned':fixed,'sample_addresses':samples,
 'runtime_checks_run':False,'game_or_catalogue_writes':False})
print(json.dumps({'room_count':26,'anchors':42,'samples':samples,'assignments':[(r['address'],r['layout'],r['view_policy']) for r in rooms]}))
