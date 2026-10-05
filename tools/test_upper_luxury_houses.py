import json,unittest
from pathlib import Path
from collections import Counter
from shapely.geometry import Polygon,box,LineString
R=Path(__file__).resolve().parents[1]
class LuxuryReservations(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads((R/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json').read_text());cls.rooms=cls.p['replacements'];cls.placed=[r for r in cls.rooms if r['proposed_floor_boundary']]
 def test_exact_replacement_counts(self):
  self.assertEqual(Counter(r['tier']for r in self.rooms),{'deluxe':50,'premium':25,'royalty':5,'supreme':1})
  ids={r['source_envelope_index']for r in self.rooms};self.assertEqual(len(ids),81)
  keep=set(self.p['retained_D17_standard_source_indices']);self.assertEqual(len(keep),19);self.assertFalse(ids&keep)
  self.assertEqual(len(ids|keep)+900,1000);self.assertEqual(self.p['counts']['admission_cap_unchanged'],2000)
 def test_all_units_now_have_explicit_reservations(self):
  self.assertEqual(len(self.placed),81);self.assertEqual(sum(r['proposed_floor_boundary']is None for r in self.rooms),0)
  self.assertFalse(any(r['upper_level_is_new_unit']for r in self.rooms))
  self.assertEqual(sum(r['upper_floor_y']is not None for r in self.rooms),6)
 def test_hull_and_programme_clearance(self):
  hull=Polygon(json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m'])
  programmes=[r for r in json.loads((R/'data/reference/directory_allocations.json').read_text())['records']if r['deck']==17]
  for r in self.placed:
   p=Polygon(r['proposed_floor_boundary']);self.assertTrue(p.is_valid);self.assertTrue(hull.buffer(1e-5).covers(p))
   for q in programmes:self.assertLess(p.intersection(box(q['x'][0],q['z'][0],q['x'][1],q['z'][1])).area,1e-5)
 def test_no_suite_overlap_or_narrow_opposing_view(self):
  for i,r in enumerate(self.placed):
   p=Polygon(r['proposed_floor_boundary'])
   for s in self.placed[i+1:]:self.assertLess(p.intersection(Polygon(s['proposed_floor_boundary'])).area,1e-5)
   if r['tier']!='deluxe':continue
   z=p.centroid.y;edge=max(abs(p.bounds[0]),abs(p.bounds[2]))
   for s in self.placed:
    if s['house']!=r['house']or s['tier']=='deluxe':continue
    hit=Polygon(s['proposed_floor_boundary']).intersection(LineString([(-130,z),(130,z)]))
    if not hit.is_empty:self.assertGreaterEqual(min(abs(hit.bounds[0]),abs(hit.bounds[2]))-edge,9.8)
 def test_central_standards_and_crown_dependencies(self):
  standard=self.p['replanned_standard_units'];self.assertEqual(len(standard),19)
  for a in standard:
   shape=Polygon(a['proposed_floor_boundary'])
   for r in self.rooms:self.assertLess(shape.intersection(Polygon(r['proposed_floor_boundary'])).area,1e-5)
  crown=json.loads((R/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').read_text())
  for r in self.rooms:
   self.assertLess(r['proposed_external_roof_limit_y'],118)
   if r['upper_floor_y']is not None:
    for q in crown['programmes']:self.assertLess(Polygon(r['proposed_floor_boundary']).intersection(Polygon(q['proposed_floor_boundary'])).area,1e-5)
  self.assertEqual({r['historical_D18_programme']for r in self.p['historical_D18_overlap_dependencies']},{'D18_directory_05','D18_directory_06'})
 def test_source_identity_unchanged(self):
  guests=json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
  for r in self.rooms:
   src=guests[r['source_envelope_index']];self.assertEqual(src['deck'],17)
   self.assertEqual(r['historical_stable_id'],src['stable_id']);self.assertEqual(r['source_allocation'],{'x':src['x'],'z':src['z']})
if __name__=='__main__':unittest.main()
