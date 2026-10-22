from pathlib import Path
import json,struct,hashlib,copy
from shapely.geometry import shape,box
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');W=R/'BlenderCatalogue/assets/sunset_specialty_bank_20261022';G=R/'Game';P=G/'sunset_specialty_bank_20261022';pack=json.loads((W/'PLAN.json').read_text());src=G/'assets/models/SUNSET_ARCHITECTURE_lift_r003.glb';b=src.read_bytes();glb=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);owners={q['source_part_id']:n['name']for n in glb['nodes']for q in n.get('extras',{}).get('source_part_ranges',[])};sp=next((R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001').rglob('sunset_conservatory_house/outputs/house_r002/PLAN.json'));house=json.loads(sp.read_text());changes=[];witnesses=[]
for r in pack['rooms']:
 a=r['allocation'];door=next(x for x in r['doors']if x['controller']=='guest_entry_door.gd');y=a['floor_y'];z=door['position'][2];floor=unary_union([shape(p['geometry'])for p in house['floor_regions']if abs(p['floor_y']-y)<.001]);sample=box(-45.9,z-.9,-42.1,z+.9);missing=sample.difference(floor).area;witnesses.append({'allocation':a['source_envelope_index'],'street_approach_missing_area_m2':missing,'floor_y':y});assert missing<.00001,(a['source_envelope_index'],missing)
for part in house['parts']:
 if part['category']not in ['guard','public_glass'] or part.get('kind')!='beam':continue
 a,b=part['a'],part['b'];hits=[]
 for r in pack['rooms']:
  door=next(d for d in r['doors']if d['controller']=='guest_entry_door.gd');edge=-45.98 if r['allocation']['allocation_x'][0]<-45 else -42.02;y=r['allocation']['floor_y'];z=door['position'][2]
  if abs(a[0]-edge)<.001 and abs(b[0]-edge)<.001 and y-.01<=min(a[1],b[1])<=y+1.2 and max(a[1],b[1])<=y+1.2 and max(a[2],b[2])>=z-.95 and min(a[2],b[2])<=z+.95:hits.append((z-.95,z+.95))
 if not hits:continue
 assert part['name'] in owners
 segments=[(min(a[2],b[2]),max(a[2],b[2]))]if abs(a[2]-b[2])>.1 else []
 for lo,hi in hits:
  out=[]
  for l,h in segments:
   if h<=lo or l>=hi:out.append((l,h))
   else:
    if l<lo:out.append((l,lo))
    if h>hi:out.append((hi,h))
  segments=out
 replacements=[]
 for j,(lo,hi)in enumerate(segments):
  q=copy.deepcopy(part);q['name']+='__Sunset47Retained'+str(j);q['a'][2]=lo;q['b'][2]=hi;replacements.append(q)
 changes.append({'original':part,'batch':owners[part['name']],'replacements':replacements})
plan={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'changes':changes,'street_approach_witnesses':witnesses,'room_count':47,'door_clear_width_m':1.9,'whole_structural_capacity_accepted':False}
(W/'GUARD_PLAN_R003.json').write_text(json.dumps(plan,indent=2)+'\n');(P/'evidence/STREET_OWNER_CHECK_R003.json').write_text(json.dumps({'status':'PASS','actual_retained_floor_source':str(sp.relative_to(R)),'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'witnesses':witnesses,'guard_parts':len(changes),'guard_batches':len(set(c['batch']for c in changes))},indent=2)+'\n');print('Sunset actual47 street approaches supported; guard parts',len(changes),'batches',len(set(c['batch']for c in changes)))
