"""Fit a two-level public crown connection; wider crown remains a proposal."""
from pathlib import Path
import json
from shapely.geometry import box, Polygon
R=Path(__file__).resolve().parents[1]
owner='aft_crown_link'
layout=json.loads((R/'data/spatial_layout.json').read_text())
levels=[d['floor_elevation_m']for d in json.loads((R/'data/design_contract.json').read_text())['deck_datums']]
assert levels[16:]==[102,106.5]
foot=box(-7.8,106,7.8,139);lift=box(-1.82,110.98,1.82,115.02);stair=box(-3.1,123,3.1,133.7)
records=json.loads((R/'data/reference/directory_allocations.json').read_text())['records']+json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
# Preserve every existing allocation; proposals do not redefine actual rooms.
for record in records:
 assert foot.intersection(box(record['x'][0],record['z'][0],record['x'][1],record['z'][1])).area<1e-6,record
assert Polygon(json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m']).covers(foot)
assert all(foot.intersection(Polygon(v['boundary'])).area<1e-6 for v in layout['voids'] if v.get('authoring_owner')!=owner)
def ring(p):return [list(q)for q in p.exterior.coords[:-1]]
layout['regions']=[r for r in layout['regions'] if r.get('authoring_owner')!=owner]
for deck in ['D17','D18']:
 layout['regions'].append({'id':deck+'_aft_crown_link_floor','authoring_owner':owner,'deck':deck,'boundary':ring(foot),'holes':[],'priority':80,'thickness':.24,'material_role':'guest_floor','status':'Two-level public connection; broader crown and luxury rooms remain proposals'})
layout['voids']=[v for v in layout['voids'] if v.get('authoring_owner')!=owner]
layout['voids'] += [{'id':owner+'_lift','authoring_owner':owner,'decks':['D17','D18'],'boundary':ring(lift),'source':'Two-level physical lift with supported lower pit pan'}, {'id':owner+'_stairs','authoring_owner':owner,'decks':['D18'],'boundary':ring(stair),'source':'4.5m switchback; lower base retained'}]
d={'id':owner,'status':'Reconstructed source pending fresh runtime and visual acceptance','origin':[0,102,119],'root_name':'AftCrownLink_WIP','persistent_id':'aft_crown_link_001','enclosure_file':'AST-CIR-005_upper_link.glb','floor_y':[102,106.5],'deck_numbers':[17,18],'floor_boundary':ring(foot),'lift_opening':ring(lift),'stair_opening':ring(stair),'lift':{'name':'AftCrownLift','identity_prefix':'aft_crown','district_label':'Crown link','gate_origin_xz':[-1.8,113],'cap_y':[109.73,109.85],'cabin_file':'AST-CIR-003.glb'},'stairs':[{'base_y':102,'top_y':106.5,'rise':4.5,'origin':[3,102,123],'yaw_pi':True,'file':'AST-CIR-001_H450.glb'}],'scope':'Local D17/D18 connection only; no new guest units, rooms or adopted crown allocation'}
(R/'data/architecture/AFT_CROWN_LINK.json').write_text(json.dumps(d,indent=2)+'\n')
(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print('Authored two-level link, no other floor owners replaced')
