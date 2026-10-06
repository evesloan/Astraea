"""Exact theater source-floor policy; no generic theater void exemption."""
import json,hashlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
MANIFEST_SHA='f215b6a1c3a586f8fd3a329bf852afd9b3fd291cda10aaac5260d62a7b270e33'
EXPORT_SHA='fa056d66c1064cb6ee917f0fcae7d6ffccbd9426118a95c8a09f1e8b23457947'
BLEND_SHA='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
IDS=['D12_theater_gallery_seating', 'D12_theater_rear_public_returns', 'D12_theater_foyer_landings', 'D12_theater_stair_upper_landing', 'D13_theater_gallery_seating', 'D13_theater_rear_public_returns', 'D13_theater_foyer_landings', 'D13_theater_stair_upper_landing']
def verify_theater_surfaces(root,layout,elevations):
    rows={r['id']:r for r in layout['regions']}
    used=[r for r in layout['regions']if 'theater_upper_volume'in r.get('void_exemptions',[])]
    if not used:return set()
    assert {r['id']for r in used}==set(IDS),('Exact eight theater surface owners required',used)
    path=root/'data/architecture/packages/theater/SOURCE_SURFACE_MANIFEST_003.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==MANIFEST_SHA,'Theater source manifest changed'
    mesh=root/'assets/models/AST-CUL-005_static_003.glb'
    assert hashlib.sha256(mesh.read_bytes()).hexdigest()==EXPORT_SHA,'Theater static export changed'
    specs={s['region_id']:s for s in json.loads(path.read_text())['surfaces']};assert set(specs)==set(IDS)
    for ident in IDS:
        row=rows[ident];spec=specs[ident]
        assert row['deck']==spec['deck']and row.get('owner')=='grand_lantern_theater'and row.get('kind')=='authored_theater_surface'and row.get('provided_by_asset')is True,ident
        assert row.get('void_exemptions')==['theater_upper_volume']and row.get('source_surface_manifest_sha256')==MANIFEST_SHA and row.get('source_static_export_sha256')==EXPORT_SHA and row.get('source_blend_sha256')==BLEND_SHA,ident
        assert elevations[row['deck']]+row.get('offset_y',0)==spec['absolute_floor_y'] and row.get('thickness',.24)==.24,ident
        expected=unary_union([Polygon(p['boundary_xz'])for p in spec['parts']]);actual=Polygon(row['boundary'],row.get('holes',[]));assert actual.is_valid and actual.symmetric_difference(expected).area<1e-7,ident
    return set(IDS)
