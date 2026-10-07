"""Night Garden source proposal. Read retained owners; write only this subtree."""
from pathlib import Path
import copy, hashlib, json, math, sys
from collections import Counter
R=Path(__file__).resolve().parents[1]; W=R.parents[1]
B=W/'residential-batch-neighborhood-20261006/scale_domestic_r011'
G=Path('/workspace/shared/astraea-godot-production-20261003')
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj): (R/name).write_text(json.dumps(obj,indent=2)+'\n')
source=B/'assemblies/GODOT_BATCH_INSTANCE_MAP.json'; data=json.loads(source.read_text())
old=[r for r in data['instances'] if r['house']=='starboard_central_upper_house']
preserved=[r for r in data['preserved_installed'] if r['house']=='starboard_central_upper_house']
cross_path=W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json'
cross=json.loads(cross_path.read_text())['records']; full=[r for r in cross if r['house']=='starboard_central_upper_house']
boundary_path=R.parent/'HOUSE_BUILD_BOUNDARIES.json'; boundary=next(r for r in json.loads(boundary_path.read_text())['physical_neighborhoods'] if r['physical_membership_id']=='starboard_central_upper_house')
assert len(old)==80 and len(preserved)==2 and len(full)==145
assert Counter(r['historical_class'] for r in old)=={'standard':30,'family':50}
paths=[source,cross_path,boundary_path,W/'residential-neighborhood-audit-20261007/AUDIT.md',B/'source/build_family.py',B/'PROTOTYPE_PLAN.json']
paths += [G/p for p in boundary['preserved_existing_owners']]
paths += [G/'docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx', G/'docs/master_source/MASTER_CURRENT_APPLICATION.json']
for n in ['13017','13041']:paths += [G/f'data/architecture/D13_{n}_profile.json']
for aid in ['AST-SUI-001','AST-SUI-002']:
 paths += [G/f'assets/models/{aid}.glb',C/f'assets/residential_suite/source/{aid}.blend',C/f'assets/residential_suite/exports/{aid}.glb']
