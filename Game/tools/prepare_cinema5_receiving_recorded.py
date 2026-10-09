from pathlib import Path
import json,hashlib,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'))
from compile_received_section_floors import compile_received
src=json.loads((r/'data/architecture/received_section_floors.json').read_text())
for filename,key in [('SALON_RECEIVING_FLOORS_CANDIDATE.json','D12_directory_03'),('STILLROOM_RECEIVING_FLOORS_CANDIDATE.json','D12_directory_04')]:
 d=json.loads((r/'data/architecture'/filename).read_text())
 for i,row in enumerate(d['regions']):src['regions'].append(dict(id=row['id'],programme_key=key,kind='authored_room_floor' if i==0 else 'explicit_connection',boundary=row['rings'][0],connection_to='D12_fore_route'))
src['regions'] += [dict(id='D11_cinema5_missing_receiving_floor',programme_key='D11_directory_06',kind='authored_room_floor',boundary=[[11,316],[61,316],[61,244],[54,244],[54,250],[11,250]]),dict(id='D11_cinema5_spine_connection',programme_key='D11_directory_06',kind='explicit_connection',boundary=[[7.8,278],[11,278],[11,297],[4,297],[4,292],[7.8,292]],connection_to='D11_aft_route')]
result=compile_received(r,src);result['regions']=result['regions'][-2:]
result['source_checks'].update(new_owner_count=2,preceding_receiving_sha256=hashlib.sha256((r/'data/generated/received_structural_meshes.json').read_bytes()).hexdigest(),salon_receiving_sha256=hashlib.sha256((r/'data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json').read_bytes()).hexdigest(),stillroom_receiving_sha256=hashlib.sha256((r/'data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json').read_bytes()).hexdigest(),retained_aquatic_floor_owner='D11_aquatic_cinema_interface',retained_aquatic_floor_area_m2=258)
(r/'data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n')
objects=json.loads((r.parent/'BlenderCatalogue/assets/remaining_sections_20261009/E/02_cinema_5/qa/source_objects.json').read_text());contacts=[]
for obj in objects:
 b=obj.get('bounds_godot')
 if b and abs(b[1]-69.5)<.0001:contacts.append(dict(id=obj['name'],min_world=b[:3],max_world=b[3:]))
assert len(contacts)==106
(r/'data/architecture/CINEMA5_FLOOR_CONTACTS_CANDIDATE.json').write_text(json.dumps(dict(contacts=contacts),indent=2)+'\n')
print('Compiled Cinema5 additive floors and106 source datum contacts.')
