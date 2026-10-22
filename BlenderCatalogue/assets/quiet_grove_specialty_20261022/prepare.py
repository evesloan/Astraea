from pathlib import Path
import json,hashlib,copy,math
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';B=R/'BlenderCatalogue';W=B/'assets/quiet_grove_specialty_20261022';P=G/'quiet_grove_specialty_20261022'
assert not W.exists() and not P.exists()
W.mkdir();P.mkdir();(P/'runtime').mkdir();(P/'evidence').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((B/'assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json').read_text())['records']
source={};sources={};pins={}
for family in ['ninth','tenth','eleventh','twelfth']:
 f=B/f'assets/star_atlas_specialty_{family}_20261010/PLAN.json';d=json.loads(f.read_text());pins[str(f.relative_to(R))]=sha(f)
 for s in d['sources']:
  for field,hashfield in [('source','source_sha256'),('export','export_sha256')]:
   p=B/s[field];assert sha(p)==s[hashfield];pins[str(p.relative_to(R))]=sha(p)
  sources[s['catalogue_id']]=s
 for r in d['rooms']:source[r['allocation']['source_envelope_index']]=(r,f)
existing=json.loads((G/'data/architecture/QUIET_GROVE_UNITS.json').read_text())['units'];existing={x['census_source_index']for x in existing}
targets=[r for r in rows if r['house']=='starboard_forward_upper_house' and r['deck'] in ['D13','D14'] and r['production_lane']=='specialty_family_design_and_fit'];assert len(targets)==17
mapping={r['source_envelope_index']:r['source_envelope_index']-2 for r in targets};mapping.update({361:383,391:395})
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='warm_walnut',category='joinery'):
 x,y,z=lo;X,Y,Z=hi
 return dict(name=name,verts=[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],faces=copy.deepcopy(faces),role=role,category=category,runtime_collision=True)
out=[]
for a in targets:
 i=a['source_envelope_index'];assert i not in existing
 src,f=source[mapping[i]];r=copy.deepcopy(src);s=src['allocation'];sz=-1 if i==391 else 1;dz=sum(a['allocation_z'])/2-sz*sum(s['allocation_z'])/2
 def v(p):return [-p[0]-40,p[1],sz*p[2]+dz]
 prefix=f'QG{i}'
 r['allocation']=a;r['authorship']='New Quiet Grove construction derived from retained exact specialty composition; not recovery of missing work';r['source_contract']=str(f.relative_to(R));r['source_allocation']=s['source_envelope_index'];r['model_file']=f'QuietGroveSpecialty_{i}_r001.glb';r['source_transform']={'mirror_x':True,'z_sign':sz,'translation':[-40,0,dz]};r['profile_proposal']='quiet_grove_'+r['profile_proposal'];r['species_assignment']=None;r['species_ready']=False;r['operations_hold']=True
 for part in r['parts']:
  part['name']=prefix+'_'+part['name'].split('_',1)[-1];part['verts']=[v(p)for p in part['verts']]
  if sz==1:part['faces']=[list(reversed(x))for x in part['faces']]
 for kind in ['components','doors','lights']:
  for item in r[kind]:
   item['position']=v(item['position']);item['name']=prefix+'_'+item['name']
   if 'yaw'in item:item['yaw']=(-item['yaw'] if sz==1 else item['yaw']+math.pi)
   if 'persistent_id'in item:item['persistent_id']=item['persistent_id'].replace(s['proposed_runtime_id'],a['proposed_runtime_id'])
 rests=[x for x in r['components']if 'rest_slot_id'in x];assert len(rests)==a['proposed_rest_place_count']
 for j,item in enumerate(rests):item['rest_slot_id']=a['proposed_rest_slot_ids'][j]
 r['receiving_contacts']={'status':'pending actual house floor/guard/route checks; existing temporary guards retained'}
 r['window_view']={'status':'unfinished contextual visual review','outside_is_exterior':False,'target':'retained five-level Quiet Grove court' if a['allocation_x'][0]>45 else 'retained inner house gallery; contextual outlook not yet accepted'}
 if a['allocation_x'][0]>45:
  old=[x for x in r['parts']if 'OpaqueRearBoundary'in x['name']];assert len(old)==1
  r['parts'].remove(old[0]);c=sum(a['allocation_z'])/2;y=a['floor_y'];x=a['allocation_x'][1];z0,z1=a['allocation_z'];width=5.5;h=3.2
  for label,lo,hi,role,cat in [
   ('CourtSill',[x-.22,y,c-width/2],[x,y+.38,c+width/2],'warm_walnut','joinery'),
   ('CourtHeader',[x-.25,y+3.58,c-width/2],[x,y+3.8,c+width/2],'ivory_enamel','architecture'),
   ('CourtJambNorth',[x-.22,y,z0],[x,y+3.8,c-width/2],'ivory_enamel','architecture'),
   ('CourtJambSouth',[x-.22,y,c+width/2],[x,y+3.8,z1],'ivory_enamel','architecture'),
   ('CourtPanoramicGlass',[x-.08,y+.38,c-width/2],[x-.055,y+3.58,c+width/2],'hospitality_glass','window'),
   ('CourtRevealTop',[x-.48,y+3.48,c-width/2-.1],[x-.12,y+3.58,c+width/2+.1],'warm_walnut','joinery'),
   ('CourtRevealBottom',[x-.48,y+.3,c-width/2-.1],[x-.12,y+.4,c+width/2+.1],'warm_walnut','joinery'),
   ('CourtLightHousing',[x-.55,y+3.38,c-2.2],[x-.38,y+3.47,c+2.2],'champagne_metal','fixture'),
   ('CourtLightDiffuser',[x-.55,y+3.36,c-2.1],[x-.38,y+3.38,c+2.1],'opal_glow','fixture')]:r['parts'].append(box(prefix+'_'+label,lo,hi,role,cat))
  r['lights'].append(dict(name=prefix+'_CourtRevealLight',position=[x-.7,y+3.28,c],energy=.65,range=7))
 r.pop('model_sha256',None);r.pop('mesh_count',None);out.append(r)
for p in [G/'data/architecture/QUIET_GROVE_UNITS.json',G/'data/architecture/QUIET_GROVE_RECEIVING.json',G/'assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb',G/'scripts/quiet_grove_adoption.gd',G/'scripts/quiet_grove_rooms.gd',B/'assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'] :pins[str(p.relative_to(R))]=sha(p)
plan=dict(schema='astraea.quiet_grove_specialty.v1',base_commit='63cc41bda097c5d432d960045dd3ff588c4a1215',rooms=out,sources=list(sources.values()),preimage_pins=pins,rooms_count=17,reserved_rests=19,new_allocations=0,new_capacity=0,status='new native construction; integration and visual acceptance pending',existing83_unchanged=True)
assert sum(x['allocation']['proposed_rest_place_count']for x in out)==19
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Prepared17 specific Quiet Grove specialty compositions,19 existing reserved rest IDs;8? court-frontage rooms',sum(x['allocation']['allocation_x'][0]>45 for x in out))
