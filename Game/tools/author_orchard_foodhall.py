from pathlib import Path
import json
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1]
outer=Polygon([(8,-250),(49,-250),(54,-245),(54,-187),(49,-182),(8,-182)])
court=box(4,-250,24,-233);hall=outer.difference(court);public=hall.intersection(box(8,-250,49,-182))
serving=[box(29,-229,38,-218),box(29,-214,38,-203)]
groups=[]
for z in [-228,-220,-212,-204,-196,-188]:groups.append({'kind':'communal10','x':17.5,'z':z,'seats':10,'envelope':[6.3,3.4],'zone':'western communal dining'})
for z in [-246.8,-241.6,-236.4]:
 for x in [27.8,34,40.2,46.0]:
  if x==27.8 and z==-236.4:continue
  groups.append({'kind':'six','x':x,'z':z,'seats':6,'envelope':[4.2,3.4],'zone':'court-facing dining'})
for z in [-198,-191.8,-185.6]:
 for x in [29,36,43]:groups.append({'kind':'six','x':x,'z':z,'seats':6,'envelope':[4.2,3.4],'zone':'southern dining commons'})
for z in [-229,-223,-217,-211,-205]:groups.append({'kind':'six','x':45.0,'z':z,'seats':6,'envelope':[4.2,3.4],'zone':'market-side dining'})
for z in [-229,-205,-199,-193,-187]:groups.append({'kind':'six','x':11.3,'z':z,'seats':6,'envelope':[4.2,3.4],'zone':'western small groups'})
shapes=[]
for i,g in enumerate(groups):
 g['index']=i;g['id']='D10_banquet3_group_%02d'%i;w,h=g['envelope'];p=box(g['x']-w/2,g['z']-h/2,g['x']+w/2,g['z']+h/2)
 assert public.covers(p),(i,'outside public floor')
 assert all(p.intersection(v).area<1e-8 for v in serving),(i,'servery overlap')
 assert all(p.intersection(v).area<1e-8 for v in shapes),(i,'dining group overlap')
 shapes.append(p)
assert sum(g['seats']for g in groups)==240
print({'candidate_groups':len(groups),'candidate_places':240,'food_hall_floor_m2':hall.area,'public_floor_m2':public.area,'occupied_envelope_m2':sum(p.area for p in shapes),'servery_m2':sum(p.area for p in serving),'status':'Plan-fit only; no actual table meshes or occupied-seat access acceptance'})
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');owner='orchard_foodhall'
foot=hall.union(box(4,-221,8.01,-211));assert foot.is_valid
for room in json.load(open(R/'data/reference/historical_guest_census.json'))['guest_envelopes']:
 if room['deck']in [9,10,11]:assert foot.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<1e-8
assert Polygon(json.load(open(R/'data/hull_envelope.json'))['plan_xz_m']).covers(foot)
def ring(p):return[list(v)for v in p.exterior.coords[:-1]]
layout=json.load(open(R/'data/spatial_layout.json'));layout['regions']=[v for v in layout['regions']if v.get('authoring_owner')!=owner]+[{'id':'D10_orchard_foodhall_floor','authoring_owner':owner,'deck':'D10','boundary':ring(foot),'holes':[],'priority':60,'thickness':.24,'programme_owner':'D10_banquet3','status':'Authored complete dining floor with service circulation; fitted route/capacity/art acceptance pending'}]
(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
D={'id':owner,'programme_key':'D10_directory_04','historical_room_id':'D10_banquet3','name':'Orchard food hall','origin':[8,61,-250],'floor_y':61,'reserved_places':240,'candidate_groups':groups,'boundary':ring(foot),'ceiling_triangles':[[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(hall).geoms],'serving_islands':[ring(p)for p in serving],'staff_spine':{'x':[38,42],'z':[-232,-200.0]},'staff_cross':{'x':[38,54],'z':[-203.1,-199.9]},'staff_perimeter':{'x':[49,54],'z':[-245,-187]},'public_entry':[8,-216],'court_entry':[24,-234.5],'staff_entry':[49,-214],'protected_below_y':60.76,'protected_above_y':69.26,'status':'Whole-space plan and source construction underway; no occupied-seat, food service or final-art acceptance','design_sequence':['Public arrival opens to distinct communal and small-group dining','Two lower serving pavilions establish the centre and conceal connected staff work bays','Northern tables face the actual shared court through internal glazing','Quieter perimeter ceilings shelter smaller tables without repeating the formal Vesper room'],'explicit_limits':['No new programme or admission capacity','Orchard240 remains reserved until real placements and access checks are complete','Staff network outside this allocation remains incomplete','No invented outer-space windows or universal species diet']}
D['ceiling_triangles']=[]
D['ceiling_x_profile']=[[8,65.3],[13,66.0],[24,68.6],[38,68.6],[49,65.5],[54,64.6]]
D['ceiling_z_profile']=[[-250,66.2],[-233,68.6],[-203,68.6],[-182,66.2]]
for xa,xb in zip([8,13,24,38,49],[13,24,38,49,54]):
 for za,zb in zip([-250,-233,-221,-211,-203],[-233,-221,-211,-203,-182]):
  cell=hall.intersection(box(xa,za,xb,zb))
  D['ceiling_triangles'] += [[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(cell).geoms]
service_floor=unary_union([box(38,-232,42,-200),box(38,-203.1,54,-199.9),box(49,-245,54,-187)])
D['staff_floor_triangles']=[[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(service_floor).geoms]
p=R/'data/architecture/D10_orchard_foodhall.json';p.write_text(json.dumps(D,indent=2)+'\n');b=C/'assets/orchard_foodhall';(b/'source').mkdir(parents=True,exist_ok=True);(b/'exports').mkdir(exist_ok=True);(b/'source/plan_contract.json').write_text(p.read_text());print('Wrote real D10 food-hall floor/plan; integration checks pending')
