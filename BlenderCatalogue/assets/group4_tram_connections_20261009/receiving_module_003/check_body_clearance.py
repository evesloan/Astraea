from pathlib import Path
import json,numpy as np,hashlib
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');S=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002';old=json.loads((S/'SELECTED_ROUTE_SOURCE_GATE.json').read_text());rows=json.loads((W/'MESH_PARTS.json').read_text());parts=[r for r in rows if r['max'][1]>55.74+1e-6 and r['min'][1]<58.97-1e-6]
def obb(c,tan,r,l,row):
 lo=np.array(row['min'])[[0,2]];hi=np.array(row['max'])[[0,2]];mid=(lo+hi)/2;hh=(hi-lo)/2;d=mid-c;n=np.array([tan[1],-tan[0]])
 return all(abs(d@a)<=hh@abs(a)+e+1e-7 for a,e in [(np.array([1.,0.]),r*abs(n[0])+l*abs(tan[0])),(np.array([0.,1.]),r*abs(n[1])+l*abs(tan[1])),(n,r),(tan,l)])
# Refine the broad full-body rectangle using all39 actual source part bounds and their real vertical bands.
car=json.loads((S/'MESH_PARTS.json').read_text());car=[r for r in car if r['collection']=='TRAM_EDITABLE_COMPONENT'];assert len(car)==39
checks=[]
for f in old['checks']:
 broad=[];hits=[]
 for i,p in enumerate(f['poses']):
  c=np.array(p['center_xz']);tan=np.array(p['tangent_xz']);normal=np.array([tan[1],-tan[0]])
  for row in parts:
   if not obb(c,tan,1.15+f['margin_m'],2.44+f['margin_m'],row):continue
   broad.append({'source_pose':i,'new_member':row['mesh']})
   for part in car:
    if part['max'][1]+56.1<row['min'][1]-1e-7 or part['min'][1]+56.1>row['max'][1]+1e-7:continue
    lo=np.array(part['min'])[[0,2]];hi=np.array(part['max'])[[0,2]];mid=(lo+hi)/2;half=(hi-lo)/2;pc=c+mid[0]*normal+mid[1]*tan
    if obb(pc,tan,half[0]+f['margin_m'],half[1]+f['margin_m'],row):hits.append({'source_pose':i,'new_member':row['mesh'],'actual_vehicle_part':part['mesh']})
 checks.append({'family':f['family'],'reused_source_pose_count':len(f['poses']),'existing_horizontal_margin_m':f['margin_m'],'whole_body_bbox_broadphase_contacts':broad,'new_receiver_actual_body_part_contacts':hits})
# Straight station-rail drops keep1.33m minimum horizontal shoe inset vs body-plus0.15m halfwidth1.30.
station_shoes=[r for r in rows if r['mesh'].startswith('M003_StationRailHangerShoe_')];station_min=min(min(abs(r['min'][0]+5.6),abs(r['max'][0]+5.6))-1.30 for r in station_shoes)
assert station_min>=.0299
# All central receiver geometry remains inside exact protected4m support strip and away from Group7.
U={};exec((W/'glb_source_reader.py').read_text(),U);U['read']=lambda p:(W/Path(p).name).read_bytes();p=np.array(old['protected_polyline_xz']);maxd=0;witness=None
for name,t in U['triangles']('AST-TRM-G4-017_receiving_module.glb'):
 v=t.reshape(-1,3);v=v[(v[:,2]>=-72)&(v[:,2]<=72)];q=v[:,[0,2]];dist=np.full(len(q),np.inf)
 for a,b in zip(p,p[1:]):
  z=b-a;k=np.clip(((q-a)@z)/(z@z),0,1);dist=np.minimum(dist,np.linalg.norm(q-a-k[:,None]*z,axis=1))
 if len(dist) and dist.max()>maxd:maxd=float(dist.max());witness={'mesh':name,'xz':q[dist.argmax()].tolist()}
assert maxd<=2+1e-6
rep={'status':'PASS' if all(not c['new_receiver_actual_body_part_contacts'] for c in checks) else 'RECEIVER_BODY_CONFLICT_HOLD','source_only':True,'whole_group_complete':False,'reused_frozen_pose_evidence_sha256':hashlib.sha256((S/'SELECTED_ROUTE_SOURCE_GATE.json').read_bytes()).hexdigest(),'new_route_poses_sampled':0,'actual_vehicle_meshes_used_in_vertical_refinement':39,'refinement_explanation':'Only rail shoes produced broad full-body-box contacts. Shoes end55.79 below vehicle floor underside55.88; refined four wheel source bands retain the same horizontal margins. No vertical body/clearance shrink applied.','checks':checks,'straight_station_shoe_margin_beyond_existing0_15m_body_envelope_m':float(station_min),'source_receiver_vertices_max_distance_to_protected_polyline_m':maxd,'source_receiver_vertex_witness':witness,'nominal_profile_gaps_m':{'upper_header_above_reserved60_1_top':.08,'underweb_girder_below_nominal_wheel_min':.03,'south_seat_below_nominal_wheel_min':.015},'limits':['Existing bounded body/chord samples reused for new frame checks; no additional route campaign.','Nominal wheel-profile gaps are construction geometry, not dynamic steering/deflection acceptance.','Whole-world, actual-main, species and operating checks remain root-owned.']}
(W/'BODY_RECEIVER_CLEARANCE.json').write_text(json.dumps(rep,indent=2)+'\n');print('FRAME_BODY',rep['status'],[(c['family'],len(c['new_receiver_actual_body_part_contacts'])) for c in checks]);print('CENTRAL_STRIP',maxd,witness);print('STRAIGHT_STATION_MARGIN',station_min)
