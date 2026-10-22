from pathlib import Path
import json,hashlib,copy,math
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'Game';B=R/'BlenderCatalogue';P=G/'quiet_grove_bank_20261022';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not (W/'PLAN.json').exists()
previous=json.loads((G/'quiet_grove_specialty_20261022/PACKAGE_R002.json').read_text());rooms=copy.deepcopy(previous['rooms']);sources={s['catalogue_id']:s for s in previous['sources']};pins=copy.deepcopy(previous['preimage_pins']);original={}
rows=json.loads((B/'assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json').read_text())['records']
for f in (G/'data/architecture').glob('STAR_ATLAS_SPECIALTY*.json'):
 d=json.loads(f.read_text());pins[str(f.relative_to(R))]=sha(f)
 for s in d.get('sources',[]):sources[s['catalogue_id']]=s
 for r in d.get('rooms',[]):
  if r['allocation']['deck']=='D15':original[r['allocation']['source_envelope_index']]=(r,f)
for a in rows:
 if a['house']!='starboard_forward_upper_house' or a['deck']!='D15':continue
 i=a['source_envelope_index'];src,f=original[i-2];r=copy.deepcopy(src);s=src['allocation'];assert a['proposed_rest_place_count']==s['proposed_rest_place_count'];assert max(abs(a['allocation_x'][j]-[-s['allocation_x'][1]-40,-s['allocation_x'][0]-40][j])for j in range(2))<1e-7
 F=lambda p:[-p[0]-40,p[1],p[2]-370]
 r['allocation']=a;r['source_transform']={'mirror_x':True,'z_sign':1,'translation':[-40,0,-370]};r['source_contract']=str(f.relative_to(R));r['source_allocation']=s['source_envelope_index']
 for part in r['parts']:part['name']='QG'+str(i)+'_'+part['name'].split('_',1)[-1];part['verts']=[F(p)for p in part['verts']];part['faces']=[list(reversed(x))for x in part['faces']]
 for kind in ['components','doors','lights']:
  for item in r[kind]:
   item['name']='QG'+str(i)+'_'+item['name'];item['position']=F(item['position'])
   if 'yaw'in item:item['yaw']=-item['yaw']
   if 'persistent_id'in item:item['persistent_id']=item['persistent_id'].replace(s['proposed_runtime_id'],a['proposed_runtime_id'])
 for j,c in enumerate([c for c in r['components']if 'rest_slot_id'in c]):c['rest_slot_id']=a['proposed_rest_slot_ids'][j]
 rooms.append(r)
assert len(rooms)==47 and sum(r['allocation']['proposed_rest_place_count']for r in rooms)==59
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role,category):
 x,y,z=lo;X,Y,Z=hi
 return dict(name=name,verts=[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],faces=copy.deepcopy(faces),role=role,category=category,runtime_collision=category!='fixture')
