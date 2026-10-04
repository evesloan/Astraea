"""Apply reviewed aquatic shaft cuts without changing programme or slab ownership."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box,LineString
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'data/architecture/D08_D10_aquatic_access.json').read_text())
p=R/'data/spatial_layout.json';layout=json.loads(p.read_text());owner=D['id']
h=D['floor_hole_xz'];cut=box(h['x'][0],h['z'][0],h['x'][1],h['z'][1])
guests=json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
voids=[]
for deck,label in [(8,'gentle_waters'),(9,'living_gifts'),(10,'vesper')]:
 key=f'D{deck:02}'
 region=next(v for v in layout['regions'] if v['id']==key+'_'+label+'_floor')
 assert region['thickness']==.4 and region['priority']==20
 shape=Polygon(region['boundary'],region.get('holes',[]))
 assert shape.covers(cut),('Shaft no longer contained in destination',key)
 for guest in guests:
  if guest['deck']==deck:assert cut.intersection(box(guest['x'][0],guest['z'][0],guest['x'][1],guest['z'][1])).area<1e-8
 route=D['route_reservations'][0];strip=LineString(route['centerline_xz']).buffer(route['half_width_m'],cap_style=2,join_style=2)
 assert shape.difference(cut).buffer(1e-7).covers(strip),(key,'bypass leaves usable destination floor')
 voids.append({'id':f'aquatic_lift_{key}','authoring_owner':owner,'decks':[key],'boundary':[list(v) for v in cut.exterior.coords[:-1]],'source':'Reviewed aquatic lift with sealed D08 pit; no other programme cut'})
layout['voids']=[v for v in layout['voids'] if v.get('authoring_owner')!=owner]+voids
p.write_text(json.dumps(layout,indent=2)+'\n')
print(json.dumps({'shaft_cuts':len(voids),'each_area_m2':cut.area,'guest_conflicts':0,'slab_thickness_and_priority_preserved':True,'D11_cover_constructed':False}))
