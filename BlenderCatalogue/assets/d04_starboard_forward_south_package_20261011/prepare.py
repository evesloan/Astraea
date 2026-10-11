from pathlib import Path
import json,hashlib,copy,subprocess
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda d:hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
read=lambda p:json.load(open(R/p));receiving=read('BlenderCatalogue/assets/d04_starboard_forward_north_receiving_20261011/RUNTIME_PLAN.json')
assert read('Game/artifacts/d04_starboard_north_receiving_geometry.json')['status']=='PASS'
alloc=receiving['all20_units'];byidx={a['source_envelope_index']:a for a in alloc};rooms=[];courts=[];common=[];sources={};pins={};rests=[]
def reflect(v):return [-v[0],*v[1:]]
def geom(g):
 if g is None:return None
 if 'coordinates'in g:
  def walk(x):return reflect(x)if x and isinstance(x[0],(int,float))else[walk(a)for a in x]
  return {**g,'coordinates':walk(g['coordinates'])}
 return {**g,'geometries':[geom(a)for a in g['geometries']]}
def part(t,old='',new=''):
 t=copy.deepcopy(t);t['name']=t['name'].replace(old,new)if old else 'D04SFH_'+t['name'];t['verts']=[reflect(v)for v in t['verts']];t['faces']=[list(reversed(f))for f in t['faces']];return t
for batch in ['first','second','third']:
 path=f'BlenderCatalogue/assets/d04_port_forward_homes_{batch}_20261010/RUNTIME_PLAN.json';p=read(path);pins[path]=sha(R/path)
 for a in p['sources']:sources[a['catalogue_id']]=a
 for r0 in p['rooms']:
  r=copy.deepcopy(r0);old=r['source_index'];new=old+3;a=byidx[new];assert a['proposed_rest_place_count']==r['allocation']['proposed_rest_place_count'];slots=dict(zip(r['allocation']['proposed_rest_slot_ids'],a['proposed_rest_slot_ids']))
  assert a['allocation_x']==[-r['allocation']['allocation_x'][1],-r['allocation']['allocation_x'][0]]and a['allocation_z']==r['allocation']['allocation_z']
  r.update(source_index=new,allocation=a,model_file=f'D04_STARBOARD_FORWARD_HOME_{new}_r001.glb',species_ready=False,source_composition_template={'path':path,'room':old,'sha256':canon(r0)},court_side={'west':'east','east':'west'}[r['court_side']])
  for k in ['model_sha256','mesh_count','collision_policy']:r.pop(k,None)
  r['parts']=[part(t,f'D04H{old}_',f'D04SH{new}_')for t in r['parts']]
  for c in r['components']:
   c['position']=reflect(c['position']);c['yaw']=-c['yaw']
   if 'rest_slot_id'in c:c['rest_slot_id']=slots[c['rest_slot_id']]
  for k in ['approach_world','outlook_world','care_station_world']:
   if k in r:r[k]=reflect(r[k])
  for k in ['entry_to_care_waypoints','rest_approach_waypoints']:
   if k in r:r[k]=[reflect(v)for v in r[k]]
  for k in ['floor_geometry','water_geometry']:r[k]=geom(r[k])
  r['entry']['origin']=reflect(r['entry']['origin']);r['entry']['yaw']=-r['entry']['yaw'];r['entry']['persistent_id']=a['proposed_runtime_id']+':entry'
  for t in r['lights']:t['name']=t['name'].replace(f'D04H{old}_',f'D04SH{new}_');t['at']=reflect(t['at'])
  for t in r.get('rest_approach_worlds',[]):t['position']=reflect(t['position']);t['rest_slot_id']=slots[t['rest_slot_id']]
  for t0 in p['rest_reference_samples']:
   if t0['room']!=old:continue
   t=copy.deepcopy(t0);t['room']=new;t['position']=reflect(t['position']);t['yaw']=-t['yaw'];t['template_rest_slot_id']=t['rest_slot_id'];t['rest_slot_id']=next(c['rest_slot_id']for c in r['components']if c['name']==t['binding']);t['source_contact_node']=t['source_contact_node'].replace(f'D04H{old}_',f'D04SH{new}_');t['reflected_rigid_source_contact_recheck_required']=True;rests.append(t)
  if 'outlook_world'not in r:
   ax=a['allocation_x'];z0,z1=a['allocation_z'];r['outlook_world']=[ax[1]-1 if r['court_side']=='east'else ax[0]+1,16.5,z0+1.3]
  rooms.append(r)
 for t in p['commons_parts']:
  if t['name'].startswith(('D04HC_commons_','D04Commons_')):continue
  common.append(part(t))
 for c in p['courts']:
  if c['side']=='commons':continue
  courts.append({**c,'side':{'west':'east','east':'west'}[c['side']],'geometry':geom(c['geometry'])})
