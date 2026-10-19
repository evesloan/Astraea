import pathlib,json,hashlib,math,collections
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=pathlib.Path(__file__).resolve().parents[4];W=pathlib.Path(__file__).resolve().parent/'receiving_inputs';P=R/'BlenderCatalogue/assets/group3_remaining_receiving_20261019';(P/'source').mkdir(parents=True,exist_ok=True);(P/'exports').mkdir(exist_ok=True);(P/'qa').mkdir(exist_ok=True)
contractpath=R/'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_crew_bank_source_batch015/source/REMAINING_BANK_CONTRACT.json';c=json.load(open(contractpath));oldpath=R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json';old=json.load(open(oldpath));actual=json.load(open(W/'ACTUAL_D03_RECEIVING.json'));plans=json.load(open(W/'RIGID_FURNITURE_FIT_PLAN.json'))['plans'];assert all('world_translation'in p for p in plans)
# Existing main streets already own their 3.88m source selection; new porch portions stop at that exact seam.
mainstreets=unary_union([box(84.06,-344.14,87.94,344.14),box(-87.94,-344.14,-84.06,344.14)])
porches=[];rooms=[];gates=[]
originalporches=unary_union([Polygon(p['boundary'],p['holes'])for p in old['porch_shapes']])
for q in c['instances']:
 x,y,z=q['position'];side=1 if x>0 else -1;end=x+(6 if abs(q['yaw'])<.1 else -6);street=side*86
 porch=originalporches.intersection(box(min(end,street),z-1.8,max(end,street),z+1.8));assert abs(porch.area-abs(end-street)*3.6)<.001
 porches.append(porch.buffer(.14,join_style=2));e=q['source_envelope'];rooms.append(box(e['x'][0],e['z'][0],e['x'][1],e['z'][1]));sign=1 if abs(q['yaw'])<.1 else -1;dx=x+sign*7
 gates.append({'allocation_key':q['allocation_key'],'name':'AnonymousEntry_'+str(q['source_drawing_index']),'physical_component_id':'g3_anonymous_allocation_'+str(q['source_drawing_index'])+'_entry','not_room_or_berth_id':True,'position':[dx,12,z],'yaw':-math.pi/2+q['yaw'],'default_closed':True})
porchscope=unary_union(porches).difference(mainstreets);roomshape=unary_union(rooms);request=roomshape.union(unary_union(porches));previous=[]
for name in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.load(open(R/'Game/data/generated'/name))['regions']:
  if abs(q['floor_y']-12)<.002:previous.extend(Polygon(t)for t in q['triangles'])
previous.extend(Polygon(t)for p in actual['floor_parts']for t in p['triangles_xz']);prior=unary_union(previous)
cols=[]
for o in actual['obstacle_aabbs']:
 a=o['bounds'];name=o['path'].split('/')[-1]
 if a[1]<11.76 and a[4]>15.25 and any(s in name for s in ['Column','Pier','Bearing']):
  p=box(a[0]-.001,a[2]-.001,a[3]+.001,a[5]+.001)
  if p.intersects(request):cols.append({'path':o['path'],'bounds':a})
colshape=unary_union([box(q['bounds'][0]-.001,q['bounds'][2]-.001,q['bounds'][3]+.001,q['bounds'][5]+.001)for q in cols]);missing=shapely.set_precision(request.difference(prior).difference(colshape),.000001);parts=[]
def add(name,g,lo,hi,role,category,cell):
 g=shapely.set_precision(g,.000001)
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon' or p.area<1e-8:continue
  parts.append({'name':name+'_'+str(i),'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors],'triangles':[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],'y':[lo,hi],'role':role,'category':category,'batch_cell':cell})
# Retain original authored branch screens and roof, selecting only uninstalled porch fragments.
for q in old['parts']:
 if 'boundary'not in q:continue
 g=Polygon(q['boundary'],q['holes']).intersection(porchscope).difference(colshape)
 if not g.is_empty:add(q['name']+'_Received',g,*q['y'],q['role'],q['category'],q['batch_cell'])
for q,gate in zip(c['instances'],gates):
 x,y,z=q['position'];sign=1 if abs(q['yaw'])<.1 else -1;dx=gate['position'][0];xa,xb=sorted([x+sign*6,dx+sign*.18]);key=q['allocation_key']
 for j,(a,b)in enumerate([(-1.54,-1.4),(1.4,1.54)]):add(key+'_CollarSide'+str(j),box(xa,z+a,xb,z+b),12,15.2,'staff_white_paint','door_receiver',key)
 add(key+'_CollarHead',box(xa,z-1.54,xb,z+1.54),15.2,15.34,'staff_bluegrey_paint','overhead',key)
 add(key+'_GateHead',box(dx-.18,z-1.38,dx+.18,z+1.38),14.82,15.2,'staff_white_paint','door_receiver',key)
 for j,(a,b)in enumerate([(-1.4,-1.38),(1.38,1.4)]):add(key+'_GateSide'+str(j),box(dx-.18,z+a,dx+.18,z+b),12,15.2,'staff_white_paint','door_receiver',key)
# Split the source floor by original allocation to keep edits and ownership reviewable.
for q,shape,porch in zip(c['instances'],rooms,porches):
 key=q['allocation_key'];owned=missing.intersection(shape.union(porch));add(key+'_MissingFloor',owned,11.76,12,'staff_rubber','floor',key)
# Each overlapping paired porch reaches only the street midline; old floor subtraction removes their shared seam.
floorpolys=[Polygon(p['boundary'],p['holes'])for p in parts if p['category']=='floor'];floorunion=unary_union(floorpolys);assert sum(p.area for p in floorpolys)-floorunion.area<.001;assert floorunion.intersection(prior.buffer(-.00001)).area<.001
assert floorunion.symmetric_difference(missing).area<.01
held=box(-78,167.25,-66,176.75);assert roomshape.intersection(held).area<1e-8
pins={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [contractpath,oldpath,R/'Game/data/generated/structural_meshes.json',R/'Game/data/generated/received_structural_meshes.json',R/'Game/scripts/shared_crew_home.gd',R/'Game/data/architecture/SHARED_CREW_HOME.json']}
spec={'schema':1,'catalogue_id':'G3_REMAINING_BANK_RECEIVERS_20261019','file_stem':'G3_REMAINING_BANK_RECEIVERS_r001','family':'group3_crew_service_20261009','material_contract':'retained_lower_staff_network','source_pins':pins,'parts':parts,'fixtures':[],'source_allocations':183,'new_registered_berths':0,'new_room_ids':0,'C036_migration_applied':False,'new_missing_only_floor_m2':floorunion.area,'protected_column_holes':cols,'selected_original_street_parts':True,'originals_immutable':True}
(P/'source/RECEIVERS.json').write_text(json.dumps(spec,indent=2)+'\n');(W/'ENTRY_GATES.json').write_text(json.dumps(gates,indent=2)+'\n');report={'missing_floor_m2':floorunion.area,'floor_source_components':len(floorpolys),'duplicate_prior_floor_m2':floorunion.intersection(prior).area,'source_parts':len(parts),'rooms':183,'gates':183,'protected_columns':len(cols),'prior_actual_and_compiled_floor_area_m2':prior.area,'source_room_area_m2':roomshape.area,'scope':'Source plan only; current imported geometry contacts and normal view remain to be checked.'};(P/'qa/PLAN.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
