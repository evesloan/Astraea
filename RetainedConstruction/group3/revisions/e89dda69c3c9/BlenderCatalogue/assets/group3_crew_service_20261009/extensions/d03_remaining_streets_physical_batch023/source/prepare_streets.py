"""Compose remaining route streets; no anonymous porch/room identities or originals."""
from pathlib import Path
import json,hashlib,math,copy
import shapely
from shapely.geometry import Polygon,Point,box,MultiPoint
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];EXT=HERE.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
source=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json'
old=json.load(open(source));pins={str(source.relative_to(ROOT)):sha(source)}
prior_files={
 'd03_remaining_receivers_batch013':['SELECTED_STREET_PRECINCTS.json','UNIFORM_STREET_EXTENSION.json','TRAINING_RECEIVER.json','ADMINISTRATION_RECEIVER.json','UNIFORMS_RECEIVER.json','MISSING_ONLY_FLOOR_PATCH.json'],
 'labelled_crew_bank_batch014':['BANK_STREET_AND_COLLARS.json','BANK_MISSING_ONLY_FLOOR.json'],
 'fore_starboard_clinical_batch018':['CREW_FORE_STREETS.json','FORE_DOOR_RECEIVERS.json','FORE_MISSING_ONLY_FLOORS.json'],
 'd03_service_receivers_physical_batch021':['D03_SERVICE_ARCHITECTURE.json','D03_SERVICE_FRAME_INFILLS.json','D03_SERVICE_MISSING_FLOOR.json'],
 'd03_port2_live_connection_batch022':['D03_PORT2_FITTED_BRANCH.json','D03_PORT2_MISSING_FLOOR.json'],
 'port2_clinical_physical_batch016':['PORT2_MISSING_ONLY_FLOORS.json']}
previous=[];prior_lights=[]
for folder,files in prior_files.items():
 manifest=EXT/folder/'SHA256SUMS.txt'
 for line in manifest.read_text().splitlines():
  h,f=line.split('  ',1);assert sha(EXT/folder/f)==h,f
 pins[str(manifest.relative_to(ROOT))]=sha(manifest)
 for name in files:
  f=EXT/folder/'source'/name;p=json.load(open(f));pins[str(f.relative_to(ROOT))]=sha(f);previous+=p['parts'];prior_lights+=p.get('fixtures',[])
for f in [ROOT/'Game/assets/models/AST-STF-009_pool_market_home_equipment.glb',ROOT/'Game/scripts/lower_staff_network.gd',ROOT/'Game/scripts/service_door.gd',HERE/'source/CURRENT_SPINE_END_PREIMAGES.json']:
 pins[str(f.relative_to(ROOT))]=sha(f)
def shape(q):
 if 'boundary'in q:return Polygon(q['boundary'],q['holes'])
 if 'aabb'in q:
  a=q['aabb'];return box(a[0],a[4],a[1],a[5])
 return MultiPoint([(v[0],v[2])for v in q['vertices_godot']]).convex_hull
def yr(q):
 if'y'in q:return q['y']
 if'aabb'in q:return q['aabb'][2:4]
 return [min(v[1]for v in q['vertices_godot']),max(v[1]for v in q['vertices_godot'])]
def prism(out,name,g,lo,hi,role,category,cell):
 lo=round(lo,6);hi=round(hi,6)
 if hi-lo<.000001:return
 g=shapely.set_precision(g,grid_size=.000001)
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
# Retain main and interbank route strips only. Anonymous residential porch
# branches are excluded. Port fore main already belongs to the current spine.
areas=unary_union([box(54.9,-480,59.1,432.14),box(-59.1,-214.19,-54.9,432.14),box(84.06,-344.14,87.94,344.14),box(-87.94,-344.14,-84.06,344.14)])
routes=unary_union([Polygon(q['boundary'],q['holes'])for q in old['route_shape']])
scope=routes.buffer(.14,join_style=2).intersection(areas)
# Prior successors deliberately omit original caps/portal walls. Exclude their
# entire source-selection areas; a volume-only subtraction would backfill cuts.
protected_selections=[box(-105.7,-42.7,-53.4,42.7),box(53.4,-42.7,105.7,42.7),box(54.9,420,59.1,432.14),box(77.99,-143,94.01,-42.7)]
service=json.load(open(EXT/'d03_service_receivers_physical_batch021/source/D03_SERVICE_ARCHITECTURE.json'))
protected_selections += [box(*a)for a in service['selected_source_bounds']]
successor_mask=unary_union(protected_selections)
for rel in ['d03_remaining_receivers_batch013/source/prepare_precinct.py','labelled_crew_bank_batch014/source/prepare_bank.py']:
 f=EXT/rel;pins[str(f.relative_to(ROOT))]=sha(f)
