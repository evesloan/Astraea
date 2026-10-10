"""Bounded exact-source D15 receiver survey; no engine or source mutation."""
from pathlib import Path
import json,hashlib,numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from source_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'Game'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=lambda n:json.loads((G/'data/architecture'/n).read_text())
a=json.loads((R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/TIDAL_STAFF_INTERFACE.json').read_text())
house=cfg('TIDAL_LIFT_RECEIVING_CANDIDATE.json');geo=dict(triangles(house['model_file']))
pins={'Game/assets/models/'+house['model_file']:sha(G/'assets/models'/house['model_file'])}
for name in ['TIDAL_SPECIALTY_102.json','TIDAL_SPECIALTY_D13_BATCH.json','TIDAL_AQUATIC_SINGLES.json','TIDAL_AQUATIC_DOUBLE.json','TIDAL_LOW_NEST_SINGLES.json','TIDAL_QUIET_DOUBLES.json']:
 q=cfg(name);pins['Game/data/architecture/'+name]=sha(G/'data/architecture'/name)
 if q.get('frontage_model'):
  t=dict(triangles(q['frontage_model']));pins['Game/assets/models/'+q['frontage_model']]=sha(G/'assets/models'/q['frontage_model'])
  for item in q.get('frontage',{}).get('changed_batches',[]):geo[item['batch']]=t[item['batch']]
for name in ['TIDAL_D13_SERVICE_RECEIVING.json','TIDAL_D14_SERVICE_RECEIVING.json']:
 q=cfg(name)
 for item in q.get('model_bindings',[{'file':q.get('model_file')} ]):
  if 'Patch' in item['file']:continue
  for n,t in triangles(item['file']):geo[name+'/'+n]=t
  pins['Game/assets/models/'+item['file']]=sha(G/'assets/models'/item['file'])
street=cfg('TIDAL_AQUATIC_DOUBLE.json')['street_model']
for n,t in triangles(street):geo['D14street/'+n]=t
pins['Game/assets/models/'+street]=sha(G/'assets/models'/street)
def tops(y):
 out={}
 for name,t in geo.items():
  flat=t[np.all(abs(t[:,:,1]-y)<2e-4,axis=1)]
  polys=[Polygon(v[:,[0,2]]) for v in flat if Polygon(v[:,[0,2]]).area>1e-8]
  if polys:out[name]=unary_union(polys)
 return out
floors=tops(93);lower=tops(88.5);roof=tops(91.84)
for fn in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.loads((G/'data/generated'/fn).read_text())['regions']:
  if abs(q['floor_y']-93)<1e-6:floors[fn+'/'+q['id']]=unary_union([Polygon(t) for t in q['triangles']])
old=unary_union(list(floors.values()))
street_owner=next((n,p) for n,p in floors.items() if n=='TG_Batch_182') if 'TG_Batch_182' in floors else None
localfloors=[(n,p) for n,p in floors.items() if p.intersection(box(-46,-499,-42,-480)).area>1e-8]
street_end=min(p.bounds[1] for n,p in localfloors)
assert abs(street_end-(-482.2))<2e-4,localfloors
fp=next(q for q in a['floor_proposals'] if q['deck']=='D15');approach=unary_union([Polygon(q['boundary'],q['holes']) for q in fp['polygons']])
link=box(-45.7,-498.06,-42.3,-482.2)
assert approach.intersection(link).area<1e-6
newfloor=approach.union(link).difference(old)
assert newfloor.intersection(old).area<1e-7
def surface_hits(t,low,high):
 low=np.array(low);high=np.array(high)
 selected=t[np.all(t.max(axis=1)>low,axis=1)&np.all(t.min(axis=1)<high,axis=1)]
 for tri in selected:
  poly=list(tri)
  for axis in range(3):
   for bound,sign in [(low[axis],1),(high[axis],-1)]:
    out=[]
    for u,v in zip(poly,poly[1:]+poly[:1]):
     iu=(u[axis]-bound)*sign>=0;iv=(v[axis]-bound)*sign>=0
     if iu:out.append(u)
     if iu!=iv:out.append(u+(v-u)*((bound-u[axis])/(v[axis]-u[axis])))
    poly=out
  if len(poly)>2 and sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0])) for i in range(1,len(poly)-1))>1e-8:return True
 return False
candidate=[]
for name,t in geo.items():
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 if surface_hits(t,[-45.7,93.01,-498.06],[-42.3,95.7,-482.09]):candidate.append({'mesh':name,'min':lo.tolist(),'max':hi.tolist()})
house_hits=[q['mesh'] for q in candidate if '/' not in q['mesh']]
assert set(house_hits)=={'TG_Batch_183','TG_Batch_185'},house_hits
post_checks=[];parts=[]
def cube(name,b,role='staff_white_paint',cat='receiver'):
 parts.append({'name':name,'aabb':b,'role':role,'category':cat})
