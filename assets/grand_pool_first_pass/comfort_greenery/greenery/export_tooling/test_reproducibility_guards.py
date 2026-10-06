import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,unittest,types
from unittest.mock import patch
import verify_snapshot as v
import precise_normal_export as n
class ReproducibilityGuards(unittest.TestCase):
    def test_local_mapping_preserves_exact_target(self):
        self.assertEqual(v.local_evidence(str(v.TARGET/'evidence/INDEPENDENT_SOURCE_RETENTION.json')),v.HERE/'evidence/INDEPENDENT_SOURCE_RETENTION.json')
    def test_mapping_rejects_path_escape_and_unrelated_absolute_path(self):
        for p in ['../outside',str(v.TARGET.parent/'not_this_packet'),'/tmp/not_this_packet']:
            with self.assertRaises(AssertionError):v.local_evidence(p)
    def test_hash_mismatch_fails_closed(self):
        with self.assertRaises(AssertionError):v.check_hash(v.HERE/'EXPORT_INPUTS.json','0'*64)
    def test_precision_is_restored_after_success(self):
        fake=types.SimpleNamespace(__file__=n.json_record()['primitive_extractor_path'],ROUNDING_DIGIT=4)
        with patch.object(n.importlib,'import_module',return_value=fake):
            with n.precise_normals():self.assertEqual(fake.ROUNDING_DIGIT,8)
        self.assertEqual(fake.ROUNDING_DIGIT,4)
    def test_precision_is_restored_after_failure(self):
        fake=types.SimpleNamespace(__file__=n.json_record()['primitive_extractor_path'],ROUNDING_DIGIT=4)
        with patch.object(n.importlib,'import_module',return_value=fake):
            with self.assertRaises(RuntimeError):
                with n.precise_normals():raise RuntimeError('Deliberate test failure')
        self.assertEqual(fake.ROUNDING_DIGIT,4)
    def test_validated_tools_remain_byte_identical(self):
        for name,row in json.loads((v.HERE/'VALIDATED_TOOL_HASHES.json').read_text()).items():v.check_hash(v.HERE/name,row['sha256'])
if __name__=='__main__':unittest.main()
