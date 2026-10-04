"""Author the accepted integrated arrivals/fusion section in the real layout."""
from pathlib import Path
import json
from shapely.geometry import box,LineString
from shapely.ops import unary_union

r=Path(__file__).resolve().parents[1];p=r/'data/architecture/D01_D02_arrivals_fusion.json';d=json.loads(p.read_text())
def rect(v):return box(v['x'][0],v['z'][0],v['x'][1],v['z'][1])
envelope=rect(d['envelope_xz'])
d['public_upper_floor_rectangles'][0]['x']=[-20,-8]
d['lift']={'origin_xz':[-16.4,-424],'floor_heights':[0,6],'deck_numbers':[1,2],
           'floor_hole_xz':{'x':[-16.42,-12.78],'z':[-426.02,-421.98]},
           'shaft_outer_xz':{'x':[-16.58,-12.62],'z':[-426.16,-421.84]},
           'identity':'arrivals_fusion_lift_001'}
lift=rect(d['lift']['floor_hole_xz'])
entry=box(-12,-435,0,-429)
lower=envelope.union(entry).difference(lift)
public=unary_union([rect(v)for v in d['public_upper_floor_rectangles']]).union(entry)
stair_voids=unary_union([box(-39.1,-443,-35.9,-436.95),box(-39.1,-427.05,-35.9,-421)])
public=public.difference(stair_voids).difference(lift)
service=unary_union([rect(v)for v in d['service_upper_floor_rectangles']])
service_link=box(-59.5,-435,-52,-429)
service=service.union(service_link)
assert public.is_valid and service.is_valid and public.intersection(service).area<1e-6
assert envelope.covers(public.difference(entry))
assert envelope.covers(service.difference(service_link))
regions=[]
for label,deck,shape,role in [('arrivals_ground','D01',lower,'guest_floor'),('fusion_visitor_galleries','D02',public,'guest_floor'),('fusion_screened_service','D02',service,'staff_floor'),('protected_crew_cover','D03',envelope,'staff_floor')]:
    assert shape.geom_type=='Polygon',label
    regions.append({'id':deck+'_'+label,'deck':deck,'boundary':[list(v)for v in shape.exterior.coords[:-1]],'holes':[[list(v)for v in ring.coords[:-1]]for ring in shape.interiors],'priority':70,'thickness':.24,'material_role':role,'status':'Integrated arrivals/fusion structural ownership; architectural/physics acceptance pending'})
layout_path=r/'data/spatial_layout.json';layout=json.loads(layout_path.read_text());names={v['id']for v in regions};layout['regions']=[v for v in layout['regions']if v['id']not in names]+regions;layout_path.write_text(json.dumps(layout,indent=2)+'\n')
d['compiled_area_accounting']={'original_gross_programme_m2':envelope.area,'D01_floor_including_public_connection_excluding_lift_m2':lower.area,'D02_public_floor_including_connection_excluding_stairs_lift_m2':public.area,'D02_staff_floor_including_service_connection_m2':service.area,'D03_protected_opaque_floor_m2':envelope.area,'public_staff_coplanar_overlap_m2':public.intersection(service).area,'note':'Gross programme, walkable floor and machinery/exhibit volume are distinct; no passenger or crew capacity added'}
d['floor_regions']=regions
p.write_text(json.dumps(d,indent=2)+'\n')
cat=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/arrivals_fusion')
(cat/'source').mkdir(parents=True,exist_ok=True);(cat/'exports').mkdir(exist_ok=True);(cat/'source/section_contract.json').write_text(p.read_text())
print(json.dumps(d['compiled_area_accounting']))
