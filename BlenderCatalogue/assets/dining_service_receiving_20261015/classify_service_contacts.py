from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent;d=json.loads((D/'SERVICE_CANDIDATE_RUNTIME.json').read_text());r=json.loads((D/'NATIVE_RECEIVER_VERIFICATION.json').read_text());assert d['status']=='PASS';bounds={x['name']:x for x in r['bounds']};known=[];bad=[]
for row in d['old_contact_inventory']:
 name=row['part'];key=row['programme_key'];unit=key[-2:]
 for path in row['old_contacts']:
  kind=None
  if 'ExistingOpeningUpperClosure'in name:
   allowed=['0','1']if'Clean'in name else['1','2']
   if any(path.endswith('/SOL_D10_directory_'+unit+'_remaining_batch/C_service_boundary_'+x+'/StaticContact')for x in allowed):kind='new_upper_header_positive_lap_into_exact_retained_fixed_service_boundary'
  elif 'AxialFloorUnderlap'in name or 'LandingCross0_Web'in name or 'LandingCross0_Upper'in name:
   if '/CompiledStructuralFloors_NotFinishedRooms/D10_fore_route/'in path:kind='below_walk_positive_lap_into_exact_retained_axial_floor'
  elif 'RetainedFloorUnderlap'in name:
   expected='/CompiledStructuralFloors_NotFinishedRooms/D10_shared_table_reserved_cap/'if unit=='01'else'/RemainingBatchStructuralFloors/D10_directory_'+unit+'_batch_floor_0/'
   if expected in path:kind='new_plate_embedded_in_exact_preserved_dining_floor_solid'
  record={'part':name,'old_body':path,'classification':kind,'native_bounds':bounds[name]}
  (known if kind else bad).append(record)
for row in d['embedded_floor_bearing_witnesses']:
 unit=row['part'][5:7];expected='/CompiledStructuralFloors_NotFinishedRooms/D10_shared_table_reserved_cap/'if unit=='01'else'/RemainingBatchStructuralFloors/D10_directory_'+unit+'_batch_floor_0/'
 assert row['floor_contact']and row['embedded']and row['ceiling_clear']and expected in row['old_floor_owner'],row
assert len(d['embedded_floor_bearing_witnesses'])==18
report={'status':'PASS_EXACT_SOURCE_CONTACT_CLASSIFICATION'if not bad else'HOLD_UNEXPLAINED_SOURCE_CONTACTS','queried_contact_pairs':len(known),'classified_pairs':known,'embedded_floor_bearing_witnesses':d['embedded_floor_bearing_witnesses'],'unexplained_contacts':bad,'all_old_floor_preimages_empty':not d['unexplained_old_floor_preimages'],'new_floor_area_m2':r['new_floor_area_m2'],'old_pool_ceiling_geometry_changed':False,'primary_capacity_or_food_water_operation_or_final_art_accepted':False};(D/'SERVICE_CONTACT_CLASSIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACTS',len(known),'embedded',18,'unexplained',len(bad));assert not bad
