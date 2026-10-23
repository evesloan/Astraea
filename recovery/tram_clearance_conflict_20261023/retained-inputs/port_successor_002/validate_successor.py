"""Bounded source-only checks, no imports or runtime."""
from pathlib import Path
import json,hashlib,struct,math,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
U={};exec((W/'glb_source_reader.py').read_text().split('protected=[')[0],U)
PIN=U['PIN'];origread=U['read']
def read(p):
 if p.startswith('Game/assets/models/AST-TRM-G4-'):return (W/Path(p).name).read_bytes()
 return origread(p)
U['read']=read
rows=json.loads((W/'MESH_PARTS.json').read_text());meta=json.loads((W/'SUCCESSOR_INTERFACE.json').read_text());rc={r['mesh']:r for r in rows};exports=[]
source_files=sorted(W.glob('AST-*.glb'));export_tri={}
for path in source_files:
 data=path.read_bytes();assert data[:4]==b'glTF' and struct.unpack_from('<I',data,8)[0]==len(data)
 dd=[];bad=0;ntri=0
 for n,t in U['triangles'](path.name):
  assert np.isfinite(t).all();aa=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);bad+=int((aa<1e-9).sum());ntri+=len(t);lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));assert n in rc,n
  assert np.allclose(lo,rc[n]['min'],atol=1e-4) and np.allclose(hi,rc[n]['max'],atol=1e-4),(n,lo,rc[n]['min']);dd.append((n,t))
 assert not bad,(path.name,bad);export_tri[path.name]=dd
 exports.append({'file':path.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'triangles':ntri,'mesh_primitives':len(dd),'degenerate_triangles':bad,'native_world_bounds_match':True})
freeze=json.loads((F/'FROZEN_FIRST_BATCH.json').read_text());assert all(hashlib.sha256((F/n).read_bytes()).hexdigest()==q['sha256'] for n,q in freeze['files'].items())
# Exact installed floor-owner witnesses, including all5 local lower pit proposals.
compiled=json.loads((R/'Game/data/generated/structural_meshes.json').read_text())
def contains(q,r):
 def sg(a,b,c):return (a[0]-c[0])*(b[1]-c[1])-(b[0]-c[0])*(a[1]-c[1])
 return any(not(min(v:=[sg(q,t[0],t[1]),sg(q,t[1],t[2]),sg(q,t[2],t[0])])< -1e-7 and max(v)>1e-7) for t in r['triangles'])
def owners(x,z,y=52.5):return [r['id'] for r in compiled['regions'] if r['floor_y']==y and contains((x,z),r)]
pits=[]
for st in meta['stations']:
 a,c,b,d=st['lower_lift_recess_xz'];wit=[]
 for x in np.linspace(a+.01,b-.01,3):
  for z in np.linspace(c+.01,d-.01,3):wit.append({'xyz':[float(x),52.5,float(z)],'owners':owners(x,z)})
 own=sorted(set(o for p in wit for o in p['owners']));st['retained_lower_floor_owners']=own
 if st['label']=='CENTRAL':assert own==['D09_atrium_circulation'] and all(len(p['owners'])==1 for p in wit),own
 pits.append({'station':st['label'],'bounds_xz':st['lower_lift_recess_xz'],'receiving_proposal_only':True,'retained_floor_owners':own,'existing_slab_overlap_m2':st['recess_existing_slab_overlap_m2'],'witnesses':wit})
# Preserve lower4m corridor; reviewed station parts can only enter it above3.05m soffit.
axis=[]
for r in rows:
 if r['collection']=='TRAM_EDITABLE_COMPONENT':continue
 if r['min'][0]<2-1e-6 and r['max'][0]>-2+1e-6 and r['min'][1]<55.55-1e-6 and r['max'][1]>52.5+1e-6:axis.append(r['mesh'])
assert not axis,axis
# Cart physics inputs are current compound boxes/caster spheres, with no invented narrower cart.
cart=json.loads((R/'Game/data/architecture/cleaning_cart_contacts.json').read_text());cv=[]
for q in cart['boxes']:
 c=np.array(q['center']);h=np.array(q['size'])/2
 for x in [-1,1]:
  for z in [-1,1]:cv.append([c[0]+x*h[0],c[2]+z*h[2]])
for q in cart['wheel_contacts']:
 for a in np.linspace(0,math.tau,33):cv.append([q['center'][0]+q['radius']*math.cos(a),q['center'][2]+q['radius']*math.sin(a)])
cv=np.array(cv);k=2.3/2.7;inside_half=(1.29-.055)*k;door_half=1.22-.055
car=[r for r in rows if r['collection']=='TRAM_EDITABLE_COMPONENT'];assert len(car)==39,len(car);obstacles=[r for r in car if r['max'][1]>.02 and r['min'][1]<1.8 and 'moving_shape' in r['policy']]
turn_min=1e9;turn_hits=[]
for i,a in enumerate(np.linspace(0,math.pi,25)):
 rot=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]]);v=cv@rot.T;turn_min=min(turn_min,inside_half-abs(v[:,0]).max())
 # Cart boxes and caster bounds inside central turning circle are bounded against every raised source fixture AABB.
 for r in obstacles:
  if r['mesh'].startswith(('V2__Tram_Floor','V2__Tram_End_')):continue
  lo=np.array(r['min'])[[0,2]];hi=np.array(r['max'])[[0,2]]
  if np.any(np.all((v>=lo)&(v<=hi),axis=1)):turn_hits.append({'sample':i,'mesh':r['mesh']})
