"""One isolated connected-gallery finishing plan. Pure source geometry only."""
from pathlib import Path
import ast,copy,json,math,hashlib,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');OLD=S/'pool-connected-gallery-curved001'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=copy.deepcopy(json.loads((OLD/'lighting_revision002/CORE_PLAN.json').read_text()));parts=plan['parts'];original={p['name']:copy.deepcopy(p)for p in parts};changed=set();new=set()
def add(name,role,vs,faces,support,semantic,group='connected_finish',**extra):
 parts.append({'name':name,'group':group,'material_role':role,'vertices_xyz':[[float(np.float32(x))for x in v]for v in vs],'faces':faces,'support':support if isinstance(support,list)else[support],'semantic':semantic,'collision':'concave_static_surface','parent_family':'AST-AQU-016',**extra});new.add(name);return name
FACES=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,role,lo,hi,support,semantic):
 a,b,c=lo;x,y,z=hi;return add(name,role,[[a,b,c],[x,b,c],[x,b,z],[a,b,z],[a,y,c],[x,y,c],[x,y,z],[a,y,z]],FACES,support,semantic)
def loft(name,role,rings,support,semantic,closed_cycle=False,**extra):
 n=len(rings[0]);assert all(len(x)==n for x in rings);vs=[v for r in rings for v in r];faces=[]
 if not closed_cycle:faces=[list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))]
 for j in range(len(rings)if closed_cycle else len(rings)-1):
  for i in range(n):faces.append([j*n+i,j*n+(i+1)%n,((j+1)%len(rings))*n+(i+1)%n,((j+1)%len(rings))*n+i])
 return add(name,role,vs,faces,support,semantic,**extra)
def replace(name,role,vs,faces,support,semantic,**extra):
 row=next(p for p in parts if p['name']==name);row.update(material_role=role,vertices_xyz=[[float(np.float32(x))for x in v]for v in vs],faces=faces,support=support if isinstance(support,list)else[support],semantic=semantic,**extra);changed.add(name);return name
# Local material successors on already authored architecture. The untouched lift
# and retained furniture/material datablocks are excluded explicitly.
material_changes={}
for p in parts:
 n=p['name'];role=p['material_role']
 if n.startswith('EAST_Lift_')or p.get('group')=='directory':continue
 target=None
 if role in ['warm_stone','ivory_enamel']:target='finish_mineral_cream'
 elif role=='warm_walnut'and ('Canopy'in n or '_Vault_'in n or 'UpperCrown'in n):target='finish_honey_timber'
 if target:material_changes[n]={'before':role,'after':target};p['material_role']=target;changed.add(n)
