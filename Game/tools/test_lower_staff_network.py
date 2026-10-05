"""Static staff-floor gates; actual movement and scene geometry tested in Godot."""
from pathlib import Path
import json,unittest
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
class LowerStaffNetwork(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((R/'data/architecture/LOWER_STAFF_NETWORK.json').read_text())
  cls.l=json.loads((R/'data/spatial_layout.json').read_text())
 def test_bounded_three_deck_scope(self):
  self.assertEqual(self.c['deck_stops_y'],[0,6,12]);self.assertEqual([d['deck'] for d in self.c['decks']],[1,2,3])
  self.assertLess(self.c['lift']['top_cap_bottom_top_y'][1],16.5-.24)
 def test_original_floor_owners_preserved(self):
  expected={'D01_port_service_spine':7.2,'D02_fusion_screened_service':21.6,'D03_protected_crew_cover':36}
  self.assertEqual({r['preserved_owner'] for r in self.c['preserved_floor_overlaps']},set(expected))
  for r in self.c['preserved_floor_overlaps']:self.assertAlmostEqual(r['area_m2'],expected[r['preserved_owner']])
  self.assertTrue(set(expected).issubset({r['id'] for r in self.l['regions']}))
 def test_explicit_slab_owner(self):
  owned=[r for r in self.l['regions'] if r.get('authoring_owner')=='port_forward_staff_network']
  self.assertEqual(len(owned),3)
  self.assertEqual({r['deck'] for r in owned},{'D01','D02','D03'})
  self.assertTrue(all(r['render_cell_m']==20 and r['material_role']=='staff_floor' for r in owned))
 def test_source_polygons_and_supported_centrelines(self):
  ends={1:-60,2:-432,3:-216}
  for d in self.c['decks']:
   p=unary_union([Polygon(v) for v in d['floor_union_polygons_xz']])
   self.assertTrue(p.is_valid)
   route=LineString([(-21,-490),(-21,-500),(-57,-500),(-57,ends[d['deck']])])
   self.assertTrue(p.covers(route.buffer(.45,cap_style=2,join_style=2)))
 def test_no_false_arrivals_portal_or_extra_beds(self):
  d=self.c['decks'][0]
  self.assertFalse(any('arrivals' in x['name'].lower() for x in d['boundary_apertures']))
  p=unary_union([Polygon(v) for v in d['floor_union_polygons_xz']])
  self.assertEqual(p.intersection(box(-54,-466,-8,-398)).area,0)
  for t in self.c['decks'][2]['thresholds']:self.assertIn('bounded_unfurnished',t['status'])
 def test_existing_synthesis_owner_truthful(self):
  ledger=json.loads((R/'data/programme_ledger.json').read_text())
  row=next(r for r in ledger['destinations'] if r['programme_key']=='D01_directory_05')
  self.assertEqual(row['current_geometry_owner'],'scripts/staff_section.gd')
  self.assertIn('Partial',row['current_status']);self.assertIn('unfinished',row['current_status'])
if __name__=='__main__':unittest.main()
