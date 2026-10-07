from pathlib import Path
import json,copy,hashlib,collections,math,shutil
S=Path(__file__).resolve().parents[1];B=S.parent;D=B/'domestic_correction';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
old=json.loads((B/'RESIDENTIAL_500_PLAN.json').read_text());protos=json.loads((B/'PROTOTYPE_PLAN.json').read_text());views=json.loads((B.parent/'residential-reference-review-20261006/RESIDENTIAL_VIEW_CLASSIFICATION.json').read_text());viewmap={r['source_envelope_index']:r for r in views['rows']};pilot={r['census_source_index']:r for r in json.loads((B/'COURT_PILOT_PLAN.json').read_text())['rooms']}
requirements=json.loads((D/'privacy_successor/FULL_FAMILY_PRODUCTION_MATRIX_CURRENT.json').read_text());rooms=copy.deepcopy(old['rooms']);recipes=[];aliases={}
for p in protos['rooms']:
 q=copy.deepcopy(p);legacy=q['prototype_key'];name='DOMESTIC_V2__'+legacy.replace('__opaque__','__planned_window_from_opaque__').replace('__atrium__','__atrium_window__');q['address']=name;q['historical_prototype_key']=legacy;q['source_recipe_key']=name;q['view_policy']='planned_authored_outlook';q['window_geometry_profile']='sealed_window_r010';q['privacy_profile']='residential_privacy_v001';q['emphasize_ceiling_joinery']=True;q['family_sleep_bay_privacy']=q['historical_class']=='family';q['outlook_construction_status']='Per-instance purposeful target in500-row application ledger; no generic exterior aperture or runtime acceptance';q['instance_adoption_ready']=False;recipes.append(q);aliases[legacy]=name
q=copy.deepcopy(pilot[205]);q['address']='DOMESTIC_V2__standard__D_garden_salon__reviewed_court_205';q['source_recipe_key']=q['address'];q['historical_prototype_key']=None;q['prototype_instance_count']=1;q['instance_adoption_ready']=False;q['emphasize_ceiling_joinery']=False;q['family_sleep_bay_privacy']=False;recipes.append(q)
for r in rooms:
 original=copy.deepcopy(r);v=viewmap[r['census_source_index']];r['prior_r005_prototype_key']=r['prototype_key'];r['source_recipe_key']=aliases.get(r['prototype_key']);r['view_target_family']=v['recommended_target_family'];r['view_source_classification']=v['primary_outlook_classification'];r['view_source_action']=v['action'];r['view_required_before_adoption']=True;r['privacy_profile']='residential_privacy_v001';r['window_geometry_profile']='sealed_window_r010';r['kitchen_provision']='compact standard kitchenette; no full luxury kitchen';r['bathroom_provision']='fully enclosed toilet/wash/shower with retained operable privacy door';r['instance_adoption_ready']=False;r['view_target_id']='VIEW-PROPOSAL-'+r['deck']+'-'+r['house']+'-'+v['orientation']
 normal=-v['rear_world_normal_x'];r['aperture_contract']={'plane_origin_world':[round(v['rear_world_x']+normal*.12,5),r['floor_y']+2.04,r['source_origin_world_xyz'][2]],'inside_normal_world':[normal,0,0],'local_glass_vertical_m':[.475,3.605],'frame_overlap_m':{'sill':.005,'header':.005,'central_mullion':.01,'outer_jamb':.015},'one_material_per_coplanar_aperture_group':True}
 if r['census_source_index']in pilot:
  p=pilot[r['census_source_index']];assert r['rebuild_identity']==p['rebuild_identity']
  r['view_target_id']=p['view_target_id'];r['outlook_construction_status']='Actual authored three-bay court/source receiving frame; connected native adoption still pending'
  if r['census_source_index']==205:
   r['superseded_proposed_bed_anchors']=copy.deepcopy(r['bed_anchors']);r['bed_anchors']=copy.deepcopy(p['bed_anchors']);r['layout']=p['layout'];r['view_lounge_replan']=True;r['source_recipe_key']=q['source_recipe_key']
 else:r['outlook_construction_status']='Target geometry/interface construction required before runtime use'
 if r['preserve_installed']:
  r['source_recipe_key']=None;r['retrofit_status']='Preserve both installed identities/anchors/geometry. New domestic/privacy obligations require a separately reviewed retrofit; never duplicate these units.'
 for k in ['rebuild_identity','allocation_sha256','allocation_x','allocation_z','source_origin_world_xyz','source_yaw_godot','entry_persistent_id','bath_persistent_id','historical_class']:
  assert original[k]==r[k]
 if r['census_source_index']!=205:assert original['bed_anchors']==r['bed_anchors']
