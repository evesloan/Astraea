"""Counter seams, actual support surfaces, meaningful voids and finite drawer sweep."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.spatial import cKDTree
from independent_geometry import Native,SourceCache,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07';BASE=ROOT/'assets/hospitality_counters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns={str(i):Native(BASE/'exports'/f'AST-HSP-00{i}.glb') for i in [1,2]};tests=[]
def check(name,value,expected=True,**extra):
 tests.append({'name':name,'pass':bool(value)==expected,**extra})
def ray(n,name,a,b,empty=True,**sel):
 hits=n.segment_hits(C@a,C@b,**sel);check(name,not hits,empty,source_segment_m=[a,b],hit_count=len(hits),hits=hits[:3])
for i,n in ns.items():
 m=json.loads((BASE/f'AST-HSP-00{i}.manifest.json').read_text())
 for rec in m['physical_contacts']:
  p=np.asarray(rec['glb_m']);d=n.nearest(p,role='dark_rubber' if 'floor' in rec['name'] else 'warm_stone')
  check(f'{i}_{rec["name"]}',d['distance_m']<1e-6,frame_error_m=float(np.linalg.norm(C@rec['source_m']-p)),nearest=d)
 check(i+'_floor',abs(n.tris[:,:,1].min())<1e-6)
for x in [.4,1.2,2.0]:
 for z in [.30,.55]:ray(ns['1'],f'rear_open_{x}_{z}',[x,.65,z],[x,-.24,z])
 ray(ns['1'],f'guest_body_{x}',[x,-1.10,.5],[x,-.40,.5])
 ray(ns['1'],f'staff_body_{x}',[x,1.10,.5],[x,.44,.5])
ray(ns['1'],'blocked_guest_fascia_control',[1.2,-.44,.55],[1.2,-.30,.55],False)
for t in [.2,.75,1.4]:
 def point(d,z):return[(.62-d)*np.sin(t),.62-(.62-d)*np.cos(t),z]
 for z in [.3,.55]:ray(ns['2'],f'curved_service_open_{t}_{z}',point(.57,z),point(-.22,z))
ray(ns['2'],'curved_blocked_fascia_control',[.88/2**.5,.62-.88/2**.5,.55],[.99/2**.5,.62-.99/2**.5,.55],False)
seams=[]
for role in ['warm_stone','warm_walnut','ivory_enamel','dark_rubber','champagne_metal']:
 a=ns['1'].tris[ns['1'].select(role=role)].reshape(-1,3);b=ns['2'].tris[ns['2'].select(role=role)].reshape(-1,3)
 a=np.unique(a[np.abs(a[:,0]-2.399)<1e-6],axis=0);b=np.unique(b[np.abs(b[:,0]-.001)<1e-6],axis=0)
 assert len(a)>0 and len(b)>0,(role,len(a),len(b))
 err=max(cKDTree(a[:,1:]).query(b[:,1:])[0].max(),cKDTree(b[:,1:]).query(a[:,1:])[0].max());gap=float(b[:,0].min()+2.4-a[:,0].max())
 rec={'role':role,'cap_vertices':[len(a),len(b)],'section_error_m':float(err),'gap_m':gap};seams.append(rec);check('seam_'+role,err<1e-6 and abs(gap-.002)<1e-6,**rec)
# Actual source semantic parts establish drawer pan/runner contact, then export parity binds it.
s=SourceCache(OUT/'independent_source_AST-HSP-001.json')
for x in [.8415,1.5585]:
 p=C@[x,.03,.646];pan=s.nearest(p,node='drawer_open_pan_bottom');rail=s.nearest(p,node='fixed_drawer_runner')
 check('drawer_bearing_'+str(x),pan['distance_m']<1e-6 and rail['distance_m']<1e-6,pan=pan,runner=rail)
# Triangle-centroid probes are finite moving-surface evidence; touching supports are not treated as penetration.
n=ns['1'];moving=n.tris[n.select(node='proposed_linen_drawer')];centers=moving.mean(axis=1);centers=np.unique(np.round(centers,7),axis=0)
probes=centers[::max(1,len(centers)//180)]
sweeps=[]
for label,axis in [('documented_GLb_axis',[0,0,-1]),('wrong_source_axis_used_in_GLb',[0,1,0])]:
 hit=[]
 for p in probes:
  hh=[h for h in n.segment_hits(p+np.asarray(axis)*1e-5,p+np.asarray(axis)*.32,node='__static__') if h['fraction']>1e-5]
  if hh:hit.append({'from_native_m':p.tolist(),'hits':hh[:1]})
 rec={'axis':axis,'probe_count':len(probes),'blocked_probe_count':len(hit),'examples':hit[:4]};sweeps.append({'name':label,**rec})
 check(label,not hit,label=='documented_GLb_axis',**rec)
out={'pass':len(tests)>25 and all(t['pass'] for t in tests),'checks':tests,'seams':seams,'sweeps':sweeps,'inputs':[{'path':str(n.path.relative_to(ROOT)),'sha256':sha(n.path)} for n in ns.values()],'scope':'Actual native-GLB surfaces and independently evaluated source semantic support surfaces. Finite probes establish bounded component evidence only; no continuous collision/installed-room/mechanical claim.'}
(OUT/'independent_counter_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'check_count':len(tests),'failures':[t for t in tests if not t['pass']]},indent=2))
