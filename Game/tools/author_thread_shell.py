"""Author a bounded part of the existing Thread & Shell allocation, with real routes."""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');owner='thread_shell'
outer=Polygon([(8,-224),(10,-232),(20,-236),(30,-236),(37,-230),(39,-222),(39,-206),(34,-200),(24,-198),(12,-201),(8,-208)])
public_arrival=box(4,-234,12,-198)
service=box(37,-234,43,-197)
service_arrival=LineString([(4,-194.5),(40,-194.5),(40,-200)]).buffer(1.6,cap_style='flat',join_style='mitre').union(box(37.5,-198,43,-192))
footprint=unary_union([outer,public_arrival,service,service_arrival]);assert footprint.is_valid and footprint.geom_type=='Polygon'
allocation=box(8,-250,54,-182);outside=footprint.difference(allocation)
assert outside.difference(box(4,-250,8,-182)).area<1e-8,'Only explicit spine-to-allocation approach may leave the business envelope'
hull=Polygon(json.load(open(R/'data/hull_envelope.json'))['plan_xz_m']);assert hull.covers(footprint)
for room in json.load(open(R/'data/reference/historical_guest_census.json'))['guest_envelopes']:
 if room['deck'] in [8,9,10]:assert footprint.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<1e-8
boundary=[list(v)for v in footprint.exterior.coords[:-1]];tri=constrained_delaunay_triangles(footprint)
columns=[[13,-226],[13,-206],[26,-230],[26,-216],[26,-202]]
for x,z in columns:assert outer.covers(__import__('shapely').geometry.Point(x,z).buffer(1.33))
D={'id':'D09_thread_shell','programme_key':'D09_directory_04','historical_room_id':'D09_tailor3','name':'Thread & Shell','status':'Partial real destination under construction; no completed shop, sales or species-fit claim','origin':[8,52.5,-216],'floor_y':52.5,'protected_below':'D08 volume below52.26; no new underfloor intrusion','protected_above':'D10_directory_04 / D10_banquet3 Orchard food hall','cover_top_y':61,'cover_underside_y':60.76,'allocation':[[8,-250],[54,-250],[54,-182],[8,-182]],'public_outline':[list(v)for v in outer.exterior.coords[:-1]],'floor_boundary':boundary,'floor_triangles':[[list(v)for v in t.exterior.coords[:3]]for t in tri.geoms],'columns':columns,'public_entry':[8,-216],'service_entry':[40,-197],'fitting_pods':[{'id':'D09_tailor3_fitting_01','front_x':29,'back_x':37,'center_z':-225.5,'width':6.0},{'id':'D09_tailor3_fitting_02','front_x':29,'back_x':37,'center_z':-209.5,'width':6.0}],'door_variant':{'file':'AST-DOR-002_wide.glb','clear_opening_m':2.4,'outer_case_width_m':5.16},'structural_area_m2':footprint.area,'explicit_limits':['D10 cap is a future floor substrate, not an implemented food hall','Approaches join current structural spine; complete segregated service transit remains pending','No external window or hull-shell claim','No extra addressed small shop, accommodation or population']}
ceiling=outer.difference(unary_union([Point(x,z).buffer(1.55,quad_segs=4)for x,z in columns]))
D['public_triangles']=[[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(ceiling).geoms]
D['ceiling_coffers']=[[list(v)for v in h.coords[:-1]]for h in ceiling.interiors]
D['service_boundary']=[list(v)for v in service.union(service_arrival).exterior.coords[:-1]]
D['service_triangles']=[[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(service.union(service_arrival)).geoms]
layout=json.load(open(R/'data/spatial_layout.json'));layout['regions']=[v for v in layout['regions']if v.get('authoring_owner')!=owner]+[{'id':'D09_thread_shell_floor','authoring_owner':owner,'deck':'D09','boundary':boundary,'priority':60,'thickness':.24,'programme_owner':'D09_tailor3','status':'Authored retail floor/access; integrated architecture and actual traversal pending'},{'id':'D10_thread_shell_cover','authoring_owner':owner,'deck':'D10','boundary':boundary,'priority':-10,'thickness':.24,'programme_owner':'D10_banquet3','walkable_public':False,'status':'Opaque boutique cover/future Orchard food hall substrate; no upper business or access acceptance'}]
(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n');(R/'data/architecture/D09_thread_shell.json').write_text(json.dumps(D,indent=2)+'\n')
p=C/'assets/thread_shell_architecture';(p/'source').mkdir(parents=True,exist_ok=True);(p/'exports').mkdir(exist_ok=True);(p/'source/architecture_contract.json').write_text(json.dumps(D,indent=2)+'\n')
print('Thread & Shell structural footprint',round(footprint.area,2),'m2; protected neighboring allocations preserved; runtime validation pending')