# Native receiving assembled around actual retained starboard bearings; no port staff stair or commons copied.
import ast,math
from shapely.geometry import box,mapping
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
support=read(str((W/'SUPPORT_PREFLIGHT.json').relative_to(R)));assert support['status']=='PASS'
lookup={(round(f['candidate']['x'],4),round(f['candidate']['z'],4)):f['chosen']for f in support['results']}
for room in rooms:
 for t in room['parts']:
  if '_Pier_'not in t['name']:continue
  x=(min(v[0]for v in t['verts'])+max(v[0]for v in t['verts']))/2;z=(min(v[2]for v in t['verts'])+max(v[2]for v in t['verts']))/2;foundation=lookup[round(x,4),round(z,4)];old_y=min(v[1]for v in t['verts'])
  for v in t['verts']:
   if abs(v[1]-old_y)<1e-6:v[1]=foundation['foot'][1]
  t['actual_foundation_preimage']=foundation
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
helper=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for node in ast.parse(helper).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['add','cube','prism']:exec(compile(ast.get_source_segment(helper,node),'<reviewed local geometry helper>','exec'))
street=box(41.95,-445.4,46.05,-334);arrival=box(4,-406.9,44,-403.5);branch=box(46.05,-372.6,63,-367.2);floor=unary_union([street,arrival,branch]);prism('D04SFP_SouthReceivingFloor',floor,16.26,16.5);prism('D04SFP_SouthReceivingRoof',floor,20.48,20.70,role='ivory_enamel',category='roof')
for i,f in enumerate(support['results']):
 if f['candidate']['usage'].startswith('home_'):continue
 x,y,z=f['chosen']['foot'];cube(f'D04SFP_ActualBearingPier_{i:02d}',[x-.14,y,z-.14],[x+.14,16.3,z+.14])
for z in [-442,-424,-406,-388,-370,-352,-334.6]:cube('D04SFP_StreetTransfer_'+str(z),[41.95,15.98,z-.14],[58.76,16.3,z+.14])
for x in [42.2,45.8]:cube('D04SFP_StreetLong_'+str(x),[x-.14,15.98,-445.4],[x+.14,16.3,-334])
for z in [-406.65,-403.75]:cube('D04SFP_ArrivalLong_'+str(z),[4,15.98,z-.14],[44,16.3,z+.14])
for x in [8.5,20,32,43.7]:cube('D04SFP_ArrivalCross_'+str(x),[x-.14,15.98,-406.9],[x+.14,16.3,-403.5])
# Cantilever extension attaches to the supported street transfer at -370; future commons remains sealed at X63.
cube('D04SFP_CommonsApproachTransfer',[58.64,15.98,-370.14],[63,16.3,-369.86])
for x in [46.2,62.8]:cube('D04SFP_CommonsApproachLong_'+str(x),[x-.14,15.98,-372.6],[x+.14,16.3,-367.2])
guards=[]
def guard(name,a,b):
 if a[0]==b[0]:lo=[a[0]-.04,16.62,min(a[1],b[1])];hi=[a[0]+.04,17.62,max(a[1],b[1])]
 else:lo=[min(a[0],b[0]),16.62,a[1]-.04];hi=[max(a[0],b[0]),17.62,a[1]+.04]
 cube(name,lo,hi,role='hospitality_glass',category='guard');cube(name+'_Base',[lo[0],16.5,lo[2]],[hi[0],16.64,hi[2]],category='guard');cube(name+'_Cap',[lo[0],17.6,lo[2]],[hi[0],17.68,hi[2]],category='guard');guards.append(name)
for i,(a,b)in enumerate(zip(floor.exterior.coords,list(floor.exterior.coords)[1:])):
 if (a[0]==4 and b[0]==4)or(a[1]==-334 and b[1]==-334):continue
 guard(f'D04SFP_OuterGuard_{i:02d}',a,b)
lights=[]
for i,(x,z)in enumerate([(10,-405.2),(24,-405.2),(38,-405.2),*[(44,z)for z in [-439,-427,-415,-402,-388,-374,-360,-346]],(54.2,-369.9)]):
 cube(f'D04SFP_LampHousing_{i}',[x-.32,20.18,z-.26],[x+.32,20.48,z+.26],category='light_source');cube(f'D04SFP_LampLens_{i}',[x-.27,20.15,z-.21],[x+.27,20.18,z+.21],role='opal_glow',category='light_source');lights.append({'name':f'D04SFP_LampLens_{i}','at':[x,20.12,z]})
for x in [42.1,45.9]:
 for z in [-445.15,-430.5,-415.7,-408.3,-388,-370,-352,-334.6]:cube('D04SFP_RoofPost_'+str(x)+'_'+str(z),[x-.08,16.3,z-.1],[x+.08,20.5,z+.1])
