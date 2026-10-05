import unittest,json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
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
 def test_screened_links_are_continuous_and_clear(self):
  links=self.p['service_link_reservations']+self.p['observation_service_links']
  corridors=[LineString(r['path_xz']).buffer(r['width_m']/2,cap_style=2,join_style=2)for r in links]
  corridors += [box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])for r in self.p['screened_side_corridor_reservations']]
  self.assertEqual(unary_union(corridors).geom_type,'Polygon')
  cores=[Polygon(self.p['preserved_central_core']['boundary']),Polygon(self.p['aft_arrival_and_alternative_descent']['two_level_core_boundary'])]
  for corridor in corridors:
   for core in cores:self.assertLess(corridor.intersection(core).area,1e-6)
   for room in self.p['programmes']:self.assertLess(corridor.intersection(Polygon(room['proposed_floor_boundary'])).area,1e-6)
 def test_cap_and_lower_cover_constraints(self):
  core=json.loads((R/'data/architecture/PRIMARY_ATRIUM_CORE.json').read_text())
  self.assertEqual(self.p['preserved_central_core']['authored_shaft_cap_top_y'],core['lift']['cap_y'][1])
  self.assertTrue(self.p['existing_cover_reconciliation']['retain_geometry'])
  self.assertEqual(self.p['atrium_support_and_cover_gate']['retain_opaque_cover']['x'],[-48,48])
  self.assertEqual(self.p['aft_arrival_and_alternative_descent']['floor_heights'],[102,106.5])
 def test_geometry_stays_proposal(self):
  layout=json.loads((R/'data/spatial_layout.json').read_text())
  self.assertFalse(any(r.get('authoring_owner')=='D18_command_crown'for r in layout['regions']))
  self.assertLess(self.p['dimensions']['proposed_longitudinal_span_m'],self.p['dimensions']['source_longitudinal_span_m'])
if __name__=='__main__':unittest.main()
