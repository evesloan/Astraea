from pathlib import Path
import numpy as np,json,struct,math,hashlib
ROOT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
OUT=Path(__file__).resolve().parent
P=ROOT/'qa/batch10/assembly/plan.json';F=ROOT/'qa/batch10/assembly/preflight.json'
plan=json.loads(P.read_text());preflight=json.loads(F.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

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

def to_ship(tris,item):
 # glTF(x,y,z) -> Blender source(x,-z,y), then proposed Z rotation and ship translation.
 p=tris[..., [0,2,1]].copy();p[...,1]*=-1
 p+=np.array(item.get('_context_source_translation_m',[0,0,0]))
 a=math.radians(item['source_z_rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 p=p@R.T
 p=p[..., [0,2,1]];p[...,2]*=-1;p+=np.array(item['ship_origin_m']);return p

def clip_prism(poly,lo,hi):
 out=list(poly)
 for k in range(3):
  for sign,bound in [(1,lo[k]),(-1,hi[k])]:
   ps=out;out=[]
   if not ps:return []
   for a,b in zip(ps,ps[1:]+ps[:1]):
    da=sign*(a[k]-bound);db=sign*(b[k]-bound)
    if da>=0:out.append(a)
    if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
 return out

result={'scope':'Independent read-only exported-mesh reservation screen. Six new components plus four disclosed QA-context meshes. No host fit, body/cart swept volume, floor support, moving-door or visual acceptance.','plan_sha256':sha(P),'preflight_sha256':sha(F),'tolerance_m':1e-5,'items':[]}
alltris=[]
for item in plan['items']:
 path=ROOT/item['path'];t=to_ship(read_glb(path),item);alltris.append(t);v=t.reshape(-1,3);mn=v.min(0);mx=v.max(0)
 witness=next(r for r in preflight['items'] if r['key']==item['key']);assert sha(path)==witness['glb_sha256']
 diff=max(np.max(np.abs(mn-witness['actual_bounds']['min_ship_m'])),np.max(np.abs(mx-witness['actual_bounds']['max_ship_m'])))
 assert diff<2e-5,(item['key'],diff)
 tram_hit=(min(mx[0],45)>max(mn[0],35)+1e-5 and min(mx[2],52)>max(mn[2],-52)+1e-5)
 # Continuous mesh intersection check within 4m x 3.08m proposed strip, with boundary tolerance.
 lo=np.array([46,.01,-2+1e-5]);hi=np.array([98,3.09,2-1e-5]);cand=t[(t.max(1)>=lo).all(1)&(t.min(1)<=hi).all(1)]
 intrusions=sum(bool(clip_prism(list(q),lo,hi)) for q in cand)
 rec={'key':item['key'],'glb_sha256':sha(path),'min_ship_m':mn.tolist(),'max_ship_m':mx.tolist(),'imported_preflight_bounds_max_delta_m':float(diff),'positive_plan_overlap_with_tram_reserve':bool(tram_hit),'mesh_triangles_inside_proposed_strip_interior':intrusions,'new_component_triangles':len(t)}
 assert not tram_hit and intrusions==0,rec
 result['items'].append(rec)
result['qa_context']=[]
for context in preflight['context']:
 parent=next(r for r in plan['items'] if r['key']==context['parent_component'])
 item={**parent,'_context_source_translation_m':context['local_source_translation_m']}
 path=ROOT/context['path'];assert sha(path)==context['sha256']
 t=to_ship(read_glb(path),item);v=t.reshape(-1,3);mn=v.min(0);mx=v.max(0)
 diff=max(np.max(np.abs(mn-context['actual_bounds']['min_ship_m'])),np.max(np.abs(mx-context['actual_bounds']['max_ship_m'])))
 assert diff<2e-5,(context['key'],diff)
 tram_hit=(min(mx[0],45)>max(mn[0],35)+1e-5 and min(mx[2],52)>max(mn[2],-52)+1e-5)
 lo=np.array([46,.01,-2+1e-5]);hi=np.array([98,3.09,2-1e-5]);cand=t[(t.max(1)>=lo).all(1)&(t.min(1)<=hi).all(1)]
 intrusions=sum(bool(clip_prism(list(q),lo,hi)) for q in cand)
 rec={'key':context['key'],'glb_sha256':sha(path),'min_ship_m':mn.tolist(),'max_ship_m':mx.tolist(),'imported_preflight_bounds_max_delta_m':float(diff),'positive_plan_overlap_with_tram_reserve':bool(tram_hit),'mesh_triangles_inside_proposed_strip_interior':intrusions,'mesh_triangles':len(t),'new_design':False,'production_dependency':False,'support_and_actor_fit':'not tested'}
 assert not tram_hit and intrusions==0,rec
 result['qa_context'].append(rec)
q=[r for r in result['items'] if r['key'] in ['quiet','cove']];mn=np.array([r['min_ship_m'] for r in q]).min(0);mx=np.array([r['max_ship_m'] for r in q]).max(0)
result['quiet_cove_group']={'min_ship_m':mn.tolist(),'max_ship_m':mx.tolist(),'candidate_zone_x':[60,67.2],'candidate_zone_z':[-7.4,-2],'maximum_height_m':3.8,'route_edge_margin_m':round(-2-mx[2],6),'height_margin_m':round(3.8-mx[1],6),'x_side_margins_m':[round(mn[0]-60,6),round(67.2-mx[0],6)]}
assert mn[0]>=60-1e-5 and mx[0]<=67.2+1e-5 and mn[2]>=-7.4-1e-5 and mx[2]<=-2+1e-5 and mx[1]<=3.8+1e-5
terminal=next(r for r in result['items'] if r['key']=='terminal');service=next(r for r in result['items'] if r['key']=='service');portal=next(r for r in result['items'] if r['key']=='portal')
result['portal_terminal']={'portal_to_tram_min_x_gap_m':round(portal['min_ship_m'][0]-45,6),'terminal_strip_z_margin_m':round(terminal['min_ship_m'][2]-2,6),'inside_historical_terrace_z_sample':terminal['min_ship_m'][2]>=-14 and terminal['max_ship_m'][2]<=14,'floor_support_and_host_guard_fit':'unverified','guest_door_x52_nominal_x_gap_m':round(52-max(portal['max_ship_m'][0],terminal['max_ship_m'][0]),6),'moving_door_sweep_and_cassette':'unknown; positive nominal gap is not mechanism fit'}
result['service_end']={'nominal_gap_to_historical_service_door_plane_x98_m':round(98-service['max_ship_m'][0],6),'route_edge_margin_m':round(service['min_ship_m'][2]-2,6),'host_guest_polygon_and_cassette':'unknown'}
result['strip_check']={'x':[46,98],'y':[.01,3.09],'z':[-1.99999,1.99999],'method':'Exact triangle/polygon clipping against an open-boundary planning prism, tolerance 0.00001m; six new component meshes and four disclosed QA-context meshes','actor_cart_clearance_certification':False,'unknown_host_leaves_x52_x98_excluded':True}
controls=[]
for name,tris,lo,hi in [('portal_jamb_blocked',alltris[0],np.array([47.9,.5,2.3]),np.array([49.4,1.5,2.45])),('quiet_back_blocked',alltris[2],np.array([63,.5,-5.25]),np.array([64,1.5,-4.7]))]:
 cand=tris[(tris.max(1)>=lo).all(1)&(tris.min(1)<=hi).all(1)]
 n=sum(bool(clip_prism(list(t),lo,hi)) for t in cand)
 assert n>0,(name,n)
 controls.append({'name':name,'intersecting_triangles':n,'passed':True})
result['positive_geometry_controls']=controls
assert sha(P)==result['plan_sha256'] and sha(F)==result['preflight_sha256']
for item in plan['items']:
 rec=next(r for r in result['items'] if r['key']==item['key']);assert sha(ROOT/item['path'])==rec['glb_sha256']
for item in preflight['context']:
 rec=next(r for r in result['qa_context'] if r['key']==item['key']);assert sha(ROOT/item['path'])==rec['glb_sha256']
result['input_hashes_unchanged_after_screen']=True
result['status']='passes geometric reservation screen for six new components and four QA-context meshes only'
(OUT/'exported_arrangement_screen.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
