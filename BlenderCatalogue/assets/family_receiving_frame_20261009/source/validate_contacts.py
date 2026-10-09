from pathlib import Path
import json,sys,hashlib
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box,shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1];d=json.load(open(O/'RECEIVING_PLAN.json'));regions={q['id']:q for q in json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions']};hits=[]
for row in d['contact_interfaces']:
 for key,region in [('lower_contact_volume','D12_aft_route'),('upper_contact_volume','D13_aft_route')]:
  v=row[key];q=regions[region];floor=unary_union([Polygon(t)for t in q['triangles']]);foot=box(v[0],v[2],v[3],v[5]);area=foot.intersection(floor).area;overlap=min(v[4],q['floor_y'])-max(v[1],q['floor_y']-q['thickness']);assert abs(area-.27)<1e-6 and overlap>0
  hits.append({'region':region,'z':row['station_z'],'contact_area_m2':area,'vertical_overlap_m':overlap})
source=json.load(open(R/'BlenderCatalogue/assets/family_lift_receiving_20261009/LIFT_GEOMETRY_PLAN.json'));floor=unary_union([shape(q['geometry'])for q in source['floor_regions']if q['floor_y']==84]);feet=[]
for q in d['source_reactions_connected_via_retained_slab']:
 x0,z0,x1,z1=q['footprint_xz'];p=box(x0,z0,x1,z1);missing=p.difference(floor).area;assert missing<1e-6,q['source_part'];feet.append({'source_part':q['source_part'],'retained_floor_contact_m2':p.area})
for p,sha in d['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==sha
result={'status':'PASS_BOUNDED_GEOMETRY','members':len(d['parts']),'source_pins_verified':len(d['source_pins']),'axial_slab_contacts':hits,'supported_retained_feet':feet,'held_reactions':d['held_source_reactions'],'lift_underplate':'Includes full shaft jamb/back and pit footprint below83.76; recess remains open.','limitations':'Geometry contact only. Full primary hull/capacity, inner Celestial receiver and visual review remain unfinished.'};(O/'CONTACT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print('CONTACTS_PASS',len(hits),len(feet))
