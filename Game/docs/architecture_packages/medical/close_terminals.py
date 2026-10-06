from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];out=ROOT/'data/architecture/packages/medical'
p=json.loads((out/'D05_MEDICAL_SECTION_PLAN.json').read_text()); term=[]
# Rectangles are complete reserved clear/movement volumes, not certified human/species dimensions.
for room in p['programmes']:
 x=room['envelope']['x'];z=room['envelope']['z'];sgn=1 if x[0]>0 else -1;center=sum(z)/2;central=room['programme_key'][-2:] in ['05','06'];rear=max(abs(v) for v in x);cleanx=102 if central else 57;dirtyx=108 if central else 61
 def xr(a,b):return sorted([sgn*a,sgn*b])
 def rr(a,b,c,d):return [*xr(a,b),c,d]
 # Clinically segregated thresholds at opposite end zones. Dirty transverse spur crosses longitudinal clean network explicitly.
 doors=[]
 for role,dz in [('clean',-30),('soiled',30)]:
  zz=center+dz;door={'role':role,'origin_xz':[sgn*rear,zz],'clear_aperture_m':[3.6,2.4],'sliding_leaf_motion_reserved_rect':rr(rear-.4,rear+.4,zz-3.7,zz+3.7),'leaf_type':'opposed 1.8m leaves; two 1.9m pockets outside clear aperture','internal_turn_rect':rr(rear-4,rear-.4,zz-1.8,zz+1.8),'external_turn_rect':rr(rear,rear+3.6,zz-1.8,zz+1.8),'leaf_swing_into_route':False};doors.append(door)
 node={'outer_rect':rr(cleanx-4,cleanx+4,center+26,center+34),'crossing_clear_rect':rr(cleanx-1.8,cleanx+1.8,center+28.2,center+31.8),'soiled_spur_rect':rr(rear,dirtyx+1.8,center+28.2,center+31.8),'longitudinal_clean_through_center_x':sgn*cleanx,'gated_portals':[{'center_xz':[sgn*cleanx,center+26],'orientation':'across clean longitudinal route'},{'center_xz':[sgn*cleanx,center+34],'orientation':'across clean longitudinal route'},{'center_xz':[sgn*(cleanx-4),center+30],'orientation':'across soiled transverse spur'},{'center_xz':[sgn*(cleanx+4),center+30],'orientation':'across soiled transverse spur'}],'clear_aperture_m':[3.6,2.4],'pocket_length_each_side_m':1.9,'operational_dependence':'mutually exclusive clean-through or sealed-soiled crossing; doors/interlock/signals not implemented; no simultaneous segregated flow or sterile-separation claim','parent_corridor_adoption':'replace local corridor segment with controlled junction, compiler union floors only; never duplicate slabs'}
 term.append({'programme_key':room['programme_key'],'rear_doors':doors,'controlled_crossing':node,'door_and_turn_envelope_status':'plan-reserved gross footprints; loaded-cart/species operation pending','clean_spur_rect':rr(rear,cleanx+1.8,center-31.8,center-28.2)})
p['terminal_interfaces']=term;p['capacity_policy']='Direct printed quantities 20 beds /4 surgical suites /12 quarantine rooms /8 triage pods /6 laboratories /2 pharmacy stores are accepted as source-required architecture fit targets: master Tables2/3 confirm D05 care/research and prohibit treatment gameplay; no current override changes these clinical counts. They remain unbuilt targets, not occupancy/admitted-capacity or residential totals.'
(out/'D05_MEDICAL_SECTION_PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
# Exact finite rectangle screens against parent allocations and hull polygon.
ns={'__file__':str(ROOT/'docs/architecture_packages/medical/build_plan.py')};exec((ROOT/'docs/architecture_packages/medical/build_plan.py').read_text().split('ledger=')[0],ns)
clip,area,rectpoly=ns['clip'],ns['area'],ns['rectpoly'];hull=json.loads((ROOT/'data/hull_envelope.json').read_text())['plan_xz_m'];checks=[]
for t in term:
 room=next(r for r in p['programmes'] if r['programme_key']==t['programme_key']);env=[*room['envelope']['x'],*room['envelope']['z']];intrusions=[]
 for d in t['rear_doors']:
  for k in ['internal_turn_rect','external_turn_rect','sliding_leaf_motion_reserved_rect']:
   r=d[k];assert abs(area(clip(hull,r))-area(rectpoly(r)))<1e-7
  assert abs(area(clip(rectpoly(env),d['internal_turn_rect']))-area(rectpoly(d['internal_turn_rect'])))<1e-7
 for other in p['programmes']:
  e=[*other['envelope']['x'],*other['envelope']['z']]
  ov=area(clip(rectpoly(e),t['controlled_crossing']['outer_rect']))
  if ov>1e-6:intrusions.append({'programme_key':other['programme_key'],'overlap_m2':ov})
 assert abs(area(clip(hull,t['controlled_crossing']['outer_rect']))-area(rectpoly(t['controlled_crossing']['outer_rect'])))<1e-7
 assert all(v['programme_key']==t['programme_key'] for v in intrusions)
 checks.append({'crossing_node_inside_hull_plan':True,'no_other_parent_intrusion':True,'programme_key':t['programme_key'],'rear_turns_inside_own_parent':True,'all_door_motion_and_turn_footprints_inside_hull_plan':True,'crossing_node_programme_intrusions':intrusions,'clean_spur_and_soiled_spur_separated_longitudinally_m':56.4,'operational_separation_required':True})
(out/'D05_TERMINAL_CHECKS.json').write_text(json.dumps({'checks':checks,'sterile_flow_certification':False,'scope':'exact plan reservation tests; runtime mechanisms and species fit not tested'},indent=2)+'\n')
print('Closed',len(term),'terminal plans; controlled crossings remain operationally dependent')
