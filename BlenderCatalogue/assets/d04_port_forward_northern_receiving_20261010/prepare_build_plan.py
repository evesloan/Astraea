from pathlib import Path
import json,hashlib
from shapely.geometry import box,shape,Polygon,mapping
from shapely.ops import unary_union
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'));prior=json.load(open(W/'PLAN.json'));parts=[]
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def prism(name,lo,hi,role,category,collide=True):
 x,y,z=lo;X,Y,Z=hi;parts.append({'name':name,'verts':[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],'faces':faces,'role':role,'category':category,'runtime_collision':collide,'runtime_visual':True})
# Geometric construction proposal: all new foundation paths reach the retained
# hull keel pan rather than assuming a missing D03 slab.
rows=[-331.6,-324.3,-316.9,-309.5,-302.1,-294.8];lanes=[-64.5,-46.35,-41.65,-26.5]
feet=[{'x':x,'z':z,'y':-3.2,'kind':'north_room_and_court_transfer'}for z in rows for x in lanes]
feet +=[{'x':x,'z':z,'y':-3.2,'kind':'street_connector'}for z in[-364.5,-348,-333.5]for x in[-46.35,-41.65]]
feet +=[{'x':x,'z':z,'y':-3.2,'kind':'commons_care_pocket'}for z in[-354.5,-342.5]for x in[-54.4,-46.35]]
for i,f in enumerate(feet):
 x,z=f['x'],f['z'];prism(f'D04NR_KeelShoe_{i}',[x-.45,-3.2,z-.45],[x+.45,-2.95,z+.45],'champagne_metal','keel_shoe');prism(f'D04NR_Pier_{i}',[x-.3,-2.95,z-.3],[x+.3,15.4,z+.3],'champagne_metal','foundation_pier')
for i,x in enumerate(lanes):
 lo=-331.6 if i in[0,3]else-366.;prism(f'D04NR_LongTransfer_{i}',[x-.3,15.4,lo],[x+.3,16.26,-294.8],'champagne_metal','transfer_frame')
for i,z in enumerate(rows):prism(f'D04NR_CrossTransfer_{i}',[-64.8,15.4,z-.3],[-26.2,16.26,z+.3],'champagne_metal','transfer_frame')
for i,z in enumerate([-364.5,-348,-333.5]):prism(f'D04NR_StreetTransfer_{i}',[-46.65,15.4,z-.3],[-41.35,16.26,z+.3],'champagne_metal','transfer_frame')
for i,z in enumerate([-354.5,-342.5]):prism(f'D04NR_CareTransfer_{i}',[-54.7,15.4,z-.3],[-46.05,16.26,z+.3],'champagne_metal','transfer_frame')
prism('D04NR_CareLongTransfer',[-54.7,15.4,-355],[-54.1,16.26,-342],'champagne_metal','transfer_frame')
street=box(-46.05,-366,-41.95,-294.8);bay=box(-54.8,-355,-46.05,-342);floor=unary_union([street,bay]).difference(shape(old['floor_geometry']));roof=unary_union([street,bay]).difference(shape(old['roof_geometry']))
# All missing-only surfaces are explicit polygon extrusions, keeping old floors.
def extrusion(name,poly,lo,hi,role,category):
 from shapely.ops import triangulate
 tris=[t for t in triangulate(poly)if poly.covers(t.representative_point())];vs=[];fs=[]
 for y in[lo,hi]:
  for t in tris:
   q=list(t.exterior.coords)[:3];k=len(vs);vs.extend([[x,y,z]for x,z in q]);fs.append([k,k+2,k+1]if y==lo else[k,k+1,k+2])
 for ring in[poly.exterior,*poly.interiors]:
  c=list(ring.coords)
  for a,b in zip(c,c[1:]):
   k=len(vs);vs.extend([[a[0],lo,a[1]],[b[0],lo,b[1]],[b[0],hi,b[1]],[a[0],hi,a[1]]]);fs.append([k,k+1,k+2,k+3])
 parts.append({'name':name,'verts':vs,'faces':fs,'role':role,'category':category,'runtime_collision':True,'runtime_visual':True})
