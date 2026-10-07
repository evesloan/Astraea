from pathlib import Path
import json,hashlib,math,collections
S=Path(__file__).resolve().parents[1];B=S.parent
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=read(S/'RESIDENTIAL_500_CURRENT_APPLICATION.json');configs={r['source_recipe_key']:r for r in read(S/'PROTOTYPE_PLAN.json')['rooms']}
base={r['census_source_index']:r for r in read(B/'runtime_staging/data/RESIDENTIAL_BATCH_RUNTIME.json')['units']}
pilot={r['census_source_index']:r for r in read(B/'connected_pilot_review_r011/data/architecture/RESIDENTIAL_CONNECTED_PILOT_205.json')['rooms']}
instances=[];sections=collections.defaultdict(list);prototypes={};bind_count=0
for key,cfg in configs.items():
 folder=S/'outputs/production_r011'/key;r=read(folder/'SOURCE_RECEIPT.json')
 prototypes[key]={'source_blend':str((folder/'assembly.blend').relative_to(S)),'source_blend_sha256':sha(folder/'assembly.blend'),'shell_glb':str((folder/'shell.glb').relative_to(S)),'shell_glb_sha256':sha(folder/'shell.glb'),'source_receipt_sha256':sha(folder/'SOURCE_RECEIPT.json'),'layout':cfg['layout'],'class':cfg['historical_class'],'component_placements':r['placements'],'bed_anchors':r['historical_bed_anchors'],'local_frame':'Blender X=right,Y=inward,Z=up; exported Godot X=right,Y=up,Z=outward','native_profile':'sealed r010 aperture and exterior privacy v001; source recipe geometry does not construct per-unit outlook'}
for row in plan['rooms']:
 if row['preserve_installed']:continue
 i=row['census_source_index'];key=row['source_recipe_key'];proto=prototypes[key];bindings=[]
 for anchor in row['bed_anchors']:
  idx=anchor['historical_anchor_index'];original=next(x for x in base[i]['anchor_bindings']if x['unit_anchor_index']==idx)
  matches=[x for x in proto['bed_anchors']if all(abs(a-b)<1e-5 for a,b in zip(x['source_xyz'],anchor['source_xyz']))];assert len(matches)==1,(i,anchor,matches)
  pi=matches[0]['historical_anchor_index'];p=next(x for x in proto['component_placements']if x['label']=='HistoricalBedAnchor_'+str(pi));assert p['source_xyz']==anchor['source_xyz']
  binding={**original,'prototype_anchor_index':pi,'prototype_marker_name':'DATUM_bed_'+str(pi),'prototype_component_label':'HistoricalBedAnchor_'+str(pi),'source_xyz':anchor['source_xyz'],'world_xyz':anchor['world_xyz'],'coordinate_evidence':anchor['evidence']}
  if i==205:
   expected=next(x for x in pilot[i]['anchor_bindings']if x['unit_anchor_index']==idx);assert binding['unit_slot_key']==expected['unit_slot_key'];assert binding['world_xyz']==expected['world_xyz']
  else:
   for f in ['unit_slot_key','unit_anchor_index','source_xyz','world_xyz','slot_identity_status']:assert binding[f]==original[f],(i,f)
  u,v,w=anchor['source_xyz'];x,y,z=row['source_origin_world_xyz'];a=row['source_yaw_godot'];world=[x+math.cos(a)*u-math.sin(a)*v,y+w,z-math.sin(a)*u-math.cos(a)*v];assert max(abs(a-b)for a,b in zip(world,anchor['world_xyz']))<1e-5
  bindings.append(binding);bind_count+=1
 section=row['deck']+'__'+row['house'];sections[section].append(i)
 instances.append({**row,'anchor_bindings':bindings,'component_placements':proto['component_placements'],'section_id':section,'source_shell':proto['shell_glb'],'source_shell_sha256':proto['shell_glb_sha256'],'source_recipe_sha256':proto['source_receipt_sha256'],'runtime_enabled':False,'source_props_variant':configs[key]['occupant_props_variant'],'requested_props_variant':row['occupant_props_variant'],'props_variation_status':'Shared source recipe realizes these books; extra per-unit seeds remain proposals','original_court_pilot_binding':{'runtime_source_revision':'r010','preserve_reviewed_shell_until_explicit_successor':True}if i in pilot else None})
assert len(instances)==498 and len(sections)==18 and bind_count==1296
slotids=[x['unit_slot_key']for r in instances for x in r['anchor_bindings']];assert len(set(slotids))==1296
out=S/'assemblies';out.mkdir(exist_ok=False)
for section,indices in sections.items():
 rows=[r for r in instances if r['census_source_index']in indices]
 d={'section_id':section,'source_count':len(rows),'source_indices':indices,'streaming_default_enabled':False,'view_ready':False,'outlook_targets':sorted(set(r['view_target_id']for r in rows)),'instances':rows,'existing_floor_void_geometry_changed':False,'new_support_required_before_runtime':'Use exact per-section existing-owner survey and reviewed additive receiving design; do not reuse pilot frame blindly.'}
 (out/(section+'.json')).write_text(json.dumps(d,indent=2)+'\n')
summary={'regular_units':500,'new_instances':498,'protected_installed':2,'source_recipes':18,'section_count':18,'rest_slots_total':1300,'new_rest_bindings':bind_count,'adjacency_edges':len(plan['adjacency_edges']),'unit_count_delta':0,'source_geometry_status':'18 actual saved Blender recipes + exact GLB; per-unit outlook/receiving construction still required','game_or_catalogue_writes':False,'runtime_adoption':False,'section_sizes':{k:len(v)for k,v in sections.items()}}
(out/'GODOT_BATCH_INSTANCE_MAP.json').write_text(json.dumps({'schema':'astraea.corrected_residential_source_batch.v2','summary':summary,'prototypes':prototypes,'instances':instances,'preserved_installed':[r for r in plan['rooms']if r['preserve_installed']]},indent=2)+'\n')
(S/'qa/EXPLICIT_1296_ANCHOR_BINDINGS.json').write_text(json.dumps({'status':'PASS_IDENTITY_ORDINAL_COORDINATE_CROSSWALK','summary':summary,'unique_slot_ids':len(set(slotids)),'changed_proposed_coordinates':'source205 only, already reviewed; slot IDs exact','prototype_receipts_and_actual_component_placements_checked':True},indent=2)+'\n')
print(json.dumps(summary,indent=2))