# Original rigid arrival seating deliberately stays outside the main street and reserved commons.
bench=next(a for a in read('BlenderCatalogue/catalogue_manifest.json')['assets']if a['catalogue_id']=='AST-FUR-001');sources[bench['catalogue_id']]=bench
receiving_bindings=[{'catalogue_id':'AST-FUR-001','name':'SouthArrivalBench','position':[37,16.5,-406.1],'yaw':math.pi/2}]
cube('D04SFP_DirectoryPlinth',[39.5,16.5,-406.8],[41.15,16.72,-406.3],role='warm_walnut',category='fitting');cube('D04SFP_DirectoryFrame',[39.52,16.7,-406.78],[41.13,18.8,-406.54],category='fitting');cube('D04SFP_DirectoryFace',[39.64,16.82,-406.54],[41.01,18.67,-406.51],role='ivory_enamel',category='fitting')
receiving_parts=parts;pre=[]
for t in receiving_parts:
 if t['category']!='guard':continue
 lo=[min(v[i]for v in t['verts'])for i in range(3)];hi=[max(v[i]for v in t['verts'])for i in range(3)];cx=(lo[0]+hi[0])/2
 if abs(cx-41.95)>.001 and abs(cx-46.05)>.001:continue
 cuts=[]
 for room in rooms:
  if abs(room['entry']['origin'][0]-cx)>.4:continue
  z=room['entry']['origin'][2]
  if lo[2]<z<hi[2]:cuts.append([z-1.78,z+1.78])
 if cuts:pre.append({'name':t['name'],'preimage':t,'preimage_sha256':canon(t),'cuts_z':sorted(cuts)})
success=[]
for q in pre:
 t=q['preimage'];lo=min(v[2]for v in t['verts']);hi=max(v[2]for v in t['verts']);start=lo
 for j,(a,b)in enumerate(q['cuts_z']+[[hi,hi]]):
  if a>start:
   piece=copy.deepcopy(t);piece['name']=t['name']+'_Successor_'+str(j);piece['category']='guard_successor';piece['verts']=[[v[0],v[1],start if abs(v[2]-lo)<1e-6 else a]for v in t['verts']];success.append(piece)
  start=b
assert len(pre)==6 and sum(len(q['cuts_z'])for q in pre)==30
north_end=[{'name':t['name'],'preimage':t,'preimage_sha256':canon(t)}for t in receiving['parts']if t['name']in ['D04SF_OuterGuard_00','D04SF_OuterGuard_00_Base','D04SF_OuterGuard_00_Cap']];assert len(north_end)==3
crosswalk='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';allunits=read(crosswalk)['records']
for u in allunits:
 if u['deck']=='D04':assert floor.intersection(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-8,u['source_envelope_index']
for a in sources.values():f='BlenderCatalogue/'+a['source'];pins[f]=sha(R/f)
for f in [crosswalk,'BlenderCatalogue/catalogue_manifest.json','Game/scripts/ship.gd','Game/scripts/structural_floor_builder.gd','Game/data/programme_ledger.json','Game/assets/models/D04_STARBOARD_NORTH_RECEIVING_r001.glb','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json']:pins[f]=sha(R/f)
assert len(rooms)==10 and sum(r['allocation']['proposed_rest_place_count']for r in rooms)==12
P={'schema':'astraea.d04.starboard.southern_physical_package.v1','base_commit':base,'house_id':receiving['house_id'],'all_twenty_allocations_unchanged':alloc,'rooms':rooms,'courts':courts,'commons_parts':common,'receiving_parts':receiving_parts,'receiving_lights':lights,'receiving_bindings':receiving_bindings,'receiving_floor_geometry':mapping(floor),'receiving_floor_m2':floor.area,'guard_preimages':pre,'guard_successor_parts':success,'north_end_guard_preimages':north_end,'foundation_preimages':support['results'],'rest_reference_samples':rests,'sources':list(sources.values()),'source_pins':pins,'new_units':0,'new_rest_places':0,'physical_home_candidates':10,'reserved_rests_fitted':12,'physical_house_proposals_after_batch':20,'species_ready_rooms':0,'active':False,'open_room_entries':False,'limits':['Full commons remains unbuilt beyond sealed X63 approach','Dedicated service circulation/loaded vertical transport remain unfinished','D03cap and original keel bearings establish geometry, not sized engineering','Operational privacy/occupancy/save/species fit/biology/final graphics held'],'phase_evidence':{}}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print({'rooms':len(rooms),'rests':12,'private_courts':len(courts),'receiving_floor_m2':floor.area,'support_positions':len(support['results']),'owned_parts':sum(len(r['parts'])for r in rooms)+len(common)+len(receiving_parts)+len(success)})