extrusion('D04NR_MissingOnlyFloor',floor,16.26,16.5,'warm_stone','floor');extrusion('D04NR_MissingOnlyRoof',roof,20.46,20.68,'ivory_enamel','roof')
# Receiving remains safely guarded until the ten room fronts are authored.
for side,x in[('West',-46.11),('East',-41.89)]:
 segments=[(-366,-355),(-342,-294.8)]if side=='West'else[(-366,-294.8)]
 for i,(lo,hi)in enumerate(segments):
  prism(f'D04NR_{side}Guard_{i}',[x-.06,16.5,lo],[x+.06,17.66,hi],'ivory_enamel','guard')
for z in[-294.8]:prism('D04NR_EndGuard_'+str(abs(z)).replace('.','_'),[-46.05,16.5,z-.06],[-41.95,17.66,z+.06],'ivory_enamel','end_guard')
# Street roof supports sit in future front-wall zones, outside the4.1m route.
for i,z in enumerate([-364.5,-354.5,-348,-342.5,-333.5,*rows]):
 for side,x in[('W',-46.17),('E',-41.83)]:prism(f'D04NR_UpperPier_{side}_{i}',[x-.12,16.5,z-.16],[x+.12,20.1,z+.16],'ivory_enamel','upper_pier')
 prism(f'D04NR_PortalHeader_{i}',[-46.35,20.1,z-.18],[-41.65,20.46,z+.18],'ivory_enamel','roof_bearing')
# Enclosed care/resting bay has an opaque service-side edge and visible fixtures.
prism('D04NR_CareWestWall',[-54.98,16.5,-355],[-54.8,20.46,-342],'ivory_enamel','care_enclosure')
for i,z in enumerate([-355,-342]):prism(f'D04NR_CareEndWall_{i}',[-54.8,16.5,z-.09],[-46.05,20.46,z+.09],'ivory_enamel','care_enclosure')
for i,z in enumerate([-354.5,-342.5]):
 prism(f'D04NR_CareUpperPier_{i}',[-54.52,16.5,z-.16],[-54.28,20.1,z+.16],'ivory_enamel','upper_pier');prism(f'D04NR_CareRoofBeam_{i}',[-54.52,20.1,z-.18],[-46.05,20.46,z+.18],'ivory_enamel','roof_bearing')
lights=[]
for i,z in enumerate([-363,-351,-339,-328,-316.9,-305,-296.5]):
 prism(f'D04NR_LampHousing_{i}',[-44.3,20.0,z-.3],[-43.7,20.12,z+.3],'champagne_metal','light_source',False);prism(f'D04NR_LampLens_{i}',[-44.23,19.96,z-.23],[-43.77,20.0,z+.23],'opal_glow','light_source',False);lights.append({'name':f'D04NR_LampLens_{i}','at':[-44,19.93,z]})
for i,z in enumerate([-351,-345]):
 prism(f'D04NR_CareLampHousing_{i}',[-52.8,20.0,z-.3],[-52.2,20.12,z+.3],'champagne_metal','light_source',False);prism(f'D04NR_CareLampLens_{i}',[-52.73,19.96,z-.23],[-52.27,20.0,z+.23],'opal_glow','light_source',False);lights.append({'name':f'D04NR_CareLampLens_{i}','at':[-52.5,19.93,z]})
# Original catalogue furnishings remain rigid sources, not scale/recolor substitutes.
fittings=[{'source':'BlenderCatalogue/assets/furniture/AST-FUR-001_day_window_bench.blend','prefix':'D04NR_QuietBench','origin':[-53.8,16.5,-345],'yaw':0},{'source':'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend','prefix':'D04NR_CareCabinet','origin':[-53.8,16.5,-352.2],'yaw':0}]
pins=dict(prior['source_pins']);extra=['Game/assets/models/AST-HUL-001.glb','BlenderCatalogue/assets/lower_hull_body/source/AST-HUL-001.blend','BlenderCatalogue/assets/lower_hull_body/source/body_contract.json','Game/data/generated/structural_meshes.json','Game/data/whole_ship_layout.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg','BlenderCatalogue/references/landings/staff_corridor_services.png']+[f['source']for f in fittings]+['Game/data/architecture/D04_PORT_FORWARD_HOMES_FIRST.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_SECOND.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json']
for name in extra:pins[name]=sha(R/name)
for stage in['FIRST','SECOND','THIRD']:
 for f,h in json.load(open(R/('Game/data/architecture/D04_PORT_FORWARD_HOMES_'+stage+'.json')))['model_pins'].items():pins['Game/assets/models/'+f]=h
