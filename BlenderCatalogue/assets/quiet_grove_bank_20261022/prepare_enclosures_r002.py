from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[3];P=R/'Game/quiet_grove_bank_20261022';W=R/'BlenderCatalogue/assets/quiet_grove_bank_20261022';d=json.loads((P/'PACKAGE.json').read_text());rows=[]
for room in d['rooms']:
 a=room['allocation'];idx=a['source_envelope_index'];parts=[]
 for p in room['parts']:
  if p['category']!='cocoon_privacy':continue
  j=int(p['name'].split('_Cocoon')[1][:2])-1;m=room['rest_moves'][j];s=m['source_component']['position'];t=m['target_component']['position'];c=math.cos(m['yaw_delta']);n=math.sin(m['yaw_delta']);verts=[]
  for v in p['verts']:
   x,y,z=[v[k]-s[k] for k in range(3)];verts.append([t[0]+c*x+n*z,t[1]+y,t[2]-n*x+c*z])
  lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
  assert lo[0]>=a['allocation_x'][0]-.001 and hi[0]<=a['allocation_x'][1]+.001 and lo[2]>=a['allocation_z'][0]-.001 and hi[2]<=a['allocation_z'][1]+.001
  parts.append(dict(name=p['name'],source=s,target=t,yaw_delta=m['yaw_delta'],expected_min=lo,expected_max=hi,rest_slot_id=m['slot_id']))
 if parts:
  clearance=58.95-max(p['expected_max'][0] for p in parts) if a['allocation_x'][0]>45 else min(p['expected_min'][0] for p in parts)-29.05
  assert clearance>=2.8
  native=W/f'QuietGroveBank_{idx}_r001.blend'
  rows.append(dict(index=idx,room_id=a['proposed_runtime_id'],model_file=room['model_file'],source_native=native.name,source_native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),native_successor=f'QuietGroveBank_{idx}_r002.blend',runtime_delta=f'QuietGroveEnclosure_{idx}_r002.glb',parts=parts,complete_liner_view_clearance_m=clearance))
out=dict(schema='quiet_grove_enclosures_r002',protected_parent='09e53bd502a6fcec8f6b82bc6f9b13b32f08f20b',package_sha256=hashlib.sha256((P/'PACKAGE.json').read_bytes()).hexdigest(),rooms=rows,policy='Move entire fixed cocoon enclosure by its already-authored support/door rigid transform. Preserve originals, contacts, IDs, allocation and privacy. No new hull/structural cuts.',visual_accepted=False)
(P/'ENCLOSURES_R002.json').write_text(json.dumps(out,indent=2)+'\n')
print('authored',len(rows),'rooms',sum(len(x['parts']) for x in rows),'parts')