byaddress={r['address']:r for r in rooms};assert all(byaddress[a]['layout']!=byaddress[b]['layout']for a,b in old['adjacency_edges']);assert len(rooms)==500 and sum(len(r['bed_anchors'])for r in rooms)==1300
counts=collections.Counter(r['source_recipe_key']for r in rooms if not r['preserve_installed'])
for q in recipes:q['prototype_instance_count']=counts[q['source_recipe_key']]
assert sum(counts.values())==498 and len(recipes)==18
plan=copy.deepcopy(old);plan.update(status='Corrected isolated source production application; no Game adoption. Old r005 retained as superseded candidate.',rooms=rooms,representative_sample_addresses=[p['address']for p in recipes],prototype_count=18,legacy_prototype_aliases=aliases,current_privacy_authority='Sentinel_1367a9f10c748191835bf2083b1308da',views='Every unit has a sealed real window interface with an explicit purposeful court/atrium/garden/loggia class. Outlook targets remain proposals until actual construction/interfaces pass; no generic space view is invented.',current_binding_matrix_sha256=hashlib.sha256((D/'privacy_successor/FULL_FAMILY_PRODUCTION_MATRIX_CURRENT.json').read_bytes()).hexdigest(),new_source_placements=498,preserved_installed=2,unit_count_delta=0)
(S/'RESIDENTIAL_500_CURRENT_APPLICATION.json').write_text(json.dumps(plan,indent=2)+'\n');(S/'PROTOTYPE_PLAN.json').write_text(json.dumps({'status':'18reusable source recipes preserving17legacy recipes plus reviewed garden-salon variant; runtime pending purposeful outlook construction','rooms':recipes,'representative_sample_addresses':[r['address']for r in recipes]},indent=2)+'\n');(S/'FULL_FAMILY_PRODUCTION_MATRIX_CURRENT.json').write_text(json.dumps(requirements,indent=2)+'\n')
for rel in ['inputs/build_residential_suite.py','inputs/build_twin_retreat_suite.py','qa/GENERATOR_INPUTS.json','domestic_correction/bathroom_review/bathroom_enclosure_patch.py']:
 src=CAT/'assets/residential_connected_pilot/successors/r010'/rel;dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
for f in (D/'outputs/kitchenette_r001').iterdir():
 dst=S/'domestic_correction/outputs/kitchenette_r001'/f.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
generator=(CAT/'assets/residential_connected_pilot/successors/r010/source/build_family.py').read_text();generator=generator.replace("['real_atrium_candidate','authored_court_candidate']","['real_atrium_candidate','authored_court_candidate','planned_authored_outlook']");marker="    ns={'__file__':str(ROOT/'inputs'/template),'CAT':CAT}"
insert='''    if cfg.get('emphasize_ceiling_joinery',False):
        # Preserve every authored ceiling curve. Broaden the existing timber
        # transition within the unchanged7.2m envelope for readable hierarchy.
        code=replace_once(code,"ha-.045,ha+.045,hb+.045,'warm_walnut',.16)","ha-.075,ha+.045,hb+.045,'warm_walnut',.20)")
''';assert generator.count(marker)==1;generator=generator.replace(marker,insert+marker)
marker='''    # Stable local bed identity derives from historical marker coordinates.''';insert='''    if cfg.get('family_sleep_bay_privacy',False):
        third=min(cfg['bed_anchors'],key=lambda a:a['source_xyz'][1])['source_xyz'];side=1 if third[0]>0 else -1
        # Screen the third adult rest support without moving historical anchors
        # or narrowing the central1.8m passage. This is a screened bay, not a
        # claimed separate luxury bedroom.
        wall('SUI_FamilyThirdRestPrivacy',(side*.95,6.0),(side*.95,7.50),0,1.55,1.55,'oatmeal_weave',.10)
        wall('SUI_FamilyThirdRestCap',(side*.95,6.0),(side*.95,7.50),1.55,1.60,1.60,'warm_walnut',.12)
        datum('family_third_rest_approach',(side*1.8,4.8,0))
''';assert generator.count(marker)==1;generator=generator.replace(marker,insert+marker);(S/'source/build_family.py').write_text(generator)
report={'status':'PASS_IDENTITY_ALLOCATION_BED_AND_ADJACENCY_APPLICATION_CHECK','units':500,'new':498,'installed_preserved':2,'rest_places':1300,'source_recipes':18,'legacy_recipes_preserved':17,'only_rest_coordinate_successor':'Already reviewed explicit205proposal; exact rest-slot IDs remain in per-instance bindings','adjacency_edges_unchanged':len(old['adjacency_edges']),'view_classes':dict(collections.Counter(r['view_target_family']for r in rooms)),'source_recipe_instances':dict(counts),'game_writes':False,'runtime_adoption_ready':False};(S/'qa/APPLICATION_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