hull=json.load(open(R/'BlenderCatalogue/assets/lower_hull_body/source/body_contract.json'));keel=Polygon(hull['rings'][0]['inner'])
assert all(keel.covers(box(f['x']-.45,f['z']-.45,f['x']+.45,f['z']+.45))for f in feet)
crew=json.load(open(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json'))['instances'];conflicts=[]
for i,f in enumerate(feet):
 foot=box(f['x']-.45,f['z']-.45,f['x']+.45,f['z']+.45)
 for c in crew:
  e=c['source_envelope']
  if foot.intersection(box(e['x'][0],e['z'][0],e['x'][1],e['z'][1])).area>1e-8:conflicts.append([i,c['allocation_key']])
assert not conflicts,conflicts
# Source allocations remain immutable; only new receiving surfaces are outside them.
allunits=old['units'];assert all(floor.intersection(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-8 for u in allunits)
removed=[a for a in old['parts']if a['name'].startswith('D04PF_UpperGuard_10')];assert len(removed)==3
plan={'schema':'astraea.d04.northern_build.v1','status':'UNFINISHED','base_canonical_commit':'4793432b2c2025ebddc595ea1275caa21030a222','house_id':prior['house_id'],'source_pins':pins,'all20_allocations_unchanged':allunits,'remaining_ten_allocations':prior['remaining_ten_allocations_unchanged'],'reserved_rests_remaining':13,'parts':parts,'foundation_feet':feet,'foundation_owner':'LowerHullBody_WIP','foundation_source_mesh':'HUL_KeelPan','foundation_y':-3.2,'foundation_count':len(feet),'foundation_shoes_covered_by_original_keel':True,'crew_proposal_conflicts':conflicts,'floor_geometry':mapping(floor),'roof_geometry':mapping(roof),'street_floor_area_m2':street.area,'care_pocket_floor_area_m2':bay.area,'new_floor_area_m2':floor.area,'lights':lights,'source_fittings':fittings,'guard_preimages':removed,'sealed_start_guard':None,'open_receiving_connection':False,'model_file':'D04_PORT_FORWARD_NORTHERN_RECEIVING_r001.glb','native_file':'D04NorthernReceivingAndTransfer.blend','staff_ceiling_preserved_y_max':15.34,'new_transfer_frame_y_range':[15.4,16.26],'clear_street_width_m':4.1,'clear_street_height_below_headers_m':3.6,'care_cart_station':[-51.8,16.5,-351.9],'quiet_bench_approach':[-51.8,16.5,-345],'all_lower_programme_allocations_clear':True,'new_runtime_installed':False,'new_guest_units':0,'new_rest_places':0,'rooms_built':0,'primary_load_accepted':False,'cart_safe_vertical_accepted':False,'ordinary_graphics_CRT_hardware_accepted':False,'limits':['Geometric keel bearings and transfer continuity only; structural/load/buckling/torsion/pressure engineering not certified','Ten northern interiors/thirteen reserved rests remain after receiving','Care cabinet/bench are static original fittings, not stock/save/seated behavior','Complete neighborhood commons/service/environment/biology, cart-safe vertical,D17 and all8groups remain construction','Original source geometry,200 crew proposals,private outlook and public/staff routes remain protected','No ordinary Godot/CRT/hardware acceptance from headless or Blender diagnostics']}
(W/'BUILD_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'parts':len(parts),'foundation_feet':len(feet),'source_pins':len(pins),'new_floor_m2':floor.area,'room_allocations_changed':0,'crew_proposal_conflicts':0}))
