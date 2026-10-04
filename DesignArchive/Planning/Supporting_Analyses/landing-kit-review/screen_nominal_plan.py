from pathlib import Path
import json,hashlib,math,itertools,struct
import numpy as np
ROOT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
OUT=Path(__file__).resolve().parent
P=ROOT/'qa/batch11/assembly/plan.json';C=ROOT/'batches/batch11/CONTRACT.md'
L=ROOT/'references/landings/R3_constraint_ledger.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads(P.read_text());ledger=json.loads(L.read_text())
assert sha(L)==plan['input_ledger_sha256']
def read_glb(path):
 b=path.read_bytes();magic,version,length=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and length==len(b);i=12;chunks={}
 while i<len(b):
  n,t=struct.unpack_from('<II',b,i);i+=8;chunks[t]=b[i:i+n];i+=n
 g=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
 def acc(idx):
  a=g['accessors'][idx];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);item=np.dtype(dt).itemsize;stride=v.get('byteStride',n*item)
  return np.ndarray((a['count'],n),dtype=dt,buffer=blob,offset=off,strides=(stride,item)).copy()
 def matrix(node):
  if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
  x,y,z,w=node.get('rotation',[0,0,0,1]);R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
  m=np.eye(4);m[:3,:3]=R@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
 tris=[]
 def walk(idx,parent):
  node=g['nodes'][idx];M=parent@matrix(node)
  if 'mesh' in node:
   for q in g['meshes'][node['mesh']]['primitives']:
    assert q.get('mode',4)==4
    p=acc(q['attributes']['POSITION']);p=(M@np.column_stack([p,np.ones(len(p))]).T).T[:,:3]
    ii=acc(q['indices']).reshape(-1) if 'indices' in q else np.arange(len(p));tris.append(p[ii].reshape(-1,3,3))
  for c in node.get('children',[]):walk(c,M)
 for idx in g['scenes'][g.get('scene',0)]['nodes']:walk(idx,np.eye(4))
 return np.concatenate(tris)


sources={'AST-LND-001':[[-.7,.7],[0,.65],[0,2.8]],'AST-LND-002':[[-.7,.7],[0,.75],[0,1.05]],'AST-LND-003':[[-.65,.65],[0,.45],[0,2.5]],'AST-LND-004':[[-.75,.75],[0,.75],[0,1.05]]}
R3=ledger['candidate_dispositions'][2];landing={r['name']:r for r in R3['reservations'] if 'landing' in r['name']}
def overlap(x,z,r):return max(0,min(x[1],r['ship_x'][1])-max(x[0],r['ship_x'][0]))*max(0,min(z[1],r['ship_z'][1])-max(z[0],r['ship_z'][0]))
report={'scope':'Proposed component-envelope and declared-context bounds screen only. No final new-component mesh, attachment, collision, body/cart, moving-door, floor/support or host-fit acceptance.','plan_sha256':sha(P),'contract_sha256':sha(C),'R3_ledger_sha256':sha(L),'items':[]}
for item in plan['items']:
 a=math.radians(item['source_z_rotation_deg']);c,s=math.cos(a),math.sin(a);origin=item['ship_origin_m'];pts=[]
 for x,y,z in itertools.product(*sources[item['catalogue_id']]):
  bx,by=c*x-s*y,s*x+c*y;pts.append([origin[0]+bx,origin[1]+z,origin[2]-by])
 mn=[min(v[k] for v in pts) for k in range(3)];mx=[max(v[k] for v in pts) for k in range(3)];given=item['candidate_ship_bounds_m']
 assert max(abs(mn[k]-given['min'][k]) for k in range(3))<1e-8 and max(abs(mx[k]-given['max'][k]) for k in range(3))<1e-8
 B=item['inspection_source_origin_m'];inspection=[B[0]-44,B[2],-B[1]-378]
 assert max(abs(inspection[k]-origin[k]) for k in range(3))<1e-8
 front=[s,0,c] # source front (0,-1,0) after rotation, then Y-up ship mapping
 host=landing['Guest landing' if item['key'].startswith('guest') else 'Service landing']
 assert mn[0]>=host['x'][0] and mx[0]<=host['x'][1] and mn[2]>=host['z'][0] and mx[2]<=host['z'][1]
 hits=[{'name':r['name'],'area_m2':overlap([mn[0],mx[0]],[mn[2],mx[2]],r)} for r in plan['empty_plan_reservations'] if overlap([mn[0],mx[0]],[mn[2],mx[2]],r)>1e-8]
 assert not hits,hits
 rec={'key':item['key'],'computed_bounds_ship_m':{'min':mn,'max':mx},'front_ship_xyz':front,'inside_R3_landing':True,'empty_reservation_intersections':hits,'core_plane_z_minus378_gap_m':round(mn[2]+378,6),'cross_street_start_z_minus374_gap_m':round(-374-mx[2],6),'height_kind':item['height_kind']}
 report['items'].append(rec)
