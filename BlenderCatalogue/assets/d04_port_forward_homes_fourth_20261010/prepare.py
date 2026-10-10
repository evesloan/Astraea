from pathlib import Path
import json,hashlib,copy,math
from shapely.geometry import Polygon,box,mapping,shape
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010';assert not W.exists();W.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010';N=R/'BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010';P=json.loads((S/'PLAN.json').read_text());RT=json.loads((S/'RUNTIME_PLAN.json').read_text());NP=json.loads((N/'BUILD_PLAN.json').read_text());units=NP['all20_allocations_unchanged'];new=[];rooms=[]
for oldidx,idx in zip([928,940,952,964],[886,898,910,922]):
 r=copy.deepcopy(next(q for q in RT['rooms']if q['source_index']==oldidx));a=copy.deepcopy(next(q for q in units if q['source_envelope_index']==idx));assert a['proposed_rest_place_count']==1 and a['allocation_x']==r['allocation']['allocation_x'];dz=a['allocation_z'][0]-r['allocation']['allocation_z'][0];assert abs(a['allocation_z'][1]-r['allocation']['allocation_z'][1]-dz)<1e-6
 def trans(v):v=list(v);v[2]+=dz;return v
 r['parts']=[q for q in r['parts']if q['category']not in ['frame','truss_brace']]
 for q in r['parts']:q['name']=q['name'].replace(str(oldidx),str(idx));q['verts']=[trans(v)for v in q['verts']]
 for c in r['components']:
  c['position']=trans(c['position'])
  if 'rest_slot_id'in c:c['rest_slot_id']=a['proposed_rest_slot_ids'][0]
 for key in ['approach_world','outlook_world']:r[key]=trans(r[key])
 r['entry']['origin']=trans(r['entry']['origin']);r['entry']['persistent_id']=a['proposed_runtime_id']+':entry';r['allocation']=a;r['source_index']=idx;r['model_file']=f'D04_PORT_FORWARD_HOME_{idx}_r001.glb';r['floor_geometry']=mapping(Polygon([(x,z+dz)for x,z in r['floor_geometry']['coordinates'][0]]))
 if r['water_geometry']:r['water_geometry']=mapping(shape(r['water_geometry']).__class__([(x,z+dz)for x,z in r['water_geometry']['coordinates'][0]]))
 for l in r['lights']:l['at']=trans(l['at']);l['name']=l['name'].replace(str(oldidx),str(idx))
 for key in ['model_sha256','mesh_count','collision_policy']:r.pop(key,None)
 rooms.append(r)
P.update(schema='astraea.d04.fourth_homes.plan.v1',base_commit='45496fdd3eb1397d94e1adb58eeb71bf78267743',rooms=rooms,selected_source_indices=[886,898,910,922],foundation_feet=[],commons_parts=[],commons_components=[],courts=[],guard_preimages=[],guard_successor_parts=[],commons_frame_preimages=[],frame_joint_preimages=[],connection_accepted=False,open_room_entries=False,prior_physical_proposals_preserved=10,physical_proposals_after_batch=14)
# Reuse reviewed authored primitive definitions without executing its historical plan.
s=(S/'prepare.py').read_text();defs=s[:s.index('from shapely import affinity')];defs=defs.replace('R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent','');ns={'R':R,'W':W};exec(defs,ns);cube=ns['cube'];prism=ns['prism'];parts=ns['parts']
for side,(x0,x1)in [('west',(-62.2,-58.95)),('east',(-29.05,-26.2))]:
 z0,z1=-331.6,-317.0;poly=box(x0,z0,x1,z1);prefix='D04HC4_'+side+'_';prism(prefix+'Floor',poly,16.26,16.5,category='court_floor');prism(prefix+'Roof',poly,20.46,20.66,role='ivory_enamel',category='roof');out=x0 if side=='west'else x1;lo,hi=(out,out+.18)if side=='west'else(out-.18,out)
 cube(prefix+'PrivacyScreen',[lo,16.5,z0],[hi,18.45,z1],role='ivory_enamel',category='privacy_screen');cube(prefix+'GlassUpper',[lo,18.45,z0],[hi,20.46,z1],role='hospitality_glass',category='window')
 for j,z in enumerate([z0,z1]):cube(prefix+'End_'+str(j),[x0,16.5,z-.09],[x1,20.46,z+.09],role='ivory_enamel',category='shell')
 for j,z in enumerate([z0+1.5,(z0+z1)/2,z1-1.5]):
  px=out+(1.0 if side=='west'else-1.05);bed=box(px-.45,z-.65,px+.45,z+.65).buffer(.2,quad_segs=3);prism(prefix+'Planter_'+str(j),bed,16.5,17.02,role='warm_stone',category='planter');prism(prefix+'Soil_'+str(j),bed.buffer(-.1),17.02,17.06,role='warm_walnut',category='planter')
  for k,(dx,dz,h)in enumerate([(-.18,-.26,.7),(.18,.15,1.05),(0,.38,.65)]):prism(prefix+f'LeafMass_{j}_{k}',box(px+dx-.22,z+dz-.27,px+dx+.22,z+dz+.27).buffer(.18,quad_segs=2),17.05,17.05+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
 P['courts'].append({'side':side,'geometry':mapping(poly),'floor_area_m2':poly.area,'public_access':False,'staff_horticultural_service_held':True,'outlook':'enclosed private planted court, no occupied-volume or hull window'})
P['commons_parts']=copy.deepcopy(parts);parts.clear()
for q in NP['parts']:
 if q['name']not in ['D04NR_WestGuard_1','D04NR_EastGuard_0']:continue
 lo=[min(v[k]for v in q['verts'])for k in range(3)];hi=[max(v[k]for v in q['verts'])for k in range(3)];west='West'in q['name'];cuts=sorted([(r['entry']['origin'][2]-1.78,r['entry']['origin'][2]+1.78)for r in rooms if(r['court_side']=='west')==west]);cursor=lo[2]
 P['guard_preimages'].append({'name':q['name'],'preimage':copy.deepcopy(q),'cuts_z':cuts})
 for j,(a,b)in enumerate(cuts+[(hi[2],hi[2])]):
  if a>cursor: cube('D04H4_'+q['name']+'_Successor_'+str(j),[lo[0],lo[1],cursor],[hi[0],hi[1],a],role=q['role'],category='guard_successor')
  cursor=b
P['guard_successor_parts']=copy.deepcopy(parts);parts.clear()
# Pin all protected production predecessors and every reused source.
inputs=set(P['source_pins'])|set(NP['source_pins'])
for section in ['first','second','third','northern_receiving']:
 d=R/'BlenderCatalogue/assets'/('d04_port_forward_homes_'+section+'_20261010'if section!='northern_receiving'else'd04_port_forward_northern_receiving_20261010')
 inputs.update(str(p.relative_to(R))for p in d.glob('*.blend'));inputs.add(str((d/'RUNTIME_PLAN.json').relative_to(R)))
inputs.update(['Game/scripts/d04_port_forward_northern_receiving.gd','Game/data/architecture/D04_PORT_FORWARD_NORTHERN_RECEIVING.json','Game/assets/models/D04_PORT_FORWARD_NORTHERN_RECEIVING_r003.glb','Game/data/architecture/D04_PORT_FORWARD_HOMES_SECOND.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json'])
for p in R.glob('Game/assets/models/D04_PORT_FORWARD_HOME_*.glb'):inputs.add(str(p.relative_to(R)))
P['source_pins']={p:sha(R/p)for p in sorted(inputs)}
records=json.loads((R/'BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records']
for court in P['courts']:
 for a in records:assert shape(court['geometry']).intersection(box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1])).area<1e-7