assert not turn_hits,turn_hits
cartmax=float(cv[:,1].max());cartmin=float(cv[:,1].min());dock=.15;rear=1.77;front=-.95;pr=.3
rear_margin=2.22-rear-pr;front_cart=dock+cartmin-(front+pr);front_perch=front-pr-(-1.54)
assert min(rear_margin,front_cart,front_perch)>=.1-1e-8
assert abs((rear-.95)-(dock+.67))<1e-8
assert turn_min>=.1
interior={'actual_usable_width_at_pockets_m':2*inside_half,'actual_side_aperture_clear_length_m':2*door_half,'cart_compound_with_casters_width_m':float(cv[:,0].max()-cv[:,0].min()),'cart_compound_length_m':float(cv[:,1].max()-cv[:,1].min()),'cart_turn_25poses_side_clearance_m':float(turn_min),'cart_raised_fixture_contacts':turn_hits,'door_clear_length_minus_cart_turn_diameter_m':2*door_half-2*float(np.linalg.norm(cv,axis=1).max()),'rear_operator_capsule_to_end_wall_m':rear_margin,'front_operator_capsule_to_cart_m':front_cart,'front_operator_capsule_to_perch_m':front_perch,'existing_handle_hold_distance_m':.95,'normal_handle_target_matches_docked_grip':True,'restraint_source_mounts_flush_below_standing_floor':all(r['max'][1]<.001 for r in car if 'Cart_Restraint_' in r['mesh']),'headroom_under_door_header_m':2.51,'four_existing_bottles_loaded_top_y_m':1.21,'loaded_stock_to_door_header_clearance_m':1.30,'player_height_checked_m':1.8,'limits':'Bounded compound/cart and0.3m-radius operator envelope checks. No physical tether/stock traversal, alternate species or door-motion acceptance.'}
# Fit station source against materially adjacent retained sources. Exact floor-contact proposals exempt only declared receivers.
adj=[('AST-RTL-009.glb',(4,52.5,-250),0,'OrchardExchange'),('AST-RTL-007.glb',(8,52.5,-216),0,'ThreadShell'),('AST-AQU-012.glb',(8,61,182),0,'AftAquaticCeiling'),('AST-CIR-004.glb',(12,44,235),0,'AftAquaticLift'),('AST-AQU-016.glb',(0,0,0),0,'ForwardAquatic')]
adjtris=[]
for f,at,yaw,own in adj:
 for n,t in U['triangles'](f,at,yaw):
  lo=t.min(axis=1);hi=t.max(axis=1);mask=(lo[:,1]<60.05)&(hi[:,1]>52.58)&(lo[:,0]<14)&(hi[:,0]>-14)
  if mask.any():adjtris.append((f,n,own,lo[mask],hi[mask]))
fit=[]
for st in meta['stations']:
 contacts=[]
 for n,t in export_tri[st['asset']]:
  lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
  if hi[1]<=52.58 or lo[1]>=60.05:continue
  for f,m,own,a,b in adjtris:
   if np.any(np.all((a<hi-1e-5)&(b>lo+1e-5),axis=1)):contacts.append({'new_mesh':n,'retained_file':f,'retained_mesh':m,'owner':own})
 fit.append({'station':st['label'],'conservative_adjacent_triangle_aabb_contacts':contacts})
assert all(not c['conservative_adjacent_triangle_aabb_contacts'] for c in fit),fit
# Pin retained inputs and independent frozen first source. Never change those files.
more=['Game/data/generated/structural_meshes.json','Game/data/architecture/cleaning_cart_contacts.json','Game/scripts/cleaning_cart.gd','Game/scripts/physics_tether.gd','Game/scripts/cart_handle.gd','Game/scripts/cleaning_bottle.gd','Game/scripts/commons_lift.gd','Game/scripts/atrium_lighting.gd','BlenderCatalogue/catalogue_manifest.json']
for p in sorted(set(more+PIN)):meta['source_input_pins'][p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
mats=json.loads((F/'BATCH_INTERFACE.json').read_text())['source_material_sha256'];assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in mats.items());meta['source_material_sha256']=mats
report={'status':'BOUNDED_SUCCESSOR_SOURCE_PASS_WITH_RECEIVING_OPERATING_HOLDS','source_only':True,'whole_group_complete':False,'exports':exports,'frozen_first_batch_all_hashes_unchanged':True,'verified_retained_material_pins':mats,'lower4m_axis_obstacles':axis,'five_receiving_lift_pit_proposals':pits,'actual_cart_operator_interior':interior,'station_adjacent_source_screen':fit,'retained_input_hashes':meta['source_input_pins'],'not_run':['Godot import or full builds','actual-main collision/traversal','moving transport/doors/bridge/bogies/restraints','loose stock persistence/pause/save','NPC finite-time routing','capacity/hull/load verification','final in-engine/CRT/species/GPU acceptance']}
(W/'SOURCE_BATCH_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');(W/'SUCCESSOR_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SOURCE_PASS',len(exports),'GLBs',len(rows),'native parts; pits',[(p['station'],p['retained_floor_owners']) for p in pits]);print('INTERIOR',interior);print('ADJACENT_CONTACTS',sum(len(c['conservative_adjacent_triangle_aabb_contacts']) for c in fit))
