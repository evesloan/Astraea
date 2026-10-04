"""Author the reviewed D11 cover with explicit Cinema5 ownership; no new room."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1];p=R/'data/spatial_layout.json';d=json.loads(p.read_text());owner='aquatic_D11_cover'
outer=box(8,182,54,250);cinema=box(11,244,54,250);rest=outer.difference(cinema)
allocations=json.load(open(R/'data/reference/directory_allocations.json'))['records'];record=next(v for v in allocations if v['programme_key']=='D11_directory_06')
assert box(record['x'][0],record['z'][0],record['x'][1],record['z'][1]).intersection(outer).equals(cinema)
for v in d['voids']:
 if 'D11' in v['decks']:assert outer.intersection(Polygon(v['boundary'])).area<1e-8
for region in d['regions']:
 if region['deck']=='D11' and region.get('authoring_owner')!=owner:assert outer.intersection(Polygon(region['boundary'],region.get('holes',[]))).area<1e-8
for guest in json.load(open(R/'data/reference/historical_guest_census.json'))['guest_envelopes']:
 if guest['deck']==11:assert outer.intersection(box(guest['x'][0],guest['z'][0],guest['x'][1],guest['z'][1])).area<1e-8
regions=[]
for name,g,programme in [('cinema_interface',cinema,'D11_directory_06'),('hall_cover',rest,None)]:
 regions.append({'id':'D11_aquatic_'+name,'authoring_owner':owner,'deck':'D11','boundary':[list(v)for v in g.exterior.coords[:-1]],'holes':[],'priority':-10,'thickness':.4,'material_role':'guest_floor','walkable_public':False,'protected_programme_key':programme,'status':'Structural cover/substrate only; no new D11 destination, capacity, route or lift stop'})
d['regions']=[r for r in d['regions']if r.get('authoring_owner')!=owner]+regions;p.write_text(json.dumps(d,indent=2)+'\n');print({'cover_m2':outer.area,'protected_cinema_substrate_m2':cinema.area,'remaining_m2':rest.area,'top_y':69.5,'underside_y':69.1})
