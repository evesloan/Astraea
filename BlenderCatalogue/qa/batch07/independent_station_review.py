"""Station physical contacts, hollow openings, child frames and proposed removals."""
from pathlib import Path
import json,hashlib,numpy as np,itertools
from independent_geometry import Native,SourceCache,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07';BASE=ROOT/'assets/hospitality_stations';tests=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value,**kw):tests.append({'name':name,'pass':bool(value),**kw})
ns={i:Native(BASE/'exports'/f'AST-HSP-00{i}.glb') for i in [3,4]};ss={i:SourceCache(OUT/f'independent_source_AST-HSP-00{i}.json') for i in [3,4]}
for i,n in ns.items():
 m=json.loads((BASE/f'AST-HSP-00{i}.manifest.json').read_text());lookup={o.get('name'):j for j,o in enumerate(n.g.doc['nodes'])}
 for j,node in enumerate(n.g.doc['nodes']):
  ex=node.get('extras',{});p=ex.get('position_gltf_yup_m')
  if p is None:continue
  actual=n.world[j][:3,3];check(str(i)+'_marker_frame_'+node['name'],np.linalg.norm(actual-p)<1e-6 and np.linalg.norm(C@ex['position_blender_source_m']-p)<1e-6,actual_native_world_m=actual.tolist())
  kind=ex['kind'];name=node['name']
  if kind in ['physical_support_contact','physical_annular_base_contact','physical_receiving_floor','physical_caddy_runner_contact','physical_drip_base_contact']:
   near=n.nearest(p);check(str(i)+'_physical_'+name,near['distance_m']<1e-6,nearest=near)
  if name.startswith('CUP_BASE_RING_CONTACT') or name.startswith('CUP_PLACEMENT'):
   check(name+'_follows_drip',n.parents.get(j)==lookup['DRIP_TRAY'])
  if name in ['CADDY_STAFF_GRIP','DISH_TRAY_RECEIVING_SURFACE']:
   check(name+'_follows_caddy',n.parents.get(j)==lookup['RECEIVING_CADDY'])
 for r in m['proposed_motion_nodes']:
  idx=lookup[r['name']];axis=np.asarray(r['translation_axis_gltf_yup']);check(r['name']+'_axis',np.linalg.norm(axis-C@r['translation_axis_blender_source'])<1e-8)
  t=n.tris[n.select(node='__'+r['name']+'__')];centers=np.unique(np.round(t.mean(axis=1),7),axis=0);centers=centers[centers[:,1]>(.052 if i==3 else .874)+1e-5];probes=centers[::max(1,len(centers)//190)]
  for label,vec in [('correct',axis),('wrong_source_axis',np.asarray(r['translation_axis_blender_source']))]:
   hits=[]
   for p in probes:
    h=n.segment_hits(p+vec*1e-5,p+vec*r['travel_m'],node='__static__')
    if h:hits.append(h[0])
   check(r['name']+'_'+label,(not hits) if label=='correct' else bool(hits),probes=len(probes),blocked_count=len(hits),examples=hits[:3])
# Physical drip/base and caddy/rail contacts measured on both independent source surfaces.
for a,b,p in [('drip_catch_floor','weighted_rounded_base',[0,-.074,.052])]:
 ra=ss[3].nearest(C@p,node=a);rb=ss[3].nearest(C@p,node=b);check('drip_actual_bearing',ra['distance_m']<1e-6 and rb['distance_m']<1e-6,moving=ra,fixed=rb)
for x in [-.421,.421]:
 p=C@[x,.015,.874];ra=ss[4].nearest(p,node='caddy_rail_contact');rb=ss[4].nearest(p,node='caddy_runner');check('caddy_actual_bearing_'+str(x),ra['distance_m']<1e-6 and rb['distance_m']<1e-6,moving=ra,fixed=rb)
for x in [-.14,.14]:
 # Wall enters a real manifold and is no longer floating below the crown.
 hits=ss[3].segment_hits(C@[x+.012,-.095,.440],C@[x+.012,-.095,.451],node='ivory_twin_spout_manifold');check('spout_root_manifold_'+str(x),bool(hits),hits=hits)
 h=ns[3].segment_hits(C@[x,-.095,.370],C@[x,-.095,.431]);check('actual_open_nozzle_bore_'+str(x),not h,hits=h)
 h=ns[3].segment_hits(C@[x+.012,-.095,.370],C@[x+.012,-.095,.431]);check('nozzle_wall_blocked_control_'+str(x),bool(h),hit_count=len(h))
 for xx in [x-.045,x,x+.045]:
  for yy in [-.14,-.095,-.05]:
   h=ns[3].segment_hits(C@[xx,yy,.083],C@[xx,yy,.36]);check('cup_clear_'+str((xx,yy)),not h,hits=h)
for x in [-.225,0,.225]:
 for z in [.97,1.05,1.13]:
  h=ns[4].segment_hits(C@[x,-.5,z],C@[x,.2,z]);check('common_tray_entry_'+str((x,z)),not h,hits=h)
h=ns[4].segment_hits(C@[0,.015,.88],C@[0,.015,.9]);check('blocked_receiving_floor_control',bool(h),hit_count=len(h))
# Host counter support and standing-body zones in installed source coordinates.
host=Native(ROOT/'assets/hospitality_counters/exports/AST-HSP-001.glb');m=json.loads((BASE/'AST-HSP-003.manifest.json').read_text());offset=np.array([.7,0,.9])
for r in m['physical_contacts']:
 p=np.asarray(r['source_m'])+offset;d=host.nearest(C@p,role='warm_stone');check('host_'+r['name'],d['distance_m']<1e-6,nearest=d)
hv=host.tris.reshape(-1,3)@C;lo=hv.min(axis=0);hi=hv.max(axis=0)
for r in m['clearances']:
 if r['name'] not in ['guest_beverage_approach','staff_rear_service','above_worktop_guest_reach','above_worktop_staff_reach']:continue
 a=np.asarray(r['min_source_m'])+offset;b=np.asarray(r['max_source_m'])+offset;overlap=np.minimum(hi,b)-np.maximum(lo,a)
 check('host_reservation_'+r['name'],bool((overlap<=0).any()),installed_bounds=[a.tolist(),b.tolist()],aabb_overlap_lengths_m=overlap.tolist())
out={'pass':len(tests)>70 and all(t['pass'] for t in tests),'checks':tests,'inputs':[{'path':str(n.path.relative_to(ROOT)),'sha256':sha(n.path)} for n in list(ns.values())+[host]],'scope':'Actual native GLB and independent source semantic surfaces; source coordinates converted once, native hierarchy resolved before points are compared. Finite motion probes omit established tangential bearing plane. No fluid/food/electrical/device control, engine, mechanics or actor certification.'}
(OUT/'independent_station_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'check_count':len(tests),'failures':[t for t in tests if not t['pass']]},indent=2))
