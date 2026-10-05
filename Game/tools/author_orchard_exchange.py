from pathlib import Path
import json
from shapely.geometry import box,Polygon
R=Path(__file__).resolve().parents[1]
layout=json.load(open(R/'data/spatial_layout.json'))
foot=box(4,-250,24,-233)
stair=box(7.9,-248.1,14.1,-237.45)
lift=box(18.28,-243.52,21.92,-239.48)
allocation=box(8,-250,54,-182)
assert foot.difference(allocation).difference(box(4,-250,8,-182)).area<1e-8
assert Polygon(json.load(open(R/'data/hull_envelope.json'))['plan_xz_m']).covers(foot)
for room in json.load(open(R/'data/reference/historical_guest_census.json'))['guest_envelopes']:
 if room['deck']in [8,9,10,11]:assert foot.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<1e-8
for deck in ['D09','D10']:
 print(deck,[(r['id'],round(foot.intersection(Polygon(r['boundary'],r.get('holes',[]))).area,3)) for r in layout['regions']if r.get('deck')==deck and foot.intersection(Polygon(r['boundary'],r.get('holes',[]))).area>1e-8])
print({'court_footprint_m2':foot.area,'upper_clear_m2':foot.difference(stair.union(lift)).area,'stair_rise_m':8.5,'existing_stair_model':'AST-CIR-001','lower_y':52.5,'upper_y':61,'roof_max_y':69.24,'D11_underside_protected_y':69.26,'guest_envelope_overlaps':0,'status':'Geometric study only; no source edited'})
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');owner='orchard_exchange'
def ring(poly):return[list(p)for p in poly.exterior.coords[:-1]]
layout['regions']=[r for r in layout['regions']if r.get('authoring_owner')!=owner]
for deck,y in [('D09',52.5),('D10',61)]:
 layout['regions'].append({'id':deck+'_orchard_exchange_floor','authoring_owner':owner,'deck':deck,'boundary':ring(foot),'holes':[],'priority':70,'thickness':.24,'programme_owner':'D09_tailor3'if deck=='D09'else'D10_banquet3','status':'Shared local arrival court under construction; destination capacity and access pending'})
layout['voids']=[v for v in layout['voids']if v.get('authoring_owner')!=owner]
layout['voids'] += [{'id':'orchard_exchange_stair','authoring_owner':owner,'decks':['D10'],'boundary':ring(stair),'source':'Local8.5m two-flight connection, no canonical datum movement'}, {'id':'orchard_exchange_lift','authoring_owner':owner,'decks':['D09','D10'],'boundary':ring(lift),'source':'Actual local lift; D09 pit remains within slab thickness'}]
D={'id':owner,'status':'Local shared arrival court under construction, no completed food hall or occupied capacity claim','programme_keys':['D09_directory_04','D10_directory_04'],'historical_room_ids':['D09_tailor3','D10_banquet3'],'origin':[4,52.5,-250],'floor_y':[52.5,61],'boundary':ring(foot),'stair_opening':ring(stair),'lift_opening':ring(lift),'stair':{'file':'AST-CIR-001.glb','origin':[8,52.5,-237.5],'rise_m':8.5,'flight_width_m':2.5,'risers':50,'midlanding_y':56.75},'lift':{'origin_xz':[18.3,-241.5],'floor_heights':[52.5,61],'deck_numbers':[9,10],'staging_xz':[15.8,-241.5],'shaft_outer_xz':{'x':[18.12,22.12],'z':[-243.66,-239.34]},'pit_pan_y':[52.26,52.30],'cap_y':[64.23,64.35]},'roof_y':[69.1,69.24],'protected_below_y':52.26,'protected_above_y':69.26,'columns':[[5.45,-248.4],[22.48,-248.4]],'structural_changes':['Add340m2 shared court floors onD09/D10,31.25m2 overlap resolved by explicit ownership priority','CutD10 only for stairs; lift pit constrained toD09 slab','Remove obsoleteD09 north apron rail where the new floor joins','No deck elevations, guest envelopes, cinema allocation or dining capacity altered'],'next_destination':'Orchard food hall remains reserved240places, not fitted or populated'}
(R/'data/architecture/D09_D10_orchard_exchange.json').write_text(json.dumps(D,indent=2)+'\n')
(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
b=C/'assets/orchard_exchange';(b/'source').mkdir(parents=True,exist_ok=True);(b/'exports').mkdir(exist_ok=True);(b/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
print('Authored existing-project floor/section contract; geometry and runtime validation remain pending')
