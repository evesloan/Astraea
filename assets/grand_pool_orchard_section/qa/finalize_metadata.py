"""Finalize non-geometric handoff metadata BEFORE the last verification run."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=R/'source/connected_contract.json';D=json.loads(p.read_text())
D['status']='Editable connected source construction; runtime adoption and full programme completion pending'
D['section']['note']='Source-authored section fits protected datums with explicit retained-keel contacts and transfer depths. This is geometric game architecture, not real-world load, drainage, waterproofing or accessibility certification.'
D['accessible_ramp']['status']='Source-authored ramp and guards; runtime controller, loaded-cart comfort and species acceptance pending'
D['wet_market_link']['status']='Source-authored 6.3m CIR001 stair derivative and fitted two-stop enclosure; existing-controller integration pending'
D['wet_market_link']['environmental_boundary']['status']='Full-height glazed source boundary, sealed headers/cassette edges, real retained doorway fitting previews; runtime door instances pending'
D['staff']['status']='Upper source shaft/cap and enclosed service routes authored in AST-STF-009 derivative; preserve lower identities, pending runtime integration'
D['staff']['adopted_screen_reason']='Original planning screen did not block all open-aperture corner rays. New bounded baffle passes1444 source rays; retained532 changing-position/heading cart/operator proxy poses are in QA, not force-driven acceptance.'
D['staff']['route_pose_evidence']='qa/plan_route_verification.json / screened_cart_proxy.route_poses'
D['integration_transforms']={'AST-AQU-016':{'position_world':[0,0,0],'rotation_y':0,'scale':[1,1,1],'operation':'new assembly'},'AST-CIR-005_forward_pool_market':{'position_world':[0,0,-432],'rotation_y':0,'scale':[1,1,1],'operation':'replace only forward_public_core_001 original forward_core representation'},'AST-STF-009_pool_market':{'position_world':[0,0,0],'rotation_y':0,'scale':[1,1,1],'operation':'replace lower staff network visual; do not duplicate it'}}
D['environmental_door_infill']={'existing_family':'AST-DOR-002_wide','clear_width_m':2.4,'leaf_opening_height_m':2.5,'cassette_outer_pocket_width_m':5.12,'header_width_m':5.16,'header_top_above_floor_m':2.66,'side_seal_strips_local_x':[[-2.58,-2.56],[2.56,2.58]],'source_ownership':'Static seal strips/transoms belong to AST-AQU-016; existing articulated door remains separate runtime family','public_core_portals':'Open6m-wide3.2m-high connections, no closure or fake transom'}
D['new_geometry_ownership']={'one_new_unique_family':'AST-AQU-016 / grand_pool_orchard_section','core_derivative':'AST-CIR-005_forward_pool_market, same AST-CIR-005 owner','staff_derivative':'AST-STF-009_pool_market, same AST-STF-009 owner','embedded_stair_derivative':'AST-CIR-001_H630_GPM, not a new unique design','compiler_floors_exported':False,'water_exported':False,'dynamic_door_previews_exported':False}
for n in['assets/guest_entry_door/source/AST-DOR-002_wide.blend','assets/guest_entry_door/exports/AST-DOR-002_wide.glb','assets/commons_lift_cabin/source/AST-CIR-003_five_stop.blend','assets/telescoping_gate/source/AST-DOR-003.blend']:
 D['preserved_catalogue_inputs'][n]=sha(C/n)
p.write_text(json.dumps(D,indent=2)+'\n')
print('Final contract metadata',sha(p))
