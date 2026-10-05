import unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class UpperSections(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=json.loads((R/'data/architecture/UPPER_SECTION_COORDINATION.json').read_text())
 def test_total_height_budget(self):
  roofs=[self.s['crown']['external_roof_limit_y']]+[p['external_roof_limit_y']for p in self.s['private_upper_pavilions']]
  self.assertLessEqual(max(roofs)-self.s['provisional_exterior_bottom_y'],118)
 def test_installed_cap_and_clearance(self):
  c=self.s['crown'];self.assertGreater(c['provisional_clear_ceiling_y']-106.5,4)
  self.assertGreater(c['cap_to_transfer_zone_m'],1)
  self.assertGreaterEqual(self.s['transfer_reservation']['bottom_y'],c['provisional_clear_ceiling_y'])
 def test_no_new_units_or_post_inside_void(self):
  self.assertEqual(len(self.s['private_upper_pavilions']),6)
  self.assertTrue(all(p['unit_count_increment']==0 for p in self.s['private_upper_pavilions']))
  self.assertTrue(all(abs(x)>48 for x in self.s['transfer_reservation']['perimeter_bearing_x']))
 def test_covers_retained(self):self.assertTrue(all(c['retain']for c in self.s['retained_covers']))
if __name__=='__main__':unittest.main()