P['transfer_contact_samples']=[]
for r in rooms:
 a=r['allocation'];xs=[a['allocation_x'][0]+.3,sum(a['allocation_x'])/2,a['allocation_x'][1]-.3]
 for z,beam in [(a['allocation_z'][0]+.12,0 if r['source_index']in[886,898]else 1),(a['allocation_z'][1]-.12,1 if r['source_index']in[886,898]else 2)]:
  for x in xs:P['transfer_contact_samples'].append({'at':[x,16.26,z],'owner':'D04NR_CrossTransfer_'+str(beam),'room':r['source_index']})
for court in P['courts']:
 coords=court['geometry']['coordinates'][0];xs=sorted(set(x for x,z in coords));
 for z,beam in[(-331.48,0),(-324.3,1),(-317.12,2)]:
  for x in[xs[0]+.3,sum(xs)/2,xs[1]-.3]:P['transfer_contact_samples'].append({'at':[x,16.26,z],'owner':'D04NR_CrossTransfer_'+str(beam),'court':court['side']})
P['limits']=['Architectural proposals only: no new units/rest slots/species capacity','Six northern interiors/nine rests remain after this four-home batch;full commons/service/environment/biology still unfinished','Support contact to retained receiving frame is geometry evidence, not primary engineering','Protected original homes, crew/pool, routes/privacy and source fittings remain unchanged','Cart-safe vertical access and ordinary Godot/CRT/hardware acceptance remain held']
# Exact runtime rest samples from prior verified originals, rigidly translated only.
P['rest_reference_samples']=[]
for oldidx,idx in zip([928,940,952,964],[886,898,910,922]):
 oldr=next(r for r in RT['rooms']if r['source_index']==oldidx);newr=next(r for r in rooms if r['source_index']==idx);dz=newr['allocation']['allocation_z'][0]-oldr['allocation']['allocation_z'][0]
 for q in RT['rest_reference_samples']:
  if q['room']!=oldidx:continue
  q=copy.deepcopy(q);q['room']=idx;q['position'][2]+=dz;q['source_contact_node']=q['source_contact_node'].replace(str(oldidx),str(idx));P['rest_reference_samples'].append(q)
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare.py').write_text(Path(__file__).read_text());print(json.dumps({'rooms':P['selected_source_indices'],'owned_parts':sum(len(r['parts'])for r in rooms)+len(P['commons_parts'])+len(P['guard_successor_parts']),'source_pins':len(P['source_pins']),'transfer_samples':len(P['transfer_contact_samples']),'court_m2':sum(c['floor_area_m2']for c in P['courts'])}))
