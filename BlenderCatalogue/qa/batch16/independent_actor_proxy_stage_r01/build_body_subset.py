"""Optional body-only unchanged-shape subset of the already-generated frozen detailed proposals.
Stage 1 is the existing complete original family rebuild; this is explicitly Stage 2.
python build_body_subset.py [--base-collision PATH] [--output PATH]
"""
from pathlib import Path
import argparse,json,hashlib
HERE=Path(__file__).resolve().parent
EXPECTED_BASE_SHA256='fb81adfa4436e2d9378ee3b6e39bc4d8eaf6a7820b3c38f43174dd163baca740'
RETAIN={
'AST-CUL-003':{
 'left_continuous_floor_runner','right_continuous_floor_runner','left_shaped_timber_end','right_shaped_timber_end','left_rounded_arm_cap','right_rounded_arm_cap','left_navy_fibre_end_return','right_navy_fibre_end_return','lower_rear_cross_tie','swept_crown_back_shell','contoured_amber_back_pad','folding_timber_pan','shaped_amber_seat_pad'},
'AST-CUL-004':{
 'left_front_rubber_sole','left_rear_rubber_sole','right_front_rubber_sole','right_rear_rubber_sole','clipped_ballast_base','service_column_front_web','service_column_left_wall','service_column_right_wall','removable_rear_service_cover','rear_cover_pull_bridge','rear_pull_left_return','rear_pull_right_return','supported_clipped_work_tray','left_tray_gusset','right_tray_gusset','front_paper_retaining_lip','clipped_cue_notes_backer','inactive_rehearsal_notes_face','light_yoke_crossbar','left_light_yoke_upright','right_light_yoke_upright','formed_light_hood','light_rear_spine','left_forward_light_end_shield','left_rear_light_end_shield','right_forward_light_end_shield','right_rear_light_end_shield','downturned_glare_shield','recessed_opal_diffuser','inactive_local_control_pad'}
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def omission_reason(part):
 if part=='protected_internal_cable_proposal' or part.startswith('cable_retention_'):
  return 'Internal cable/service-retention detail inside retained column walls and the closed cover. It remains visible and noncolliding in this optional body subset when the cover is removed. Not a primary floor/rest/work/grip/control surface; use unchanged detailed geometry for any service/tool contact or interaction targeting. No body-size exclusion is assumed.'
 assert any(token in part for token in ('bearing_sector','fixed_pivot_stub','retained_hinge_pin','inner_pin_retainer','fixed_aim_stub','retained_aim_pin','aim_pin_inner_retainer')),part
 return 'Fine retained-pivot mechanism detail, intentionally outside this optional body-contact selection. The unchanged exact detailed proposal remains authoritative for radial/axial bearing, mechanism, service and precise interaction checks. No load-support or operating constraint is supplied by this subset.'
def build(base):
 assert sha(base)==EXPECTED_BASE_SHA256,'This optional subset is bound to the accepted r07 detailed proposal; review any changed base before regeneration.'
 data=json.loads(base.read_text());assets={}
 for ident,kept_parts in RETAIN.items():
  entry=data[ident];seen=set();kept=[];omitted=[]
  for shape in entry['shapes']:
   assert len(shape['covered_parts'])==1,'Expected exact one-semantic-solid detailed profiles'
   part=shape['covered_parts'][0];seen.add(part)
   if part in kept_parts:kept.append(shape)
   else:omitted.append({'base_shape_id':shape['name'],'covered_parts':shape['covered_parts'],'parent_root':shape['parent_root'],'movement_group':shape['movement_group'],'reason':omission_reason(part)})
  assert kept_parts<=seen
  expected=(43,13,30)if ident=='AST-CUL-003'else(56,30,26);assert(len(entry['shapes']),len(kept),len(omitted))==expected
  assets[ident]={'status':'Optional body-contact proposal only; not adopted, not a replacement for the exact detailed mechanism/interaction set','source_frame':entry['source_frame'],'exchange_frame':entry['exchange_frame'],'detailed_shape_count':len(entry['shapes']),'body_shape_count':len(kept),'omitted_shape_count':len(omitted),'retained_shape_ids':[s['name']for s in kept],'omitted_shapes':omitted,'shapes':kept,'preserve_voids':entry['preserve_voids'],'base_motion_records':entry['motion_records'],'retained_moving_shape_ids':{m['root']:[s['name']for s in kept if s['parent_root']==m['root']]for m in entry['motion_records']},'transforms_policy':'Every retained shape dictionary is byte-value identical to the detailed proposal, including source/native point arrays and original movement ownership. Bind the existing real roots; never flatten a moving part or regenerate an enclosing hull.','no_new_intrusion':'For every identical root pose, this union is a subset of the detailed union. Removing shapes cannot add intrusion or close any existing hole/use/approach void. This does not validate the host, anatomy, engine or detailed mechanisms.'}
 return {'schema':'astraea_optional_body_collision_subset_v1','revision':'r07-body-subset-01','base_dependency':{'logical_path':'assets/auditorium_use/collision_proposals.json','sha256':sha(base),'provenance':'Generated output of the accepted original source-only family rebuild; deliberately a second-stage input, not an original clean source input'},'generator':{'logical_path':'assets/auditorium_use/actor_proxies/build_body_subset.py','sha256':sha(Path(__file__))},'selection_policy':'Pure unchanged-shape subset. No new or inflated hull, proxy mesh, source/export/manifest change, runtime installation or engine adoption.','interaction_policy':'Use the unchanged marker API, physical visual parts and detailed collision set for precise interaction/control/service targeting. Body selection never deletes or retargets markers.','assets':assets}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base-collision',type=Path,default=HERE.parent/'collision_proposals.json');p.add_argument('--output',type=Path,default=HERE/'body_collision_subset.json');args=p.parse_args();out=build(args.base_collision);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print([(k,v['body_shape_count'],v['omitted_shape_count'])for k,v in out['assets'].items()])
