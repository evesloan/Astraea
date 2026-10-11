from pathlib import Path
import json,copy,hashlib,math,ast,subprocess
from shapely.geometry import box,Polygon,shape,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];read=lambda f:json.load(open(R/f));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
paths=['Game/data/architecture/D04_STARBOARD_FORWARD_NORTH_RECEIVING.json','Game/data/architecture/D04_STARBOARD_FORWARD_NORTH_HOMES.json','Game/data/architecture/D04_STARBOARD_FORWARD_SOUTH_PACKAGE.json','Game/data/architecture/D04_STARBOARD_FULL_COMMONS.json'];NR,NH,SR,CO=map(read,paths)
cross='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';units=read(cross)['records'];aft=[u for u in units if u['house']=='port_aft_lower_habitat_house'];assert len(aft)==20 and sum(u['proposed_rest_place_count']for u in aft)==25
transform=lambda v,d=0:[-v[0],v[1],-v[2]+d]
def geom(g,d=0):
 if g is None:return None
 def walk(v):return[-v[0],-v[1]+d]if isinstance(v[0],(int,float))else[walk(a)for a in v]
 return{**g,'coordinates':walk(g['coordinates'])}
def part(p,prefix,d=0):
 a=copy.deepcopy(p);a['name']=prefix+p['name'];a['verts']=[transform(v,d)for v in p['verts']];a.pop('actual_foundation_preimage',None);return a
