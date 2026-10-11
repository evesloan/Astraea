from pathlib import Path
import json,hashlib,subprocess,copy
from shapely.geometry import box,mapping
from shapely.ops import unary_union,triangulate
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_staff_riser_20261011';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins=json.load(open(W/'AUDIT_SOURCE_PINS.json'));cat=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))['assets'];assert len(cat)==190
files=['BlenderCatalogue/catalogue_manifest.json','Game/scripts/service_door.gd','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/landings/staff_corridor_services.png','Game/docs/reference_register/staff_lift_reference_20261003.jpg','BlenderCatalogue/assets/d04_port_central_neighborhood_20261011/PLAN.json']
for a in cat:
 if a['catalogue_id'] in ['AST-STF-007','AST-STF-008','AST-CIR-003','AST-DOR-003']:
  files += ['BlenderCatalogue/'+a[k] for k in ['source','export']];files += ['Game/assets/models/'+Path(a['export']).name] if (R/'Game/assets/models'/Path(a['export']).name).exists() else []
for f in files:pins[f]=sha(R/f)
protected={f:sha(R/f)for f in subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines()if f.startswith(('Game/','BlenderCatalogue/')) and f.endswith(('.blend','.glb'))};assert len(protected)==4309,len(protected)
(W/'PROTECTED_NATIVE_EXPORT_PREIMAGES.json').write_text(json.dumps(protected,indent=2)+'\n')
P={'schema':'astraea_port_central_staff_catchment_v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'active':False,'source_pins':pins,'master_chapters_reviewed':[5,7,11],'design_identity':'Screened cold institutional service approach from D01 hull-side staff network to D04 port-central northern receiving catchment','new_units':0,'new_rest_places':0,'unchanged_six_neighborhoods':True,'old_forward_lift_unchanged':True,'riser_reservation':'port_service_riser_3','stop_decks':[1,4],'stop_heights':[0,16.5],'unstopped_decks':[2,3],'shared_vertical_and_lobbies':True,'clean_used_new_horizontal_lanes_physically_separated':True,'route_gross_width_m':5.6,'service_doors':[{'name':'UsedServiceDoor','at':[-53.7,0,-100.6],'persistent_id':'port_central_d01_used_service_door_001'},{'name':'CleanServiceDoor','at':[-53.7,0,-97.8],'persistent_id':'port_central_d01_clean_service_door_001'}],'cabinet_at':[-60.4,16.5,-38.2],'limits':['Terminal cells form a connected staff receiving catchment, not the final links into commons or private court work thresholds. Those links remain physical backlog.','D01 upstream network, both landing lobbies and the two-stop cabin are shared. This is not whole-ship clean/used segregation.','No D02/D03 stops, no cuts into retained Training or Staff Administration ceilings.','Loaded service operations, engineering/load sizing, ordinary-game/CRT/hardware/final acceptance, providers/privacy/occupancy/save/biology remain open.','Two older unpublished r004 native byte versions remain unavailable; their exports are not substitutes.'],'parts':[],'lights':[]}
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def addbox(name,lo,hi,role='staff_panel',category='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z
 p={'name':'PCS_'+name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':category,'runtime_collision':True};P['parts'].append(p);return p
lower=unary_union([box(-55.2,-102,-18.8,-96.4),box(-22.8,-96.4,-18.8,-84),box(-23.1,-91.2,-22.8,-88.8)])
upper=unary_union([box(-64.6,-102,-18.8,-96.4),box(-64.6,-96.4,-59,-37.5),box(-22.8,-96.4,-18.8,-84),box(-23.1,-91.2,-22.8,-88.8)])
def slab(poly,y0,y1,name,role,category):
 for i,t in enumerate(triangulate(poly)):
  if not poly.covers(t.representative_point()):continue
  q=list(t.exterior.coords)[:-1];verts=[[x,y,z]for y in[y0,y1]for x,z in q];P['parts'].append({'name':'PCS_'+name+str(i),'verts':verts,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'category':category,'role':role,'runtime_collision':True})
for label,poly,y in [('D01',lower,0),('D04',upper,16.5)]:
 slab(poly,y-.24,y,label+'Floor','rubber_floor','floor');slab(poly,y+3.2,y+3.32,label+'Roof','staff_panel','roof')
 coords=list(poly.exterior.coords)
 for i,(a,b)in enumerate(zip(coords,coords[1:])):
  x,z=a;X,Z=b
  # Actual old-network mouth and controller-owned lift threshold are open.
  if abs(x+55.2)<1e-5 and abs(X+55.2)<1e-5:continue
  if abs(x+23.1)<1e-5 and abs(X+23.1)<1e-5:continue
  # Thin boundary faces extend outwards; no change to lane's planned width.
  if abs(x-X)<1e-5:addbox(label+'Boundary'+str(i),(x-.06,y,min(z,Z)),(x+.06,y+3.2,max(z,Z)))
  else:addbox(label+'Boundary'+str(i),(min(x,X),y,z-.06),(max(x,X),y+3.2,z+.06))
 # Split newly authored clean and closed-used branches, shared landing at east.
 start=-55.2 if label=='D01'else -61.8
 addbox(label+'CleanUsedDivider',(start,y,-99.26),(-23.1,y+3.2,-99.14))
 if label=='D04':addbox('D04CleanUsedLongDivider',(-61.86,y,-99.2),(-61.74,y+3.2,-37.5))
 # Readable practical linear fixtures at both lanes; visible housing/lens support.
 centers=[(x,z)for x in[-50,-41,-32,-21]for z in[-100.6,-97.8]]
 if label=='D04':centers += [(x,z)for x in[-63.2,-60.4]for z in[-90,-80,-70,-60,-50,-40]]
 for i,(x,z)in enumerate(centers):
  addbox(label+'FixtureHousing'+str(i),(x-.65,y+3.015,z-.15),(x+.65,y+3.2,z+.15),'zinc','fixture')
  q=addbox(label+'FixtureLens'+str(i),(x-.6,y+3.005,z-.105),(x+.6,y+3.025,z+.105),'opal_glow','fixture');P['lights'].append({'name':q['name'],'at':[x,y+2.995,z]})
# Shaft on the reserved site; east gate pockets/frame have their original width.
addbox('ShaftWest',(-27.2,-3.2,-92.2),(-27.08,19.7,-87.8),'staff_panel','shaft')
for tag,z,Z in [('South',-92.2,-92.08),('North',-87.92,-87.8)]:addbox('Shaft'+tag,(-27.08,-3.2,z),(-22.8,19.7,Z),'staff_panel','shaft')
for tag,z,Z in [('South',-92.08,-91.92),('North',-88.08,-87.92)]:addbox('ShaftEast'+tag,(-22.92,-3.2,z),(-22.8,19.7,Z),'staff_panel','shaft')
for i,(y,Y)in enumerate([(-3.2,-.24),(2.85,16.5),(19.35,19.7)]):addbox('ShaftEastBlank'+str(i),(-22.92,y,-91.92),(-22.8,Y,-88.08),'staff_panel','shaft')
addbox('ShaftCap',(-27.2,19.7,-92.2),(-22.8,19.94,-87.8),'zinc','roof')
addbox('ShaftPit',(-27.2,-3.2,-92.2),(-22.8,-2.96,-87.8),'zinc','floor')
# Exact probed hull feet: shared column where both authored slabs meet it.
site=json.load(open(W/'SITE_PREFLIGHT.json'));seen=set();P['support_preimages']=site['support_feet']
for i,p in enumerate(site['support_feet']):
 assert p['accepted']and not p['volume_blockers'];x,Y,z=p['top'];key=(round(x,3),round(z,3))
 if key in seen:continue
 seen.add(key);y=p['source_max_y'];addbox('HullShoe'+str(i),(x-.12,y,z-.12),(x+.12,y+.08,z+.12),'zinc','support');addbox('HullColumn'+str(i),(x-.12,y+.08,z-.12),(x+.12,Y,z+.12),'zinc','support')
# Local reveals cover the bounded old wall cut edge while retaining source header.
for tag,z,Z in [('South',-102.06,-101.96),('North',-96.44,-96.34)]:addbox('SourceMouthJamb'+tag,(-55.36,0,z),(-55.1,2.85,Z),'zinc','wall')
addbox('SourceMouthHeader',(-55.36,2.85,-102),(-55.1,3.2,-96.4),'zinc','wall')
# Reuse exact closed used-bin parts with translation only; no inventory/provider.
old=json.load(open(R/'BlenderCatalogue/assets/d04_port_central_neighborhood_20261011/PLAN.json'))
for q in old['assemblies']['CO']:
 if q['name'].startswith('PCC_ReturnBin')and q['name'].endswith('0'):
  n=copy.deepcopy(q);n['name']='PCS_'+q['name'];n['verts']=[[x+11.8,y,z-29.1]for x,y,z in q['verts']];P['parts'].append(n)
P['floor_geometry']={'D01':mapping(lower),'D04':mapping(upper)};P['new_floor_m2']={'D01':lower.area,'D04':upper.area};P['support_unique_columns']=len(seen);P['wall_patch']=json.load(open(W/'WALL_PATCH_PROVENANCE.json'));P['wall_patch_file']=P['wall_patch']['native_export']['export'];P['structure_file']='D04_PORT_CENTRAL_STAFF_STRUCTURE_r001.glb';P['phase_evidence']={'authored':[],'geometry':[],'connected':[]}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_AUTHORING_INPUT_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print('Prepared parts',len(P['parts']),'floor',P['new_floor_m2'],'columns',len(seen))
