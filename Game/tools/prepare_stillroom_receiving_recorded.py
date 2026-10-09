from pathlib import Path
import json,sys,hashlib
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'))
from compile_received_section_floors import compile_received
geo=json.load((r/'docs/receiving_audits/stillroom_receiving_geometry.json').open())
src=json.loads((r/'data/architecture/received_section_floors.json').read_text())
salon=json.loads((r/'data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json').read_text())
for i,row in enumerate(salon['regions']):
 src['regions'].append(dict(id=row['id'],programme_key='D12_directory_03',kind='authored_room_floor' if i==0 else 'explicit_connection',boundary=row['rings'][0],connection_to='D12_fore_route'))
src['regions'] += [dict(id='D12_stillroom_receiving_floor',programme_key='D12_directory_04',kind='authored_room_floor',boundary=geo['recommended_floor_boundary']),dict(id='D12_stillroom_spine_connection',programme_key='D12_directory_04',kind='explicit_connection',boundary=geo['recommended_connector_boundary'],connection_to='D12_fore_route')]
result=compile_received(r,src);result['regions']=result['regions'][-2:]
result['source_checks'].update(new_owner_count=2,preceding_receiving_sha256=hashlib.sha256((r/'data/generated/received_structural_meshes.json').read_bytes()).hexdigest(),salon_receiving_sha256=hashlib.sha256((r/'data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json').read_bytes()).hexdigest(),source_glb_sha256=geo['source_glb_sha256'])
(r/'data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n')
objects=json.loads((r.parent/'BlenderCatalogue/assets/remaining_sections_20261009/E/03_stillroom/qa/source_objects.json').read_text())
contacts=[]
for obj in objects:
 b=obj.get('bounds_godot')
 if b and abs(b[1]-78)<.0001: contacts.append(dict(id=obj['name'],min_world=b[:3],max_world=b[3:]))
assert len(contacts)==161,len(contacts)
(r/'data/architecture/STILLROOM_FLOOR_CONTACTS_CANDIDATE.json').write_text(json.dumps(dict(contacts=contacts),indent=2)+'\n')
print('Compiled two disjoint Stillroom receiving owners and161 contacts.')
