"""Reuse pinned prior compiled records only after unchanged input/shape proof."""
import hashlib
import json
from shapely.geometry import Polygon
from shapely.ops import unary_union

LAYOUT_SHA = "587e2a0d618b4957eab68c5dd437fdfed93ef4c7dab138d9b62326a53d1d6da2"
COMPILED_SHA = "3322c84a8dc2d456c6652d641bc0e02a38b27ec1095b95d5d494a1456b14f52b"
CONTRACT_SHA = "8790e9997fd39c6ddd8a494f665b2a438a7160ec31f343bd858ce5c036fa569a"


def effective_shapes(layout, elevations):
    levels = {row["id"]: elevations[row["deck"]] + row.get("offset_y", 0) for row in layout["regions"]}
    shapes = {}
    for row in layout["regions"]:
        shape = Polygon(row["boundary"], row.get("holes", []))
        for void in layout["voids"]:
            if row["deck"] in void["decks"] and void["id"] not in row.get("void_exemptions", []):
                shape = shape.difference(Polygon(void["boundary"]))
        shapes[row["id"]] = shape
    owned = {}
    for row in layout["regions"]:
        shape = shapes[row["id"]]
        for other in layout["regions"]:
            if abs(levels[row["id"]] - levels[other["id"]]) < 1e-6 and other.get("priority", 0) > row.get("priority", 0):
                shape = shape.difference(shapes[other["id"]])
        owned[row["id"]] = shape
    return owned


def preserve_prior_records(root, layout, elevations, owned, outputs):
    base = root / "data/architecture/packages/theater/retained"
    old_layout_path = base / "spatial_layout.json"
    old_compiled_path = base / "structural_meshes.json"
    assert hashlib.sha256(old_layout_path.read_bytes()).hexdigest() == LAYOUT_SHA
    assert hashlib.sha256(old_compiled_path.read_bytes()).hexdigest() == COMPILED_SHA
    assert hashlib.sha256((root / "data/design_contract.json").read_bytes()).hexdigest() == CONTRACT_SHA
    old_layout = json.loads(old_layout_path.read_text())
    old_compiled = json.loads(old_compiled_path.read_text())
    assert {k: v for k, v in layout.items() if k != "regions"} == {k: v for k, v in old_layout.items() if k != "regions"}, "Prior global layout/void contract changed"
    old_rows = {row["id"]: row for row in old_layout["regions"]}
    current_rows = {row["id"]: row for row in layout["regions"]}
    assert len(current_rows) == len(layout["regions"]), "Duplicate current owner"
    prior_shapes = effective_shapes(old_layout, elevations)
    for ident, row in old_rows.items():
        assert current_rows.get(ident) == row, ("Prior input owner changed", ident)
        assert prior_shapes[ident].equals(owned[ident]), ("Prior effective owned shape changed", ident)
    generated = {row["id"]: row for row in outputs}
    old_records = {row["id"]: row for row in old_compiled["regions"]}
    reordered = []
    for ident, prior in old_records.items():
        candidate = generated[ident]
        assert set(candidate) == set(prior), ident
        for key in prior:
            if key not in ("triangles", "rings", "structural_area_m2"):
                assert candidate[key] == prior[key], ("Prior compiled metadata changed", ident, key)
        old_mesh = unary_union([Polygon(triangle) for triangle in prior["triangles"]])
        new_mesh = unary_union([Polygon(triangle) for triangle in candidate["triangles"]])
        assert old_mesh.equals(new_mesh) and old_mesh.equals(prior_shapes[ident]), ("Prior mesh footprint changed", ident)
        assert abs(prior["structural_area_m2"] - candidate["structural_area_m2"]) <= 1e-9, ident
        if candidate != prior:
            reordered.append(ident)
    preserved = [old_records.get(row["id"], row) for row in outputs]
    assert all(next(row for row in preserved if row["id"] == ident) == prior for ident, prior in old_records.items())
    return preserved, {
        "previous_layout_sha256": LAYOUT_SHA,
        "previous_compiled_sha256": COMPILED_SHA,
        "exact_retained_layout_records": len(old_rows),
        "exact_retained_compiled_records": len(old_records),
        "new_compiled_records": len(preserved) - len(old_records),
        "physically_equivalent_regeneration_differences": reordered,
        "effective_owned_shapes_exactly_equal": True,
        "engineering_guard_update_required": True,
    }
