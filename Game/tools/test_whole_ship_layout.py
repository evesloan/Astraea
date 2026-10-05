"""Whole-ship coverage gates; counts never certify finished geometry."""
import unittest,json
from compile_whole_ship_layout import ROOT,build,rect
from shapely.geometry import box,Polygon
class WholeShipLayout(unittest.TestCase):
 def setUp(self):self.plan=build()
 def test_all_decks_and_programmes_once(self):
  self.assertEqual([d['deck']for d in self.plan['decks']],[f'D{i:02}'for i in range(1,19)])
  keys=[k for d in self.plan['decks']for k in d['programme_keys']]
  self.assertEqual(len(keys),161);self.assertEqual(len(set(keys)),161)
  self.assertEqual(set(keys),{r['programme_key']for r in self.plan['programmes']})
 def test_accommodation_and_shops_preserved(self):
  counts={d['deck']:d['guest_envelope_count']for d in self.plan['decks']if d['guest_envelope_count']}
  self.assertEqual(counts,{'D04':120,'D13':160,'D14':240,'D15':180,'D16':200,'D17':100})
  self.assertEqual(sum(d['retail_envelope_count']for d in self.plan['decks']),100)
  self.assertEqual(self.plan['protected_totals']['luxury_replacements_within_guest_units'],81)
  self.assertEqual(self.plan['protected_totals']['crew_people_including_player'],400)
 def test_courts_affect_five_commons_without_guest_loss(self):
  self.assertEqual(len(self.plan['residential_court_reservations']),4)
  for c in self.plan['residential_court_reservations']:
   self.assertEqual(len(c['affected_programmes']),5);self.assertFalse(c['guest_envelope_conflicts'])
   self.assertEqual(c['upper_cover_y']-c['floor_y'],22.5)
   self.assertGreater(c['area_m2'],5000)
   self.assertGreater(len(c['potential_outward_view_source_indices']),40)
   self.assertTrue(Polygon(c['boundary']).is_valid)
 def test_cores_and_bypasses_fit_plan(self):
  hull=Polygon(json.loads((ROOT/'data/hull_envelope.json').read_text())['plan_xz_m'])
  allocations=json.loads((ROOT/'data/reference/directory_allocations.json').read_text())['records']
  for c in self.plan['longitudinal_vertical_core_reservations']:
   self.assertEqual(len(c['decks']),18);self.assertFalse(c['programme_guest_shop_conflicts'])
   for x in c['required_bypass_x_ranges']:
    p=box(x[0],c['z'][0]-c['bypass_end_extension_m'],x[1],c['z'][1]+c['bypass_end_extension_m'])
    self.assertTrue(hull.covers(p))
    self.assertTrue(all(p.intersection(rect(r)).area<1e-6 for r in allocations))
 def test_every_space_has_one_vertical_coordination_group(self):
  stacks=self.plan['neighbourhood_stacks'];self.assertEqual(len(stacks),10)
  for field,count in [('programme_keys',161),('guest_envelope_source_indices',1000),('retail_envelope_source_indices',100),('crew_envelope_source_indices',200)]:
   values=[v for group in stacks for v in group[field]]
   self.assertEqual(len(values),count);self.assertEqual(len(set(values)),count)
 def test_staff_risers_remain_separate_and_crosslink_is_preserved(self):
  self.assertEqual(len(self.plan['staff_riser_reservations']),10)
  for r in self.plan['staff_riser_reservations']:self.assertFalse(r['allocation_conflicts'])
  for c in self.plan['longitudinal_vertical_core_reservations']:
   self.assertEqual(c['preserved_crosslink_local_z'],[-3,3])
   self.assertGreaterEqual(c['stair_reservation_local_z'][0],4)
  link=self.plan['arrivals_service_link_reservation']
  self.assertFalse(link['public_crossing_required']);self.assertTrue(all(p[0]<-4 for p in link['route_xz']))
 def test_houses_account_for_every_guest_once(self):
  h=self.plan['residential_houses'];ids=[i for row in h for i in row['guest_envelope_source_indices']]
  self.assertEqual(len(h),12);self.assertEqual(len(ids),1000);self.assertEqual(len(set(ids)),1000)
  self.assertEqual(sum(len(r['guest_envelope_source_indices'])for r in h if r['decks']==['D04']),120)
 def test_crew_footprints_and_assignment_remain_distinct(self):
  self.assertEqual(sum(d['crew_bank_envelope_count']for d in self.plan['decks']),200)
  self.assertEqual(self.plan['protected_totals']['crew_people_including_player'],400)
  self.assertIn('Unresolved',self.plan['crew_assignment_gate'])
 def test_raised_pool_protects_lower_sport_and_upper_dining(self):
  p=self.plan['aquatic_section_reservations'][0]
  self.assertGreater(p['proposed_basin_bottom_y'],p['lower_arrival_y'])
  self.assertLess(p['proposed_wet_deck_y'],p['market_gallery_y'])
  self.assertLess(p['market_gallery_y'],p['protected_dining_floor_y'])
  self.assertAlmostEqual(p['minimum_1_to_12_ramp_run_m'],p['wet_deck_rise_m']*12)
  self.assertFalse(p['guest_envelope_conflicts']);self.assertEqual(len(p['affected_programmes']),3)
 def test_reservations_do_not_cut_floors_or_claim_completion(self):
  voids={v['id']for v in json.loads((ROOT/'data/spatial_layout.json').read_text())['voids']}
  reservations=self.plan['residential_court_reservations']+self.plan['longitudinal_vertical_core_reservations']
  self.assertTrue(all(c['id']not in voids for c in reservations))
  self.assertTrue(all(not d['final_layout_accepted']for d in self.plan['decks']))
  self.assertGreaterEqual(len(self.plan['unresolved_finalization_gates']),8)
if __name__=='__main__':unittest.main()