write(HERE/'source/PRIOR_SUCCESSOR_SELECTION_EXCLUSIONS.json',dict(source_pins=pins,selections=[list(a.bounds)for a in protected_selections],purpose='Preserve existing caps omitted and receiving apertures cut by prior successors; never restore their original street geometry.'))
# The completed central detours are prior batch013 geometry/floor; use them.
pre=[]
for q in previous:
 lo,hi=yr(q)
 if hi<=12 or lo>=15.34:continue
 g=shape(q).intersection(scope)
 if g.area<1e-10:continue
 assert'vertices_godot'not in q,'Custom roof requires literal section proof before overlap: '+q['name']
 pre.append((g,lo,hi,q['name']))
# Fit only new roof/wall members around literal protected D04 source contacts.
# Existing screens remain full barriers; the owner must resolve three zones.
protected=json.load(open(HERE/'source/PROTECTED_D04_SCOPE_CONTACTS.json'))
pins.update(protected['source_pins']);pins[str((HERE/'source/PROTECTED_D04_SCOPE_CONTACTS.json').relative_to(ROOT))]=sha(HERE/'source/PROTECTED_D04_SCOPE_CONTACTS.json')
for q in protected['contacts']:
 g=Polygon(q['footprint']).buffer(.0001,join_style=2).intersection(scope)
 pre.append((g,q['min'][1],q['max'][1],q['runtime_name']))
# Preserve the existing D04 neighbourhood lower-route enclosure as a shared
# receiver. No parallel wall/roof corridor is introduced inside its roof zone.
existing_route_zones=unary_union([Polygon(q['footprint'])for q in protected['contacts']if q['runtime_name']in['D04SC_LowerStaffCeiling','SAC_LowerSharedRoof','PACO_D04SC_LowerStaffCeiling']])
successor_mask=successor_mask.union(existing_route_zones)
cache={};parts=[];selected=[]
for q in old['parts']:
 g=shape(q).intersection(scope).difference(successor_mask);lo,hi=yr(q)
 if g.area<1e-10:continue
 selected.append(q['name']);levels=sorted({round(v,6)for v in[lo,hi,*[v for _,a,b,_ in pre for v in[a,b]if lo<v<hi]]})
 for a,b in zip(levels,levels[1:]):
  if(a,b)not in cache:cache[a,b]=unary_union([s for s,l,h,n in pre if l<b and h>a])
  prism(parts,q['name']+'_Remaining_'+str(a),g.difference(cache[a,b]),a,b,q['role'],q['category'],q['batch_cell'])
fixtures=[]
for q in old['fixtures']:
 x,y,z=q['position']
 if not scope.contains(Point(x,z))or successor_mask.covers(Point(x,z)):continue
 if any(math.dist(q['position'],p['position'])<.2 for p in prior_lights):continue
 # Source housing/lens must be wholly outside prior solids to own a new light.
 if any(g.contains(Point(x,z))and lo<15.04 and hi>15.015 for g,lo,hi,n in pre):continue
 q=copy.deepcopy(q);q.update(color=[.78,.88,1],energy=.9,range_m=8,runtime_calibration='Existing supported staff-task first-pass profile; final photometry held');fixtures.append(q)
# Named current end-wall derivative is owner-facing; new gate geometry only.
door=dict(name='D03PortSpineContinuationGate',position=[-57,12,-213.9],yaw=math.pi,persistent_id=None)
infills=[]
for suffix,x0,x1,y0 in [('Left',-58.8,-58.38,12),('Right',-55.62,-55.2,12),('Head',-58.38,-55.62,14.82)]:
 prism(infills,'PortContinuation'+suffix,box(x0,-214.19999,x1,-213.72),y0,15.2,'staff_white_paint','door_receiver','port_continuation')