report['margins']={'guest_each_component_to_central_strip_m':0.1,'guest_outside_landing_edges_m':0.1,'guest_directory_front_strip_gap_m':2.15,'guest_waiting_front_strip_gap_m':2.05,'staff_return_to_west_empty_region_m':0.65,'staff_stow_to_west_empty_region_m':0.25,'staff_component_z_separation_m':0.1}
report['directions']={'guest':'Front +shipZ; core-bound approach moves -Z from the shared cross-street/guest spur. Central and full-width front empty strips remain connected.','staff':'Front -shipX; D12 west-side approach moves +X, then can turn -Z toward the unknown core plane. Upper +Z exit to shared cross-street remains open.'}
report['context']=[]
for context in plan['context']:
 parent=next(r for r in plan['items'] if r['key']==context['parent'])
 glb=ROOT/context['path'];t=read_glb(glb);v=t.reshape(-1,3);v=v[:,[0,2,1]];v[:,1]*=-1
 M=np.array(context['parent_local_source_matrix']);v=(M@np.column_stack([v,np.ones(len(v))]).T).T[:,:3]
 a=math.radians(parent['source_z_rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 v=v@R.T;v=v[:,[0,2,1]];v[:,2]*=-1;v+=np.array(parent['ship_origin_m']);mn=v.min(0);mx=v.max(0);B=parent['candidate_ship_bounds_m']
 inside=bool((mn>=np.array(B['min'])-1e-5).all() and (mx<=np.array(B['max'])+1e-5).all())
 hits=[{'name':r['name'],'area_m2':overlap([mn[0],mx[0]],[mn[2],mx[2]],r)} for r in plan['empty_plan_reservations'] if overlap([mn[0],mx[0]],[mn[2],mx[2]],r)>1e-8]
 report['context'].append({'key':context['key'],'glb_sha256':sha(glb),'ship_min_m':mn.tolist(),'ship_max_m':mx.tolist(),'inside_parent_candidate_envelope':inside,'empty_plan_reservation_intersections':hits,'attachment_support_light_aim':'unverified'})
report['context_status']='Existing fixture meshes transformed at current proposed parent placements; their bounding extents are checked, while mounting, support, aim and final assembled meshes remain for later review.' 
report['unresolved']=plan['unknown_host_dimensions']
report['cautions']=['Component target heights are not verified host headroom.','0.1m nominal separations/edge margins are not trim allowance or actor clearance.','Unknown moving door/cassette fit may constrain these candidate positions later.','The 6x4m landing reservation is not a safe solid envelope; named empty strips must remain empty.','D12 pit/slab and D11 Music coexistence and upper-hull fit remain unresolved.']
assert sha(P)==report['plan_sha256'] and sha(C)==report['contract_sha256'] and sha(L)==report['R3_ledger_sha256']
report['status']='Pass nominal placement, facing and reserved-plan logic only' if all(r['inside_parent_candidate_envelope'] and not r['empty_plan_reservation_intersections'] for r in report['context']) else 'Main nominal boxes pass; context envelope conflict needs review'
(OUT/'batch11_nominal_screen.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
