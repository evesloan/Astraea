"""Check the rebuilt terrace geometry and reserved service-tram support footprint."""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
root=Path(__file__).resolve().parents[1];mesh=json.loads((root/'data/generated/structural_meshes.json').read_text());contours=json.loads((root/'data/reference/atrium_contours.json').read_text())
route=LineString([(0,-72),(0,-56),(40,-52),(40,52),(0,56),(0,72)]).buffer(2,cap_style=2,join_style=2)
results=[]
for c in contours['decks']:
 regions=[r for r in mesh['regions'] if r['deck']==c['deck']]
 floors=unary_union([Polygon(t) for r in regions for t in r['triangles']])
 missing=route.difference(floors).area
 assert missing<.01,(c['deck'],missing)
 inner=Polygon(c['inner'])
 intrusion=floors.intersection(inner.buffer(-.01)).area
 assert intrusion<.01,(c['deck'],'clear opening filled',intrusion)
 results.append({'deck':c['deck'],'four_metre_route_support_missing_m2':round(missing,6),'clear_opening_intrusion_m2':round(intrusion,6)})
assert len(results)==16
out={'checks':results,'scope':'Continuous four-metre-wide structural support reservation only; no actual tram, loaded-cart dynamics, boarding, furnishing clearance or final architectural acceptance.'}
(root/'docs/ATRIUM_ROUTE_SUPPORT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS:16 terrace levels support the four-metre route reservation and keep their actual inner openings clear')