# Fit a warm mineral skin to the actual structural pier3 shaft. Nothing changes
# the retained pier itself or its flared base/capital silhouette.
contract=json.loads((C/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text())
pier=next(p for p in contract['source_parts']if p['name']=='GP_UpperPier_3');ring=[v for v in pier['world_vertices']if v[1]==53.05]
center=np.mean(np.asarray(ring)[:,[0,2]],axis=0)
for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
 a=np.array([a[0],a[2]]);b=np.array([b[0],b[2]]);edge=b-a;normal=np.array([edge[1],-edge[0]])/np.linalg.norm(edge)
 if np.dot(normal,(a+b)/2-center)<0:normal=-normal
 # Trim corners by 1mm so independent face panels do not intersect each other.
 unit=edge/np.linalg.norm(edge);a=a+unit*.001;b=b-unit*.001;outa=a+normal*.018;outb=b+normal*.018
 poly=[a,b,outb,outa];vs=[[v[0],y,v[1]]for y in [53.075,58.975]for v in poly]
 add(f'FIN_Pier3_MineralFace_{i}','finish_mineral_cream',vs,FACES,'GP_UpperPier_3','Source-fitted18mm mineral facing; retained pier/base/capital and circulation unchanged',grain_axis_xyz=[0,1,0])
# Continuous actual-bearing finish of the visible longitudinal return. The
# original rib crossing stays open; these are closed supported panels, no floor.
for i,(a,b)in enumerate([(-461.1,-451.45),(-450.55,-441.64),(-439.36,-435.4)]):
 box(f'FIN_LongReturn_Underside_{i}','finish_mineral_cream',[-12.82,59.774,a],[-12.18,59.8,b],'GP_LongCeilingReturn_-12.5','Finite mineral soffit directly under the retained ceiling return')
 box(f'FIN_LongReturn_PublicFace_{i}','finish_mineral_cream',[-12.844,59.774,a],[-12.82,60.76,b],'GP_LongCeilingReturn_-12.5','Closed public face and edge, distinct from the floor and timber')
# Existing source cup/lens identities remain paired. Six physically supported
# source lights remain six. All optical properties await native acceptance.
fixtures=copy.deepcopy(plan['fixture_reservations']);byfixture={f['name']:f for f in fixtures}
proposals=[('EAST_Bay_LightReserve_0','Bay',[-13.3,57.15,-447.8],[-10.5,60.02,-453.6]),('CG_Directory_LightReserve','Fore',[-13.3,57.15,-457.0],[-10.6,60.05,-460.5]),('CG_Counter_LightReserve','Market',[-13.3,57.15,-438.3],[-10.5,60.02,-444.3])]
for marker,label,pos,target in proposals:
 f=byfixture[marker];axis=np.array(target)-pos;axis=axis/np.linalg.norm(axis);right=np.cross(axis,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,axis);pos=np.asarray(pos);N=20
 def ring_at(along,r):return [(pos+axis*along+right*math.cos(2*math.pi*k/N)*r+up*math.sin(2*math.pi*k/N)*r).tolist()for k in range(N)]
 plate=loft(f'FIN_{label}_OpticRearBearing','champagne_metal',[ring_at(-.15,.215),ring_at(-.13,.215)],f'FIN_{label}_HeadYoke','Full rear bearing disk for the real optic; source housing back seats on its front face')
 rings=[ring_at(-.13,.20),ring_at(.015,.20),ring_at(.015,.176),ring_at(-.10,.176)];vs=[v for r in rings for v in r];faces=[]
 for j in range(4):
  for k in range(N):faces.append([j*N+k,j*N+(k+1)%N,((j+1)%4)*N+(k+1)%N,((j+1)%4)*N+k])
 replace(f['housing'],'champagne_metal',vs,faces,plate,'Larger visible cross-crown optic; cup back has full physical bearing, front aperture remains open',grain_axis_xyz=right.tolist())
 vs=ring_at(-.045,.176)+ring_at(-.033,.176);faces=[list(range(N-1,-1,-1)),list(range(N,N*2))]+[[k,(k+1)%N,(k+1)%N+N,k+N]for k in range(N)]
 replace(f['physical_lens'],'lens',vs,faces,f['housing'],'Finite visible opal source lens, behind the actual light marker',collision='visual_lens_no_contact',cast_shadow=False)
 z=float(pos[2]);support=f'FIN_LongReturn_Underside_{0 if z< -451.45 else 1 if z< -441.64 else 2}'
 box(f'FIN_{label}_CeilingSeat','champagne_metal',[-12.66,59.734,z+.27],[-12.34,59.774,z+.59],support,'Real bolted bearing against the newly finished retained ceiling return')
 box(f'FIN_{label}_DropStem','champagne_metal',[-12.555,57.00,z+.365],[-12.445,59.734,z+.475],f'FIN_{label}_CeilingSeat','Continuous source-backed stem; lower end remains4.5m above the gallery floor')
 box(f'FIN_{label}_ProjectionArm','champagne_metal',[-13.43,57.00,z+.365],[-12.445,57.11,z+.475],f'FIN_{label}_DropStem','Finite connected outward arm; no route-height intrusion')
 box(f'FIN_{label}_HeadYoke','champagne_metal',[-13.43,57.00,z+.045],[-13.32,57.11,z+.475],f'FIN_{label}_ProjectionArm','Physical yoke cradling the optic rear bearing; fixed metal joint')
 f.update(position_xyz=pos.tolist(),direction_xyz=axis.tolist(),mounting='cross_crown',intended_receiver_xyz=target,source_supports=[plate,f'FIN_{label}_CeilingSeat'],proposed_energy=.85,half_angle_degrees=55,native_acceptance_pending=True)
# Downlight source geometry remains seated in its actual old canopy. Keep its
# direction for this first coherent native comparison; exact source receivers
# include all retained furniture and proposed stock, not a bare-floor proxy.
for f in fixtures:
 if f['name']not in {p[0]for p in proposals}:f.update(proposed_energy=.42,half_angle_degrees=55,native_acceptance_pending=True)
plan.update(status='COHERENT_FINISH_SOURCE_PLAN_PENDING_FIT',parts=parts,fixture_reservations=fixtures,source_base=str(C/'assets/grand_pool_first_pass/architectural_composition/connected_curved_gallery001/export_revision001/directory_sampler_revision003/source/AST-AQU-016_connected_curved_gallery_directory_sampler_r03.blend'),source_base_sha256='cec736ae273f0403f823a6aa7f78007d1c88daf4f5236c2832fea17286778520',modified_existing_parts=sorted(changed),new_parts=sorted(new),material_changes=material_changes,source_finish_revision='002',source_scope_proposal_sha256=sha(B/'SCOPE_PROPOSAL.md'),old_pool_lights_unchanged=True,old_floor_and_route_owners_unchanged=True,actual_native_acceptance=False)
(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'parts':len(parts),'modified_existing_parts':len(changed),'new_parts':len(new),'local_material_reassignments':len(material_changes),'fixtures':len(fixtures),'plan_sha256':sha(B/'CORE_PLAN.json')}))
