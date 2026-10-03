"""Regression checks for opening review; does not mutate production layout."""
import unittest
from audit_vertical_programme import opening_conflicts

class OpeningReview(unittest.TestCase):
    def setUp(self):
        self.guests = [{'deck':13, 'x':[0,10], 'z':[0,10]}, {'deck':14, 'x':[0,10], 'z':[0,10]}]
    def opening(self, boundary, decks=None):
        return {'id':'test', 'decks':decks or ['D13'], 'boundary':boundary}
    def test_intrusion_is_reported_only_on_affected_deck(self):
        result = opening_conflicts(self.guests,[self.opening([[5,5],[15,5],[15,15],[5,15]])])
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['overlap_m2'],25)
        self.assertEqual(result[0]['deck'],13)
    def test_touching_boundary_is_not_intrusion(self):
        self.assertEqual(opening_conflicts(self.guests,[self.opening([[10,0],[20,0],[20,10],[10,10]])]),[])
    def test_offset_opening_uses_real_polygon(self):
        result=opening_conflicts(self.guests,[self.opening([[5,5],[15,5],[5,15]])])
        self.assertEqual(result[0]['overlap_m2'],25)
    def test_invalid_polygon_is_rejected(self):
        with self.assertRaises(AssertionError):
            opening_conflicts(self.guests,[self.opening([[0,0],[10,10],[0,10],[10,0]])])
    def test_multiple_decks_are_checked(self):
        result=opening_conflicts(self.guests,[self.opening([[0,0],[10,0],[10,10],[0,10]],['D13','D14'])])
        self.assertEqual(len(result),2)

if __name__=='__main__':unittest.main()
