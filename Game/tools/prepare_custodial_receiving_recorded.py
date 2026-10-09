from pathlib import Path
import json,hashlib,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'))
from compile_received_section_floors import compile_received
src=json.loads((r/'data/architecture/received_section_floors.json').read_text())
for filename,key,connector in [('SALON_RECEIVING_FLOORS_CANDIDATE.json','D12_directory_03','D12_fore_route'),('STILLROOM_RECEIVING_FLOORS_CANDIDATE.json','D12_directory_04','D12_fore_route'),('CINEMA5_RECEIVING_FLOORS_CANDIDATE.json','D11_directory_06','D11_aft_route')]:
 d=json.loads((r/'data/architecture'/filename).read_text())
 for i,row in enumerate(d['regions']):src['regions'].append(dict(id=row['id'],programme_key=key,kind='authored_room_floor' if i==0 else 'explicit_connection',boundary=row['rings'][0],connection_to=connector))
src['regions'] += [dict(id='D01_custodial_receiving_floor',programme_key='D01_directory_10',kind='authored_room_floor',boundary=[[8,398],[54,398],[54,466],[8,466]],material_role='staff_floor'),dict(id='D01_custodial_spine_connection',programme_key='D01_directory_10',kind='explicit_connection',boundary=[[4,458],[8,458],[8,462],[4,462]],connection_to='D01_aft_route',material_role='staff_floor')]
result=compile_received(r,src);result['regions']=result['regions'][-2:]
result['source_checks'].update(new_owner_count=2,preceding_receiving_sha256=hashlib.sha256((r/'data/generated/received_structural_meshes.json').read_bytes()).hexdigest())
for key,f in [('salon','SALON'),('stillroom','STILLROOM'),('cinema5','CINEMA5')]:result['source_checks'][key+'_receiving_sha256']=hashlib.sha256((r/f'data/architecture/{f}_RECEIVING_FLOORS_CANDIDATE.json').read_bytes()).hexdigest()
(r/'data/architecture/CUSTODIAL_RECEIVING_FLOORS_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n')
p=r.parent/'BlenderCatalogue/assets/remaining_sections_20261009/A/D01_directory_10';props=json.loads((p/'docs/FLOOR_RECEIVING_PROPOSAL.json').read_text());contacts=[]
for row in props['actual_source_bearing_parts']:
 v=[v for t in row['bottom_bearing_faces_xz'] for v in t];contacts.append(dict(id=row['source_node'],min_world=[min(q[0] for q in v),0,min(q[1] for q in v)],max_world=[max(q[0] for q in v),0,max(q[1] for q in v)]))
assert len(contacts)==292
(r/'data/architecture/CUSTODIAL_FLOOR_CONTACTS_CANDIDATE.json').write_text(json.dumps(dict(contacts=contacts),indent=2)+'\n')
print('Compiled Custodial Depot receiving floors and292 source datum contacts.')
