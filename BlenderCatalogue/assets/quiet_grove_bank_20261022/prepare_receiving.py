from pathlib import Path
import json,struct,copy,hashlib
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');W=R/'BlenderCatalogue/assets/quiet_grove_bank_20261022';G=R/'Game';p=R/'BlenderCatalogue/assets/residential_hotels/quiet_grove_20261007_r001/residential-neighborhood-courts-20261007/outputs/sf_house_r002/PLAN.json';house=json.loads(p.read_text());pack=json.loads((W/'RUNTIME_PLAN.json').read_text());pack['rooms']=[r for r in pack['rooms']if r['allocation']['deck']=='D15'];src=G/'assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb';b=src.read_bytes();glb=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);owners={q['source_part_id']:n['name']for n in glb['nodes']for q in n.get('extras',{}).get('source_part_ranges',[])};changes=[]
for part in house['parts']:
 if not part['name'].startswith('StreetExposed'):continue
 a,b=part['a'],part['b'];hits=[]
 for r in pack['rooms']:
  door=next(d for d in r['doors']if d['controller']=='guest_entry_door.gd');x=41.95 if r['allocation']['allocation_x'][1]<45 else 46.05;y=r['allocation']['floor_y'];z=door['position'][2]
  if abs(a[0]-x)<.001 and y-.01<=a[1]<=y+1.2 and max(a[2],b[2])>=z-.95 and min(a[2],b[2])<=z+.95:hits.append((z-.95,z+.95))
 if not hits:continue
 segments=[(min(a[2],b[2]),max(a[2],b[2]))] if 'Rail'in part['name']else[]
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
  q=copy.deepcopy(part);q['name']+='__QG30RetainedSegment'+str(j);q['a'][2]=lo;q['b'][2]=hi;replacements.append(q)
 changes.append(dict(original=part,batch=owners[part['name']],replacements=replacements))
assert changes and len({r['allocation']['source_envelope_index']for r in pack['rooms']})==30
out=dict(source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),changes=changes,door_clear_width_m=1.9,unrelated_guard_parts_unchanged=True,room_count=30,scope='Remove only original guard beam parts intersecting30 door openings; reconstruct retained outside segments with closed ends. No original floors/hull/cap changed.')
(W/'GUARD_PLAN.json').write_text(json.dumps(out,indent=2)+'\n');print('guard source parts',len(changes),'batches',len({x['batch']for x in changes}))
