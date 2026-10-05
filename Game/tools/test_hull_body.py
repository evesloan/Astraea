import unittest,json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1]
class HullBody(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((R/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())
 def test_source_hashes_current(self):
  for p,h in self.d['source_sha256'].items():self.assertEqual(hashlib.sha256((R/p).read_bytes()).hexdigest(),h)
 def test_all_decks_and_counts(self):
  self.assertEqual([x['deck']for x in self.d['levels']],['D%02d'%i for i in range(1,19)])
  for kind,total in [('directory',161),('guest',1000),('crew_bank',200)]:self.assertEqual(sum(x['source_counts'][kind]for x in self.d['levels']),total)
 def test_no_claimed_conflicts(self):
  self.assertTrue(all(not x['allocation_conflicts']and not x['compiled_floor_conflicts']for x in self.d['levels']))
 def test_reference_size_and_height(self):
  hull=Polygon(self.d['levels'][3]['outer_boundary']);self.assertAlmostEqual(hull.bounds[2]-hull.bounds[0],240);self.assertAlmostEqual(hull.bounds[3]-hull.bounds[1],1082);self.assertEqual(self.d['total_height_m'],118)
 def test_reserve_inside_body(self):
  for x in self.d['levels']:
   a=Polygon(x['outer_boundary']);b=Polygon(x['inner_reservation_boundary']);self.assertTrue(a.covers(b));self.assertGreater(a.boundary.distance(b.boundary),.99)
 def test_chine_widens_upward(self):
  knots=self.d['lower_body_knots'];self.assertTrue(all(a['y']<b['y'] and a['inset_m']>b['inset_m']for a,b in zip(knots,knots[1:])))
 def test_top_not_full_width_story(self):
  self.assertIn('compact crown',self.d['roof_rule']);self.assertIn('Reference fit only',self.d['levels'][17]['section_role']);self.assertFalse(self.d['summary']['source_or_runtime_geometry_changed'])
if __name__=='__main__':unittest.main()
