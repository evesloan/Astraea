#!/usr/bin/env python3
"""Exact member schedule and conservative source-fit screen; no engine/source authoring."""
from pathlib import Path
import os
import json,math,hashlib
import numpy as np
from shapely.geometry import Polygon,box
S=Path(os.environ.get('ASTRAEA_RESIDENTIAL_STAGE_ROOT',str(Path(__file__).resolve().parents[1])));P=Path(os.environ.get('ASTRAEA_RESIDENTIAL_SOURCE_ROOT',str(S.parent)));G=Path('/workspace/shared/astraea-godot-production-20261003')
parts=json.load(open(P/'domestic_correction/court_source/PARTS.json'))['objects'];byname={r['name']:r for r in parts};members=[]
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def add(name,vs,kind,contacts,note):
 vs=np.array(vs,dtype=float);members.append({'name':name,'category':kind,'vertices_world_xyz':vs.tolist(),'faces':faces,'bounds_world_min_xyz':vs.min(axis=0).tolist(),'bounds_world_max_xyz':vs.max(axis=0).tolist(),'intended_contact_owners':contacts,'purpose':note,'material_role':'champagne_metal' if 'Web' in name or 'Shoe' in name or 'Post' in name else 'ivory_enamel'})
def rect(name,x0,x1,y0,y1,z0,z1,contacts,note,kind='support'):
 vs=[(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];add(name,vs,kind,contacts,note);members[-1]['shape']={'type':'box','min_world_xyz':[x0,y0,z0],'max_world_xyz':[x1,y1,z1]}
def beam(name,a,b,width,depth,contacts,note):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);t=(b-a)/np.linalg.norm(b-a);s=np.array((0,0,1)if abs(t[2])<.95 else (1,0,0),dtype=float);s-=t*s.dot(t);s/=np.linalg.norm(s);u=np.cross(t,s);u/=np.linalg.norm(u);vs=[p+s*w+u*h for p in [a,b]for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]];add(name,vs,'support',contacts,note);members[-1]['shape']={'type':'beam','a_world_xyz':a.tolist(),'b_world_xyz':b.tolist(),'width_m':width,'depth_m':depth,'width_axis_world':s.tolist(),'depth_axis_world':u.tolist()}
zs=[-331.5,-325.1,-316.6,-309.5]
for i,z in enumerate(zs):
 beam(f'RF_LowerUpperExtension_{i}',(28.72,83.48,z),(45.95,83.48,z),.45,.48,[f'SUP_transfer_upper_{i}'],'Butt joins actual court upper chord; all new material remains below retained D13 slab lower face83.78')
 beam(f'RF_LowerDiagonal_{i}',(4.14,78.25,z),(45.80,83.48,z),.38,.38,[f'SUP_spine_mast_{i}',f'SUP_D12_receiver_{i}',f'RF_LowerUpperExtension_{i}'],'Deeper triangulated extension from same real D12 shoe/mast; no new duplicate shoe')
 for j,x in enumerate([14.1,28.72,42.20]):
  yy=78.25+(x-4.14)/(45.8-4.14)*5.23
  beam(f'RF_LowerWeb_{i}_{j}',(x,yy,z),(x,83.48,z),.22,.22,[f'RF_LowerDiagonal_{i}',f'SUP_transfer_upper_{i}'if x<28.72 else f'RF_LowerUpperExtension_{i}'],'Explicit truss web within unallocated D12 volume')
 for side,x in [('inner',42.2),('outer',45.8)]:
  rect(f'RF_StreetPost_{side}_{i}',x-.15,x+.15,83.72,87.0,z-.15,z+.15,[f'RF_LowerUpperExtension_{i}',f'RF_StreetBearer_{side}'],'Post stays in D13 street margin, outside all guest allocations')
 beam(f'RF_StreetTransom_{i}',(42.2,88.02,z),(45.8,88.02,z),.34,.48,[f'RF_StreetBearer_inner',f'RF_StreetBearer_outer'],'Street underside support; lower level clear headroom3.78m')
# Continuous deep bearing edges and stepped room receiving lips.
rect('RF_RearBearer',28.46,28.90,87.0,88.10,-331.90,-309.35,[f'ROOF_EastPier_{i}'for i in range(4)],'Deep rear edge member at real court piers, wholly outside room allocations')
rect('RF_RearBearingCap',28.46,29.28,88.10,88.28,-331.90,-309.50,['RF_RearBearer'],'Shallow rear bearing lip meets retained shell underside; starts above lower shell top88.04')
for side,x in [('inner',42.2),('outer',45.8)]:
 rect(f'RF_StreetBearer_{side}',x-.17,x+.17,87.0,88.26,-337.79,-309.50,[f'RF_StreetPost_{side}_{i}'for i in range(4)]+['RF_ArrivalUpper_0','RF_ArrivalUpper_1'],'Deep edge beam in street margin,3.0m above future D13 floor')
