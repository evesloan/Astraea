"""Author the central public core in the existing ship; preserve all other owners."""
from pathlib import Path
import json
from shapely.geometry import box,Polygon
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
owner='primary_atrium_core';layout=json.loads((R/'data/spatial_layout.json').read_text());contract=json.loads((R/'data/design_contract.json').read_text());levels=[d['floor_elevation_m']for d in contract['deck_datums']]
foot=box(-7.8,-113,7.8,-80);lift=box(-1.82,-108.02,1.82,-103.98);stair=box(-3.1,-96,3.1,-85.3)
records=json.loads((R/'data/reference/directory_allocations.json').read_text())['records']+json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']+json.loads((R/'data/reference/D03_crew_envelopes.json').read_text())['records']
assert all(foot.intersection(box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])).area<1e-6 for r in records)
assert Polygon(json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m']).covers(foot)
assert all(foot.intersection(Polygon(v['boundary'])).area<1e-6 for v in layout['voids']if v.get('authoring_owner')!=owner)
def ring(p):return[list(q)for q in p.exterior.coords[:-1]]
layout['regions']=[r for r in layout['regions']if r.get('authoring_owner')!=owner]
for i in range(18):layout['regions'].append({'id':f'D{i+1:02}_primary_atrium_core_floor','authoring_owner':owner,'deck':f'D{i+1:02}','boundary':ring(foot),'holes':[],'priority':80,'thickness':.24,'material_role':'guest_floor','status':'Central public lift/stair platform under validation; no final art or complete ship claim'})
layout['voids']=[v for v in layout['voids']if v.get('authoring_owner')!=owner]
layout['voids'] += [{'id':owner+'_lift','authoring_owner':owner,'decks':[f'D{i:02}'for i in range(1,19)],'boundary':ring(lift),'source':'Physical3.6x4m cabin clearance; fitted pit pan remains withinD01 slab thickness'}, {'id':owner+'_stairs','authoring_owner':owner,'decks':[f'D{i:02}'for i in range(2,19)],'boundary':ring(stair),'source':'Real stacked switchbacks; D01base floor retained; exposed edges guarded'}]
D={'id':owner,'core_reservation':'atrium_threshold_vertical_core','status':'Authored source under construction and validation','origin':[0,0,-100],'floor_y':levels,'floor_boundary':ring(foot),'lift_opening':ring(lift),'stair_opening':ring(stair),'lift':{'gate_origin_xz':[-1.8,-106],'shaft_outer_x':[-2,2],'shaft_outer_z':[-108.2,-103.8],'pit_pan_y':[-.24,-.20],'cap_y':[109.73,109.85],'cabin_file':'AST-CIR-003_eighteen_stop.glb'},'stairs':[{'base_y':levels[i],'top_y':levels[i+1],'rise':levels[i+1]-levels[i],'origin':[3,levels[i],-96],'yaw_pi':True,'file':{4.5:'AST-CIR-001_H450.glb',6:'AST-CIR-001_H600.glb',8.5:'AST-CIR-001.glb'}[levels[i+1]-levels[i]]}for i in range(17)],'scope':'One central public core; other public cores, all staff risers, hull exterior and full destination routes remain unfinished','minimum_cabin_top_y':109.44,'hull_clearance_status':'Inside nominal118m reference height, but finished height-dependent hull remains unaccepted'}
(R/'data/architecture/PRIMARY_ATRIUM_CORE.json').write_text(json.dumps(D,indent=2)+'\n');(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
b=C/'assets/primary_atrium_core';(b/'source').mkdir(parents=True,exist_ok=True);(b/'exports').mkdir(exist_ok=True);(b/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
print('Central18-deck floor/shaft/stair contract authored; physical and visual acceptance pending')
