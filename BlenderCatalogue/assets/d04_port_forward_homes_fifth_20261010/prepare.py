from pathlib import Path
import json,hashlib,copy
from shapely.geometry import shape,box,Polygon,mapping
from shapely import affinity
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_homes_fifth_20261010';assert not W.exists();W.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();F=R/'BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010';T=R/'BlenderCatalogue/assets/d04_port_forward_homes_third_20261010';N=R/'BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010';FP=json.loads((F/'PLAN.json').read_text());FR=json.loads((F/'RUNTIME_PLAN.json').read_text());TR=json.loads((T/'RUNTIME_PLAN.json').read_text());NP=json.loads((N/'BUILD_PLAN.json').read_text());P=copy.deepcopy(FP);rooms=[];rest_samples=[];bindings=[(FR,910,934),(FR,922,946),(FR,886,958),(TR,988,970),(TR,976,982),(TR,988,994)]
for proto,oldidx,idx in bindings:
 r=copy.deepcopy(next(r for r in proto['rooms']if r['source_index']==oldidx));a=copy.deepcopy(next(u for u in P['all_twenty_allocations_unchanged']if u['source_envelope_index']==idx));assert a['allocation_x']==r['allocation']['allocation_x']and a['proposed_rest_place_count']==r['allocation']['proposed_rest_place_count'];dz=a['allocation_z'][0]-r['allocation']['allocation_z'][0];assert abs(a['allocation_z'][1]-r['allocation']['allocation_z'][1]-dz)<1e-7
 def move(v):v=list(v);v[2]+=dz;return v
 r['parts']=[q for q in r['parts']if q['category']not in['frame','truss_brace']]
 for q in r['parts']:q['name']=q['name'].replace(str(oldidx),str(idx));q['verts']=[move(v)for v in q['verts']]
 slot=0
 for q in r['components']:
  q['position']=move(q['position'])
  if'rest_slot_id'in q:q['rest_slot_id']=a['proposed_rest_slot_ids'][slot];slot+=1
 assert slot==a['proposed_rest_place_count']
 for key in['approach_world','outlook_world','care_station_world']:
  if key in r:r[key]=move(r[key])
 for key in['entry_to_care_waypoints','rest_approach_waypoints']:
  if key in r:r[key]=[move(v)for v in r[key]]
 if'rest_approach_worlds'in r:
  for j,q in enumerate(r['rest_approach_worlds']):q['position']=move(q['position']);q['rest_slot_id']=a['proposed_rest_slot_ids'][j]
 else:r['rest_approach_worlds']=[{'rest_slot_id':a['proposed_rest_slot_ids'][0],'position':r['approach_world'],'operational_access_verified':False}]
 r['entry']['origin']=move(r['entry']['origin']);r['entry']['persistent_id']=a['proposed_runtime_id']+':entry';r['allocation']=a;r['source_index']=idx;r['model_file']=f'D04_PORT_FORWARD_HOME_{idx}_r001.glb'
 for key in['floor_geometry','water_geometry']:
  if r.get(key):r[key]=mapping(affinity.translate(shape(r[key]),yoff=dz))
 for q in r['lights']:q['name']=q['name'].replace(str(oldidx),str(idx));q['at']=move(q['at'])
 for key in['model_sha256','mesh_count','collision_policy']:r.pop(key,None)
 # Keep each inherited original-rest contact exactly, with its target's existing slot.
 for q in proto['rest_reference_samples']:
  if q['room']!=oldidx:continue
  q=copy.deepcopy(q);q['room']=idx;q['position']=move(q['position']);q['source_contact_node']=q['source_contact_node'].replace(str(oldidx),str(idx));q['rest_slot_id']=next(c['rest_slot_id']for c in r['components']if c['name']==q['binding']);rest_samples.append(q)
 rooms.append(r)
