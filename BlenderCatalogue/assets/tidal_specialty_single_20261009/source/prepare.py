from pathlib import Path
import json,math,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box,mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');O=R/'BlenderCatalogue/assets/tidal_specialty_single_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
parts=[];floors=[];stairs=[]
def slab(name,poly,lo,hi,role='warm_stone',category='floor',collision=True):
 if poly.is_empty:return
 if poly.geom_type!='Polygon':
  for i,p in enumerate(poly.geoms):slab(name+'_'+str(i),p,lo,hi,role,category,collision)
  return
 poly=orient(poly,sign=1);vs=[];fs=[]
 for t in constrained_delaunay_triangles(poly).geoms:
  q=list(orient(t,sign=1).exterior.coords)[:3];k=len(vs);vs.extend([(x,lo,z)for x,z in q]+[(x,hi,z)for x,z in q]);fs.extend([(k,k+1,k+2),(k+5,k+4,k+3)])
 for ring in [poly.exterior,*poly.interiors]:
  for a,b in zip(ring.coords,list(ring.coords)[1:]):
   k=len(vs);vs.extend([(a[0],lo,a[1]),(a[0],hi,a[1]),(b[0],hi,b[1]),(b[0],lo,b[1])]);fs.append((k,k+1,k+2,k+3))
 parts.append({'name':name,'verts':vs,'faces':fs,'role':role,'category':category,'runtime_collision':collision})
def cube(name,a,b,role='warm_walnut',category='architecture',collision=True):slab(name,box(a[0],a[2],b[0],b[2]),a[1],b[1],role,category,collision)
def rail(name,a,b,y):
 dx,dz=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dz);ux,uz=-dz/n*.04,dx/n*.04
 poly=Polygon([(a[0]+ux,a[1]+uz),(b[0]+ux,b[1]+uz),(b[0]-ux,b[1]-uz),(a[0]-ux,a[1]-uz)])
 slab(name+'_Infill',poly,y+.08,y+1.08,'hospitality_glass','guard');slab(name+'_Cap',poly.buffer(.02,join_style=2),y+1.08,y+1.14,'champagne_metal','guard')
