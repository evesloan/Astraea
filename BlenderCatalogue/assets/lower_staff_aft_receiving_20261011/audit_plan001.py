from pathlib import Path
import json,hashlib
from shapely.geometry import shape,Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));poly=shape(P['floor_geometry']);checks=0;old_area=0.;source_contacts=[]
for file in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json']:
 for region in json.load(open(R/file))['regions']:
  if region['floor_y']!=0:continue
  original=unary_union([Polygon(q)for q in region['triangles']]);area=poly.intersection(original).area;assert area<1e-8,(region['id'],area);old_area+=area;checks+=1
  shared=poly.boundary.intersection(original.boundary).length
  if shared>1e-6:source_contacts.append({'original_floor':region['id'],'contact_edge_length_m':shared})
assert {x['original_floor']for x in source_contacts}=={'D01_aft_apron','D01_aft_route'}
assert all(abs(x['contact_edge_length_m']-3.6)<1e-6 for x in source_contacts)
layout=json.load(open(R/'Game/data/whole_ship_layout.json'));conflicts=[]
for part in P['parts']:
 lo=[min(v[i]for v in part['verts'])for i in range(3)];hi=[max(v[i]for v in part['verts'])for i in range(3)]
 for programme in layout['programmes']:
  checks+=1;y=programme['floor_y'];x0,x1=programme['allocation_x'];z0,z1=programme['allocation_z']
  if hi[1]<=y+.00001 or lo[1]>=y+4.25:continue
  if min(x1,hi[0])-max(x0,lo[0])>1e-6 and min(z1,hi[2])-max(z0,lo[2])>1e-6:conflicts.append({'part':part['name'],'programme':programme['programme_key']})
assert not conflicts,conflicts
for row in P['support_preimages']:
 x,_,z=row['top'];foot=box(x-.12,z-.12,x+.12,z+.12);assert poly.covers(foot),(x,z);checks+=1
 frame=[q for q in P['parts']if q['category']=='frame'and 'FloorStringer'in q['name']]
 supported=any(box(min(v[0]for v in q['verts']),min(v[2]for v in q['verts']),max(v[0]for v in q['verts']),max(v[2]for v in q['verts'])).buffer(.00002).covers(foot)for q in frame);assert supported,(x,z);checks+=1
old=json.load(open(W/'PROTECTED_NATIVE_EXPORT_PREIMAGES.json'))
for f,h in old.items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
report={'status':'PASS','checks':checks,'programmes':len(layout['programmes']),'programme_volume_conflicts':conflicts,'new_missing_only_floor_m2':poly.area,'original_floor_overlap_m2':old_area,'original_source_floor_contacts':source_contacts,'prior_native_export_files_byte_identical':len(old),'support_columns_fit_within_owned_floor_and_stringers':len(P['support_preimages']),'float32_source_contact_tolerance_m':.00002,'primary_structural_engineering_accepted':False,'original_D03_rooms_ceiling_and_floor_untouched':True}
(W/'PROGRAMME_AND_FLOOR_PREFLIGHT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','checks','new_missing_only_floor_m2','original_floor_overlap_m2']}))
