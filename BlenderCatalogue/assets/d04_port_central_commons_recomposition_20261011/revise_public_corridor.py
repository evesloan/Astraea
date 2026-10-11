from pathlib import Path
import json,hashlib,copy
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011';p=json.load(open(W/'PLAN.json'));(W/'RETAINED_CONNECTED_ATTEMPT_R004_PLAN.json').write_text(json.dumps(p,indent=2)+'\n');(W/'CONNECTION_ATTEMPT003_HOLD.json').write_bytes((R/'Game/artifacts/d04_port_central_commons_recomposition_connection.json').read_bytes());(W/'INTEGRATION_ATTEMPT001_RECEIPT.json').write_bytes((W/'INTEGRATION_RECEIPT.json').read_bytes());ship=R/'Game/scripts/ship.gd';line='\tload("res://scripts/d04_port_central_commons_recomposition.gd").build(self)\n';s=ship.read_text();assert s.count(line)==1;s=s.replace(line,'');assert hashlib.sha256(s.encode()).hexdigest()==p['source_pins']['Game/scripts/ship.gd'];ship.write_text(s);p['active']=False
for q in p['moves']:
 if q['delta'][0]==-15:q['delta'][0]=-17
 elif q['delta']==[4,0,0]:q['delta'][0]=2.8
for i in [1,2]:
 g=p['gates'][i]
 for k in ['pivot','closed_center','sweep_min','sweep_max','control_at']:g[k][0]-=2
 for q in p['copied_gate_parts']:
  if q['name']in g['members']+g['control_members']:
   for v in q['verts']:v[0]-=2
for q in p['parts']:
 name=q['name']
 if name.startswith(('PCR_StockFrontFill','PCR_StockNewHeader','PCR_ReturnNewHeader')):
  for v in q['verts']:v[0]-=2
 elif name=='PCR_FrontGuestBoundary':
  for v in q['verts']:
   if abs(v[0]+83.79)<1e-6:v[0]=-86.14
 elif name=='PCR_EastGuestBoundary':
  for v in q['verts']:v[0]=-86.30 if abs(v[0]+83.95)<1e-6 else -86.14
 elif name=='PCR_FrontSouthJoin':
  for v in q['verts']:
   if abs(v[0]+91)<1e-6:v[0]=-93
 elif name=='PCR_FrontSouthJoinEast':
  for v in q['verts']:v[0]=-86.30 if abs(v[0]+84.3)<1e-6 else -86.14
for b in p['front_clip_boxes'].values():
 for k in ['min','max']:b[k][0]-=2
for q in p['route_samples']:
 if q[0]in [-89.976,-87.476]:q[0]-=2
p['service_group_translation']=[-17,0,3];p['quiet_group_translation']=[2.8,0,0];p['staff_floor_footprints'][2]={'lo':[-93.2,-.3],'hi':[-86.3,2.6],'missing_floor':False};p['moved_light_nodes']=[{'name':q['name']+'_Light','delta':q['delta']}for q in p['moves']if q['name'].startswith(('PCC_Lamp2_Lens','PCC_Lamp4_Lens','PCC_Lamp5_Lens'))];p['guest_route_points']=[[-84,16.5,z]for z in[-13,-10.5,-3,0,3,7,10.5,13]]+[[-64,16.5,0],[-70,16.5,0],[-86.8,16.5,7]];p['original_house_street_clear_footprint']={'x':[-86.05,-81.95],'z':[-13,13],'y_clear':[16.5,19.2],'width_m':4.1,'unchanged_receiving_floor_and_guards':True};p['patch_file']='D04_PORT_CENTRAL_COMMONS_PATCH_r003.glb';p['structure_file']='D04_PORT_CENTRAL_COMMONS_REAR_ROUTE_r005.glb';p.pop('independently_retained_inactive_geometry_commit',None);p.pop('sealed_receipt_sha256',None)
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json']:f.write_text(json.dumps(p,indent=2)+'\n')
s=(W/'author_native004.py').read_text().replace('D04PortCentralCommonsPatch_r002.blend','D04PortCentralCommonsPatch_r003.blend').replace('D04PortCentralCommonsRearRoute_r002.blend','D04PortCentralCommonsRearRoute_r005.blend');(W/'author_native007.py').write_text(s);(W/'revise_public_corridor.py').write_bytes(Path(__file__).read_bytes());print('INACTIVE_PUBLIC_CORRIDOR_RECOMPOSITION_READY')