rect('RF_FrontBearingLip',41.72,42.03,88.10,88.26,-331.90,-309.50,['RF_StreetBearer_inner'],'Short receiving flange over room-front interstitial zone, not through lower suite')
rect('RF_FrontBearingStep',41.72,41.95,88.26,88.28,-331.90,-309.50,['RF_FrontBearingLip'],'Step matches0.22m suite floor versus0.24m street floor without overlapping either slab')
for i,z in enumerate([-331.75,-324.30,-316.90,-309.50]):
 beam(f'RF_RoomEndWeb_{i}',(28.68,87.55,z),(42.20,87.55,z),.16,1.10,['RF_RearBearer','RF_StreetBearer_inner'],'Deep1.10m web lies only in existing lower-room end/party gap;0.02m side clearance in0.20m gaps')
 rect(f'RF_RoomEndCap_{i}',28.68,41.95,88.10,88.28,z-.25,z+.25,[f'RF_RoomEndWeb_{i}','RF_RearBearingCap','RF_FrontBearingStep'],'Shallow top flange above lower shell head; real area bearing on each D14 room end')
# Northern arrival: two triangulated supports in the real unallocated gap.
for i,z in enumerate([-337.79,-334.21]):
 rect(f'RF_ArrivalD12Shoe_{i}',3.70,4.28,78.0,78.22,z-.38,z+.38,['D12_fore_route'],'Only new receiving shoes; outer0.30m spine strip, like retained court shoes',kind='receiver')
 rect(f'RF_ArrivalSpineMast_{i}',3.99,4.29,78.20,87.90,z-.15,z+.15,[f'RF_ArrivalD12Shoe_{i}',f'RF_ArrivalUpper_{i}'],'Spine-edge vertical, mostly outboard; route test mandatory onD12/13/14')
 beam(f'RF_ArrivalUpper_{i}',(3.75,88.04,z),(45.95,88.04,z),.40,.44,['D14_fore_route',f'RF_ArrivalSpineMast_{i}'],'Actual underside bearing atY88.26 and top support under arrival slab;42.2m triangulated member')
 beam(f'RF_ArrivalDiagonal_{i}',(4.14,78.25,z),(45.80,88.04,z),.42,.42,[f'RF_ArrivalSpineMast_{i}',f'RF_ArrivalUpper_{i}'],'Full-depth10m triangular arrival support contained in northern unallocated gap')
 for j,x in enumerate([14.1,28.72,42.2]):
  yy=78.25+(x-4.14)/(45.8-4.14)*(88.04-78.25)
  beam(f'RF_ArrivalWeb_{i}_{j}',(x,yy,z),(x,88.04,z),.26,.26,[f'RF_ArrivalDiagonal_{i}',f'RF_ArrivalUpper_{i}'],'Explicit arrival-truss web; never traverses lower guest allocation')
# OBB SAT. Exact boxes/beam convex vertices, with axes generated from face/edge vectors.
def axes(v):
 e=[v[1]-v[0],v[3]-v[0],v[4]-v[0]];return[e/np.linalg.norm(e)for e in e]
def separate(v,w,touch=True):
 av=axes(v);aw=axes(w);aa=av+aw+[np.cross(a,b)for a in av for b in aw]
 for a in aa:
  if np.linalg.norm(a)<1e-9:continue
  a=a/np.linalg.norm(a);p=v@a;q=w@a
  gap=max(q.min()-p.max(),p.min()-q.max())
  if (gap>1e-5 if touch else gap>=-1e-7):return True
 return False
def rectv(lo,hi):return np.array([(x,y,z)for z in [lo[2],hi[2]]for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]],dtype=float)
levels={r['deck_id']:r['floor_elevation_m']for r in json.load(open(G/'data/design_contract.json'))['deck_datums']}
obstacles=[]
for i,r in enumerate(json.load(open(G/'data/reference/historical_guest_census.json'))['guest_envelopes']):
 deck=f'D{r["deck"]:02d}';y=levels[deck]
 # Source-fit occupied shell bounds, not a license to reduce room clearances.
 lo=[r['x'][0],y-.22,r['z'][0]];hi=[r['x'][1],y+4.04,r['z'][1]]
 obstacles.append((f'guest_source_{i}',rectv(lo,hi),lo,hi))
for r in json.load(open(G/'data/programme_ledger.json'))['destinations']:
 if not r.get('historical_envelope'):continue
 deck=r['historical_deck'];idx=int(deck[1:]);e=r['historical_envelope'];y=levels[deck];top=levels.get(f'D{idx+1:02d}',118)
 lo=[e['x'][0],y,e['z'][0]];hi=[e['x'][1],top,e['z'][1]];obstacles.append((r['programme_key'],rectv(lo,hi),lo,hi))