floor_old=[]
for rel in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:
 f=ROOT/rel;p=json.load(open(f));pins[rel]=sha(f);floor_old+=p['regions']
physical_floor_file=HERE/'source/RETAINED_PHYSICAL_FLOOR_SURVEY.json';physical=json.load(open(physical_floor_file));assert not physical['new_remaining_street_package_present']
pins[str(physical_floor_file.relative_to(ROOT))]=sha(physical_floor_file);pins['Game/scripts/ship.gd']=sha(ROOT/'Game/scripts/ship.gd')
existing=unary_union([Polygon(t)for q in floor_old if q['deck']=='D03'for t in q['triangles']]+[Polygon(t)for t in physical['triangles']]);prior_floor=unary_union([shape(q)for q in previous if yr(q)[1]==12])
request=scope.union(unary_union([shape(q)for q in infills]));missing=request.difference(existing).difference(prior_floor);floors=[]
prism(floors,'RemainingD03StreetMissingFloor',missing,11.76,12,'staff_floor','floor','D03_remaining_streets')
base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
write(HERE/'source/REMAINING_STREET_ARCHITECTURE.json',dict(base,catalogue_id='AST-STF-G3-056',parts=parts,fixtures=fixtures,selected_original_parts=selected,anonymous_porch_branches_constructed=False))
write(HERE/'source/REMAINING_STREET_FRAME_INFILLS.json',dict(base,catalogue_id='AST-STF-G3-057',parts=infills,fixtures=[]))
write(HERE/'source/REMAINING_STREET_MISSING_FLOOR.json',dict(base,catalogue_id='AST-STF-G3-058',parts=floors,fixtures=[],new_floor_m2=missing.area,original_and_prior_and_retained_physical_floor_overlay_m2=0))
preimage=json.load(open(HERE/'source/CURRENT_SPINE_END_PREIMAGES.json'))
contract=dict(base,parent_handoff_commit='229e94a67997b910160836366e3e12348544fbc0',current_spine_source=preimage['current_source'],current_spine_sha256=preimage['current_source_sha256'],exact_current_meshes_to_replace=[q['name']for q in preimage['preimage_meshes']],other_current_composite_meshes_retained=284,cut_min=preimage['proposed_cut_min'],cut_max=preimage['proposed_cut_max'],door_bindings=[door],fixtures=fixtures,new_floor_m2=missing.area,scope_polygons=[dict(boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors])for p in shapely.get_parts(scope)],source_programmes_or_banks_or_D01_D04_modified=False,anonymous_porch_branches_constructed=False,original_port_fore_spine_duplicated=False,current_D04_lower_route_enclosure_duplicated=False,existing_D04_route_zones=[dict(boundary=list(g.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in g.interiors])for g in shapely.get_parts(existing_route_zones)],prior_packages_required=['group3_completion_20261011_with_labelled_bank','group3_fore_starboard_clinical_20261011','group3_d03_services_20261011','group3_d03_port2_20261011'],owner_current_spine_patch_required=True,protected_D04_source_geometry_notches_m=.0001,held_main_crossings=[dict(x=57,z_range=[-383.4,-378.88],source=['D04SC_LowerServiceWall_1','D04SC_LowerServiceWall_7']),*protected['held_main_crossings'][1:]],protected_current_D04_source_contacts=protected['contacts'],interbank_worker_offsets=protected['worker_route_offsets_only'],whole_route_connected=False,operation_and_population_ids=None,registered_berths=0,flow_separation_or_full_group_acceptance=False)
write(HERE/'source/REMAINING_STREETS_CONTRACT.json',contract)
print(json.dumps(dict(source_parts=len(parts),fixture_profiles=len(fixtures),new_floor_m2=missing.area,scope_area_m2=scope.area,original_parts_selected=len(selected),prior_geometry_solid_pieces=len(pre),porch_branches=False,shared_patch_owner_held=True)))
