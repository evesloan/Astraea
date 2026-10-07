from pathlib import Path
import json,math,hashlib,struct,numpy as np
B=Path(__file__).parent;P=B.parent;plan=json.loads((P/'CORE_PLAN.json').read_text());parts={p['name']:p for p in plan['parts']};s=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def roof(x,z,a,b,rise):
 n=24;i=max(0,min(n-1,int((z-a)/(b-a)*n)));t=(z-a)/(b-a)*n-i;v=math.sin(math.pi*i/n)*(1-t)+math.sin(math.pi*(i+1)/n)*t;return 56.02+.17*(x+10.85)+rise*v
# One direct-use and one real cap-mounted upward source per inhabited group.
choices={'CG_Directory_LightReserve':(-10.57,-458.,-461.1,-454.,1.22,'up'), 'EAST_Bay_LightReserve_0':(-10.04238795325113,-450.5,-454.,-445.,1.22,'up'), 'CG_Counter_LightReserve':(-10.52,-440.4,-445.,-435.4,1.40,'up'), 'CG_Service_LightReserve':(-10.52,-440.,-445.,-435.4,1.40,'down')}
changed=[];optics=[]
for r in plan['fixture_reservations']:
 if r['name']in choices:
  x,z,a,b,rise,direction=choices[r['name']];h=lambda x,z:roof(x,z,a,b,rise)+(0.28 if direction=='up'else 0);sg=1 if direction=='up'else -1;cup=parts[r['housing']];lens=parts[r['physical_lens']];N=len(cup['vertices_xyz'])//4;old=cup['vertices_xyz'];centre=np.array(old[:N]).mean(0);rad=math.hypot(old[0][0]-centre[0],old[0][2]-centre[2]);inn=np.mean([math.hypot(v[0]-centre[0],v[2]-centre[2])for v in old[2*N:3*N]])
  for p,rr in [(cup,[(rad,0),(rad,sg*.11),(inn,sg*.11),(inn,sg*.028)]),(lens,[(inn,sg*.067),(inn,sg*.055)])]:
   p['vertices_xyz']=[[s(x+rrr*math.cos(2*math.pi*k/N)),s(h(x+rrr*math.cos(2*math.pi*k/N),z+rrr*math.sin(2*math.pi*k/N))+dy),s(z+rrr*math.sin(2*math.pi*k/N))]for rrr,dy in rr for k in range(N)];p['semantic']='Real cap-mounted crown uplight'if direction=='up'else'Canopy downlight for combined service and counter use';changed.append(p['name'])
  r['position_xyz']=[s(x),s(h(x,z)+sg*.103),s(z)];dz=.001;n=np.array([-.17,1,-(h(x,z+dz)-h(x,z-dz))/(2*dz)])*sg;r['direction_xyz']=(n/np.linalg.norm(n)).tolist();r['mounting']=direction
  r['physical_support']='CurvedCap'if direction=='up'else'CurvedSoffit'
 else:r['mounting']='down'
 r['proposed_energy']=.42;r['half_angle_degrees']=55;r['native_balance_accepted']=False
 optics.append({'name':r['name'],'position_xyz':r['position_xyz'],'direction_xyz':r['direction_xyz'],'mounting':r['mounting'],'energy':.42,'half_angle_degrees':55,'range_m':'derive from exact receiving surfaces after ray check','physical_housing':r['housing'],'physical_lens':r['physical_lens']})
plan['parts']=list(parts.values());plan['source_base']=str(P/'source_build001/source/AST-AQU-016_connected_curved_gallery.blend');plan['source_base_sha256']='5ceb6e36f3733949889445e472b31db836b63773f1420fd63db369e43d572d3d';plan['modified_existing_parts']=sorted(changed);plan['new_parts']=[];plan['status']='SOURCE_LIGHTING_REVISION_PURE_PLAN_PENDING_MOUNT_RECEIVER_FIT';plan['optical_revision']='002';plan['preserved_approved_composition_sha256']=sha(P/'CORE_PLAN.json')
(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(B/'OPTICAL_PROPOSAL.json').write_text(json.dumps({'status':'ACTUAL_CAP_UPLIGHT_AND_USE_DOWNLIGHT_PROPOSAL_PENDING_RAYS','rationale':'The original six apertures all faced below the low vaults; no direct rays could reach the upper crown. Reuse same six real source candidates as paired upward/downward local sources. No unsupported ambient or shared renderer changes.','source_count_before':6,'source_count_after':6,'active_cap':8,'new_unique_design_ids':0,'body_meshes_changed':changed,'fixtures':optics,'source_preview_total_watts_before':2310,'source_preview_total_watts_proposed':1764,'production_settings_changed':False},indent=2)+'\n');print('Prepared',len(changed),'source fixture meshes; same6source candidates')
