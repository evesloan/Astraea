from pathlib import Path
import json
D=Path(__file__).resolve().parent;p=json.loads((D/'FITTED_CURRENT_CONTACTS_r010.json').read_text());accepted=[];bad=[]
for site in p['sites']:
 kit=site['kit']
 for row in site['contacts']:
  part=row['part'];expected=set();reason=''
  if kit=='TIDAL':
   if 'ColumnBase_'in part:expected={'TG_Batch_81'};reason='20mm base bearing into retained D17 floor'
   elif '_Weather_'in part:expected={'TG_Batch_283'};reason='Bounded collar overlap into retained roof edge'
   elif '_UtilityLightMount'in part:expected={'TG_Batch_283'};reason='Original lamp-to-retained utility cover positive support'
  else:
   if '_ColumnBase_'in part or part.endswith('_Foot'):expected={'QG_Batch_134'};reason='20mm base bearing into retained D17 floor'
   elif '_Weather_'in part:expected={'QG_Batch_462'};reason='Bounded collar overlap into retained roof edge'
   elif '_RampLeg1'in part or '_Ramp1Stringer'in part:expected={'QG_Batch_134'};reason='Low ramp underside retained slab bearing;no new transfer/guard contact'
   elif '_CanopySuspension'in part:expected={'QG_Batch_171'};reason='20mm suspension foot penetration into raised timber panel'
   elif 'OverheadPlantCasing'in part:expected={'QG_Batch_171'};reason='20mm casing bearing into raised timber panel';assert 107.57<row['min'][1]<107.59 and row['max'][1]<108.04
   elif 'WetLight-6_Mount'in part:expected={'QG_Batch_172'};reason='Retained source mount plus positive new adapter into raised acoustic panel'
  for path in row['contacts']:
   node=path.rsplit('/',2)[-2]
   r={'kit':kit,'part':part,'target':path,'meaning':reason}
   if node in expected and not row['saturated']:accepted.append(r)
   else:bad.append(r)
assert p['new_contacts_in_original_eight_metre_main_lanes']==[];assert all(x['unmatched_outside_triangles']==0 for x in p['roof_outside_preservation']);feet=[x for s in p['sites']for x in s['column_floor_preimages']];assert len(feet)==32 and all(x['floor_y']is not None and abs(x['floor_y']-102)<.002 for x in feet)
r={'status':'PASS_EXACT_CONTAINED_BEARINGS_AND_SEALS'if not bad else'FAIL_UNEXPLAINED_CONTACTS','classified_contacts':accepted,'unexplained_contacts':bad,'retained_floor_pins':len(feet),'eight_metre_main_lane_new_contacts':0,'original_roof_triangles_exact':sum(x['untouched_original_triangles_exact']for x in p['roof_outside_preservation']),'structural_water_pressure_operating_acceptance':False};(D/'CONTACT_CLASSIFICATION_r010.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(accepted),'unexplained',len(bad));assert not bad,bad
