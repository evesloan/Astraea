"""Current bounded crown ownership and geometry gates, separate from old proposals."""
from pathlib import Path
import hashlib,json,unittest
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from audit_programme_floor_connections import build
R=Path(__file__).resolve().parents[1]
class CentralCrown(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((R/'data/architecture/CENTRAL_CROWN_RUNTIME.json').read_text())
  cls.layout=json.loads((R/'data/spatial_layout.json').read_text())
  cls.ledger={r['programme_key']:r for r in json.loads((R/'data/programme_ledger.json').read_text())['destinations']}
 def test_exact_six_programmes_and_export(self):
  self.assertEqual({r['programme_key'] for r in self.c['programmes']},{f'D18_directory_{i:02}'for i in range(2,8)})
  self.assertEqual(hashlib.sha256((R/'assets/models/AST-CMD-001.glb').read_bytes()).hexdigest(),self.c['export_sha256'])
  self.assertEqual(len(self.ledger),161)
 def test_existing_floor_support_and_area(self):
  compiled=json.loads((R/'data/generated/structural_meshes.json').read_text())
  floor=unary_union([Polygon(t)for r in compiled['regions']if abs(r['floor_y']-106.5)<1e-6 for t in r['triangles']])
  total=0
  for p in self.c['programmes']:
   shape=Polygon(p['boundary']);self.assertTrue(shape.is_valid);self.assertLess(shape.difference(floor).area,1e-6);total+=shape.area
  self.assertAlmostEqual(total,6504)
 def test_six_metre_north_belt(self):
  belt=box(-48,-80,48,-74)
  self.assertEqual(self.c['public_fore_cross_street']['centreline_z'],-77)
  for p in self.c['programmes']:self.assertEqual(Polygon(p['boundary']).intersection(belt).area,0)
  for d in self.c['doors'][6:8]:
   self.assertEqual(abs(d['position'][0]),8);self.assertAlmostEqual(d['position'][2],-73.8)
   self.assertGreaterEqual(d['position'][2]-d['fixed_frame_half_depth'],-74)
 def test_current_ledger_boundaries(self):
  for p in self.c['programmes']:
   r=self.ledger[p['programme_key']];self.assertEqual(r['current_boundary_xz'],p['boundary']);self.assertEqual(r['current_geometry_owner'],'scripts/central_command_crown.gd')
   self.assertIn('historical_envelope',r)
 def test_floor_audit_uses_adopted_targets(self):
  report=build();rows={r['programme_key']:r for r in report['programmes']}
  for p in self.c['programmes']:
   r=rows[p['programme_key']];self.assertEqual(r['target_boundary_basis'],'adopted_current_geometry');self.assertAlmostEqual(r['connected_floor_overlap_m2'],Polygon(p['boundary']).area,places=3)
   self.assertFalse(r['route_accepted'])
 def test_original_covers_and_no_duplicate_slabs(self):
  rows={r['id']:r for r in self.layout['regions']}
  self.assertEqual(Polygon(rows['D18_atrium_structural_cap']['boundary']).area,12288)
  cover=rows['D18_starboard_house_cover'];self.assertIsNone(cover['programme_owner']);self.assertEqual(cover['previous_programme_reservation'],'D18_directory_06')
  base=json.loads((R/'data/architecture/D13_D14_starboard_commons.json').read_text());self.assertEqual(cover['boundary'],base['envelope_xz_m'])
  self.assertFalse(any(r.get('authoring_owner')=='D18_central_crown'for r in self.layout['regions']))
 def test_piers_avoid_existing_floor_and_voids(self):
  support=self.c['support'];self.assertEqual(support['pier_centres_xz'],[[-51.5,-71],[-51.5,71],[51.5,-71],[51.5,71]])
  for x,z in support['pier_centres_xz']:
   p=box(x-.4,z-.6,x+.4,z+.6)
   for r in self.layout['regions']:self.assertLess(p.intersection(Polygon(r['boundary'],r.get('holes',[]))).area,1e-6)
   for v in self.layout['voids']:self.assertEqual(p.intersection(Polygon(v['boundary'])).area,0)
 def test_height_and_window_scope(self):
  self.assertLessEqual(self.c['roof']['roof_top_limit_y']+3.5,118)
  self.assertEqual(self.c['roof']['ceiling_y'],111)
  self.assertEqual(len(self.c['windows']),3)
  self.assertEqual(len(self.c['light_markers']),74)
 def test_historical_source_unchanged(self):
  proposal=json.loads((R/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').read_text())
  self.assertEqual(proposal['source_sha256'],hashlib.sha256((R/'data/reference/directory_allocations.json').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