refs=[C/'references/intimate/image(20261002-000722).png',C/'references/dense/image(20261002-001051).png',C/'references/botanical/atrium_reference.png',W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png']
paths+=refs
pins={str(p):sha(p) for p in paths}
save('qa/INPUT_PINS.json',pins)
save('qa/REFERENCE_INSPECTION.json',{'actual_master_DOCX':str(paths[-5]) if False else str(G/'docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx'),'chapters_personally_read':[5,6,32],'chapter_32_table_read':True,'images_personally_inspected_full_pixels':[{'path':str(p),'sha256':sha(p)}for p in refs],'observations':['Intimate and dense: layered timber threshold, low sitting edge, patterned warm weave, ceiling contour, framed garden glimpse. Exposed opposite sleeping rooms in the image are not accepted privacy.','Botanical: occupied planted islands and staggered social edges sit around a purposeful void; preserve the existing Night Garden composition instead of inventing a replacement megacourt.','Privacy image: useful clear view from the seated domestic interior. Exterior must remain opaque/polished at oblique, upper, seated and standing observers.'],'architectural_translation':['Glimpse parlor: longitudinal side bench and separate transverse writing pocket, staggered paired rest shoulders and a low floating-looking but wall-supported reading canopy.','Nested gallery: opposed staggered conversation chairs, longitudinal writing gallery, paired offset rest screens and two high split arches framing the same exact rest anchors.','Both keep every inherited main ceiling curve and reserve a central view approach between recovered rear beds.'],'runtime_privacy_evidence':'Existing sealed r010 128-case evidence is isolated detail evidence only; no new-room or house runtime pass.'})

# Graph includes the two protected built neighbors, but never changes them.
allrows=old+preserved; by={r['address']:r for r in allrows}; adj={a:set()for a in by}
for a in allrows:
 for b in allrows:
  if a['address']>=b['address'] or a['deck']!=b['deck']:continue
  ax,az=a['historical_door_marker_xz'];bx,bz=b['historical_door_marker_xz']
  if (abs(ax-bx)<.1 and abs(az-bz)<7.5)or(abs(ax-bx)>3 and abs(az-bz)<.1):adj[a['address']].add(b['address']);adj[b['address']].add(a['address'])
# Existing plans count as distinct; new two-plan graph is bipartite for each street.
designs={}
for seed in sorted(r['address']for r in old):
 if seed in designs:continue
 designs[seed]=0;todo=[seed]
 while todo:
  a=todo.pop()
  for b in adj[a]:
   if b not in {r['address']for r in old}:continue
   if b in designs:assert designs[b]!=designs[a]
   else:designs[b]=1-designs[a];todo.append(b)
units=[];prototypes={};anchors=[]
for r0 in sorted(old,key=lambda r:r['census_source_index']):
 r=copy.deepcopy(r0); h=1 if r['bed_anchors'][0]['source_xyz'][0]<0 else -1
 design=['glimpse_parlor','nested_gallery'][designs[r['address']]];cl=r['historical_class'];key=f'NG_r001__{cl}__{design}__'+('L'if h==1 else'R')
 placements=[]
 def add(label,path,point,yaw=0,candidate=False):
  v={'label':label,'source_xyz':list(point),'source_yaw':yaw,'catalogue_source':None if candidate else path}
  if candidate:v.update(candidate_source=str(B/path),candidate_export=str((B/path).with_suffix('.glb')))
  placements.append(v)
 for i,a in enumerate(r['bed_anchors']):
  assert a['historical_anchor_index']==i and a['evidence']=='exact recovered atlas inset marker'
  add('HistoricalBedAnchor_'+str(i),'assets/guest_rest/source/AST-SLP-001.blend',a['source_xyz'])
  binding=r['anchor_bindings'][i]; assert binding['unit_anchor_index']==i
  binding['prior_generic_prototype_anchor_index']=binding['prototype_anchor_index'];binding['prototype_anchor_index']=i;binding['prototype_marker_name']='DATUM_bed_'+str(i);binding['prototype_component_label']='HistoricalBedAnchor_'+str(i)
  anchors.append({'unit_id':r['rebuild_identity'],'source_index':r['census_source_index'],'slot_id':binding['unit_slot_key'],'ordinal':i,'old_source_xyz':a['source_xyz'],'new_source_xyz':a['source_xyz'],'old_world_xyz':a['world_xyz'],'new_world_xyz':a['world_xyz'],'coordinate_status':a['evidence'],'changed':False})
 if design=='glimpse_parlor':
  add('NightGardenSittingBench','assets/furniture/AST-FUR-001_day_window_bench.blend',(-h*2.18,5.45,0),h*math.pi/2)
  add('NightGardenCommonTable','assets/furniture/AST-FUR-003_day_table.blend',(-h*1.04,5.70,0))
  add('NightGardenWritingChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*2.08,7.24,0),math.pi)
 else:
  add('NightGardenSittingChairA','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*2.17,4.98,0),math.pi)
  add('NightGardenSittingChairB','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*2.05,6.63,0),0)
  add('NightGardenCommonTable','assets/furniture/AST-FUR-003_day_table.blend',(-h*2.07,5.80,0))
  add('NightGardenWritingChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*1.78,7.65,0),-h*math.pi/2)
 add('NightGardenWindowChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',(h*2.80,12.05,0),h*math.pi/2)
 for label,asset,pt in [('bath_vanity','001',(-3.44,3.1,0)),('bath_wc','002',(-2.8,.9,0)),('bath_shower','003',(-1.38,.905,0))]:add(label,'assets/guest_wash/source/AST-SAN-'+asset+'.blend',pt)
 add('EntryDoor','assets/guest_entry_door/source/AST-DOR-002.blend',(0,-.05,0))
 add('BathroomDoor','assets/guest_privacy_door/source/AST-DOR-001.blend',(-.7,2.9,0),math.pi/2)
 add('SuiteKitchenette','domestic_correction/outputs/kitchenette_r001/suite_kitchenette.blend',(3.025,1.4,0),-math.pi/2,True)
 r.update(night_garden_variant=key,night_garden_design=design,night_garden_handing=h,prior_source_recipe_key=r['source_recipe_key'],source_recipe_key=key,component_placements=placements,source_shell=f'outputs/source_r004/{key}/shell.glb',source_shell_sha256=None,source_recipe_sha256=None,source_detail_props_layer=None,source_props_variant='Night Garden authored family',props_variation_status='Deterministic eight-source mapping',finished=False,runtime_enabled=False,instance_adoption_ready=False)
 r['window_source_scope']={'real_finite_aperture_authored':True,'receiving_geometry':r['view_target_family'],'receiving_geometry_status':r['outlook_construction_status'],'outlook_action':r['view_source_action'],'hull_aperture_created':False,'D16_outer_constrained':r['deck']=='D16'and r['source_origin_world_xyz'][0]>85,'royalty790_underside_protected':r['census_source_index']in[590,614]}
 r['privacy_acceptance']={'finite_sealed_profile':'sealed_window_r010','opaque_exterior_clear_interior_required':True,'whole_house_runtime_accepted':False}
 units.append(r)
 if key not in prototypes:
  p=copy.deepcopy(r);p.update(address=key,representative_unit_id=r['address'],representative_source_index=r['census_source_index'],layout='A_open_salon',palette='teal',view_policy='planned_authored_outlook',emphasize_ceiling_joinery=True,preserve_installed=False);prototypes[key]=p
edges=sorted({tuple(sorted([a,b]))for a,bs in adj.items()for b in bs})
result={'schema':'astraea.night_garden_interiors.v1','status':'Source proposal; no runtime adoption','house_id':'starboard_central_upper_house','source_map_sha256':sha(source),'unit_count':80,'preserved_installed_count':2,'supported_lane_total':82,'whole_house_count':145,'whole_house_candidate_counts':boundary['candidate_family_counts'],'counts':dict(Counter(r['historical_class']for r in units)),'rest_slot_count':210,'supported_lane_rest_slots':214,'prototype_count':len(prototypes),'units':units,'preserved_installed':preserved,'prototypes':list(prototypes.values()),'adjacency_edges':edges,'adjacency_pass':all(a not in designs or b not in designs or designs[a]!=designs[b]for a,b in edges),'exact_recovered_coordinates_changed':0,'upper_specialty_unbuilt':47,'VIP_unbuilt':7,'D17_standard_separate_fit_count':9,'whole_ship_units_unchanged':1000,'independent_D04_units':120,'D04_annex':False,'Game_or_Catalogue_writes':False}
assert len(anchors)==210 and len(prototypes)==8 and result['adjacency_pass']
save('NIGHT_GARDEN_80_PLACEMENT_MAP.json',result);save('REST_SLOT_PROVENANCE.json',{'all_coordinates_exact_recovered':True,'coordinates_changed':0,'rows':anchors})
runtime=json.loads((G/'data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json').read_text()); proposed={r['source_envelope_index']:r for r in runtime['units_preserved']}
fit=[]
for r in full:
 if r['production_lane']!='D17_retained_standard_replan':continue
 p=proposed[r['source_envelope_index']];x0,x1=p['candidate_x'];z0,z1=p['candidate_z']; pts=r['historical_bed_anchor_markers']; inside=[x0<=q['x']<=x1 and z0<=q['z']<=z1 for q in pts]
 fit.append({'source_index':r['source_envelope_index'],'historical_address':r['historical_address'],'exact_rest_slot_ids':r['proposed_rest_slot_ids'],'exact_recovered_rest_anchors_xz':pts,'historical_allocation':{'x':r['allocation_x'],'z':r['allocation_z']},'candidate_boundary':p['candidate_boundary'],'anchors_inside_candidate':[{'ordinal':i,'inside':yes}for i,yes in enumerate(inside)],'all_recovered_anchors_fit':all(inside),'source_prototype_assigned':None,'copied_from_lower_deck':False,'status':'HELD: candidate footprint conflicts with exact recovered anchor(s); resolve geometry without silently moving recovered evidence'if not all(inside)else'HELD: no actual interior, access or receiving-window fit yet','support_status':p['compiler_candidate']['status'],'runtime_adopted':False})
assert len(fit)==9
save('D17_NINE_RETAINED_STANDARD_FIT.json',{'count':9,'records':fit,'all_exact_rest_anchors_preserved':True,'new_interiors_built':0})
save('FULL_145_SCOPE.json',{'house':boundary,'units':[dict(r,night_garden_source_status=('protected_installed_no_edit'if r['source_envelope_index']in[16,40]else'new_supported_interior_source'if r['source_envelope_index']in{u['census_source_index']for u in units}else'D17_separate_geometry_fit_held'if r['production_lane']=='D17_retained_standard_replan'else'explicit_unbuilt_specialty_or_VIP'))for r in full],'separate_D04_house_count':20,'separate_D04_no_theme_or_annex':True,'owner_preservation_pins':{str(G/k):pins[str(G/k)]for k in boundary['preserved_existing_owners']},'installed_retrofit_required':'D13-13017 and D13-13041 remain byte-identical and unthemed. Enclosed domestic/privacy/kitchen obligations need a separate reviewed retrofit; current source does not claim them complete.','commons_rule':'Preserve planted gathering island, offset arrivals, alternating stairs, five-stop lift, D15 writing, D16 conversation, D17 reading, retained pendant bearing and partial Royalty790 approach/platform. No new commons slabs or cuts.'})
print('NIGHT_GARDEN_PLAN_READY',len(units),len(prototypes),len(anchors),'D17_fit',sum(r['all_recovered_anchors_fit']for r in fit),'/',len(fit))
