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
for batch in ['fourth','fifth']:
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
  rooms.append(r)
 for t in p['commons_parts']:common.append(part(t))
 for c in p['courts']:courts.append({**c,'side':{'west':'east','east':'west'}[c['side']],'geometry':geom(c['geometry'])})
# Exact bounded six-member replacement: two long guards, their base and cap.
pre=[];success=[]
for t in receiving['parts']:
 if t['name'] not in [f'D04SF_OuterGuard_{n:02d}{s}'for n in [1,6]for s in ['', '_Base','_Cap']]:continue
 pre.append({'name':t['name'],'preimage':t,'preimage_sha256':canon(t)})
# Right street edge is a service-wall continuation; discover by actual X boundedness rather than assume ring index.
for t in receiving['parts']:
 lo=[min(v[i]for v in t['verts'])for i in range(3)];hi=[max(v[i]for v in t['verts'])for i in range(3)]
 if t['category']=='guard' and abs((lo[0]+hi[0])/2-46.05)<.001 and hi[2]-lo[2]>35 and t['name']not in [p['name']for p in pre]:pre.append({'name':t['name'],'preimage':t,'preimage_sha256':canon(t)})
assert len(pre)==3,len(pre)
for p in pre:
 t=p['preimage'];lo=min(v[2]for v in t['verts']);hi=max(v[2]for v in t['verts']);cuts=sorted([[sum(r['allocation']['allocation_z'])/2-1.78,sum(r['allocation']['allocation_z'])/2+1.78]for r in rooms if abs(r['entry']['origin'][0]-sum([min(v[0]for v in t['verts']),max(v[0]for v in t['verts'])])/2)<.4]);assert len(cuts)==5
 p['cuts_z']=cuts;start=lo
 for j,(a,b)in enumerate(cuts+[[hi,hi]]):
  if a>start:
   q=copy.deepcopy(t);q['name']='D04SFH_'+t['name']+'_Successor_'+str(j);q['verts']=[[v[0],v[1],start if abs(v[2]-lo)<.000001 else a]for v in t['verts']];q['category']='guard_successor';success.append(q)
  start=b
# Court beam ends extend existing supports with declared exact preimages, source never replaced.
frames=[]
def box(name,lo,hi):
 x,y,z=lo;X,Y,Z=hi;return {'name':name,'verts':[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'role':'champagne_metal','category':'frame','runtime_collision':True}
for t in receiving['parts']:
 if not t['name'].startswith('D04SF_StreetTransfer_'):continue
 lo=[min(v[i]for v in t['verts'])for i in range(3)];hi=[max(v[i]for v in t['verts'])for i in range(3)];frames.append({'name':t['name'],'preimage':t,'preimage_sha256':canon(t),'joint_overlap_m':.12})
 common.append(box('D04SFH_CourtTransferWest_'+str(len(frames)),[26.08,lo[1],lo[2]],[lo[0]+.12,hi[1],hi[2]]));common.append(box('D04SFH_CourtTransferEast_'+str(len(frames)),[hi[0]-.12,lo[1],lo[2]],[62.4,hi[1],hi[2]]))
assert len(frames)==6
for a in sources.values():f='BlenderCatalogue/'+a['source'];pins[f]=sha(R/f)
for f in ['BlenderCatalogue/catalogue_manifest.json','BlenderCatalogue/assets/d04_starboard_forward_north_receiving_20261011/PLAN.json','Game/assets/models/D04_STARBOARD_NORTH_RECEIVING_r001.glb','Game/scripts/ship.gd','Game/data/programme_ledger.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json']:pins[f]=sha(R/f)
assert sum(r['allocation']['proposed_rest_place_count']for r in rooms)==13
P={'schema':'astraea.d04.starboard.northern_homes.v1','base_commit':base,'house_id':receiving['house_id'],'all_twenty_allocations_unchanged':alloc,'rooms':rooms,'courts':courts,'commons_parts':common,'guard_preimages':pre,'guard_successor_parts':success,'frame_joint_preimages':frames,'rest_reference_samples':rests,'sources':list(sources.values()),'source_pins':pins,'new_units':0,'new_rest_places':0,'physical_home_candidates':10,'reserved_rests_fitted':13,'remaining_southern_interiors':10,'remaining_southern_rests':12,'species_ready_rooms':0,'active':False,'open_room_entries':False,'limits':['Southern receiving and full commons unbuilt','Shared public/service approach; full segregation and loaded vertical route open','Primary engineering, operational privacy, body fit, occupancy, save and final graphics held'],'phase_evidence':{}}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print({'rooms':len(rooms),'rests':13,'courts':len(courts),'ownedparts':sum(len(r['parts'])for r in rooms)+len(common),'guardpreimages':len(pre),'successors':len(success),'framejoints':len(frames),'sourcepins':len(pins)})