violations=[]
for m in members:
 lo=np.array(m['bounds_world_min_xyz']);hi=np.array(m['bounds_world_max_xyz']);v=np.array(m['vertices_world_xyz'])
 for label,w,olo,ohi in obstacles:
  if np.any(np.array(ohi)<=lo+1e-7)or np.any(np.array(olo)>=hi-1e-7):continue
  if not separate(v,w,False):violations.append([m['name'],label])
voids=[]
for m in members:
 poly=Polygon([(v[0],v[2])for v in m['vertices_world_xyz']]).convex_hull
 for void in json.load(open(G/'data/spatial_layout.json'))['voids']:
  if poly.intersection(Polygon(void['boundary'])).area>1e-7:voids.append([m['name'],void['id']])
# Reachability from actual source receiver members. No disconnected anonymous solids.
anchors={k:rectv(v['bounds_world_min_xyz'],v['bounds_world_max_xyz'])for k,v in byname.items()if k.startswith(('ROOF_EastPier_','SUP_transfer_upper_','SUP_spine_mast_','SUP_D12_receiver_'))}
anchors.update({'D12_fore_route':rectv([-4,77.76,-530],[4,78,-80]),'D14_fore_route':rectv([-4,88.26,-530],[4,88.5,-80])})
allv={m['name']:np.array(m['vertices_world_xyz'])for m in members};edges=[];anchor_contacts=[]
for name,v in allv.items():
 for label,w in anchors.items():
  if not separate(v,w):anchor_contacts.append([name,label])
 for label,w in allv.items():
  if label>name and not separate(v,w):edges.append([name,label])
reached={a for a,b in anchor_contacts}
while True:
 new=reached|{b for a,b in edges if a in reached}|{a for a,b in edges if b in reached}
 if new==reached:break
 reached=new
report={'status':'PASS_CONSERVATIVE_SOURCE_FIT_PROPOSAL'if not violations and not voids and len(reached)==len(members)else'CONFLICT','members':len(members),'all1000_guest_and_programme_tests':'Exact convex-box SAT against guest source volumes floor-0.22 through floor+4.04 and programme full datum intervals; no positive-volume intersection','guest_programme_intersections':violations,'protected_void_plan_intersections':voids,'connected_to_actual_receivers':len(reached),'unconnected':sorted(set(allv)-reached),'new_member_contacts':edges,'actual_source_receiver_contacts':anchor_contacts,'D13_street_clear_band_x':[42.35,45.65],'D13_street_clear_width_m':3.3,'D13_street_crossmember_min_headroom_m':3.78,'D12_extension_under_D13_floor_gap_m':.06,'D13_shell_top_to_shallow_cap_gap_m':.06,'deep_party_gap_web_side_clearance_m':.02,'D12_extra_shoes_count':2,'D12_extra_shoes_route_gate':'Run original actual cart shapes/player sweep atX2.5, z-340..-306; retain four products. No full-width unchanged claim.','source_basis':{'court_source_glb_sha256':hashlib.sha256((P/'domestic_correction/court_source/source.glb').read_bytes()).hexdigest(),'room_floor_underside':88.28,'D13_future_shell_top':88.04,'D13_future_floor_bottom':83.78},'limits':['Proposal only, not authored Blender source, not an installed or structurally certified frame','Source author must run actual exported mesh contacts/exclusions, then parent view review','New diagonal/court cross-bracing crossings are intentional same-frame connections; no source geometry is removed','Actual existing D12 scenery/fixtures and physics-route collisions beyond programme envelopes remain native gates']}
(S/'qa/RECEIVING_FRAME_PROPOSAL_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');(S/'data/architecture/RECEIVING_FRAME_PROPOSAL.json').write_text(json.dumps({'status':report['status'],'units':'metres','coordinate_frame':'Godot world XYZ; Blender (X,-Z,Y)','source_only_not_installed':True,'source_pins':{str(q):hashlib.sha256(q.read_bytes()).hexdigest() for q in [P/'COURT_PILOT_PLAN.json',P/'domestic_correction/court_source/PARTS.json',P/'domestic_correction/court_source/source.glb',G/'data/spatial_layout.json',G/'data/generated/structural_meshes.json',G/'data/reference/historical_guest_census.json',G/'data/programme_ledger.json']},'materials':'Retained court warm_walnut/ivory_enamel/champagne_metal; source author coordinates roles','members':members,'checks':'qa/RECEIVING_FRAME_PROPOSAL_CHECKS.json'},indent=2)+'\n');print({k:v for k,v in report.items()if k not in ['new_member_contacts','actual_source_receiver_contacts']})
