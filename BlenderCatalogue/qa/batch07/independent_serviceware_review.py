"""Actual storage support/withdrawal and trolley native hierarchy/contact probes."""
from pathlib import Path
import json,hashlib,numpy as np
from independent_geometry import Native,SourceCache,C,rotate_axis
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07';BASE=ROOT/'assets/hospitality_serviceware';tests=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value,**kw):tests.append({'name':name,'pass':bool(value),**kw})
ns={i:Native(BASE/'exports'/f'AST-HSP-00{i}.glb') for i in [5,6]}
ss={i:SourceCache(OUT/f'independent_source_AST-HSP-00{i}.json') for i in [5,6]}
for i,n in ns.items():
 m=json.loads((BASE/f'AST-HSP-00{i}.manifest.json').read_text());lookup={o.get('name'):j for j,o in enumerate(n.g.doc['nodes'])}
 for r in m['native_marker_records']:
  p=np.asarray(r['position_gltf_yup_m']);actual=n.world[lookup[r['node']]][:3,3];source=r.get('support_mesh',r.get('foot_mesh',r.get('wheel_mesh','006_rear_dark_push_grip')))
  near=ss[i].nearest(p,node=source);export=n.nearest(p)
  check(str(i)+'_'+r['node'],np.linalg.norm(actual-p)<1e-6 and np.linalg.norm(C@r['position_blender_m']-p)<1e-6 and near['distance_m']<1e-6 and export['distance_m']<1e-6,nearest_named_source=near,nearest_export=export,native_marker_m=actual.tolist())
 for st in m['stock_groups']:
  mask=np.asarray([st['node'] in x for x in ss[i].nodes]);v=ss[i].tris[mask].reshape(-1,3);check(st['node']+'_bottom_support_height',abs(v[:,1].min()-st['support_z_m'])<1e-6,measured_native_y=float(v[:,1].min()))
# Retained tests for every stacked support relationship, not merely a nominal marker.
s=ss[5]
for kind,count,levels in [('tray',2,3),('plate',4,2)]:
 for lev in range(levels):
  for k in range(1,count):
   low=f'005_{kind}_stock_{lev}_piece_{k-1}';high=f'005_{kind}_stock_{lev}_piece_{k}';v=np.unique(s.tris[s.nodes==high].reshape(-1,3),axis=0)
   ds=[s.nearest(p,node=low)['distance_m'] for p in v];check(high+'_rests_on_previous',min(ds)<1e-6,minimum_vertex_to_surface_gap_m=float(min(ds)),sampled_upper_vertices=len(v))
 for lev,z in enumerate([.245,.473,.701] if kind=='tray' else [.245,.535]):
  for k,x in enumerate([-.462,.024] if kind=='tray' else [.080,.468]):
   p=C@[x,.02,z-.020];a=s.nearest(p,node=f'005_{kind}_shelf_{lev}');b=s.nearest(p,node=f'005_{kind}_shelf_{lev}_folded_cleat_{k}')
   check(f'{kind}_{lev}_cleat_{k}_contact',a['distance_m']<1e-6 and b['distance_m']<1e-6,shelf=a,cleat=b)
# Explicit tray-withdrawal surface sweeps against fixed carcass, plus wrong-axis obstruction controls.
n=ns[5]
for lev in range(3):
 t=n.tris[n.select(node=f'005_tray_stock_{lev}__')];probes=np.unique(np.round(t.mean(axis=1),7),axis=0)[::3];probes=probes[probes[:,1]>[.245,.473,.701][lev]+1e-5] # Established tangential bearing plane is contact, not obstructed travel
 for label,axis in [('rear',[0,0,-1]),('wrong_up',[0,1,0])]:
  blocks=[]
  for p in probes:
   h=n.segment_hits(p+np.asarray(axis)*1e-5,p+np.asarray(axis)*.72,node='005_fixed_carcass')
   if h:blocks.append(h[0])
  check(f'tray_{lev}_{label}',(not blocks) if label=='rear' else bool(blocks),probe_count=len(probes),blocked_count=len(blocks),examples=blocks[:2])
# Actual fork/wheel nodes, pivots and finite rotation at native Y-up.
n=ns[6];m=json.loads((BASE/'AST-HSP-006.manifest.json').read_text());lookup={o.get('name'):j for j,o in enumerate(n.g.doc['nodes'])}
for r in m['wheels']:
 si=lookup[r['swivel_node']];ai=lookup[r['axle_node']];sp=np.asarray(r['swivel_pivot_gltf_yup_m']);wc=np.asarray(r['wheel_center_gltf_yup_m'])
 check(r['tag']+'_native_pivots',np.linalg.norm(n.world[si][:3,3]-sp)<1e-6 and np.linalg.norm(n.world[ai][:3,3]-wc)<1e-6 and n.parents[ai]==si)
 def descendants(i):
  found={i}
  for ch in n.g.doc['nodes'][i].get('children',[]):found|=descendants(ch)
  return found
 vi=np.concatenate([n.node_vertices[j] for j in descendants(si) if j in n.node_vertices]);wheel=np.concatenate([n.node_vertices[j] for j in descendants(ai) if j in n.node_vertices])
 radial=np.linalg.norm((vi-sp)[:,[0,2]],axis=1).max();check(r['tag']+'_sweep_radius',radial<=.091,measured_radius_m=float(radial))
 floors=[];wrong=[]
 for angle in np.arange(24)*np.pi/12:
  v=np.asarray([sp+rotate_axis(p-sp,[0,1,0],angle) for p in vi]);floors.append(float(v[:,1].min()))
  w=np.asarray([sp+rotate_axis(p-sp,[0,0,1],angle) for p in vi]);wrong.append(float(w[:,1].min()))
 check(r['tag']+'_swivel_preserves_floor',max(abs(x) for x in floors)<1e-6,native_floor_range=[min(floors),max(floors)],angle_samples=24)
 check(r['tag']+'_wrong_axis_sensitive',max(abs(x) for x in wrong)>.01,wrong_floor_range=[min(wrong),max(wrong)])
 spin=[]
 for angle in np.arange(24)*np.pi/12:
  v=np.asarray([wc+rotate_axis(p-wc,[1,0,0],angle) for p in wheel]);spin.append(float(v[:,1].min()))
 check(r['tag']+'_axle_spin_floor',max(abs(x) for x in spin)<1e-6,floor_range=[min(spin),max(spin)])
# Physical grip underhand approach and tier void controls.
for x in [-.16,0,.16]:
 h=n.segment_hits(C@[x,.50,.86],C@[x,.30,.86]);check('grip_underhand_void_'+str(x),not h,hits=h[:2])
 h=n.segment_hits(C@[x,.40,.5],C@[x,-.18,.5]);check('lower_tier_access_'+str(x),not h,hits=h[:2])
h=n.segment_hits(C@[0,.40,.20],C@[0,0,.20]);check('blocked_lower_tier_control',bool(h),hit_count=len(h))
out={'pass':len(tests)>60 and all(t['pass'] for t in tests),'checks':tests,'inputs':[{'path':str(n.path.relative_to(ROOT)),'sha256':sha(n.path)} for n in ns.values()],'scope':'Actual GLB native-frame transforms and independently evaluated source support surfaces. Twenty-four swivel/axle samples are geometric controls only; no rolling, cargo, controller, mechanical/load or whole-room certification.'}
(OUT/'independent_serviceware_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'check_count':len(tests),'failures':[t for t in tests if not t['pass']]},indent=2))
