from pathlib import Path
import json,hashlib,numpy as np,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';P=json.load(open(W/'D14_SHARED_RECEIVER_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005/glb_source_reader.py').read_text();u={'R':R,'PIN':[],'np':np};exec('import math, struct, json\n'+s[s.index('def read(p):'):s.index('def contacts(')],u)
F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';street=json.load(open(G/'data/architecture/TIDAL_AQUATIC_DOUBLE.json'))['street_model']
def read(p):
 f=Path(p).name
 if (W/f).exists():return(W/f).read_bytes()
 if f=='AST-STF-G3-003.glb':return(F/'exports'/f).read_bytes()
 return(R/p).read_bytes()
u['read']=read
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
receiver=dict(u['triangles'](N['receiving_export']));patch=dict(u['triangles'](N['named_patch_export']));assert len(receiver)==22 and len(patch)==3
for p in P['new_parts']:
 t=receiver[p['name']];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));b=p['aabb'];assert np.max(abs(lo-np.array([b[0],b[2],b[4]])))<1e-4;assert np.max(abs(hi-np.array([b[1],b[3],b[5]])))<1e-4,p['name']
f=receiver['D14_SharedReceiverMissingFloor'];top=f[np.all(abs(f[:,:,1]-88.5)<1e-4,axis=1)];norm=np.cross(top[:,1]-top[:,0],top[:,2]-top[:,0]);assert np.all(norm[:,1]>0),'upward winding';floorpoly=unary_union([Polygon(t[:,[0,2]])for t in top]);assert abs(floorpoly.area-P['missing_only_floor']['area_m2'])<1e-4
# Reuse exact triangle clipping from the local survey; it counts source surface intersections, not architecture acceptance.
u2={'__file__':str(W/'screen_local_candidates.py')};src=(W/'screen_local_candidates.py').read_text();exec(src[:src.index('results=[]')],u2);hit=u2['exact_hit'];matches=[]
def tri_key(t):return tuple(sorted(tuple(round(float(v),5)for v in pt)for pt in t))
for spec in P['named_source_replacements']:
 file='AST-STF-G3-003.glb'if spec['source_family']=='group3'else street;old=dict(u['triangles'](file))[spec['mesh']];new=patch[spec['mesh']];keys={tri_key(t)for t in new};lo=np.array(spec['cut']['min']);hi=np.array(spec['cut']['max']);uncut=[t for t in old if hit(np.array([t]),lo,hi)[0]==0];errors=[]
 for t in uncut:
  sorted_t=np.array(sorted(tuple(v)for v in t));best=min(np.max(abs(sorted_t-np.array(sorted(tuple(v)for v in q))))for q in new);errors.append(float(best));assert best<1e-4,(spec['mesh'],best)
 matches.append({'mesh':spec['mesh'],'unaffected_actual_original_triangles_matched':len(uncut),'source_export_coordinate_tolerance_m':.0001,'maximum_coordinate_error_m':max(errors,default=0),'export_triangles':len(new)})
# Screen all new post/beam members below the link against actual installed source, keeping declared toe wall/foot contact explicit.
existing=dict(u['triangles']('AST-RES-TIDAL_lift_fit_r003.glb'));existing.update({'D13/'+n:t for n,t in u['triangles']('AST-RES-TIDAL_D13_service_receiving_r001.glb')});existing.update({'D14Street/'+n:t for n,t in u['triangles'](street)if n!='D14_SouthStreetEndGuard'})
contacts=[]
for p in P['new_parts']:
 if p['category']not in['receiving_frame','named_d13_floor_receiver','named_existing_street_receiver']:continue
 b=p['aabb'];lo=np.array([b[0],b[2],b[4]]);hi=np.array([b[1],b[3],b[5]])
 for n,t in existing.items():
  c,ar=hit(t,lo,hi)
  if c:
   allowed=(p['category']=='named_d13_floor_receiver'and n.startswith('D13/TidalStaffWallLow_D13_-6_-63_0'))or(p['category']=='named_existing_street_receiver'and n=='D14Street/D14_SouthStreetFloor')
   contacts.append({'new_member':p['name'],'retained_receiver':n,'clipped_triangles':c,'intentional':allowed});assert allowed,(p['name'],n)
# Eight stationary rectangular adult proxies and floor points on this link only, with open-source doorway geometry later reviewed visually.
points=[[-44,-498.15],[-44,-498.0],[-44,-497.0],[-44,-496.0],[-44,-495.0],[-44,-494.0],[-44,-493.65],[-44,-493.4]];fp=unary_union([floorpoly,unary_union([Polygon(x['boundary'],x['holes'])for x in next(x for x in json.load(open(F/'source/TIDAL_STAFF_INTERFACE.json'))['floor_proposals']if x['deck']=='D14')['polygons']]),u2['u']['ownerpoly']['D14_final_south_street/D14_SouthStreetFloor']]);external=dict(receiver);external.update(patch);external.update({'street/'+n:t for n,t in u['triangles'](street)if n not in patch});witness=[]
for x,z in points:
 assert fp.buffer(1e-4).covers(box(x-.01,z-.01,x+.01,z+.01));lo=np.array([x-.32,88.54,z-.32]);hi=np.array([x+.32,90.4,z+.32]);hits=[n for n,t in external.items()if hit(t,lo,hi)[0]];assert not hits,hits;witness.append({'xz':[x,z],'supported_floor':True,'stationary_rectangular_proxy_clear':True})
# Existing unscaled leaf/hardware vertices; 17 sampled source poses each leaf. Factory rebate contacts are outside this external screen.
door=dict(u['triangles']('AST-STF-008.glb'));leafnames=[n for n in door if any(k in n.lower()for k in ['leaf','push','seal'])];pose_checks=0
for side,hinge,sign in [('LEFT',-1.2,1),('RIGHT',1.2,-1)]:
 ns=[n for n in leafnames if side in n]
 assert ns
 for fraction in np.linspace(0,1,17):
  angle=fraction*np.pi/2*sign;c=np.cos(angle);s=np.sin(angle)
  for name in ns:
   t=door[name].copy();x=t[:,:,0]-hinge;z=t[:,:,2].copy();t[:,:,0]=x*c+z*s+hinge;t[:,:,2]=-x*s+z*c;t+=np.array(P['door_binding']['position']);lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));lo[1]+=1e-5;hi[1]-=1e-5
   collisions=[n for n,q in external.items()if hit(q,lo,hi)[0]];assert not collisions,(side,fraction,name,collisions);pose_checks+=1
r={'schema':1,'status':'PASS','scope':'source-only local geometry; no engine/runtime test','receiving_meshes':len(receiver),'receiver_triangles':sum(len(x)for x in receiver.values()),'named_patch_meshes':len(patch),'named_patch_triangles':sum(len(x)for x in patch.values()),'missing_floor_m2':floorpoly.area,'floor_top_winding_upward':True,'unchanged_triangles':matches,'intentional_receiving_source_contacts':contacts,'receiving_bearings':P['receiving_contacts'],'eight_floor_and_stationary_rectangular_proxies':witness,'sampled_leaf_hardware_external_pose_boxes':pose_checks,'door_model_unscaled':True,'source_pins_unchanged':True,'upper_lift_activated':False,'structural_load_capacity_accepted':False,'errors':[]}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
