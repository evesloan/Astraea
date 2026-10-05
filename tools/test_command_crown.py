import unittest,json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1]
class CrownPlan(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=json.loads((R/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').read_text())
 def test_all_programmes_and_source_preserved(self):
  src=R/'data/reference/directory_allocations.json';a={r['programme_key']:r for r in json.loads(src.read_text())['records']if r['deck']==18}
  self.assertEqual(self.p['source_sha256'],hashlib.sha256(src.read_bytes()).hexdigest())
  self.assertEqual(set(a),{r['programme_key']for r in self.p['programmes']})
  for r in self.p['programmes']:
   self.assertEqual(r['source_allocation'],{'x':a[r['programme_key']]['x'],'z':a[r['programme_key']]['z']})
   self.assertEqual(r['floor_y'],106.5)
 def test_no_programme_or_built_core_overlap(self):
  polys=[Polygon(r['proposed_floor_boundary'])for r in self.p['programmes']];core=Polygon(self.p['preserved_central_core']['boundary'])
  for i,p in enumerate(polys):
   self.assertTrue(p.is_valid);self.assertEqual(p.intersection(core).area,0)
   for q in polys[i+1:]:self.assertEqual(p.intersection(q).area,0)
 def test_public_route_separate_from_rooms(self):
  c=self.p['public_gallery_reservation'];gallery=box(c['x'][0],c['z'][0],c['x'][1],c['z'][1])
  for r in self.p['programmes']:self.assertEqual(Polygon(r['proposed_floor_boundary']).intersection(gallery).area,0)
 def test_geometry_stays_proposal(self):
  layout=json.loads((R/'data/spatial_layout.json').read_text())
  self.assertFalse(any(r.get('authoring_owner')=='D18_command_crown'for r in layout['regions']))
  self.assertLess(self.p['dimensions']['proposed_longitudinal_span_m'],self.p['dimensions']['source_longitudinal_span_m'])
if __name__=='__main__':unittest.main()
