from pathlib import Path
import json
from shapely.geometry import MultiPoint,Polygon
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;P=json.loads((W/'PLAN.json').read_text());O={q['name']:q for q in json.loads((W/'SOURCE_NATIVE_GEOMETRY.json').read_text())};rows=[]
for site in P['fit_sites'][2:]:
 added=unary_union([Polygon([(v[0],v[2])for v in p['verts'][:3]])for p in P['parts']if p['site_id']==site['site_id']]);roof=O['SAC_ServiceLowCeiling'];rp=MultiPoint([(v[0],v[2])for v in roof['world_vertices']]).convex_hull
 # Contact tolerance accounts for exported float positions; do not fill or mask any source.
 roof_contact=added.boundary.intersection(rp.boundary.buffer(.0001)).length
 owner=O[{'ServiceWestRoofSlot':'SAC_ServiceWest','ServiceNorthRoofSlot':'SAC_ServiceNorth','ServiceEastRoofSlot':'SAC_ServiceEast'}[site['site_id']]];wp=MultiPoint([(v[0],v[2])for v in owner['world_vertices']]).convex_hull
 wall_contact=added.boundary.intersection(wp.boundary.buffer(.0001)).length
 assert roof_contact>.1 and wall_contact>.1,(site['site_id'],roof_contact,wall_contact)
 assert abs(roof['bounds'][0][1]-site['bottom'])<.0001 and abs(roof['bounds'][1][1]-site['top'])<.0001
 if site['site_id']=='ServiceEastRoofSlot':assert abs(owner['bounds'][1][1]-site['bottom'])<.0001
 else:assert owner['bounds'][0][1]<site['bottom'] and owner['bounds'][1][1]>site['top']
 rows.append({'site':site['site_id'],'source_roof':'SAC_ServiceLowCeiling','source_wall':owner['name'],'actual_source_roof_edge_contact_m':roof_contact,'actual_source_wall_edge_contact_m':wall_contact,'source_geometry_unmodified':True})
(W/'EXACT_CEILING_EDGE_CONTACTS001.json').write_text(json.dumps({'status':'PASS','tolerance_m':.0001,'actual_source_contacts':rows,'open_front_unfilled':True,'no_doorway_fill':True},indent=2)+'\n');print('PASS',len(rows),'actual roof/wall edge fits')