P.update(schema='astraea.d04.fifth_homes.plan.v1',base_commit='b400473140215863d38aac5a66f80b60e7103656',rooms=rooms,selected_source_indices=[r['source_index']for r in rooms],foundation_feet=[],commons_parts=[],commons_components=[],courts=[],guard_preimages=[],guard_successor_parts=[],commons_frame_preimages=[],frame_joint_preimages=[],connection_accepted=False,open_room_entries=False,prior_physical_proposals_preserved=14,physical_proposals_after_batch=20,rest_reference_samples=rest_samples)
s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();defs=s[:s.index('from shapely import affinity')].replace('R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent','');ns={'R':R,'W':W};exec(defs,ns);cube=ns['cube'];prism=ns['prism'];parts=ns['parts']
for side,(x0,x1)in[('west',(-62.2,-58.95)),('east',(-29.05,-26.2))]:
 z0,z1=-316.8,-294.8;poly=box(x0,z0,x1,z1);prefix='D04HC5_'+side+'_';prism(prefix+'Floor',poly,16.26,16.5,category='court_floor');prism(prefix+'Roof',poly,20.46,20.66,role='ivory_enamel',category='roof');outside=x0 if side=='west'else x1;lo,hi=(outside,outside+.18)if side=='west'else(outside-.18,outside)
 cube(prefix+'PrivacyScreen',[lo,16.5,z0],[hi,18.45,z1],role='ivory_enamel',category='privacy_screen');cube(prefix+'GlassUpper',[lo,18.45,z0],[hi,20.46,z1],role='hospitality_glass',category='window')
 for j,z in enumerate([z0,z1]):cube(prefix+'End_'+str(j),[x0,16.5,z-.09],[x1,20.46,z+.09],role='ivory_enamel',category='shell')
 for j,z in enumerate([z0+1.5,z0+7.4,z1-7.4,z1-1.5]):
  px=outside+(1.0 if side=='west'else-1.05);bed=box(px-.45,z-.65,px+.45,z+.65).buffer(.2,quad_segs=3);prism(prefix+'Planter_'+str(j),bed,16.5,17.02,role='warm_stone',category='planter');prism(prefix+'Soil_'+str(j),bed.buffer(-.1),17.02,17.06,role='warm_walnut',category='planter')
  for k,(dx,dz,h)in enumerate([(-.18,-.26,.7),(.18,.15,1.05),(0,.38,.65)]):prism(prefix+f'LeafMass_{j}_{k}',box(px+dx-.22,z+dz-.27,px+dx+.22,z+dz+.27).buffer(.18,quad_segs=2),17.05,17.05+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
 P['courts'].append({'side':side,'geometry':mapping(poly),'floor_area_m2':poly.area,'public_access':False,'staff_horticultural_service_held':True,'outlook':'enclosed private planted court, no occupied-volume or hull window'})
P['commons_parts']=copy.deepcopy(parts);parts.clear()
for q in FP['guard_successor_parts']:
 if not q['name'].endswith('_Successor_2'):continue
 lo=[min(v[k]for v in q['verts'])for k in range(3)];hi=[max(v[k]for v in q['verts'])for k in range(3)];west='West'in q['name'];cuts=sorted((r['entry']['origin'][2]-1.78,r['entry']['origin'][2]+1.78)for r in rooms if(r['court_side']=='west')==west);cursor=lo[2];P['guard_preimages'].append({'name':q['name'],'preimage':copy.deepcopy(q),'cuts_z':cuts})
 for j,(a,b)in enumerate(cuts+[(hi[2],hi[2])]):
  assert lo[2]<=a<=b<=hi[2]
  if a>cursor:cube('D04H5_'+q['name']+'_Remaining_'+str(j),[lo[0],lo[1],cursor],[hi[0],hi[1],a],role=q['role'],category='guard_successor')
  cursor=b
P['guard_successor_parts']=copy.deepcopy(parts);parts.clear();assert len(P['guard_preimages'])==2
P['guard_successor_inherited_joint_contacts']={}
def bounds(q):return[[min(v[k]for v in q['verts'])for k in range(3)],[max(v[k]for v in q['verts'])for k in range(3)]]
predecessors=NP['parts']+FP['commons_parts']+[q for r in FP['rooms']for q in r['parts']]
for q in P['guard_successor_parts']:
 lo,hi=bounds(q);g=next(g for g in P['guard_preimages']if g['name']in q['name']);gl,gh=bounds(g['preimage']);assert all(gl[k]<=lo[k]<=hi[k]<=gh[k]for k in range(3));P['guard_successor_inherited_joint_contacts'][q['name']]=[orig['name']for orig in predecessors if orig['name']not in['D04NR_WestGuard_1','D04NR_EastGuard_0']and all(bounds(orig)[0][k]<hi[k]-.002 and bounds(orig)[1][k]>lo[k]+.002 for k in range(3))]
P['transfer_contact_samples']=[]
for i,r in enumerate(rooms):
 a=r['allocation'];xs=[a['allocation_x'][0]+.3,sum(a['allocation_x'])/2,a['allocation_x'][1]-.3];row=0 if i<2 else 1 if i<4 else 2
 for z,beam in[(a['allocation_z'][0]+.12,2+row),(a['allocation_z'][1]-.12,3+row)]:
  for x in xs:P['transfer_contact_samples'].append({'at':[x,16.26,z],'owner':'D04NR_CrossTransfer_'+str(beam),'room':r['source_index']})
for court in P['courts']:
 xs=sorted(set(x for x,z in court['geometry']['coordinates'][0]))
 for z,beam in[(-316.68,2),(-309.5,3),(-302.1,4),(-294.92,5)]:
  for x in[xs[0]+.3,sum(xs)/2,xs[1]-.3]:P['transfer_contact_samples'].append({'at':[x,16.26,z],'owner':'D04NR_CrossTransfer_'+str(beam),'court':court['side']})
for f in P['transfer_contact_samples']:
 x,y,z=f['at'];f['exact_coplanar_original_owners']=[q['name']for q in NP['parts']if q['category']=='transfer_frame'and abs(bounds(q)[1][1]-y)<1e-8 and bounds(q)[0][0]-.051<=x<=bounds(q)[1][0]+.051 and bounds(q)[0][2]-.051<=z<=bounds(q)[1][2]+.051];assert f['owner']in f['exact_coplanar_original_owners']
inputs=set(FP['source_pins']);inputs.update(str(p.relative_to(R))for p in F.glob('*.blend'));inputs.update(['BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/PLAN.json','BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/RUNTIME_PLAN.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_FOURTH.json','Game/scripts/d04_port_forward_homes_fourth.gd']);inputs.update('Game/assets/models/'+q['export']for q in FR['native_export_records']);P['source_pins']={p:sha(R/p)for p in sorted(inputs)}
records=json.loads((R/'BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records']
for court in P['courts']:
 for a in records:assert shape(court['geometry']).intersection(box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1])).area<1e-7
P['limits']=['Six final architectural proposals and nine preserved existing rest slots; no added capacity/species readiness','All20 physical rooms/25rest positions only after this scoped connection gate; full commons/service/activity/environment remain unfinished','Geometry contact to original receiving transfer is not primary/load engineering acceptance','Habitat operation/biology, cart-safe vertical and ordinary Godot/CRT/hardware acceptance remain held','Original homes/sources/allocations/private outlook/public-staff routes protected'];(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare.py').write_text(Path(__file__).read_text());print(json.dumps({'rooms':P['selected_source_indices'],'rest_slots':sum(r['allocation']['proposed_rest_place_count']for r in rooms),'rest_samples':len(rest_samples),'owned_parts':sum(len(r['parts'])for r in rooms)+len(P['commons_parts'])+len(P['guard_successor_parts']),'source_pins':len(P['source_pins']),'transfer_samples':len(P['transfer_contact_samples'])*9,'court_m2':sum(c['floor_area_m2']for c in P['courts'])}))
