"""Count physical retained source witnesses without adding capacity or roster keys."""
from pathlib import Path
import json,re,hashlib,numpy as np
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
pins={};checks=[]
def check(n,ok):checks.append(dict(name=n,pass_check=bool(ok)));assert ok,n
def load(file):
 f=ROOT/'Game/assets/models'/file;pins[str(f.relative_to(ROOT))]=sha(f);return GLB(f)
def witness(g,name):
 v,f,_,_=g.geometry(name);v=np.asarray(v);check('physical_mesh_'+name,len(f)>0 and np.isfinite(v).all());return dict(runtime_name=name,triangles=len(f),min=v.min(axis=0).tolist(),max=v.max(axis=0).tolist())
dining=load('SOL_D03_directory_04_source001.glb');seats=[n for n in dining.by_name if re.fullmatch(r'Mess_\d+_\d+_seat-?1_\d+',n)];check('exact_300_retained_dining_seat_meshes',len(seats)==300)
seat_witnesses=[witness(dining,n)for n in seats]
manifest=ROOT/'Game/data/architecture/crew_batch/runtime_manifest.json';pins[str(manifest.relative_to(ROOT))]=sha(manifest);rows=json.load(open(manifest))['sections'];programmes={}
required={'05':['E_demonstrationarrivalheader','E_practicalarrivalheader','E_equipmentarrivalheader','E_focusedarrivalheader'],'07':['E_social_active_separator','E_active_south','E_quiet_front_middle'],'08':['E_briefing_portthresholdheader','E_briefing_starboardthresholdheader']}
for key in['05','06','07','08','10']:
 f=ROOT/f'Game/data/architecture/crew_batch/D03_directory_{key}_NODE_NAME_MAP.json';pins[str(f.relative_to(ROOT))]=sha(f);mapping=json.load(open(f));by_name={q['source_name']:q['runtime_name']for q in mapping};row=[q for q in rows if q['programme']=='D03_directory_'+key][0];g=load(row['model_file']);w=[]
 for name in required.get(key,[]):check('source_name_mapping_'+name,name in by_name);q=witness(g,by_name[name]);q['source_name']=name;w.append(q)
 programmes['D03_directory_'+key]=dict(model=row['model_file'],physical_source_meshes=sum('mesh'in n for n in g.by_name.values()),explicit_subspace_witnesses=w,source_import_light_count=row['source_import_light_count'],retained_mounted_light_profiles=len(row['mounted_receiving_lights']),space_person_capacity_or_gameplay_accepted=False)
 if key=='10':
  bodies=[q for q in mapping if re.fullmatch(r'E_change_\d+_locker_\d+_\d+body',q['source_name'])];cells=sorted({int(q['source_name'].split('_')[2])for q in bodies});check('six_distinct_retained_change_cell_groups',cells==[1,2,3,4,5,6]);check('84_physical_locker_bodies',len(bodies)==84)
  programmes['D03_directory_10'].update(distinct_source_change_cell_groups=cells,physical_locker_body_meshes=84,locker_witnesses=[dict(source_name=q['source_name'],**witness(g,q['runtime_name']))for q in bodies],personal_storage_entitlements_400_mapped=False)
depot=load('SOL_D03_directory_03_remaining_r001.glb');check('installed_depot_447_original_meshes',sum('mesh'in n for n in depot.by_name.values())==447)
q=dict(status='PASS_RETAINED_PHYSICAL_SOURCE_CENSUS_ONLY',source_pins=pins,checks=len(checks),dining=dict(required_places=300,retained_physical_seat_meshes=300,unique_assigned_dining_anchors=None,crew_total_requirement=400,simultaneous_meal_capacity_for_400=False,meal_cadence_food_stock_species_and_sitting_gameplay_accepted=False,seat_witnesses=seat_witnesses),training=dict(required_cells=4,distinct_named_source_cell_headers=4,source_cell_names=['demonstration','practical','equipment','focused'],operational_acceptance=False),briefing=dict(required_rooms=2,distinct_named_source_room_headers=2,operational_acceptance=False),recreation=dict(required_sections=3,named_source_sections=['social','active','quiet'],historical_minimum_places=12,occupancy_or_operational_acceptance=False),change=dict(required_cells=6,physical_source_cell_groups=6,physical_locker_body_meshes=84,personal_storage_entitlements_400_mapped=False),security=dict(required_stations=6,accepted_location_map=None,administration_support_not_six_stations=True,locations_officer_and_bridge_access_held=True),depot=dict(installed_original_meshes=447,duplicate_room_or_physics_cart_created=False,stock_acceptance=False),programmes=programmes,room_headers_ids_originals_capacity_and_registry_modified=False,details=checks,full_group_accepted=False)
(HERE/'qa/RETAINED_PROGRAMME_SOURCE_CENSUS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['status','checks','training','briefing','recreation','change','security','depot']}))
