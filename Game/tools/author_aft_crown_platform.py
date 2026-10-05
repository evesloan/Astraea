"""Plan missing-only aft floors and adopt only explicitly pinned, reviewed sources.
Dry-run planning never mutates live files. Adoption does not imply runtime acceptance.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
from shapely.geometry import Polygon
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
OWNER = 'aft_crown_platform'
BRIEF = R / 'data/architecture/AFT_CROWN_PLATFORM_CONSTRUCTION.json'


def record_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(record_bytes(value)).hexdigest()


def substrate(layout):
    result = copy.deepcopy(layout)
    result['regions'] = [r for r in result['regions'] if r.get('authoring_owner') != OWNER]
    return result


def plan_floors(layout, brief):
    """Return a fresh complete layout, rejecting any change to reviewed substrate."""
    result = substrate(layout)
    assert digest(result) == brief['baseline']['layout_records_sha256'], 'Current substrate changed; re-coordinate before adoption'
    existing_rows = [r for r in result['regions'] if r['deck'] == 'D18' and abs(r.get('offset_y', 0)) < 1e-6]
    existing = unary_union([Polygon(r['boundary'], r.get('holes', [])) for r in existing_rows])
    protected = unary_union([Polygon(v['boundary']) for v in result['voids'] if 'D18' in v.get('decks', [])])
    priority = min(r.get('priority', 0) for r in existing_rows)
    assert priority == -10, 'Reviewed minimum coplanar priority changed'
    added = []
    for kind in ['foyer', 'upper_horizon']:
        spec = brief['floors'][kind]
        target = Polygon(spec['boundary'])
        assert target.is_valid and abs(target.area - spec['gross_m2']) < 1e-7
        assert abs(target.intersection(protected).area - spec['protected_openings_m2']) < 1e-7
        assert abs(target.intersection(existing.difference(protected)).area - spec['existing_actual_floor_m2']) < 1e-7
        missing = target.difference(existing).difference(protected)
        expected = unary_union([Polygon(p) for p in spec['expected_missing_boundaries']])
        assert missing.symmetric_difference(expected).area < 1e-7, 'Reviewed missing footprint changed: ' + kind
        assert abs(missing.area - spec['new_floor_m2']) < 1e-7
        assert missing.geom_type == 'MultiPolygon' and len(missing.geoms) == 2
        for side, polygon in zip(['port', 'starboard'], sorted(missing.geoms, key=lambda p: p.centroid.x)):
            assert polygon.is_valid and not polygon.interiors
            assert polygon.intersection(existing).area < 1e-7
            assert polygon.intersection(protected).area < 1e-7
            assert abs(polygon.area - spec['component_m2']) < 1e-7
            result['regions'].append({
                'id': 'D18_aft_crown_platform_' + kind + '_' + side,
                'authoring_owner': OWNER, 'deck': 'D18',
                'boundary': [list(q) for q in polygon.exterior.coords[:-1]], 'holes': [],
                'priority': priority, 'thickness': brief['datums']['slab_depth'],
                'render_cell_m': 24,
                'material_role': 'guest_floor',
                'status': 'Missing-only aft platform infill; source, runtime, visual and route acceptance remain separate gates'
            })
            added.append(polygon)
    assert abs(sum(p.area for p in added) - 5517.2) < 1e-7
    assert abs(unary_union(added).area - 5517.2) < 1e-7
    return result


def verified_source(catalogue, family, identity, export_sha, contract_sha):
    """Verify exact registered paths and reviewed bytes, retaining contract verbatim."""
    for sha in [export_sha, contract_sha]:
        assert isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'Explicit reviewed SHA-256 required'
    catalogue = Path(catalogue)
    rows = [r for r in json.loads((catalogue / 'catalogue_manifest.json').read_text())['assets'] if r['catalogue_id'] == identity]
    assert len(rows) == 1, 'Catalogue identity must be unique: ' + identity
    row = rows[0]
    base = 'assets/' + family + '/'
    assert row['family'] == family
    assert row['export'] == base + 'exports/' + identity + '.glb'
    assert row['source'] == base + 'source/' + identity + '.blend'
    assert row['manifest'] == base + identity + '.manifest.json'
    assert row['export_sha256'] == export_sha
    export = (catalogue / row['export']).read_bytes()
    assert hashlib.sha256(export).hexdigest() == export_sha, 'Final reviewed export changed: ' + identity
    source = catalogue / row['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256'], 'Registered editable source changed: ' + identity
    contract_bytes = (catalogue / base / 'source/section_contract.json').read_bytes()
    assert hashlib.sha256(contract_bytes).hexdigest() == contract_sha, 'Reviewed contract changed: ' + identity
    contract = json.loads(contract_bytes)
    assert contract['catalogue_id'] == identity
    return {'identity': identity, 'export_bytes': export, 'contract_bytes': contract_bytes, 'contract': contract}


def prepare_adoption(layout, brief, catalogue, final005_sha, revised002_sha, final005_contract_sha, revised002_contract_sha):
    """Return an in-memory candidate only; never manufacture runtime completion.

    Both assets and their exact source contracts must be reviewed first. A caller
    still must perform the bounded 002 part diff and understand the final runtime
    schema before copying this candidate to any live destination.
    """
    floors = plan_floors(layout, brief)
    sources = [
        verified_source(catalogue, 'aft_crown_platform', 'AST-CMD-005', final005_sha, final005_contract_sha),
        verified_source(catalogue, 'aft_command', 'AST-CMD-002', revised002_sha, revised002_contract_sha),
    ]
    assert revised002_sha != brief['baseline']['original_002_export_sha256'], 'Revised 002 required; original solid returns cannot be adopted'
    return {'layout': floors, 'sources': sources, 'runtime_acceptance': 'pending', 'live_write_allowed': False}


def author(catalogue=None, final005_sha=None, revised002_sha=None,
           final005_contract_sha=None, revised002_contract_sha=None,
           audit_sha=None, preservation_sha=None):
    """Adopt only after explicit final source and independent review pins."""
    if not all([catalogue, final005_sha, revised002_sha, final005_contract_sha,
                revised002_contract_sha, audit_sha, preservation_sha]):
        raise RuntimeError('Explicit final source, contact and preservation hashes are required for live adoption')
    catalogue = Path(catalogue)
    brief = json.loads(BRIEF.read_text())
    bundle = prepare_adoption(json.loads((R/'data/spatial_layout.json').read_text()), brief,
                              catalogue, final005_sha, revised002_sha,
                              final005_contract_sha, revised002_contract_sha)
    qa = catalogue/'assets/aft_crown_platform/qa'
    proofs = {}
    for filename, expected in [('independent_contact_audit.json', audit_sha),
                               ('002_actual_preservation.json', preservation_sha)]:
        raw = (qa/filename).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected, 'Final reviewed QA changed: '+filename
        proofs[filename] = json.loads(raw)
        assert proofs[filename].get('pass') is True
    audit = proofs['independent_contact_audit.json']
    for key, expected in [('005_export',final005_sha),('002_export',revised002_sha),
                          ('005_contract',final005_contract_sha),('002_contract',revised002_contract_sha)]:
        assert audit['hashes'][key] == expected
    preservation = proofs['002_actual_preservation.json']
    assert preservation['all_old_markers_exact']
    assert preservation['all_old_contract_fields_exact_except_two_appended_doors']
    platform = copy.deepcopy(bundle['sources'][0]['contract'])
    aft = copy.deepcopy(bundle['sources'][1]['contract'])
    assert platform['programme_key'] == 'D18_directory_09'
    assert platform['floor_y'] == 106.5 and platform['floor_thickness'] == .24
    assert {d['name'] for d in platform['doors']} == {'aft_platform_port_service_exit','aft_platform_starboard_service_exit'}
    assert {d['name'] for d in aft['doors']} == {'D18_directory_08_entry','D18_directory_10_entry',
        'aft_command_port_front','aft_command_starboard_front','aft_command_port_exit','aft_command_starboard_exit'}
    # All checks precede writes. Floor-only stage does not reclassify the programme ledger.
    for data, sha in [(platform,final005_sha),(aft,revised002_sha)]:
        data['export_sha256'] = sha
        data['runtime_status'] = 'Supported aft platform integration; runtime, visual and aggregate acceptance pending'
    def write(path, value):
        path.write_text(json.dumps(value,indent=2)+'\n')
    write(R/'data/spatial_layout.json',bundle['layout'])
    write(R/'data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json',platform)
    write(R/'data/architecture/AFT_COMMAND_RUNTIME.json',aft)
    for source in bundle['sources']:
        (R/'assets/models'/(source['identity']+'.glb')).write_bytes(source['export_bytes'])
    print(json.dumps({'new_floor_m2':5517.2,'programme_ledger_changed':False,
                      'guest_or_crew_units_changed':False,'runtime_acceptance':'pending'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--catalogue', default='/workspace/shared/astraea-catalogue-continuation-20261002')
    for flag in ['platform-sha','aft-sha','platform-contract-sha','aft-contract-sha','audit-sha','preservation-sha']:
        parser.add_argument('--'+flag)
    args = parser.parse_args()
    if args.dry_run:
        brief = json.loads(BRIEF.read_text())
        candidate = plan_floors(json.loads((R/'data/spatial_layout.json').read_text()), brief)
        rows = [r for r in candidate['regions'] if r.get('authoring_owner') == OWNER]
        print(json.dumps({'dry_run':True,'new_regions':len(rows),
            'new_floor_m2':sum(Polygon(r['boundary']).area for r in rows),
            'priority':-10,'live_files_written':False,'source_and_runtime_acceptance':'pending'}))
    else:
        author(args.catalogue,args.platform_sha,args.aft_sha,args.platform_contract_sha,
               args.aft_contract_sha,args.audit_sha,args.preservation_sha)