row=next(q for q in json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records']if q['source_envelope_index']==102)
assert row['proposed_runtime_id']=='AST-UNIT-D13-b93f57e92db46ca1' and row['rest_place_count']==1
outline=box(-58.95,-302,-46.05,-294.8)
slab('TQ102_Floor',outline,83.76,84,'warm_stone')
# Compact perimeter enclosure; layered upper edge makes the entry and window recesses legible.
cube('TQ102_NorthWall',[-58.95,84,-302],[-46.05,87.7,-301.78],'ivory_enamel')
cube('TQ102_SouthWall',[-58.95,84,-295.02],[-46.05,87.7,-294.8],'ivory_enamel')
# Court-facing paired windows above a deep seat, not an invented hull view.
cube('TQ102_WestSill',[-58.95,84,-301.78],[-58.65,84.75,-295.02])
cube('TQ102_WestHeader',[-58.95,87,-301.78],[-58.65,87.7,-295.02])
for i,z in enumerate([-301.65,-298.4,-295.15]):cube('TQ102_WestPier_'+str(i),[-58.95,84.75,z-.13],[-58.52,87,z+.13])
for i,(a,b)in enumerate([(-301.52,-298.53),(-298.27,-295.28)]):cube('TQ102_CourtGlass_'+str(i),[-58.89,84.75,a],[-58.81,87,b],'hospitality_glass','window')
# Recessed sliding entry, with physical room-side pockets and a high opaque lintel.
for i,(a,b)in enumerate([(-301.78,-300.14),(-296.66,-295.02)]):cube('TQ102_FrontWall_'+str(i),[-46.3,84,a],[-46.05,87.7,b],'ivory_enamel')
cube('TQ102_EntryLintel',[-46.3,86.72,-300.14],[-46.05,87.7,-296.66])
# A foyer screen turns the sightline away from rest without obstructing the central approach.
slab('TQ102_PrivacyScreen',Polygon([(-50.9,-297.0),(-49.5,-296.8),(-49.1,-296.5),(-49.2,-296.32),(-49.6,-296.6),(-50.9,-296.8)]),84,86.4,'warm_walnut','privacy')
# Wash alcove to the north-east; 1.35m open doorway on south edge.
cube('TQ102_WashWest',[-51.3,84,-301.78],[-51.08,87.4,-299.5],'ivory_enamel')
for i,(a,b)in enumerate([(-51.08,-49.55),(-48.2,-46.3)]):cube('TQ102_WashSouth_'+str(i),[a,84,-299.65],[b,87.4,-299.45],'ivory_enamel')
cube('TQ102_WashLintel',[-49.55,86.28,-299.65],[-48.2,87.4,-299.45])
# Service cabinet accessible from foyer; real shelves and recessed control mounting.
cube('TQ102_ServiceBack',[-46.75,84.15,-296.32],[-46.4,86.15,-295.35])
for i,y in enumerate([84.15,84.75,85.35,85.95]):cube('TQ102_ServiceShelf_'+str(i),[-47.35,y,-296.32],[-46.4,y+.08,-295.35])
for z in [-296.32,-295.43]:cube('TQ102_ServiceSide_'+str(z),[-47.35,84.15,z],[-46.4,86.15,z+.08])
cube('TQ102_ControlMount',[-47.4,85.04,-296.19],[-47.34,85.48,-295.55],'champagne_metal','service_control')
# Belongings and activity edge are separate from cocoon approach and wash doorway.
for j,x in enumerate([-54.0,-52.8]):
 cube('TQ102_StorageBack_'+str(j),[x,84,-295.55],[x+1.05,86.2,-295.08])
 for i,y in enumerate([84.08,84.75,85.4,86.1]):cube(f'TQ102_StorageShelf_{j}_{i}',[x,y,-295.92],[x+1.05,y+.08,-295.08])
cube('TQ102_ActivityTop',[-57.5,84.72,-296.6],[-55.7,84.8,-295.65])
for x in [-57.35,-55.85]:cube('TQ102_ActivityLeg_'+str(x),[x,84,-296.5],[x+.1,84.72,-295.8],'champagne_metal')
# Curved court-side seat as an authored built-in rather than an isolated chair.
seat=Polygon([(-58.5,-297.5),(-57.85,-297.5),(-57.7,-297.1),(-57.75,-296.55),(-57.95,-295.85),(-58.5,-295.65)])
slab('TQ102_WindowSeatBase',seat,84.05,84.4);slab('TQ102_WindowSeatCushion',seat.buffer(-.035),84.4,84.54,'teal_weave')
# Close the room under the next deck without inventing a walkable upper floor.
slab('TQ102_Ceiling',outline,87.7,87.9,'ivory_enamel','ceiling')
for i,(a,b)in enumerate([(-58.55,-57.9),(-51.9,-51.5),(-46.65,-46.25)]):cube('TQ102_CeilingRib_'+str(i),[a,87.46,-301.6],[b,87.7,-295.2])
lights=[]
for i,(x,z)in enumerate([(-52,-298.25),(-56.4,-296.8),(-48.3,-300.65)]):
 cube('TQ102_LightHousing_'+str(i),[x-.4,87.32,z-.25],[x+.4,87.7,z+.25],'champagne_metal','fixture')
 cube('TQ102_LightDiffuser_'+str(i),[x-.32,87.28,z-.2],[x+.32,87.32,z+.2],'opal_glow','fixture',False)
 lights.append({'name':'TQ102_CeilingLight_'+str(i),'position':[x,87.24,z],'range':6,'energy':.8})
source_pins={}
for rel in ['Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb','Game/data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json','Game/data/generated/structural_meshes.json','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']:
 source_pins[rel]=hashlib.sha256((R/rel).read_bytes()).hexdigest()
plan={'schema':'astraea.tidal_specialty_single.v1','status':'new_authored_composition_not_final_accepted','allocation':row,'parts':parts,'lights':lights,'source_pins':source_pins,'component':{'path':'assets/quiet_cocoon_support_20261009','world_origin':[-55.6,84,-300.05],'godot_yaw':-math.pi/2},'doors':[{'name':'EntryDoor','world_origin':[-46.18,84,-298.4],'godot_yaw':math.pi/2,'source':'AST-DOR-002','identity':row['proposed_runtime_id']+':entry'},{'name':'WashDoor','world_origin':[-48.875,84,-299.55],'godot_yaw':0,'source':'AST-DOR-001','identity':row['proposed_runtime_id']+':wash'}],'source_fixtures':[{'catalogue_id':'AST-SAN-001','origin':[-51,84,-300.35],'yaw':0},{'catalogue_id':'AST-SAN-002','origin':[-49.5,84,-301.3],'yaw':0},{'catalogue_id':'AST-SAN-003','origin':[-47.5,84,-301.0],'yaw':0}],'guard_opening_world':{'min':[-46.1,83.99,-300.22],'max':[-45.88,85.25,-296.58]},'limits':['No recovered historical species assignment or save identity claimed','Cocoon fit to actual body/pose and final eye-level CRT review remain open','No pressure/gas/temperature or molting simulation','No Mindo charging design','Source-authored one-room composition before any mass repetition','No extra guest units or rest places','Wet fixtures are retained ordinary source placeholders for later species-compatible review'],'reference_review':'Luxury_single_space_view_8079.jpg inspected: rounded privacy, fitted activity/storage, layered ceiling; room has court view instead of space view.'}
(O/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'source/prepare.py').write_text(Path(__file__).read_text());print('parts',len(parts),'floor area',outline.area)
