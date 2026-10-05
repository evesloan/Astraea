"""Pure floor/source-gate planning checks. Never import Godot or alter live data."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from author_aft_crown_platform import OWNER, R, BRIEF, author, digest, plan_floors, prepare_adoption, record_bytes, substrate, verified_source


class AftCrownPlatformPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brief = json.loads(BRIEF.read_text())
        cls.original = substrate(json.loads((R / 'data/spatial_layout.json').read_text()))
        cls.protected_files = ['data/spatial_layout.json', 'data/generated/structural_meshes.json', *cls.brief['preservation']['files_sha256']]
        cls.before_files = {p: (R / p).read_bytes() for p in cls.protected_files}
        cls.current_compiled = [r for r in json.loads((R / 'data/generated/structural_meshes.json').read_text())['regions'] if not r['id'].startswith('D18_aft_crown_platform_')]
        cls.candidate = plan_floors(cls.original, cls.brief)
        # Compiler runs only from a complete bounded temporary input copy.
        with tempfile.TemporaryDirectory(prefix='astraea-aft-platform-plan-') as temp:
            root = Path(temp)
            for folder in ['tools', 'data/generated', 'docs']:
                (root / folder).mkdir(parents=True, exist_ok=True)
            for file in ['tools/compile_layout.py', 'data/design_contract.json']:
                shutil.copy2(R / file, root / file)
            def compile_rows(layout):
                (root / 'data/spatial_layout.json').write_text(json.dumps(layout))
                subprocess.run([sys.executable, str(root / 'tools/compile_layout.py')], env=os.environ.copy(), check=True, capture_output=True, text=True)
                return json.loads((root / 'data/generated/structural_meshes.json').read_text())
            cls.compiled_before = compile_rows(cls.original)
            cls.compiled_after = compile_rows(cls.candidate)

    @classmethod
    def tearDownClass(cls):
        for path, before in cls.before_files.items():
            if (R / path).read_bytes() != before:
                raise AssertionError('Protected live file changed during planning checks: ' + path)

    def rows(self):
        return [r for r in self.candidate['regions'] if r.get('authoring_owner') == OWNER]

    def test_preserves_all_original_source_records_and_voids(self):
        before = copy.deepcopy(self.original)
        result = plan_floors(self.original, self.brief)
        self.assertEqual(before, self.original)
        self.assertEqual(record_bytes(substrate(result)), record_bytes(before))
        self.assertEqual(result['voids'], before['voids'])

    def test_exact_four_component_areas_and_total(self):
        self.assertEqual(len(self.rows()), 4)
        areas = sorted(Polygon(r['boundary']).area for r in self.rows())
        self.assertEqual([round(a, 6) for a in areas], [1154.6, 1154.6, 1604, 1604])
        self.assertAlmostEqual(unary_union([Polygon(r['boundary']) for r in self.rows()]).area, 5517.2)
        for kind, expected in [('foyer', 2309.2), ('upper_horizon', 3208)]:
            self.assertAlmostEqual(sum(Polygon(r['boundary']).area for r in self.rows() if kind in r['id']), expected)

    def test_idempotent(self):
        self.assertEqual(self.candidate, plan_floors(self.candidate, self.brief))

    def test_infill_has_minimum_coplanar_priority(self):
        old = [r for r in self.original['regions'] if r['deck'] == 'D18' and abs(r.get('offset_y', 0)) < 1e-6]
        for new in self.rows():
            self.assertEqual(new['priority'], -10)
            self.assertTrue(all(new['priority'] <= r.get('priority', 0) for r in old))
            self.assertEqual(new['thickness'], .24)
        compiled = [r for r in self.compiled_after['regions'] if r['id'].startswith('D18_aft_crown_platform_')]
        self.assertTrue(all(r['floor_y'] == 106.5 and r['thickness'] == .24 for r in compiled))

    def test_all_245_live_compiled_records_stay_byte_equivalent(self):
        self.assertEqual(len(self.current_compiled), 245)
        self.assertEqual(digest(self.current_compiled), self.brief['baseline']['compiled_records_sha256'])
        before = self.compiled_before['regions']
        self.assertEqual(record_bytes(before), record_bytes(self.current_compiled))
        after = {r['id']: r for r in self.compiled_after['regions']}
        self.assertEqual(len(after), 249)
        for row in self.current_compiled:
            # Serialize the whole record without canonicalizing array/ring order.
            self.assertEqual(json.dumps(row, separators=(',', ':')).encode(), json.dumps(after[row['id']], separators=(',', ':')).encode(), row['id'])

    def test_core_holes_are_810456_and_never_filled(self):
        protected = unary_union([Polygon(v['boundary']) for v in self.original['voids'] if 'D18' in v['decks']])
        self.assertAlmostEqual(protected.intersection(box(-36, 102, 36, 142)).area, 81.0456)
        for row in self.rows():
            self.assertAlmostEqual(Polygon(row['boundary']).intersection(protected).area, 0)
        for row in self.compiled_after['regions']:
            if row['id'].startswith('D18_aft_crown_platform_'):
                for triangle in row['triangles']:
                    self.assertAlmostEqual(Polygon(triangle).intersection(protected).area, 0)

    def test_no_existing_substrate_or_slab_overlap(self):
        old = unary_union([Polygon(r['boundary'], r.get('holes', [])) for r in self.original['regions'] if r['deck'] == 'D18' and abs(r.get('offset_y', 0)) < 1e-6])
        for row in self.rows():
            self.assertAlmostEqual(Polygon(row['boundary']).intersection(old).area, 0)
        self.assertTrue(self.compiled_after['source_checks']['no_coplanar_region_overlap'])
        self.assertTrue(self.compiled_after['source_checks']['no_intersecting_slab_volumes'])

    def test_changed_existing_substrate_rejected(self):
        changed = copy.deepcopy(self.original)
        changed['regions'].append({'id': 'unreviewed', 'deck': 'D18', 'boundary': [[20, 110], [21, 110], [21, 111], [20, 111]]})
        with self.assertRaisesRegex(AssertionError, 'substrate changed'):
            plan_floors(changed, self.brief)

    def test_equal_area_substrate_change_rejected(self):
        changed = copy.deepcopy(self.original)
        row = next(r for r in changed['regions'] if r['id'] == 'D18_aft_crown_link_floor')
        row['boundary'] = [[x + .001, z] for x, z in row['boundary']]
        with self.assertRaisesRegex(AssertionError, 'substrate changed'):
            plan_floors(changed, self.brief)

    def test_changed_void_or_owner_metadata_rejected(self):
        for key in ['voids', 'regions']:
            changed = copy.deepcopy(self.original)
            changed[key][0]['unreviewed_metadata'] = True
            with self.assertRaisesRegex(AssertionError, 'substrate changed'):
                plan_floors(changed, self.brief)

    def test_programme_guest_crew_counts_and_sources_unchanged(self):
        for path, expected in self.brief['preservation']['files_sha256'].items():
            self.assertEqual(hashlib.sha256((R / path).read_bytes()).hexdigest(), expected)
        ledger = json.loads((R / 'data/programme_ledger.json').read_text())
        self.assertEqual(len(ledger['destinations']), 161)
        self.assertEqual(ledger['accommodation']['guest_unit_target'], 1000)
        self.assertEqual(ledger['accommodation']['crew_including_player'], 400)
        self.assertEqual(len(json.loads((R / 'data/reference/historical_guest_census.json').read_text())['guest_envelopes']), 1000)
        self.assertEqual(len(json.loads((R / 'data/reference/D03_crew_envelopes.json').read_text())['records']), 200)
        self.assertEqual(sum(r['programme_key'] == 'D18_directory_09' for r in ledger['destinations']), 1)

    def test_live_adoption_disabled(self):
        with self.assertRaisesRegex(RuntimeError, 'intentionally disabled'):
            author()


class AftCrownSourceGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='astraea-aft-source-gate-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rows = []
        self.sha = {}
        for family, identity in [('aft_crown_platform', 'AST-CMD-005'), ('aft_command', 'AST-CMD-002')]:
            base = 'assets/' + family + '/'
            source = base + 'source/' + identity + '.blend'
            export = base + 'exports/' + identity + '.glb'
            manifest = base + identity + '.manifest.json'
            contract = base + 'source/section_contract.json'
            contents = {source: b'isolated editable test fixture', export: identity.encode(), contract: json.dumps({'catalogue_id': identity, 'status': 'Not accepted', 'opaque_source_contract': {'preserve': [1, 2]}}).encode()}
            for path, content in contents.items():
                (self.root / path).parent.mkdir(parents=True, exist_ok=True)
                (self.root / path).write_bytes(content)
            self.sha[identity] = (hashlib.sha256(contents[export]).hexdigest(), hashlib.sha256(contents[contract]).hexdigest())
            self.rows.append({'catalogue_id': identity, 'family': family, 'source': source, 'export': export, 'manifest': manifest, 'export_sha256': self.sha[identity][0], 'source_sha256': hashlib.sha256(contents[source]).hexdigest()})
        self.save()

    def save(self):
        (self.root / 'catalogue_manifest.json').write_text(json.dumps({'assets': self.rows}))

    def verify005(self):
        return verified_source(self.root, 'aft_crown_platform', 'AST-CMD-005', *self.sha['AST-CMD-005'])

    def test_exact_source_contract_bytes_preserved(self):
        verified = self.verify005()
        self.assertEqual(verified['contract_bytes'], (self.root / 'assets/aft_crown_platform/source/section_contract.json').read_bytes())
        self.assertEqual(verified['contract']['status'], 'Not accepted')
        self.assertNotIn('runtime_status', verified['contract'])

    def test_wrong_hash_rejected(self):
        for index in [0, 1]:
            shas = list(self.sha['AST-CMD-005']); shas[index] = '0' * 64
            with self.assertRaises(AssertionError):
                verified_source(self.root, 'aft_crown_platform', 'AST-CMD-005', *shas)

    def test_duplicate_identity_wrong_family_or_paths_rejected(self):
        original = copy.deepcopy(self.rows)
        self.rows.append(copy.deepcopy(self.rows[0])); self.save()
        with self.assertRaises(AssertionError): self.verify005()
        for key in ['family', 'source', 'export', 'manifest']:
            self.rows = copy.deepcopy(original)
            self.rows[0][key] = 'wrong_identity'; self.save()
            with self.assertRaises(AssertionError): self.verify005()

    def test_staging_requires_both_reviewed_exports_and_contracts(self):
        brief = json.loads(BRIEF.read_text())
        layout = substrate(json.loads((R / 'data/spatial_layout.json').read_text()))
        args = [layout, brief, self.root, self.sha['AST-CMD-005'][0], self.sha['AST-CMD-002'][0], self.sha['AST-CMD-005'][1], self.sha['AST-CMD-002'][1]]
        bundle = prepare_adoption(*args)
        self.assertFalse(bundle['live_write_allowed'])
        self.assertEqual(bundle['runtime_acceptance'], 'pending')
        self.assertEqual([s['identity'] for s in bundle['sources']], ['AST-CMD-005', 'AST-CMD-002'])
        for index in range(3, 7):
            bad = list(args); bad[index] = '0' * 64
            with self.assertRaises(AssertionError): prepare_adoption(*bad)
        brief['baseline']['original_002_export_sha256'] = self.sha['AST-CMD-002'][0]
        with self.assertRaisesRegex(AssertionError, 'Revised 002 required'):
            prepare_adoption(*args)


if __name__ == '__main__':
    unittest.main()
