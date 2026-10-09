from pathlib import Path
import json,sys,hashlib,math
import shapely
from shapely.geometry import box,Polygon,mapping
from shapely.ops import unary_union
r=Path(__file__).resolve().parents[4];out=r/'BlenderCatalogue/assets/shared_crew_home_20261009'
old=json.load(open(r/'BlenderCatalogue/assets/crew_service_platform/home_dogleg_candidate_20261006/source/HOME_SPEC.json'))
room=box(-43,-438,-35,-428);hygiene=box(-35,-438,-31,-432);linen=box(-35,-432,-31,-428)
connector=unary_union([box(-42.8,-422.82,-35.2,-419.4),box(-38.4,-428,-35.2,-419.4)])
shape=unary_union([room,hygiene,linen,connector]);assert shape.is_valid
walls=shape.buffer(.14,join_style=2).difference(shape)
retained=unary_union([box(q['world_aabb'][0],q['world_aabb'][4],q['world_aabb'][1],q['world_aabb'][5]) for q in old['retained_home_parts'] if 'Panel' in q['name'] or 'Enamel' in q['name'] or 'Bumper' in q['name'] or 'Lip' in q['name']])
entry=box(-42.8,-423.1,-39.2,-422.7)
walls=walls.difference(retained).difference(entry)
# Two real annex entrances, with solid lintels above the clear portals.
partitions=unary_union([box(-35.07,-438,-34.93,-428),box(-35,-432.07,-31,-431.93)])
doors=[box(-35.2,-433.9,-34.8,-432.5),box(-35.2,-430.5,-34.8,-429.1)]
partitions=partitions.difference(unary_union(doors));walls=unary_union([walls,partitions])
assert walls.intersection(retained).area<1e-7
cover=box(-54,-466,-8,-398);assert cover.covers(shape.buffer(.14,join_style=2))
parts=[]
def prism(name,p,y0,y1,role):
 for i,q in enumerate(shapely.get_parts(p)):
  if q.area<1e-8:continue
  parts.append({'name':name+'_'+str(i),'boundary':list(q.exterior.coords)[:-1],'holes':[list(x.coords)[:-1] for x in q.interiors],'triangles':[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(q).geoms],'y':[y0,y1],'role':role})
def cube(name,b,role):prism(name,box(b[0],b[4],b[1],b[5]),b[2],b[3],role)
prism('HOME_Wall_Lower',walls,12,13.03,'staff_bluegrey_paint');prism('HOME_Wall_Upper',walls,13.03,15.2,'staff_white_paint')
for i,d in enumerate(doors):prism('HOME_Annex_Lintel'+str(i),d.intersection(box(-35.07,-438,-34.93,-428)),14.65,15.2,'staff_white_paint')
# Roof avoids the existing lobby cap entirely, preserving the old source.
cap=shape.buffer(.14,join_style=2)
oldcaps=unary_union([box(q['world_aabb'][0],q['world_aabb'][4],q['world_aabb'][1],q['world_aabb'][5]) for q in old['retained_home_parts'] if 'Cap' in q['name']])
prism('HOME_Ceiling',cap.difference(oldcaps),15.2,15.34,'staff_bluegrey_paint')
# Linen shelves, supported uprights and a shared low work surface.
for x in [-34.2,-31.6]:cube('LinenUpright'+str(x),[x,x+.08,12,14.2,-428.85,-428.3],'staff_zinc')
for j,y in enumerate([12.3,12.85,13.4,13.95]):cube('LinenShelf'+str(j),[-34.2,-31.52,y,y+.06,-428.85,-428.3],'staff_white_paint')
for j in range(3):cube('FoldedLinen'+str(j),[-33.9+j*.72,-33.35+j*.72,12.91,13.08,-428.78,-428.4],'staff_white_paint')
cube('SharedDesk',[-42.7,-40.2,12.73,12.8,-429.4,-428.8],'staff_white_paint')
for x in [-42.6,-40.4]:cube('DeskSupport'+str(x),[x,x+.1,12,12.73,-429.3,-428.9],'staff_zinc')
# Basin has an actual open bowl; fixtures have no live plumbing claim.
cube('BasinCabinet',[-32.0,-31.3,12,12.75,-437.3,-436.2],'staff_bluegrey_paint')
cube('BasinBase',[-32.05,-31.25,12.75,12.81,-437.35,-436.15],'staff_white_paint')
for name,b in [('L',[-32.05,-31.96,12.81,12.96,-437.35,-436.15]),('R',[-31.34,-31.25,12.81,12.96,-437.35,-436.15]),('A',[-31.96,-31.34,12.81,12.96,-437.35,-437.26]),('B',[-31.96,-31.34,12.81,12.96,-436.24,-436.15])]:cube('BasinRim'+name,b,'staff_white_paint')
cube('TapStem',[-31.48,-31.42,12.96,13.22,-436.8,-436.74],'staff_zinc');cube('TapSpout',[-31.72,-31.42,13.16,13.22,-436.8,-436.74],'staff_zinc')
# Private changing alcove screen; no sealed shower or toilet claim.
cube('WashPrivacyScreen',[-33.6,-33.46,12,14.35,-437.6,-435.2],'staff_white_paint')
fixtures=[]
for i,(x,z) in enumerate([(-40.7,-420.8),(-36.8,-424.2),(-39,-430.8),(-39,-434.2),(-32.7,-430.2),(-32.7,-435)]):
 cube('LightHousing'+str(i),[x-.4,x+.4,15.07,15.2,z-.12,z+.12],'staff_zinc');cube('LightEmitter'+str(i),[x-.36,x+.36,15.04,15.07,z-.09,z+.09],'staff_opal');fixtures.append([x,15.02,z])
placements=[]
for side,pos,yaw in [('A',[-41.5,12,-434.8],0),('B',[-36.5,12,-437.0],math.pi)]:
 placements.append({'key':side,'position':pos,'yaw':yaw,'rest_offset':[0,.565,-.9]})
pins={}
for p in [r/'Game/scripts/crew_home_approach.gd',r/'Game/scripts/lower_staff_network.gd',r/'Game/assets/models/AST-STF-010_home_dogleg_labels002.glb',r/'Game/data/generated/structural_meshes.json']:
 pins[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
d={'schema':1,'floor_y':12,'new_floor_owners':0,'parts':parts,'fixtures':fixtures,'beds':placements,'clear_area':mapping(shape),'source_pins':pins,'identity':'D03_employee_cabin0/player_home','registered_berths_added':0,'migration_applied':False,'unfinished':['C036 person and berth migration requires retained concrete keys','400 crew berth district remains unfinished','Species suitability, curtain/drawer operation and wet fixture operation','Final visual and acoustic privacy acceptance']}
(out/'source/SHARED_HOME.json').write_text(json.dumps(d,indent=2)+'\n');print({'parts':len(parts),'area':shape.area,'pins':len(pins),'new_floors':0})
