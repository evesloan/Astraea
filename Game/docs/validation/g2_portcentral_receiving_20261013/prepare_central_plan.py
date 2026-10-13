from pathlib import Path
import json,hashlib
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');parts=[]
for x in [-85.7,-82.3]:
 for z in [-23.5,-20.,-16.5]:parts.append({'name':f'lower_stub_column_{x}_{z}','bounds':[x-.09,x+.09,97.48,101.84,z-.09,z+.09],'kind':'column','allowed':['SA_D16_MissingOnlyFloor']})
for z in [-12.,-10.,-8.,-6.,-4.5]:
 parts.append({'name':f'east_arrival_column_{z}','bounds':[-64.09,-63.91,97.48,101.84,z-.09,z+.09],'kind':'column','allowed':['SA_D16_MissingOnlyFloor','SA_D17_MissingOnlyFloor']})
 parts.append({'name':f'east_arrival_slab_transfer_{z}','bounds':[-64.12,-60.95,101.78,101.84,z-.12,z+.12],'kind':'slab_transfer','allowed':['SA_D17_MissingOnlyFloor','SA_D16_EastWall_0'],'wall_attachment':'Only the shallow slab-level joint; original wall mesh/contact remains exact, no opening/cut.'})
plan={'base':'9fe069e0b8af42869dbf49b4b97d69d95b2ab63d','parts':parts,'source_floor':[[-89,-79],[-24,-16]],'proposed_route_rectangles':[[-81,-62.7,-16,-14.2],[-62.7,-60.9,-16,-3.2]],'route':'Existing east atrium arrival at(-61.8,-3.1) around intact east/north primary walls to source adjunct; only safety guard at arrival threshold may receive bounded successor.','structural_capacity_or_admission_accepted':False,'source_models_unchanged':True}
guest=json.loads((G/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];hits=[]
for r in guest:
 if r['deck']not in[16,17]:continue
 for a in plan['proposed_route_rectangles']+[[-89,-79,-24,-16]]:
  if min(a[1],r['x'][1])>max(a[0],r['x'][0]) and min(a[3],r['z'][1])>max(a[2],r['z'][0]):hits.append(r)
assert not hits
plan['guest_allocation_intersections']=hits
(P/'CENTRAL_LOWER_SUPPORT_AND_ROUTE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('PASS_ZERO_GUEST_ALLOCATION_INTERSECTIONS_CENTRAL_PLAN_REQUIRES_ACTUAL_SWEEP')
