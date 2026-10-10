from pathlib import Path
import json,hashlib,numpy as np,math
W=Path(__file__).resolve().parent
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
P=F/'boarding_north_005';S=F/'port_successor_002'
U={'W':W};exec((P/'glb_source_reader.py').read_text(),U);base=U['read']
U['read']=lambda p:(P/Path(p).name).read_bytes() if 'AST-TRM-G4-019' in p or 'AST-TRM-G4-020' in p else ((S/Path(p).name).read_bytes() if 'AST-TRM-G4' in p else base(p))
B=json.loads((P/'BRIDGE_INTERFACE.json').read_text());parts={q['mesh']:q for q in json.loads((P/'BRIDGE_MESH_PARTS.json').read_text())}
bridge=dict(U['triangles'](B['asset']));car=dict(U['triangles']('AST-TRM-G4-011_cart_tram_component.glb'))
north_mount={'station':'FORE_MIDSHIP_NORTH_PROPOSAL','station_asset':'AST-TRM-G4-020_foremid_north_candidate.glb','origin_xyz':[-7.8,56.1,-241],'yaw_rad':0,'car_origin_xyz':[-5.6,56.1,-241]}
def transform(t,at=(0,0,0),yaw=0):
 p=t.copy();x=p[:,:,0].copy();z=p[:,:,2].copy();p[:,:,0]=x*math.cos(yaw)+z*math.sin(yaw);p[:,:,2]=-x*math.sin(yaw)+z*math.cos(yaw);return p+np.array(at)
def pose(t,angle):
 p=t.copy();x=p[:,:,0].copy();y=p[:,:,1].copy();p[:,:,0]=x*math.cos(angle)-y*math.sin(angle);p[:,:,1]=x*math.sin(angle)+y*math.cos(angle);return p
# Use exact SAT from the local check, without executing its check body.
code=(P/'check_north_candidate.py').read_text();a=code.index('def intersects(');b=code.index('\nsources=',a);exec(code[a:b],globals())
poses=[];hits=[];receivers=[]
for mount in [north_mount]:
 station=dict(U['triangles'](mount['station_asset']));carworld={n:transform(t,mount['car_origin_xyz']) for n,t in car.items()};origin=mount['origin_xyz'];yaw=mount['yaw_rad'];floor=next((t for n,t in station.items() if any(k in n for k in ['Boarding_Island','Boarding_Pod','BoardingFloor'])),None);assert floor is not None
 for j in range(4):
  t=transform(bridge['BRIDGE_FixedAnchor_'+str(j)],origin,yaw);lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));flo=floor.min(axis=(0,1));fhi=floor.max(axis=(0,1));v=np.maximum(0,np.minimum(hi,fhi)-np.maximum(lo,flo));assert v.prod()>1e-6;receivers.append({'station':mount['station'],'anchor':j,'positive_overlap_volume_m3':float(v.prod())})
 toe=transform(bridge['BRIDGE_CabinReceivingTongue_20mm'],origin,yaw);cf=carworld['V2__Tram_Floor'];lo=toe.min(axis=(0,1));hi=toe.max(axis=(0,1));flo=cf.min(axis=(0,1));fhi=cf.max(axis=(0,1));v=np.maximum(0,np.minimum(hi,fhi)-np.maximum(lo,flo));assert abs(v[0]-.02)<2e-5 and abs(v[2]-2.18)<2e-5 and v[1]>.017;receivers.append({'station':mount['station'],'tongue_floor_overlap_xyz_m':v.tolist(),'positive_cabin_bearing_area_m2':float(v[0]*v[2])})
 for deg in [0,45,90]:
  rows=[];allowed=[]
  for name,t in bridge.items():
   source=pose(t,math.radians(deg)) if parts[name]['group']=='BRIDGE_MOVING_PANEL' else t;tt=transform(source,origin,yaw);lo=tt.min(axis=(0,1));hi=tt.max(axis=(0,1))
   for owner,shapes in [('station',station),('car',carworld)]:
    for n,q in shapes.items():
     a=q.min(axis=1);b=q.max(axis=1);mask=np.all((a<hi-1e-5)&(b>lo+1e-5),axis=1)
     if not mask.any():continue
     qq=q[mask];aa=a[mask];bb=b[mask];contact=False
     for nt in tt:
      l=nt.min(axis=0);h=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=h+1e-6)&(bb>=l-1e-6),axis=1))
      if any(intersects(nt,qq[i]) for i in ids):contact=True;break
     if contact:
      rec={'station':mount['station'],'pose_degrees':deg,'bridge_mesh':name,'receiver_owner':owner,'retained_mesh':n}
      # Underfloor fixed anchors/hinge mounting contact source station slab/edge on purpose.
      platform=any(k in n for k in ['Boarding_Island','Boarding_Pod','BoardingFloor','Platform_InnerFascia','Platform_OuterSoffit'])
      if owner=='station' and platform and (parts[name]['group']=='BRIDGE_FIXED_RECEIVER_ROOT' or ('Knuckle' in name and deg==0)):allowed.append(rec)
      elif owner=='car' and n=='V2__Tram_Floor' and name=='BRIDGE_CabinReceivingTongue_20mm' and deg==0:allowed.append(rec)
      else:rows.append(rec);hits.append(rec)
  poses.append({'station':mount['station'],'angle_degrees':deg,'unexpected_contacts':rows,'declared_mount_or_bearing_contacts':allowed})

receipt=P/'FROZEN_BOARDING_AND_NORTH_BATCH.json';d=json.loads(receipt.read_text());assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==v['sha256'] for n,v in d['files'].items())
rep={'status':'UNADOPTED_NORTH_BRIDGE_THREE_POSE_LOCAL_PASS' if not hits else 'UNADOPTED_NORTH_BRIDGE_LOCAL_HOLD','source_only':True,'whole_group_complete':False,'runtime_changed':False,'retained_station_identity':'FORE_MIDSHIP','master_catchment_z':-216,'proposed_physical_boarding_z':-241,'mount':north_mount,'stationary_poses':poses,'positive_receiver_checks':receivers,'unexpected_contacts':hits,'frozen005_manifest_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'frozen005_unchanged':True,'limits':['One proposed station and one actual car pose, bridge at 0/45/90 degrees only; no continuous sweep, route audit or Godot.','Root must still decide/bind physical-stop, lift, destination arrival and bridge interlock. Local pose clearance is not boarding or mechanical acceptance.']}
(W/'NORTH_BRIDGE_POSE_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],len(hits),'unexpected contacts');print(json.dumps(hits,indent=2))
