"""Author the reviewed Vesper upper dining/access profile within D10's own volume."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
layout_path=R/'data/spatial_layout.json';layout=json.loads(layout_path.read_text());owner='vesper_upper_dining'
main=Polygon([(21,182),(53.6,182),(53.6,197.8),(48.5,197.8),(46.4,199),(39,199),(36.8,197.8),(27.2,197.8),(24,196.7),(21,196.7)])
west=box(16,188.64,20.32,197.14);crosslink=box(19,194.3,26.8,197.14);corridor=box(16.4,194.3,19.24,206.42)
raw=unary_union([main,west,crosslink,corridor]);cut=box(20.48,189.98,24.12,194.02);floor=raw.difference(cut)
assert floor.is_valid and floor.geom_type=='Polygon'
assert box(8,182,54,250).covers(floor)
# Existing stair hole is kept at61; upper passage remains3.22m above it.
old_stair=box(9.8,189.8,16.2,200.5)
assert box(11,203.58,16.4,206.42).intersection(old_stair).area==0
for guest in json.load(open(R/'data/reference/historical_guest_census.json'))['guest_envelopes']:
 if guest['deck'] in [10,11]:assert floor.intersection(box(guest['x'][0],guest['z'][0],guest['x'][1],guest['z'][1])).area<1e-8
lower=next(v for v in layout['regions']if v['id']=='D10_vesper_floor');lower_shape=Polygon(lower['boundary'],lower['holes']);assert lower_shape.covers(cut)
layout['voids']=[v for v in layout['voids']if v.get('authoring_owner')!=owner]+[{'id':'vesper_local_lift_D10','authoring_owner':owner,'decks':['D10'],'boundary':[list(v)for v in cut.exterior.coords[:-1]],'source':'Local dining/gallery access; pit remains within existing D10 slab depth'}]
region={'id':'D10_vesper_upper_dining','authoring_owner':owner,'deck':'D10','offset_y':3.5,'boundary':[list(v)for v in raw.exterior.coords[:-1]],'holes':[],'priority':30,'thickness':.28,'programme_owner':'D10_banquet7','status':'Authored upper restaurant floor; access, seated fit and final art under integration','render_cell_m':12}
layout['regions']=[v for v in layout['regions']if v.get('authoring_owner')!=owner]+[region]
layout_path.write_text(json.dumps(layout,indent=2)+'\n')
base=json.load(open(R/'data/architecture/D10_vesper_dining_subset.json'));groups=[dict(v,y=61)for v in base['groups']]
new=[(x,183.9)for x in [29.3,34.7,40.1,45.5,50.9]]+[(x,189.7)for x in [29.3,34.7,40.1,50.9]]+[(x,195.5)for x in [40.1,50.9]]+[(x,248.1)for x in [25.1,31.7,38.3]]+[(18.5,z)for z in [224.8,230.6]]
for x,z in new:groups.append({'index':len(groups),'x':x,'z':z,'y':61,'seats':6,'model':'AST-DIN-001_six.glb','reserved_occupied_envelope_m':[4.2,3.4]})
for z in [183.9,189.7,195.5]:
 for x in [29.3,34.7,40.1,45.5,50.9]:groups.append({'index':len(groups),'x':x,'z':z,'y':64.5,'seats':6,'model':'AST-DIN-001_six.glb','reserved_occupied_envelope_m':[4.2,3.4]})
assert sum(v['seats']for v in groups)==240
for i,v in enumerate(groups):
 w,h=v['reserved_occupied_envelope_m'];shape=box(v['x']-w/2,v['z']-h/2,v['x']+w/2,v['z']+h/2)
 assert (floor if v['y']==64.5 else lower_shape.difference(cut)).covers(shape),(v['index'],'unsupported group')
 for u in groups[:i]:
  if u['y']!=v['y']:continue
  uw,uh=u['reserved_occupied_envelope_m'];assert shape.intersection(box(u['x']-uw/2,u['z']-uh/2,u['x']+uw/2,u['z']+uh/2)).area<1e-8
piers=[[x,182.7]for x in [26.5,32,37.4,42.8,48.2,53.5]]+[[28,195.2],[33.4,195.2],[39,197.55],[44.5,197.55],[50,197.55],[16.35,202]]
for x,z in piers:assert lower_shape.difference(cut).covers(Point(x,z).buffer(.22)),(x,z)
# Inboard rail bases respect the reviewed0.22m support allowance.
rail=floor.buffer(-.11,join_style=2)
D={'id':owner,'programme_key':'D10_directory_08','origin':[21,61,182],'floor_y':64.5,'underside_y':64.22,'floor_region_id':region['id'],'boundary':[list(v)for v in floor.exterior.coords[:-1]],'holes':[[list(v)for v in h.coords[:-1]]for h in floor.interiors],'rail_boundary':[list(v)for v in rail.exterior.coords[:-1]],'triangles':[[list(v)for v in t.exterior.coords[:3]]for t in constrained_delaunay_triangles(floor).geoms],'groups':groups,'candidate_seats':240,'runtime_fitted_before_integration':54,'piers_xz':piers,'stair':{'x':[11,16.4],'z':[203.58,206.42],'floor_y':[61,64.5],'risers':18,'clear_width_m':2.4},'lift':{'origin_xz':[20.5,192],'floor_heights':[61,64.5],'stop_ids':['D10','D10M'],'stop_names':['Dining','Upper dining'],'stop_codes':['10','M'],'floor_cut_xz':{'x':[20.48,24.12],'z':[189.98,194.02]},'shaft_outer_xz':{'x':[20.32,24.32],'z':[189.84,194.16]},'pit_pan_y':[60.76,60.8],'cap_y':[67.73,67.85],'staging_xz':[18.25,192]},'ceiling_relief_xz':{'x':[20.12,24.52],'z':[189.64,194.36]},'ceiling_relief_y':[68.2,68.36],'west_walk_xz':[[18,220],[20.5,220],[22,223],[22,234],[20,245]],'status':'Candidate240 seated plan and actual authored upper floor; moving access, guards, headroom and final art pending'}
p=R/'data/architecture/D10_vesper_mezzanine.json';p.write_text(json.dumps(D,indent=2)+'\n');dest=C/'assets/vesper_mezzanine';(dest/'source').mkdir(parents=True,exist_ok=True);(dest/'exports').mkdir(exist_ok=True);(dest/'source/section_contract.json').write_text(p.read_text())
print({'candidate_seats':240,'lower_seats':150,'upper_seats':90,'upper_floor_m2':floor.area,'guarded_floor_boundary_points':len(D['rail_boundary'])})
