"""Quick floor bearing checks for representative built foundations, not an exhaustive route audit."""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(R.parent/'AstraeaTools/pythondeps'))
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
D=json.loads((P/'docs/AQUATIC_CONSTRUCTION_PLAN.json').read_text());S=json.loads((P/'qa/source_geometry.json').read_text())
floors={}
for q in D['floor_records']:
 g=unary_union([Polygon(a['boundary'],a['holes']) for a in q['boundary_polygons_xz']]);floors.setdefault(q['top_y'],[]).append(g)
floors={y:unary_union(g) for y,g in floors.items()}
floors[42.8]=Polygon(json.loads((P/'dependencies/Game/data/aquatic_section.json').read_text())['basin']['boundary'])
shoulder=box(21,214.3,23,215.7)
rows=[]
patterns=['bearing_foot_','tube_rack_foot','river_lounge_base_','clean_towels_carcass','dirty_return_carcass','refreshments_cove','wet_service_cabinet','privacy_bench_support_','fixed_seat_mount_','island_planter_','planted_bank_','hoist_anchor','entry_grab_anchor','cascade_shoulder_bearing_','cascade_hood_post']
for n,q in S.items():
 if not any(a in n for a in patterns):continue
 y=42.8 if 'cascade_shoulder_bearing' in n else 44.0 if 'bearing_foot_' in n or 'cascade_hood_post' in n else 44.3 if 'entry_grab_anchor' in n else 45.45
 foot=MultiPoint([(a[0],a[2]) for a in q['world_vertices_xyz'] if abs(a[1]-q['bounds_min'][1])<1e-4]).convex_hull
 g=shoulder if 'cascade_hood_post' in n else floors[y]
 error=abs(q['bounds_min'][1]-y);covered=g.buffer(.001).covers(foot)
 rows.append({'part':n,'bearing_top_y':y,'as_built_bottom_y':q['bounds_min'][1],'vertical_error_m':error,'bearing_footprint_covered':covered,'pass':error<.001 and covered})
assert len(rows)>30
report={'passed':all(q['pass'] for q in rows),'sampled_foundations':len(rows),'contacts':rows,'scope':'Selected bearing/fit-out bottom-contact footprints against delivered floors and retained basin data. Broad routes, loads, body/ride physics and entire ship deferred.'}
(P/'qa/support_contact_checks.json').write_text(json.dumps(report,indent=2));print('Foundation contacts:',len(rows),'passed:',report['passed']);assert report['passed'],[q for q in rows if not q['pass']]
