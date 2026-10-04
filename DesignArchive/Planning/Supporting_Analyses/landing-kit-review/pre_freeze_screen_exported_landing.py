from pathlib import Path
import json,hashlib,struct,math,argparse
import numpy as np
A=argparse.ArgumentParser();A.add_argument('--frozen',action='store_true');A.add_argument('--preflight',default='qa/batch11/assembly/r01/preflight.json');args=A.parse_args()
ROOT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');OUT=Path(__file__).resolve().parent
P=ROOT/'qa/batch11/assembly/plan.json';C=ROOT/'batches/batch11/CONTRACT.md';F=ROOT/args.preflight
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads(P.read_text());pre=json.loads(F.read_text());assert pre['execution_complete'] and pre['inputs_unchanged_during_execution'];assert pre['plan_sha256']==sha(P)
inputs={str(p.relative_to(ROOT)):sha(p) for p in [P,C,F,ROOT/plan['input_ledger']]}
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


def ship_triangles(item,parent=None):
 t=read_glb(ROOT/item['path']);shape=t.shape;v=t.reshape(-1,3);v=v[:,[0,2,1]];v[:,1]*=-1
 owner=item
 if parent:
  M=np.array(item['parent_local_source_matrix']);v=(M@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];owner=parent
 a=math.radians(owner['source_z_rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 v=v@R.T;v=v[:,[0,2,1]];v[:,2]*=-1;v+=np.array(owner['ship_origin_m']);return v.reshape(shape)

def area(mn,mx,r):return max(0,min(mx[0],r['ship_x'][1])-max(mn[0],r['ship_x'][0]))*max(0,min(mx[2],r['ship_z'][1])-max(mn[2],r['ship_z'][0]))
report={'scope':'Independent actual six-GLB transformed-bounds and reservation screen. Does not verify host support, door/cassette, headroom, mechanism, actor/cart/species fit, contact/mount quality or visual acceptance.','phase':'final frozen receipt' if args.frozen else 'current snapshot; author source freeze not yet confirmed','source_precision_note':'Node/accessor transforms recomputed in double precision. Nominal-envelope tolerance1e-5m; Blender receipt comparison tolerance2e-5m at large world Z. These are numeric tolerances, not architectural clearance.','items':[]}
for item in plan['items']+plan['context']:
 context='parent' in item;parent=next((r for r in plan['items'] if r['key']==item.get('parent')),None)
 witness=next(r for r in pre['context' if context else 'items'] if r['key']==item['key'])
 if context:
  assert sha(ROOT/item['path'])==witness['sha256'];inputs[item['path']]=witness['sha256'];inputs[item['declared_placement_source']]=sha(ROOT/item['declared_placement_source'])
 else:
  for field,h in witness['hashes'].items():assert sha(ROOT/item[field])==h;inputs[item[field]]=h
 t=ship_triangles(item,parent);v=t.reshape(-1,3);assert np.isfinite(v).all();mn=v.min(0);mx=v.max(0);assert len(t)==witness['triangles']
 delta=max(np.max(np.abs(mn-witness['actual_ship_bounds_m']['min'])),np.max(np.abs(mx-witness['actual_ship_bounds_m']['max'])));assert delta<2e-5,(item['key'],delta)
 B=(parent or item)['candidate_ship_bounds_m'];inside=bool((mn>=np.array(B['min'])-1e-5).all() and (mx<=np.array(B['max'])+1e-5).all());assert inside,item['key']
 intersections=[{'reservation':r['name'],'overlap_m2':area(mn,mx,r)} for r in plan['empty_plan_reservations'] if area(mn,mx,r)>1e-8];assert not intersections,(item['key'],intersections)
 report['items'].append({'key':item['key'],'kind':'disclosed existing fixture context' if context else 'new component','glb_sha256':sha(ROOT/item['path']),'triangle_count':len(t),'actual_ship_min_m':mn.tolist(),'actual_ship_max_m':mx.tolist(),'lead_import_bounds_max_delta_m':float(delta),'inside_candidate_envelope':inside,'empty_plan_reservation_intersections':intersections})
report['source_triangles']=sum(r['triangle_count'] for r in report['items']);assert report['source_triangles']==pre['source_geometry_triangles']
report['margins_and_limits']=['Guest component central-strip and outer-edge nominal margins are0.1m.','Staff return/stow retain0.1m between their Z bounds; stow is0.25m east of the west empty region.','Actual fixtures fit their parent candidate boxes. Attachment normals, contact, support and emitter aim are separately reviewed.','Target heights are newly authored component dimensions, not host headroom.','No solid enters the listed empty plan strips at any height in the six checked meshes. No general walking/cart clearance is inferred.','Unknown moving-door pockets, core openings, structure, pit/Music coexistence and upper hull may still constrain the proposal.']
for name,h in inputs.items():assert sha(ROOT/name)==h,('changed_during_screen',name)
report['input_hash_guard']='passed before/after read-only screen';report['input_sha256']=inputs;report['status']='PASS actual transformed-bounds and reservation screen only'
name='batch11_frozen_export_screen.json' if args.frozen else 'batch11_current_export_screen.json'
(OUT/name).write_text(json.dumps(report,indent=2))
print(json.dumps({'status':report['status'],'phase':report['phase'],'file':str(OUT/name),'sha256':sha(OUT/name),'meshes':len(report['items']),'triangles':report['source_triangles'],'max_import_bounds_delta_m':max(r['lead_import_bounds_max_delta_m'] for r in report['items']),'input_guard':report['input_hash_guard']},indent=2))