def rot(v,t):return [math.cos(t)*v[0]+math.sin(t)*v[2],v[1],-math.sin(t)*v[0]+math.cos(t)*v[2]]
for r in rooms:
 a=r['allocation'];i=a['source_envelope_index'];prefix='QGB'+str(i);outer=a['allocation_x'][0]>45;inside=-1 if outer else 1;rear=a['allocation_x'][1 if outer else 0];cz=sum(a['allocation_z'])/2;y=a['floor_y'];r['model_file']=f'QuietGroveBank_{i}_r001.glb';r['rest_moves']=[];r['furniture_moves']=[]
 # Keep all original shell/side/entry/wash construction except the room-owned rear closure.
 removed=[];kept=[]
 for part in r['parts']:
  xs=[v[0]for v in part['verts']]
  rear_part=all(abs(x-rear)<.56 for x in xs) and (part['category'] in ['architecture','window','joinery','fixture'])
  if rear_part:removed.append(part['name'])
  else:kept.append(part)
 assert removed,(i,'no identifiable rear boundary');r['parts']=kept;r['replaced_room_owned_rear_parts']=removed
 def bx(label,xlo,xhi,ylo,yhi,zlo,zhi,role,cat):r['parts'].append(box(prefix+'_'+label,[min(xlo,xhi),ylo,zlo],[max(xlo,xhi),yhi,zhi],role,cat))
 x=rear;xin=rear+inside*.24;left,right=a['allocation_z'];pane0,pane1=cz-2.8,cz+2.8
 bx('CourtSill',x,xin,y,y+.40,pane0,pane1,'warm_walnut','joinery');bx('CourtHeader',x,xin,y+3.52,y+3.74,pane0,pane1,'ivory_enamel','architecture')
 bx('CourtNorthPier',x,xin,y,y+3.74,left,pane0,'ivory_enamel','architecture');bx('CourtSouthPier',x,xin,y,y+3.74,pane1,right,'ivory_enamel','architecture')
 bx('PrivateCourtGlass',x+inside*.055,x+inside*.08,y+.40,y+3.52,pane0,pane1,'hospitality_glass','window')
 for z in [pane0,pane1]:bx('DeepReveal_'+str(z),x+inside*.15,x+inside*.45,y+.32,y+3.58,z-.065,z+.065,'warm_walnut','joinery')
 for h in [.34,3.52]:bx('DeepReveal_'+str(h),x+inside*.15,x+inside*.45,y+h,y+h+.08,pane0,pane1,'warm_walnut','joinery')
 # Quiet enclosures face the real outlook, set back to reserve a full-width ~3m viewing lounge.
 cocoons=[c for c in r['components']if c['catalogue_id']=='AST-RST-QC-001' and 'rest_slot_id'in c];doors=[d for d in r['doors']if 'CocoonPrivacyDoor'in d['name']];assert len(doors) in [0,len(cocoons)]
 ordering=sorted(range(len(cocoons)),key=lambda j:cocoons[j]['position'][2])
 for j,c in enumerate(cocoons):
  old=copy.deepcopy(c);door=doors[j] if doors else None;dv=[door['position'][k]-old['position'][k]for k in range(3)] if door else [-math.sin(c['yaw']),0,-math.cos(c['yaw'])];delta=(-inside*math.pi/2)-math.atan2(dv[0],dv[2]);offset=(-2.2 if ordering.index(j)==0 else 2.2) if len(cocoons)>1 else (-2.2 if old['position'][2]<=cz else 2.2)
  target=[rear+inside*4.65,y,cz+offset];old_door=copy.deepcopy(door)
  if door:door['position']=[target[k]+rot(dv,delta)[k]for k in range(3)];door['yaw']+=delta
  c['position']=target;c['yaw']+=delta
  r['rest_moves'].append({'slot_id':c['rest_slot_id'],'source_component':old,'target_component':copy.deepcopy(c),'door_before':old_door,'door_after':copy.deepcopy(door),'yaw_delta':delta,'outlook_direction_x':-inside,'common_view_lounge_depth_m':2.9})
 # Rotate the whole study arrangement together: tabletop folio/fixture stay supported, chair faces its desk across the lounge.
 study=next(c for c in r['components']if c['catalogue_id']=='AST-LIB-STUDY-02');old_origin=study['position'][:];new_origin=[rear+inside*1.45,y,cz+2.05];delta=inside*math.pi/2
 for c in r['components']:
  if any(k in c['name']for k in ['LibraryStudyEdge','DayReadingChair','StudyChair','SupportedOpenFolio','HousedStudyTaskFixture']):
   old=copy.deepcopy(c);v=rot([c['position'][k]-old_origin[k]for k in range(3)],delta);c['position']=[new_origin[k]+v[k]for k in range(3)];c['yaw']+=delta;r['furniture_moves'].append({'before':old,'after':copy.deepcopy(c)})
  elif 'StreetReadingChair'in c['name']:
   old=copy.deepcopy(c);c['position']=[rear+inside*1.55,y,cz-1.65];c['yaw']=inside*math.pi/2;r['furniture_moves'].append({'before':old,'after':copy.deepcopy(c)})
 # Ceiling edges and luminous reveals are a room-scale finish, not a change to structural headroom.
 for side in [-1,1]:
  z=cz+side*3.16
  bx('CoveHousing_'+str(side),a['allocation_x'][0]+.35,a['allocation_x'][1]-.35,y+3.54,y+3.68,z-.12,z+.12,'warm_walnut','fixture')
  bx('CoveDiffuser_'+str(side),a['allocation_x'][0]+.45,a['allocation_x'][1]-.45,y+3.53,y+3.55,z-.065,z+.065,'opal_glow','fixture')
  r['lights'].append(dict(name=prefix+'_ViewLoungeLight_'+str(side),position=[rear+inside*2.1,y+3.32,cz+side*1.7],range=7,energy=.85))
 r['species_assignment']=None;r['species_ready']=False;r['operations_hold']=True;r['window_view']={'target':'retained five-level Quiet Grove court'if outer else'retained inner Quiet Grove garden/gallery volume','exterior':False,'visual_accepted':False};r['legacy_source_rest_fittings']=r.pop('rest_fittings',[]);r.pop('model_sha256',None);r.pop('mesh_count',None)
for s in sources.values():
 for f,h in [('source','source_sha256'),('export','export_sha256')]:
  p=B/s[f];assert sha(p)==s[h];pins[str(p.relative_to(R))]=sha(p)
for p in [G/'quiet_grove_specialty_20261022/PACKAGE_R002.json',G/'quiet_grove_specialty_20261022/TARGET_BINDINGS.json',G/'scripts/quiet_grove_integration_20261022/ship.gd']:pins[str(p.relative_to(R))]=sha(p)
plan={'schema':'astraea.quiet_grove_bank.v1','base_commit':'9f737647f7b867c662c02917fc9ad0810c5e43b8','rooms':rooms,'sources':list(sources.values()),'preimage_pins':pins,'newly_fitted_rooms':30,'recomposed_existing_rooms':17,'reserved_rests':59,'new_capacity':0,'status':'unfinished architectural successor, no final room/whole-ship acceptance'}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PREPARED47',sum(len(r['rest_moves'])for r in rooms),'cocoon moves,59 reserved rests')
