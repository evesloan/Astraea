from pathlib import Path
import json,hashlib,numpy as np,math
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';U={'W':W};exec((W/'glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:(W/Path(p).name).read_bytes() if 'AST-TRM-G4-019' in p or 'AST-TRM-G4-020' in p else ((S/Path(p).name).read_bytes() if 'AST-TRM-G4' in p else base(p));B=json.loads((W/'BRIDGE_INTERFACE.json').read_text());N=json.loads((W/'NORTH_STATION_INTERFACE.json').read_text());parts={q['mesh']:q for q in json.loads((W/'BRIDGE_MESH_PARTS.json').read_text())};northparts={q['mesh']:q for q in json.loads((W/'NORTH_MESH_PARTS.json').read_text())};bridge=dict(U['triangles'](B['asset']));north=dict(U['triangles'](N['asset']));car=dict(U['triangles']('AST-TRM-G4-011_cart_tram_component.glb'));exports=[]
for file,geo,rows in [(B['asset'],bridge,parts),(N['asset'],north,northparts)]:
 bad=0;cnt=0
 for name,t in geo.items():
  assert name in rows and np.isfinite(t).all();lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));assert np.allclose(lo,rows[name]['min'],atol=1e-4) and np.allclose(hi,rows[name]['max'],atol=1e-4),(name,lo,hi);bad+=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-9).sum());cnt+=len(t)
 assert not bad and len(geo)==len(rows),(file,bad,len(geo),len(rows));exports.append({'file':file,'meshes':len(geo),'triangles':cnt,'degenerate_triangles':bad,'native_export_bounds_match':True,'sha256':hashlib.sha256((W/file).read_bytes()).hexdigest()})
# The native world recipe and the actual exported successor have identical bounds.
G={'__file__':str(W/'north_candidate_geometry.py'),'__name__':'source_geometry'};exec((W/'north_candidate_geometry.py').read_text(),G)
for q in G['recipes']:
 t=north[q['name']];a=q['triangles'];assert np.allclose(t.min(axis=(0,1)),a.min(axis=(0,1)),atol=1e-4) and np.allclose(t.max(axis=(0,1)),a.max(axis=(0,1)),atol=1e-4)
# Three stationary poses of the new bridge only. No route traversal campaign.
def transform(t,at=(0,0,0),yaw=0):
 p=t.copy();x=p[:,:,0].copy();z=p[:,:,2].copy();p[:,:,0]=x*math.cos(yaw)+z*math.sin(yaw);p[:,:,2]=-x*math.sin(yaw)+z*math.cos(yaw);return p+np.array(at)
def pose(t,angle):
 p=t.copy();x=p[:,:,0].copy();y=p[:,:,1].copy();p[:,:,0]=x*math.cos(angle)-y*math.sin(angle);p[:,:,1]=x*math.sin(angle)+y*math.cos(angle);return p
# Use exact SAT from the local check, without executing its check body.
code=(W/'check_north_candidate.py').read_text();a=code.index('def intersects(');b=code.index('\nsources=',a);exec(code[a:b],globals())
poses=[];hits=[];receivers=[]
for mount in B['placements']:
 if mount['station']=='FORE_MIDSHIP':continue
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
for mount in B['placements']:mount['source_fit_gate']='HELD_FOREMID_PAPERMOON' if mount['station']=='FORE_MIDSHIP' else ('BRIDGE_LOCAL_SOURCE_PASS' if not any(q['station']==mount['station'] for q in hits) else 'BRIDGE_LOCAL_HOLD')
for p,h in {**B['retained_source_pins'],**B['source_material_pins'],**N['retained_source_pins'],**N['source_material_pins']}.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
for folder,file in [(F,'FROZEN_FIRST_BATCH.json'),(S,'FROZEN_SUCCESSOR_BATCH.json'),(F/'receiving_module_003','FROZEN_RECEIVING_MODULE.json'),(F/'central_stair_receiving_004','FROZEN_CENTRAL_STAIR_BATCH.json')]:
 d=json.loads((folder/file).read_text());assert all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==v['sha256'] for n,v in d['files'].items())
report={'status':'BRIDGE_AND_NORTH_EXPORT_BOUNDED_PASS' if not hits else 'BRIDGE_LOCAL_SOURCE_HOLD','source_only':True,'whole_group_complete':False,'exports':exports,'bridge_three_pose_checks_four_unaffected_stations':poses,'positive_station_and_car_receiver_checks':receivers,'unexpected_bridge_contacts':hits,'foremid_original_binding_held':True,'north_source_recipe_export_bounds_match':True,'all_four_prior_slices_unchanged':True,'limits':['Three stationary bridge poses only; no Godot/import, moving traversal or all-species acceptance.','North station local check uses generic and received floors; proposed new docking coordinate−241 remains unadopted.','Operational controller/interlock, primary hull/capacity, missing-only lower-annex/stair/lift receiving and final main-world fit remain open.']};(W/'SOURCE_BATCH_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');(W/'BRIDGE_INTERFACE.json').write_text(json.dumps(B,indent=2)+'\n');print(report['status'],'unexpected',len(hits));print(json.dumps(hits,indent=2));print('EXPORTS',exports)
