from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union,triangulate
W=Path(__file__).resolve().parent;R=W.parents[3]
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());assert 'AST-TRM-G4-027' not in json.dumps(cat)
regions=[];pins={}
for n in ['structural_meshes.json','received_structural_meshes.json']:
 p=R/'Game/data/generated'/n;regions+=json.loads(p.read_text())['regions'];pins[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
floor=unary_union([Polygon(t) for q in regions if q['floor_y']==52.5 for t in q['triangles']])
rows=[]
for label,key,z,owner,room_id in [('PaperMoon','D09_directory_03',-216,'D09_papermoon_books_connection_0','D09_books2'),('PostParcels','D09_directory_07',216,'D09_post_parcels_connection_0','D09_parcel6')]:
 strips=[]
 for rect in [[-8,z-2.5,-4,z-2],[-8,z+2,-4,z+2.5]]:
  shape=box(*rect).difference(floor);ts=[]
  for p in list(shape.geoms) if hasattr(shape,'geoms') else [shape]:
   for t in triangulate(p):
    if t.difference(p).area<1e-8:ts.append([list(v) for v in list(t.exterior.coords)[:-1]])
  assert abs(sum(Polygon(t).area for t in ts)-shape.area)<1e-8
  strips.append({'bounds_xz':rect,'triangles_xz':ts,'new_only_area_m2':shape.area})
 rows.append({'label':label,'programme_key':key,'retained_room_id':room_id,'existing_floor_owner':owner,'center_z':z,
   'existing_clear_route_xz':[-8,z-2,-4,z+2],'retained_clear_width_m':4.0,'new_floor_strips':strips,
   'source_lanterns':[{'name':label+'_TerminalLantern_'+str(i),'origin':[x,54.62,z-2.43],'yaw':0.0} for i,x in enumerate([-7.4,-4.6])],
   'arrival_and_portal_unchanged':True,'route_from_axis_xyz':[-3,52.5,z],'original_portal_xyz':[-8,52.5,z]})
source=R/'BlenderCatalogue/assets/hospitality_lantern/source/AST-LGT-001.blend';pins[str(source.relative_to(R))]=hashlib.sha256(source.read_bytes()).hexdigest()
plan={'schema':'astraea.group4.terminal_edge_construction.v1','active':False,'asset':'AST-TRM-G4-027_terminal_branch_edges_r001.glb','native':'Group4_Terminal_Branch_Edges_r001.blend','terminals':rows,'source_lantern_native':str(source.relative_to(R)),'source_pins':pins,'new_floor_area_m2':sum(s['new_only_area_m2'] for r in rows for s in r['new_floor_strips']),'protected_existing_routes_unchanged':True,'new_capacity_or_room_ids':False,'limits':'Two existing terminal branches only. Existing floor/room/source retained; additive outboard ledges/guards and exact rigid source lanterns. No stock, provider or blanket161-destination acceptance.'}
(W/'TERMINAL_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('TERMINALS_PLANNED',len(rows),'branches;',plan['new_floor_area_m2'],'m2 missing-only outboard ledges')