original_rooms=NH['rooms']+SR['rooms'];rooms=[];mapping_records=[]
for u in aft:
 exact=next(r for r in original_rooms if u['allocation_x']==[-r['allocation']['allocation_x'][1],-r['allocation']['allocation_x'][0]]and u['allocation_z']==[-r['allocation']['allocation_z'][1],-r['allocation']['allocation_z'][0]])
 template=exact
 if u['proposed_rest_place_count']!=exact['allocation']['proposed_rest_place_count']:
  other_index={973:967,967:973}[exact['source_index']];template=next(r for r in original_rooms if r['source_index']==other_index)
 assert template['allocation']['proposed_rest_place_count']==u['proposed_rest_place_count'];d=sum(u['allocation_z'])/2+sum(template['allocation']['allocation_z'])/2
 r=copy.deepcopy(template);idx=u['source_envelope_index'];r.update(allocation=u,source_index=idx,model_file=f'D04_PORT_AFT_HOME_{idx}_r001.glb',source_template={'source_index':template['source_index'],'source_sha256':canon(template),'proper_rotation_y_pi':True,'translation_z':d},species_ready=False,court_side={'east':'west','west':'east'}[template['court_side']]);r['parts']=[part(a,f'PA{idx}_',d)for a in template['parts']]
 if template is not exact:
  r['parts']=[part(a,f'PA{idx}_',d)for a in template['parts']if not(a['category']=='frame'and min(v[1]for v in a['verts'])<16.5)]+[part(a,f'PA{idx}_SF_',0)for a in exact['parts']if a['category']=='frame'and min(v[1]for v in a['verts'])<16.5]
  r['source_template']['structural_grid_template_index']=exact['source_index']
 for k in ['model_sha256','mesh_count','collision_policy']:r.pop(k,None)
 slots=dict(zip(template['allocation']['proposed_rest_slot_ids'],u['proposed_rest_slot_ids']))
 for b in r['components']:
  b['position']=transform(b['position'],d);b['yaw']+=math.pi
  if 'rest_slot_id'in b:b['rest_slot_id']=slots[b['rest_slot_id']]
 for k in ['approach_world','outlook_world','care_station_world']:
  if k in r:r[k]=transform(r[k],d)
 for k in ['entry_to_care_waypoints','rest_approach_waypoints']:
  if k in r:r[k]=[transform(v,d)for v in r[k]]
 for k in ['floor_geometry','water_geometry']:r[k]=geom(r[k],d)
 r['entry']['origin']=transform(r['entry']['origin'],d);r['entry']['yaw']+=math.pi;r['entry']['persistent_id']=u['proposed_runtime_id']+':entry'
 for a in r['lights']:a['name']=f'PA{idx}_'+a['name'];a['at']=transform(a['at'],d)
 for a in r.get('rest_approach_worlds',[]):a['position']=transform(a['position'],d);a['rest_slot_id']=slots[a['rest_slot_id']]
 assert shape(r['floor_geometry']).difference(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-7
 rooms.append(r);mapping_records.append({'target_index':idx,'rotated_envelope_source_index':exact['source_index'],'actual_fitting_template_index':template['source_index'],'rests':u['proposed_rest_place_count'],'translation_z':d})
# Only two declared same-column template exchanges preserve the independently assigned aft rest reservations.
assert sum(a['translation_z']!=0 for a in mapping_records)==2
removed_nr={a['name']for a in NH['guard_preimages']+SR['north_end_guard_preimages']};removed_sr={a['name']for a in SR['guard_preimages']+CO['preimages']};assemblies={}
for label,items in [('NR',[a for a in NR['parts']if a['name']not in removed_nr]),('NH',NH['commons_parts']+NH['guard_successor_parts']),('SR',[a for a in SR['receiving_parts']if a['name']not in removed_sr]),('SH',SR['commons_parts']+SR['guard_successor_parts']),('CO',CO['parts'])]:assemblies[label]=[part(a,'PA'+label+'_')for a in items]
# Merge both receiving plates once, then subtract exact retained compiler-floor triangles at the public interfaces.
receiving=unary_union([shape(geom(NR['floor_geometry'])),shape(geom(SR['receiving_floor_geometry']))]);existing=read('Game/data/generated/structural_meshes.json');baseline=unary_union([Polygon(t)for a in existing['regions']if a['floor_y']==16.5 for t in a['triangles']]);receiving_new=receiving.difference(baseline)
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism']:exec(compile(ast.get_source_segment(text,n),'<reviewed native receiving helper>','exec'))
for label in ['NR','SR']:assemblies[label]=[a for a in assemblies[label]if a['category']not in ['floor','roof']]
prism('PA_ReceivingFloor',receiving_new,16.26,16.5);prism('PA_ReceivingRoof',receiving_new,20.48,20.70,role='ivory_enamel',category='roof');assemblies['Receiving']=parts
# Existing aft midship public-core floor owns X[-7.8,-4] at the arrival. Trim cloned horizontal members/rails to its boundary.
for a in assemblies['NR']:
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if hi[0]>-7.8 and lo[0]<-7.8 and lo[2]>=259 and hi[2]<=292:
  assert len(a['verts'])==8
  for v in a['verts']:
   if v[0]>-7.8:v[0]=-7.8
bindings={}
for label,items in [('NR',NR['rigid_bindings']),('SR',SR['receiving_bindings']),('CO',CO['rigid_bindings'])]:
 bindings[label]=copy.deepcopy(items)
 for b in bindings[label]:b['position']=transform(b['position']);b['yaw']+=math.pi
lights=[]
for label,items in [('NR',NR['lights']),('SR',SR['receiving_lights']),('CO',CO['lights'])]:
 for a in items:
  q=copy.deepcopy(a);q['name']='PA'+label+'_'+a['name'];q['at']=transform(a.get('at',a.get('position')));q.setdefault('staff',q['at'][1]<16);lights.append(q)
courts=[{**a,'side':{'east':'west','west':'east'}[a['side']],'geometry':geom(a['geometry'])}for a in NH['courts']+SR['courts']]
# Inset one original-source seam footing so all four contacts stay on one retained keel patch.
for a in assemblies['CO']:
 if a['name']in ['PACO_D04SC_KeelPier_13','PACO_D04SC_KeelShoe_13']:
  for v in a['verts']:v[0]+=.2
# Keep the aft transfer footing clear of a retained hull patch seam; continuous transfer beam remains above it.
for a in assemblies['SR']:
 if a['name']=='PASR_D04SFP_ActualBearingPier_48':
  for v in a['verts']:v[0]-=.42
allparts=[a for rows in assemblies.values()for a in rows]+[a for r in rooms for a in r['parts']];feet=[]
for a in allparts:
 lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
 if a['category']=='frame'and hi[0]-lo[0]<.5 and hi[2]-lo[2]<.5 and lo[1]<=12.001 and hi[1]>15.9:
  feet.append({'x':(lo[0]+hi[0])/2,'z':(lo[2]+hi[2])/2,'top_y':hi[1],'original_min_y':lo[1],'part_name':a['name'],'width_x':hi[0]-lo[0],'width_z':hi[2]-lo[2]})
 # The commons staff bridge also has shorter keel-to-D03 posts.
 elif a['name'].startswith('PACO_D04SC_KeelPier_'):
  feet.append({'x':(lo[0]+hi[0])/2,'z':(lo[2]+hi[2])/2,'top_y':hi[1],'original_min_y':lo[1],'part_name':a['name'],'width_x':hi[0]-lo[0],'width_z':hi[2]-lo[2]})
sources={a['catalogue_id']:a for p in [NR,NH,SR,CO]for a in p['sources']};pinpaths=paths+[cross,'Game/data/reference/D04_guest_envelopes.json','Game/data/programme_ledger.json','Game/data/generated/structural_meshes.json','Game/data/spatial_layout.json','Game/scripts/ship.gd','Game/scripts/player.gd','Game/scripts/guest_entry_door.gd','Game/scripts/aquatic_section.gd','Game/data/architecture/LOWER_STAFF_NETWORK.json','BlenderCatalogue/catalogue_manifest.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend','BlenderCatalogue/assets/circulation_architecture/AST-CIR-001_H450.manifest.json']+['BlenderCatalogue/'+a['source']for a in sources.values()]
P={'schema':'astraea.d04.port_aft.neighborhood.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'house_id':'port_aft_lower_habitat_house','commons_programme_key':'D04_directory_05','all_twenty_allocations_unchanged':aft,'rooms':rooms,'assemblies':assemblies,'bindings':bindings,'sources':list(sources.values()),'lights':lights,'source_pins':{f:sha(R/f)for f in pinpaths},'courts':courts,'receiving_floor_geometry':mapping(receiving_new),'receiving_floor_m2':receiving_new.area,'existing_public_floor_retained_m2':receiving.intersection(baseline).area,'commons_floor_geometry':geom(CO['commons_floor_geometry']),'lower_staff_floor_geometry':geom(CO['lower_staff_floor_geometry']),'negative_volume_zones':[{**a,'geometry':geom(a['geometry'])}for a in CO['negative_volume_zones']],'mapping_records':mapping_records,'support_candidates':feet,'walking_contacts':[[transform(v)for v in quad]for quad in CO['walking_contacts']],'stair_detailed_contact_replacements':['PACO_'+a for a in CO['stair_detailed_contact_replacements']],'new_units':0,'new_rest_places':0,'active':False,'limits':['Port-only forward staff network has no aft interface; new local approach meets actual shared D03aft spine, not dedicated segregation','No loaded cart/vertical service acceptance','Geometry establishes bearing continuity, not load sizing or D03crew-care engineering acceptance','Privacy/occupancy/providers/species/save/biology and final graphical art remain held'],'phase_evidence':{}}
assert len({a['name']for a in allparts})==len(allparts)
(W/'CANDIDATE_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'SUPPORT_CANDIDATES.json').write_text(json.dumps({'feet':feet},indent=2)+'\n');print({'rooms':20,'rests':25,'parts':len(allparts),'support_candidates':len(feet),'receiving_m2':receiving_new.area,'public_floor_subtracted_m2':P['existing_public_floor_retained_m2'],'two_rest_preserving_template_exchanges':True})