for label,x in [('West',-45.6),('East',-42.4)]:
 cube('D15_LinkWall_'+label,[x-.07,x+.07,93,96.2,-498.06,-482.2])
 cube('D15_LinkReceivingBeam_'+label,[x-.1,x+.1,92.46,92.76,-498.16,-482.1],'staff_zinc','receiving_frame')
 for i,z in enumerate([-497.85,-491,-487,-483]):
  toe=box(x-.1,z-.1,x+.1,z+.1);source=roof if i==0 else lower;union=unary_union(list(source.values()));coverage=toe.intersection(union).area
  assert abs(coverage-.04)<1e-6,(label,z,coverage)
  bottom=91.84 if i==0 else 88.5
  solids=[]
  for n,t in geo.items():
   lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
   if surface_hits(t,[x-.1,bottom+.0002,z-.1],[x+.1,92.46-.0002,z+.1]):solids.append(n)
  assert not solids,(label,z,solids)
  cube('D15_LinkPost_'+label+'_'+str(i),[x-.1,x+.1,bottom,92.46,z-.1,z+.1],'staff_bluegrey_paint','receiving_frame')
  post_checks.append({'post':label+'_'+str(i),'toe_area_m2':coverage,'bottom_y':bottom,'source_owners':[n for n,p in source.items() if p.intersection(toe).area>1e-8],'positive_old_solid_intersections':solids,'capacity_certified':False})
cube('D15_LinkRoof',[-45.77,-42.23,96.2,96.34,-498.2,-482.1],'staff_bluegrey_paint','overhead')
for label,x0,x1 in [('West',-45.7,-45.38),('East',-42.62,-42.3)]:cube('D15_PortalInfill_'+label,[x0,x1,93,95.84,-482.38,-482.02])
cube('D15_PortalHeaderPacking',[-45.38,-42.62,95.81,95.84,-482.38,-482.02],'staff_zinc')
cube('D15_PortalHeader',[-45.7,-42.3,95.84,96.2,-482.38,-482.02])
cube('D15_UnfinishedShaftPhysicalClosure',[-23.18,-23.02,93,96.34,-492.2,-487.8],'staff_bluegrey_paint','unfinished_shaft_closed')
for role,z in [('Clean',-493),('Returns',-487)]:cube('D15_Abandoned'+role+'WestMouthPhysicalClosure',[-62.94,-62.8,93,95.8,z-1.8,z+1.8],'staff_bluegrey_paint','abandoned_mouth_closed')
regions=[]
for i,p in enumerate(shapely.get_parts(newfloor)):
 if p.geom_type!='Polygon' or p.area<1e-7:continue
 regions.append({'id':'TIDAL_D15_MissingOnlyServiceFloor_'+str(i),'deck':'D15','floor_y':93,'thickness':.24,'material_role':'staff_floor','rings':[list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in p.interiors],'triangles':[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms],'area_m2':p.area})
keep=[p for p in a['parts'] if 'D15' in p['name'] and p['category'] not in ['upper_shaft','landing_threshold']];assert len(keep)==64
cuts=[{'mesh':'screen_wall_'+role+'_D15_-6_-63','source':'group3','cut':{'min':[-45.77,92.999,-498.31],'max':[-42.23,95.9,-497.99]}} for role in ['staff_bluegrey_paint','staff_white_paint']]+[{'mesh':n,'source':'house','cut':{'min':[-45.7,92.999,-482.31],'max':[-42.3,94.25,-482.09]}} for n in ['TG_Batch_183','TG_Batch_185']]
for p in [R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/AST-STF-G3-003.blend',R/'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-STF-G3-003.glb',R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/TIDAL_STAFF_INTERFACE.json',G/'scripts/tidal_garden_adoption.gd',G/'scripts/service_door.gd',G/'scripts/lower_staff_network.gd',G/'scripts/tidal_lift_candidate.gd',G/'assets/models/AST-STF-008.glb',G/'data/architecture/TIDAL_D13_SERVICE_RECEIVING.json',G/'data/architecture/TIDAL_D14_SERVICE_RECEIVING.json',R/'BlenderCatalogue/catalogue_manifest.json']:
 pins[str(p.relative_to(R))]=sha(p)
id='AST-RES-TIDAL-D15-SERVICE-001';assert id not in (R/'BlenderCatalogue/catalogue_manifest.json').read_text()
plan={'schema':1,'catalogue_id':id,'floor_y':93,'actual_street_end_z':street_end,'service_crossbar_edge_z':-498.06,'link_length_m':15.86,'local_source_candidates':candidate,'post_checks':post_checks,'retained_source_parts':keep,'new_parts':parts,'floor_regions':regions,'missing_only_floor_area_m2':newfloor.area,'old_floor_overlap_m2':newfloor.intersection(old).area,'cuts':cuts,'fixtures':[q for q in a['fixtures'] if 'D15' in q['name']],'door':{'name':'D15_SharedServiceDoor','persistent_id':'tidal_d15_shared_service_door_001','position':[-44,93,-482.2],'yaw':0,'scale':[1,1,1]},'source_pins':pins,'floor_sources':list(floors),'flow_use':'sequential_sealed_load_shared_portal','simultaneous_hygiene_segregation_accepted':False,'upper_staff_shaft_closed':True,'structural_load_capacity_accepted':False}
(W/'D15_RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'street_end_z':street_end,'link_m':15.86,'house_candidates':house_hits,'posts':post_checks,'floor_area_m2':newfloor.area,'old_floor_overlap_m2':0,'retained_parts':len(keep)}))
