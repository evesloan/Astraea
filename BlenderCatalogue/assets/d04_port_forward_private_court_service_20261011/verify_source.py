from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,Point
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];export={n:t for n,t in T(P['structure']['model_file'])};rows=[]
for q in P['parts']+P['successor_parts']:
 v=np.array(q['verts']);t=export[q['name']].reshape(-1,3);difference=max(np.max(abs(t.min(0)-v.min(0))),np.max(abs(t.max(0)-v.max(0))))
 assert difference<.00004,q['name'];rows.append({'name':q['name'],'max_bound_difference_m':float(difference)})
floors=[]
for f in sorted({r['model_file']for r in P['preimages']}):
 for name,tt in T(f):
  if not(name.endswith('_Floor')or name=='D04PF_ReceivedFloor'):continue
  for t in tt:
   if np.max(abs(t[:,1]-16.26))<.00004 and Polygon(t[:,[0,2]]).area>1e-7:floors.append((name,Polygon(t[:,[0,2]])))
contacts=[]
for b in P['bridges']:
 for x in [-28.65,-27.45]:
  for z in [b['bounds'][0][2]-.2,b['bounds'][1][2]+.2]:
   owners=sorted({n for n,p in floors if p.buffer(.00004).covers(Point(x,z))});assert owners,(b['index'],x,z)
   contacts.append({'bridge':b['index'],'at':[x,16.26,z],'original_floor_owners':owners,'new_bearer_contact_y':16.26})
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for r in P['native_export_records']:assert sha(W/r['native'])==r['native_sha256']and sha(W/r['export'])==r['export_sha256']
report={'status':'PASS','owned_meshes_verified':len(rows),'owned_mesh_bounds':rows,'original_floor_bearer_endpoint_contacts':contacts,'source_pins_unchanged':len(P['source_pins']),'fresh_native_repeat_identical':True,'production_active':False,'primary_load_accepted':False}
(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print('PRIVATE_COURT_SOURCE_PASS',len(rows),len(contacts))
