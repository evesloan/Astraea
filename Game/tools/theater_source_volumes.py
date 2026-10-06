"""Bounded, conservative collision guard for the eight pinned theater owners.

These are per-source-part vertical envelopes, not nominal deck slabs. A passed
guard proves disjoint interiors; an envelope hit fails closed and needs review.
This does not grant any new void exemption or static credit to a moving cabin.
"""
import hashlib
import json
from dataclasses import dataclass

from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

from theater_surface_policy import IDS, MANIFEST_SHA

GEOMETRY_SHA = "90406045c5c23e52af1850bba8ea3088cb672de072afa47a7f5e6feb39927429"
AREA_EPS = 1e-7
HEIGHT_EPS = 1e-6


@dataclass(frozen=True)
class Part:
    name: str
    shape: object
    bottom: float
    top: float


class TheaterSourceVolumes:
    def __init__(self, root, layout, theater_ids):
        self.parts = {}
        self.trees = {}
        self.bounds = {}
        if not theater_ids:
            return
        assert set(theater_ids) == set(IDS)
        base = root / "data/architecture/packages/theater"
        manifest_path = base / "SOURCE_SURFACE_MANIFEST_003.json"
        geometry_path = base / "SOURCE_GEOMETRY_003.json"
        assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == MANIFEST_SHA
        assert hashlib.sha256(geometry_path.read_bytes()).hexdigest() == GEOMETRY_SHA, "Theater source geometry changed"
        manifest = json.loads(manifest_path.read_text())
        geometry = json.loads(geometry_path.read_text())
        source_objects = {ident: [] for ident in IDS}
        for obj in geometry["objects"]:
            if obj.get("surface_region") in source_objects:
                source_objects[obj["surface_region"]].append(obj)
        rows = {row["id"]: row for row in layout["regions"]}
        assert len(rows) == len(layout["regions"]), "Duplicate layout owner"
        self.depth_counts = {}
        for spec in manifest["surfaces"]:
            ident = spec["region_id"]
            assert rows[ident].get("priority", 0) == 0, ("Theater priority not authorized", ident)
            objects = source_objects[ident]
            assert len(objects) == len(spec["parts"]), ident
            parts = []
            for surface, obj in zip(spec["parts"], objects):
                assert obj["role"] == "walkable_authored" and obj["collision_owner"] == "AST-CUL-005", obj["name"]
                boundary = surface["boundary_xz"]
                vertices = obj["vertices_world"]
                n = len(boundary)
                assert len(vertices) == 2 * n, obj["name"]
                tops = surface.get("vertex_top_y") if surface["top_y"] is None else [surface["top_y"]] * n
                depths = []
                for i, point in enumerate(boundary):
                    assert [vertices[i][0], vertices[i][2]] == point, obj["name"]
                    assert [vertices[i+n][0], vertices[i+n][2]] == point, obj["name"]
                    assert vertices[i][1] == tops[i], obj["name"]
                    depth = round(vertices[i][1] - vertices[i+n][1], 8)
                    assert depth in (.25, .45), ("Unreviewed source depth", obj["name"], depth)
                    depths.append(depth)
                assert len(set(depths)) == 1, obj["name"]
                self.depth_counts[str(depths[0])] = self.depth_counts.get(str(depths[0]), 0) + 1
                shape = Polygon(boundary)
                assert shape.is_valid and shape.area > 0, obj["name"]
                parts.append(Part(obj["name"], shape, min(v[1] for v in vertices), max(v[1] for v in vertices)))
            self.parts[ident] = parts
            self.trees[ident] = STRtree([part.shape for part in parts])
            self.bounds[ident] = (min(part.bottom for part in parts), max(part.top for part in parts))

    def validate_owned_shapes(self, owned):
        """A compiler subtraction cannot silently clip an immutable source mesh."""
        for ident, parts in self.parts.items():
            expected = unary_union([part.shape for part in parts])
            assert owned[ident].equals(expected), ("Source-backed owner was clipped or superseded", ident)

    def check_pair(self, a, b, owned, levels):
        """Called for pairs involving at least one exact source-backed owner."""
        if a["id"] not in self.parts:
            a, b = b, a
        aid, bid = a["id"], b["id"]
        assert aid in self.parts
        if bid in self.parts:
            blo, bhi = self.bounds[bid]
            if min(self.bounds[aid][1], bhi) - max(self.bounds[aid][0], blo) <= HEIGHT_EPS:
                return
            for first in self.parts[aid]:
                for index in self.trees[bid].query(first.shape):
                    second = self.parts[bid][int(index)]
                    self._assert_disjoint(first, second, aid, bid)
        else:
            second = Part(bid, owned[bid], levels[bid] - b.get("thickness", .24), levels[bid])
            if min(self.bounds[aid][1], second.top) - max(self.bounds[aid][0], second.bottom) <= HEIGHT_EPS:
                return
            for index in self.trees[aid].query(second.shape):
                self._assert_disjoint(self.parts[aid][int(index)], second, aid, bid)

    @staticmethod
    def _assert_disjoint(first, second, aid, bid):
        depth = min(first.top, second.top) - max(first.bottom, second.bottom)
        if depth <= HEIGHT_EPS:
            return
        area = first.shape.intersection(second.shape).area
        assert area < AREA_EPS, (
            "intersecting theater source-part vertical envelopes", aid, bid,
            first.name, second.name, "plan_area_m2", area, "vertical_overlap_m", depth,
        )

    def receipt(self):
        return {
            "geometry_sha256": GEOMETRY_SHA,
            "source_part_count": sum(map(len, self.parts.values())),
            "source_depth_counts_m": getattr(self, "depth_counts", {}),
            "source_owner_y_bounds": self.bounds,
            "method": "Pinned per-part source-solid min/max Y envelopes and exact source footprints; conservative fail-closed guard",
            "moving_cabin_credit": False,
        }
