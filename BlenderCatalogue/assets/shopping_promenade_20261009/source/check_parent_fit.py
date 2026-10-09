"""Check additive ownership against the read-only published parent snapshot."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
from shapely.geometry import Polygon
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];plan=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());inputs=[];retained=[]
for f in [P/'dependencies/parent_aeea210/spatial_layout.json',P/'dependencies/parent_aeea210/received_section_floors.json',P/'dependencies/parent_5a9bd1/REMAINING_BATCH_FLOORS.json',P/'dependencies/parent_5a9bd1/AQUATIC_ANNEX_FLOORS.json']:
 if not f.exists():continue
 d=json.loads(f.read_text());inputs.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 def collect(x):
  if isinstance(x,dict):
   if 'boundary' in x and (x.get('deck')=='D09' or x.get('programme_key','').startswith('D09') or x.get('id','').startswith('D09')) and x.get('offset_y',0)==0:
    retained.append(Polygon(x['boundary'],x.get('holes',[])))
   else:
    for v in x.values():collect(v)
  elif isinstance(x,list):
   for v in x:collect(v)
 collect(d)
owned=unary_union(retained);overlaps=[];dups=[];floors=plan['floor_proposals'];polys=[Polygon(x['boundary'],x.get('holes',[])) for x in floors]
for r,p in zip(floors,polys):
 a=p.intersection(owned).area
 if a>1e-7:overlaps.append({'id':r['id'],'area_m2':a})
for i,p in enumerate(polys):
 for j,q in enumerate(polys[:i]):
  if p.intersects(q) and p.intersection(q).area>1e-7:dups.append({'a':floors[i]['id'],'b':floors[j]['id'],'area_m2':p.intersection(q).area})
room_large=[]
for r in plan['rooms']:
 p=Polygon([[r['allocation_x'][0],r['allocation_z'][0]],[r['allocation_x'][1],r['allocation_z'][0]],[r['allocation_x'][1],r['allocation_z'][1]],[r['allocation_x'][0],r['allocation_z'][1]]])
 for venue in plan['retained_large_destinations']:
  x,z=venue['allocation_x'],venue['allocation_z'];v=Polygon([[x[0],z[0]],[x[1],z[0]],[x[1],z[1]],[x[0],z[1]]])
  if p.intersection(v).area>1e-7:room_large.append({'shop':r['chunk_id'],'venue':venue['programme_key']})
out={'passed':not overlaps and not dups and not room_large,'parent_snapshot':'aeea210559c2bf05e21296c412111d8cf855df3d read through existing GitHub connection; later parent performance/Quiet changes are root-owned and not certified here','read_only_inputs':inputs,'retained_parent_floor_polygons':len(retained),'new_floor_rows':len(floors),'additive_floor_parent_overlaps':overlaps,'new_floor_duplicate_ownership':dups,'shop_large_venue_allocation_overlaps':room_large,'R070':'Retained native/export/code/input byte hashes checked separately; own construction excludes its footprint and source-guarded approach','scope':'Construction plan and source ownership; root still performs consolidated runtime adoption and full final acceptance'}
(P/'qa/parent_fit_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('PARENT_FIT',out['passed']);assert out['passed'],str(overlaps)+str(dups)+str(room_large)
