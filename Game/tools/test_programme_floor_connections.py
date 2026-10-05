import unittest,json
from audit_programme_floor_connections import build,ROOT
class FloorConnections(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.audit=build()
 def test_complete_directory_crosswalk(self):
  expected={r['programme_key']for r in json.loads((ROOT/'data/reference/directory_allocations.json').read_text())['records']}
  self.assertEqual({r['programme_key']for r in self.audit['programmes']},expected)
  self.assertEqual(len(self.audit['programmes']),161)
  self.assertEqual(len(self.audit['decks']),18)
 def test_no_route_acceptance_from_plan(self):
  self.assertTrue(all(not r['route_accepted']for r in self.audit['programmes']))
  self.assertEqual(self.audit['summary']['fully_accepted_routes'],0)
 def test_asset_floor_is_not_false_negative(self):
  night=next(r for r in self.audit['programmes']if r['programme_key']=='D12_directory_06')
  self.assertGreater(night['connected_floor_overlap_m2'],0)
 def test_accounting_and_gaps(self):
  s=self.audit['summary'];self.assertEqual(s['with_connected_floor_overlap']+s['without_connected_floor_overlap'],161)
  for r in self.audit['programmes']:
   self.assertGreaterEqual(r['nearest_floor_gap_m'],0)
   self.assertLessEqual(r['connected_floor_overlap_m2'],r['allocation_area_m2']+.001)
if __name__=='__main__':unittest.main()
