"""Reproduce independent batch02 exported-byte, support and void measurements."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np

from geometry_checks import GLB, triangles, placement, contains_xy, support_probe, triangles_intersect_box

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')


def main():
    reports = []
    for family in ('structure', 'study', 'contents'):
        root = ROOT / 'assets' / ('library_' + family)
        current = [GLB(p).inspect() for p in sorted(root.rglob('*.glb'))]
        save('independent_' + family + '_glb_report.json', current)
        reports.extend(current)
    known_images = {hashlib.sha256(p.read_bytes()).hexdigest(): str(p.relative_to(ROOT))
                    for root in (ROOT/'materials', ROOT/'assets/library_contents/textures')
                    for p in root.glob('*.png')}
    textures = []
    for a in reports:
        textures.append({'asset': Path(a['path']).name,
                         'materials': [m['name'] for m in a['materials']],
                         'images': [{**im, 'source_match': known_images.get(im.get('embedded_sha256'))}
                                    for im in a['images']]})
    save('independent_texture_source_check.json', textures)

    base = ROOT/'assets/library_structure'
    structure = json.loads((base/'manifest.json').read_text())
    stock = ROOT/'assets/library_contents/AST-LIB-006_upright_book_group.glb'
    stock_variants = sorted(stock.parent.glob('AST-LIB-006_upright_book_group*.glb'))
    support_rows, nominal_rows = [], []
    for a in structure['assets']:
        geo = triangles(base/a['runtime_glb'])
        tri = np.concatenate([r['triangles'] for r in geo])
        for anchor in a['shelf_top_stock_anchors']:
            transform = placement(anchor['position_m'], anchor['rotation_z_degrees'])
            z = anchor['shelf_top_z_m']
            for stock_path in stock_variants:
                result = support_probe(geo, triangles(stock_path, transform), z)
                support_rows.append({'asset': a['catalogue_id'], 'anchor': anchor['id'], 'stock': stock_path.name, **result})
            horizontal = tri[(np.ptp(tri[:, :, 2], axis=1) < 2e-5) &
                             (np.abs(tri[:, :, 2].mean(1) - z) < 2e-5)]
            x, y = np.meshgrid(np.linspace(-.34, .34, 35), np.linspace(-.12, .12, 13))
            points = np.column_stack((x.ravel(), y.ravel(), np.zeros(x.size), np.ones(x.size)))
            p = (points @ transform.T)[:, :3]
            okay = contains_xy(p, horizontal)
            nominal_rows.append({'asset': a['catalogue_id'], 'anchor': anchor['id'],
                                 'samples': len(p), 'unsupported': int((~okay).sum())})
    save('independent_nominal_stock_support.json', nominal_rows)

    study = ROOT/'assets/library_study'
    api = json.loads((study/'integration_api.json').read_text())
    void_rows = []
    for a in api:
        geo = triangles(next(study.glob(a['catalogue_id']+'*.glb')))
        for v in a['clear_volumes_m']:
            void_rows.append({'asset': a['catalogue_id'], 'volume': v,
                              'intersections': triangles_intersect_box(geo, v['min'], v['max'])})
        for index, chair in enumerate(a['approach']['candidate_chairs']):
            v = chair.get('knee_volume_m')
            if v:
                void_rows.append({'asset': a['catalogue_id'], 'candidate_chair': index, 'volume': v,
                                  'intersections': triangles_intersect_box(geo, v['min'], v['max'])})
            rect = chair.get('outside_table_approach_rectangle_m')
            if rect:
                v = {'min': rect[0]+[0], 'max': rect[1]+[1.8]}
                void_rows.append({'asset': a['catalogue_id'], 'candidate_chair': index, 'volume': v,
                                  'scope': 'Table geometry only; candidate chair intentionally occupies part of this envelope.',
                                  'intersections': triangles_intersect_box(geo, v['min'], v['max'])})
        rect = a['approach'].get('clear_floor_entry_rectangle_m')
        if rect:
            v = {'min': rect[0]+[0], 'max': rect[1]+[1.8]}
            void_rows.append({'asset': a['catalogue_id'], 'volume': v,
                              'intersections': triangles_intersect_box(geo, v['min'], v['max'])})
        if a['catalogue_id'] == 'AST-LIB-STUDY-02':
            for anchor in a['bookstock_mounts']:
                for stock_path in stock_variants:
                    result = support_probe(geo, triangles(stock_path, placement(anchor['origin_m'], anchor['rotation_z_degrees'])), anchor['origin_m'][2])
                    support_rows.append({'asset': a['catalogue_id'], 'anchor': anchor['name'], 'stock': stock_path.name, **result})
        else:
            folio = ROOT/'assets/library_contents/AST-LIB-007_open_folio_stack.glb'
            for anchor in a['bookstock_mounts']:
                result = support_probe(geo, triangles(folio, placement(anchor['origin_m'], anchor['rotation_z_degrees'])), anchor['origin_m'][2])
                support_rows.append({'asset': a['catalogue_id'], 'anchor': anchor['name'], 'stock': 'AST-LIB-007', **result})
    save('independent_actual_stock_support.json', support_rows)
    save('independent_study_voids.json', void_rows)

    checks = []
    for a in structure['assets']:
        p = base/a['runtime_glb']; r = next(r for r in reports if Path(r['path']) == p)
        checks.append({'asset': a['catalogue_id'],
                       'source_hash_match': hashlib.sha256((base/a['source_blend']).read_bytes()).hexdigest() == a['hashes']['blend_sha256'],
                       'export_hash_match': r['sha256'] == a['hashes']['glb_sha256'],
                       'triangles_match': r['triangles'] == a['triangles_evaluated'],
                       'max_bounds_error_m': float(np.abs(np.array(r['dimensions_xyz'])-a['bounds']['dimensions_m']).max())})
    for family in ('study', 'contents'):
        root = ROOT/'assets'/('library_'+family)
        for p in sorted(root.glob('*.manifest.json')):
            a = json.loads(p.read_text()); glb = p.with_suffix('').with_suffix('.glb')
            blend = p.with_suffix('').with_suffix('.blend')
            source_hash = a.get('blend_sha256')
            if 'assembly_variant' in a:
                blend = root/a['assembly_variant']['base_source']
                source_hash = a['assembly_variant']['base_source_sha256']
            r = next(r for r in reports if Path(r['path']) == glb)
            checks.append({'asset': a['catalogue_id'],
                           'export': glb.name,
                           'source_hash_match': hashlib.sha256(blend.read_bytes()).hexdigest() == source_hash,
                           'export_hash_match': r['sha256'] == a['glb_sha256'],
                           'triangles_match': r['triangles'] == a['triangles_evaluated'],
                           'max_bounds_error_m': float(np.abs(np.array(r['dimensions_xyz'])-a['dimensions_m']).max())})
    save('independent_manifest_checks.json', checks)
    print(json.dumps({'exported_assets': len(reports),
                      'triangles': sum(r['triangles'] for r in reports),
                      'glb_issues': [r['issues'] for r in reports if r['issues']],
                      'texture_source_misses': [im['name'] for r in textures for im in r['images'] if not im['source_match']],
                      'supported_actual_stock_anchors': len(support_rows),
                      'stock_support_failures': [r['anchor'] for r in support_rows if r['projected_vertices_unsupported'] or r['interior_grid_points_unsupported'] or r['base_contact_vertices_unsupported']],
                      'void_intersections': [r for r in void_rows if r['intersections']],
                      'manifest_checks': checks}, indent=2))
    assert not any(r['issues'] for r in reports), 'Exported GLB issues'
    assert all(im['source_match'] for r in textures for im in r['images']), 'Embedded texture mismatch'
    assert not any(r['unsupported'] for r in nominal_rows), 'Unsupported nominal shelf footprint'
    assert not any(r['projected_vertices_unsupported'] or r['interior_grid_points_unsupported'] or r['base_contact_vertices_unsupported'] for r in support_rows), 'Unsupported actual stock'
    assert not any(r['intersections'] for r in void_rows), 'Geometry intrudes into declared clear volume'
    assert all(r['source_hash_match'] and r['export_hash_match'] and r['triangles_match'] and r['max_bounds_error_m'] < 1e-6 for r in checks), 'Manifest mismatch'


if __name__ == '__main__':
    main()
