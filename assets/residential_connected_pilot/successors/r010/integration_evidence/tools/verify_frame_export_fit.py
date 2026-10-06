#!/usr/bin/env python3
"""Independent actual GLB corner/contact recheck against the exact pinned proposal."""
from pathlib import Path
import ast,hashlib,json,struct
import numpy as np
S=Path(__file__).resolve().parents[1];G=Path('/workspace/shared/astraea-godot-production-20261003');P=S.parent
schedule=json.load(open(S/'data/architecture/RECEIVING_FRAME_PROPOSAL.json'));reference={m['name']:m for m in schedule['members']};p=S/'assets/models/residential_pilot_205/receiving_frame_r001.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);off=20+n;nb,t=struct.unpack_from('<II',b,off);blob=b[off+8:off+8+nb];assert t==0x004e4942
ns={'np':np};tree=ast.parse((S/'tools/propose_receiving_frame.py').read_text());wanted=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in ['axes','separate','rectv']];exec(compile(ast.Module(body=wanted,type_ignores=[]),'exact_proposal_sat','exec'),ns);separate=ns['separate'];rectv=ns['rectv']
def acc(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dim={'SCALAR':1,'VEC3':3}[a['type']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]);return np.ndarray((a['count'],dim),dtype=dt,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dim*dt.itemsize),dt.itemsize)).copy()
def matrix(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape(4,4,order='F')
 x,y,z,w=n.get('rotation',(0,0,0,1));m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',(1,1,1)));m[:3,3]=n.get('translation',(0,0,0));return m
actual={};maxerror=0;triangles=0

def walk(i,M):
 global maxerror,triangles
 n=j['nodes'][i];M=M@matrix(n)
 if 'mesh'in n:
  key=n['extras']['source_member_id'];assert key in reference and key not in actual
  q=[]
  for prim in j['meshes'][n['mesh']]['primitives']:
   xyz=acc(prim['attributes']['POSITION']);q.append((np.c_[xyz,np.ones(len(xyz))]@M.T)[:,:3]);triangles+=len(acc(prim['indices']))//3
  q=np.concatenate(q);ref=np.array(reference[key]['vertices_world_xyz']);d=np.max(np.abs(q[:,None]-ref[None,:]),axis=2);corners=q[np.argmin(d,axis=0)];error=float(np.max(np.abs(corners-ref)));maxerror=max(maxerror,error);assert error<.00003,(key,error);actual[key]=corners
 for c in n.get('children',[]):walk(c,M)
for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4))
assert len(actual)==60 and triangles==720
levels={r['deck_id']:r['floor_elevation_m']for r in json.load(open(G/'data/design_contract.json'))['deck_datums']};obstacles=[]
for index,r in enumerate(json.load(open(G/'data/reference/historical_guest_census.json'))['guest_envelopes']):
 y=levels[f'D{r["deck"]:02d}'];lo=[r['x'][0],y-.22,r['z'][0]];hi=[r['x'][1],y+4.04,r['z'][1]];obstacles.append((f'guest_source_{index}',rectv(lo,hi)))
for r in json.load(open(G/'data/programme_ledger.json'))['destinations']:
 e=r.get('historical_envelope')
 if e:
  y=levels[r['historical_deck']];top=levels.get(f'D{int(r["historical_deck"][1:])+1:02d}',118);obstacles.append((r['programme_key'],rectv([e['x'][0],y,e['z'][0]],[e['x'][1],top,e['z'][1]])))
violations=[]
for name,v in actual.items():
 for key,w in obstacles:
  # Export quantization can intrude a few micrometres into intended bearing
  # boundary planes. Reject overlap deeper than0.05mm; clearances are20/60mm.
  if np.any(w.max(axis=0)<=v.min(axis=0)+.00005)or np.any(w.min(axis=0)>=v.max(axis=0)-.00005):continue
  if not separate(v,w,False):violations.append([name,key])
parts=json.load(open(P/'domestic_correction/court_source/PARTS.json'))['objects'];anchors={r['name']:rectv(r['bounds_world_min_xyz'],r['bounds_world_max_xyz'])for r in parts if r['name'].startswith(('ROOF_EastPier_','SUP_transfer_upper_','SUP_spine_mast_','SUP_D12_receiver_'))};anchors.update({'D12_fore_route':rectv([-4,77.76,-530],[4,78,-80]),'D14_fore_route':rectv([-4,88.26,-530],[4,88.5,-80])});links=[];anchorcontacts=[]
#5e-5m tolerance matches the authored/source-float quantization budget.
def touches(a,b):
 av=ns['axes'](a);bv=ns['axes'](b)
 for axis in av+bv+[np.cross(x,y)for x in av for y in bv]:
  if np.linalg.norm(axis)<1e-9:continue
  axis=axis/np.linalg.norm(axis);p=a@axis;q=b@axis
  if max(q.min()-p.max(),p.min()-q.max())>.00005:return False
 return True
for name,v in actual.items():
 for key,w in anchors.items():
  if touches(v,w):anchorcontacts.append([name,key])
 for key,w in actual.items():
  if key>name and touches(v,w):links.append([name,key])
connected={a for a,b in anchorcontacts}
while True:
 nxt=connected|{b for a,b in links if a in connected}|{a for a,b in links if b in connected}
 if nxt==connected:break
 connected=nxt
assert not violations and len(connected)==60,(violations,sorted(set(actual)-connected))
report={'status':'PASS_ACTUAL_EXPORT_SCOPED_FIT','source_glb_sha256':hashlib.sha256(b).hexdigest(),'actual_mesh_members':60,'actual_triangles':triangles,'maximum_actual_corner_delta_from_pinned_schedule_m':maxerror,'all_actual_members_connected_to_source_receivers':len(connected),'guest_programme_positive_overlap_beyond_0_05mm':violations,'contact_tolerance_m':.00005,'assumption':'Guest source-screen height is floor-.22 through floor+4.04, corroborated for relevant D13standards in LOWER_ROOM_SCOPE_ADDENDUM.json. It does not define every future specialty/luxury/species height.','actual_anchor_contacts':anchorcontacts,'actual_member_contacts':links,'native_collision_and_load_certification':False}
(S/'qa/FRAME_ACTUAL_EXPORT_FIT.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k not in ['actual_anchor_contacts','actual_member_contacts']})
