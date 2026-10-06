#!/usr/bin/env python3
"""Read-only host-source screen; writes only the owned medical package."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'data/architecture/packages/medical'
def read(p): return json.loads((ROOT/p).read_text())
def rectpoly(r):
 x0,x1,z0,z1=r;return [[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
def area(p): return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2 if p else 0
# Sutherland-Hodgman polygon clipping against a rectangle, no external packages.
def clip(p,r):
 for axis,edge,sign in [(0,r[0],1),(0,r[1],-1),(1,r[2],1),(1,r[3],-1)]:
  q=[]
  for a,b in zip(p,p[1:]+p[:1]):
   ia=(a[axis]-edge)*sign>=-1e-9;ib=(b[axis]-edge)*sign>=-1e-9
   if ia:q.append(a)
   if ia!=ib:
    t=(edge-a[axis])/(b[axis]-a[axis]);q.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
  p=q
  if not p:break
 return p
ledger=read('data/programme_ledger.json'); spatial=read('data/spatial_layout.json');layout=read('data/whole_ship_layout.json');hull=read('data/hull_envelope.json')['plan_xz_m']
programmes=sorted([p for p in ledger['destinations'] if p['historical_deck']=='D05'],key=lambda p:p['programme_key'])
# All coordinates local u from public edge toward service edge, v from longitudinal low edge.
def world(p,r):
 x=p['historical_envelope']['x'];z=p['historical_envelope']['z'];u0,u1,v0,v1=r
 return [x[0]+u0,x[0]+u1,z[0]+v0,z[0]+v1] if x[0]>0 else [x[1]-u1,x[1]-u0,z[0]+v0,z[0]+v1]
children={1:[('triage_pod',8,7,6,6,4,4),('quarantine_room',12,7,6,6,24,4),('local_waiting_and_escort',1,14,8,6,16,1),('local_diagnostic_support',1,14,8,20,16,1),('arrival_privacy_and_escort',1,28,8,6,48,1),('clinical_staff_control',1,14,8,6,56,1),('telemedicine',1,14,8,20,56,1)],2:[('general_bed_position',20,14,4,6,4,2),('surgical_suite',4,14,8,6,44,2),('wash_transfer_and_treatment',1,28,4,6,60,1)],3:[('medical_laboratory',6,14,16,6,4,2),('specimen_handoff',1,14,12,6,52,1),('research_control',1,14,12,20,52,1)],4:[('pharmacy_xenomed_store',2,28,20,6,4,1),('controlled_issue',1,14,16,6,44,1),('receiving',1,14,16,20,44,1)],5:[('recovery_garden_lounge',1,28,32,6,4,1),('private_recovery',2,14,20,6,36,2),('accompaniment',1,28,8,6,56,1)],6:[('atmosphere_research',1,28,24,6,4,1),('local_environment_control',1,14,16,6,28,1),('sample_support',1,14,16,20,28,1),('habitat_interface_review',1,28,20,6,44,1)],7:[('consultation_pod',4,14,12,6,4,2),('remote_specialist',1,14,12,6,28,1),('escort_wait',1,14,12,20,28,1),('staff_documentation',1,28,24,6,40,1)],8:[('quiet_care_compartment',4,14,20,6,4,2),('privacy_molt_support',1,14,20,6,44,1),('crew_transfer',1,14,20,20,44,1)],9:[('hydration_support',1,28,24,6,4,1),('species_contact_review',1,14,16,6,28,1),('local_water_monitor',1,14,16,20,28,1),('wash_supply',1,28,20,6,44,1)],10:[('family_waiting_lounge',1,28,32,6,4,1),('quiet_accompaniment',1,14,20,6,36,1),('accessible_sanitary_support',1,14,20,20,36,1),('staff_assistance',1,28,8,6,56,1)]}
plan=[];checks=[]
for p in programmes:
 n=int(p['programme_key'][-2:]);env=p['historical_envelope'];r=[*env['x'],*env['z']];items=[]
 for name,count,w,l,u,v,cols in children[n]:
  for i in range(count):items.append({'id':f'{p["programme_key"]}_{name}_{i+1:02}','role':name,'rect_x0_x1_z0_z1':world(p,[u+(i%cols)*w,u+(i%cols+1)*w,v+(i//cols)*l,v+(i//cols+1)*l]),'dimensions_m':[w,l],'quantity_status':'printed reference fit target, not adopted capacity' if name in ['triage_pod','quarantine_room','general_bed_position','surgical_suite','medical_laboratory','pharmacy_xenomed_store'] else 'proposed spatial subdivision, not canonical count'})
 for role,u0,u1 in [('admission_clinical_route',0,6),('clean_staff_route',34,38),('support_and_maintenance',38,42),('soiled_return_route',42,46)]:items.append({'id':p['programme_key']+'_'+role,'role':role,'rect_x0_x1_z0_z1':world(p,[u0,u1,0,68]),'dimensions_m':[u1-u0,68],'quantity_status':'proposed'})
 a=3128.;overlaps=[]
 for f in spatial['regions']:
  if f['deck']=='D05':
   ov=area(clip(f['boundary'],r))-sum(area(clip(h,r)) for h in f.get('holes',[]))
   if ov>1e-6:overlaps.append({'id':f['id'],'raw_overlap_m2':round(ov,3)})
 conflicts=[]
 for v in spatial['voids']:
  if 'D05' in v['decks'] and area(clip(v['boundary'],r))>1e-6:conflicts.append(v['id'])
 checks.append({'programme_key':p['programme_key'],'area_m2':a,'child_overlap_pairs':[(a['id'],b['id']) for i,a in enumerate(items) for b in items[i+1:] if min(a['rect_x0_x1_z0_z1'][1],b['rect_x0_x1_z0_z1'][1])>max(a['rect_x0_x1_z0_z1'][0],b['rect_x0_x1_z0_z1'][0])+1e-8 and min(a['rect_x0_x1_z0_z1'][3],b['rect_x0_x1_z0_z1'][3])>max(a['rect_x0_x1_z0_z1'][2],b['rect_x0_x1_z0_z1'][2])+1e-8], 'inside_plan_hull':abs(area(clip(hull,r))-a)<1e-5,'current_compiler_floor_overlaps':overlaps,'protected_void_conflicts':conflicts,'all_children_inside':all(t['rect_x0_x1_z0_z1'][0]>=r[0] and t['rect_x0_x1_z0_z1'][1]<=r[1] and t['rect_x0_x1_z0_z1'][2]>=r[2] and t['rect_x0_x1_z0_z1'][3]<=r[3] for t in items)})
 plan.append({'programme_key':p['programme_key'],'name':p['name'],'envelope':env,'floor_y_m':21,'next_floor_y_m':27,'proposed_clear_ceiling_y_m':25.2,'proposed_service_zone_y_m':[25.2,26.76],'slab_reservation_y_m':[26.76,27],'floor_ownership':'compiler proposal; no asset duplicate slab','children':items})
sources=['data/programme_ledger.json','data/spatial_layout.json','data/whole_ship_layout.json','data/hull_envelope.json','docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx','docs/master_source/MASTER_CURRENT_APPLICATION.json','docs/whole_ship_plans/D05.png']
manifest={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}
ref=Path('/workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png');manifest[str(ref)]=hashlib.sha256(ref.read_bytes()).hexdigest()
package={'schema':'astraea_medical_section_planning_v1','status':'proposed source/spec package; no geometry or runtime acceptance','source_sha256':manifest,'programmes':plan,'capacity_policy':'20/4/12/8/6/2 are directly printed evidence retained as spatial fit targets pending master/owner reconciliation, never inferred from icons; no new residential berths','routes':[]}
for sign in [-1,1]:
 for role,x in [('clean_supply_and_staff',57),('soiled_return',61)]:
  pts=[[sign*x,-480],[sign*x,-70],[sign*(102 if x==57 else 108),-70],[sign*(102 if x==57 else 108),70],[sign*x,70],[sign*x,480]]
  package['routes'].append({'id':f'{role}_{"port" if sign<0 else "starboard"}','centerline_xz':pts,'width_m':3.6,'status':'new proposal, not existing navigable floor','vertical_interface':'reserved same-side staff risers at Z-490/-283/-90/+290/+490 port and -490/-323/-86/+323/+490 starboard; author screened lateral spurs independently','central_note':'outboard diversion avoids recovery/atmosphere envelopes; no central atrium crossing'})

route_checks=[]
for route in package['routes']:
 rectangles=[]
 for a,b in zip(route['centerline_xz'],route['centerline_xz'][1:]):
  w=route['width_m']/2
  rr=[min(a[0],b[0])-w,max(a[0],b[0])+w,min(a[1],b[1])-w,max(a[1],b[1])+w]
  rectangles.append(rr)
 route_checks.append({'id':route['id'],'inside_plan_hull':all(abs(area(clip(hull,r))-area(rectpoly(r)))<1e-5 for r in rectangles),'programme_intrusions':sorted(set(p['programme_key'] for p in plan for r in rectangles if area(clip(rectpoly([*p['envelope']['x'],*p['envelope']['z']]),r))>1e-6)),'protected_void_intrusions':sorted(set(v['id'] for v in spatial['voids'] if 'D05' in v['decks'] for r in rectangles if area(clip(v['boundary'],r))>1e-6)),'physical_route_acceptance':False})
(OUT/'D05_MEDICAL_SECTION_PLAN.json').write_text(json.dumps(package,indent=2)+'\n')
report={'scope':'exact plan-hull/envelope and polygon-floor screen only; no 3D hull or collision certification','checks':checks,'route_checks':route_checks,'programme_count':len(plan),'capacity_evidence':'printed table inspected at native 1491x1055 pixels','next_gate':'review capacities, floor ownership, doors and full service-route integration before shared adoption'}
(OUT/'D05_MEDICAL_PLANNING_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'programmes':len(plan),'children':sum(len(p['children']) for p in plan),'checks':checks},indent=2))
