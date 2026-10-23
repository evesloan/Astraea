#!/usr/bin/env python3
"""Read-only positive intersection witnesses. Not an engine or clearance pass."""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMIT = "de6803e7f2054cd20c2e1580a1f5c47e3f792db0"
PINNED_LOCAL = {
    "tests/validate_atrium_supports.gd": "b609552edbd560a0cc8d645f8b11abf0d6755cdb",
    "scripts/group4_completion.gd": "20b6c835685cf4ef9b857d6805fce84b3bdfb292",
    "scripts/group4_integrated_receiving.gd": "483368a8ac7d890873f74cb3d1294d3cad7d2769",
}
SELECTED = {
    "guideway": ["V2_Continuous_Web", "V2_Continuous_Rail_-0.86", "V2_Continuous_Rail_0.86"],
    "guideway_receivers": ["M003_UnderwebGirder_-1.25", "M003_UnderwebGirder_1.25"],
}


def hashes(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}


def read_glb(blob):
    assert struct.unpack_from("<4sII", blob) == (b"glTF", 2, len(blob))
    length, kind = struct.unpack_from("<II", blob, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(blob[20:20 + length])
    blength, bkind = struct.unpack_from("<II", blob, 20 + length)
    start = 28 + length
    assert bkind == 0x004E4942 and start + blength == len(blob)

    def elem(index, i):
        accessor = doc["accessors"][index]
        assert "sparse" not in accessor and i < accessor["count"]
        view = doc["bufferViews"][accessor["bufferView"]]
        assert view["buffer"] == 0
        fmt = "<" + {5121: "B", 5123: "H", 5125: "I", 5126: "f"}[accessor["componentType"]] * {"SCALAR": 1, "VEC3": 3}[accessor["type"]]
        offset = start + view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        return struct.unpack_from(fmt, blob, offset + i * view.get("byteStride", struct.calcsize(fmt)))

    def triangles(name):
        index, node = next((i, n) for i, n in enumerate(doc["nodes"]) if n.get("name") == name)
        assert index in doc["scenes"][doc.get("scene", 0)]["nodes"]
        assert not any(k in node for k in ("matrix", "translation", "rotation", "scale"))
        primitives = doc["meshes"][node["mesh"]]["primitives"]
        assert len(primitives) == 1
        primitive = primitives[0]
        assert primitive.get("mode", 4) == 4
        pos = primitive["attributes"]["POSITION"]
        assert doc["accessors"][pos]["componentType"] == 5126
        indices = primitive["indices"]
        count = doc["accessors"][indices]["count"]
        assert count % 3 == 0
        for i in range(count // 3):
            tri = [elem(pos, elem(indices, 3 * i + j)[0]) for j in range(3)]
            assert all(math.isfinite(x) for vertex in tri for x in vertex)
            yield i, tri
    return triangles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-root", type=Path, default=HERE.parent / "recovery-only-current-448eab12/Game")
    args = parser.parse_args()
    game = args.game_root
    directory = json.loads((HERE / "SOURCE_DIRECTORY_PINS.json").read_text())
    entries = {r["path"]: r for r in directory["entries"]}
    inputs = {}
    current_pins = json.loads((HERE / "CURRENT_CONTENT_PINS.json").read_text())
    assert current_pins["commit"] == COMMIT
    for row in current_pins["files"]:
        h = hashes((game / row["path"].removeprefix("Game/")).read_bytes())
        assert h["git_blob_sha1"] == row["git_blob_sha1"] and h["bytes"] == row["bytes"]
        inputs[row["path"]] = h
    for path, sha in PINNED_LOCAL.items():
        inputs["Game/" + path] = hashes((game / path).read_bytes())
        assert inputs["Game/" + path]["git_blob_sha1"] == sha
    plan_path = game / "data/architecture/GROUP4_COMPLETION_CANDIDATE.json"
    inputs["Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json"] = hashes(plan_path.read_bytes())
    plan = json.loads(plan_path.read_text())
    interface = json.loads((HERE / "retained-inputs/port_successor_002/SUCCESSOR_INTERFACE.json").read_text())
    travel_path = game / "data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"
    travel = json.loads(travel_path.read_text())
    inputs["Game/data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"] = hashes(travel_path.read_bytes())
    assert travel["source_interface_sha256"] == hashes((HERE / "retained-inputs/port_successor_002/SUCCESSOR_INTERFACE.json").read_bytes())["sha256"]
    assert travel["source_route_points_xz"] == interface["guideway"]["route_points_xz"]
    assert plan["protected_polyline_xz"] == interface["protected_polyline_xz"]
    assert interface["guideway"]["rail_head_y"] == 55.74 and interface["guideway"]["floor_y"] == 56.1
    cases = []
    for role, names in SELECTED.items():
        model = next(r for r in plan["models"] if r["role"] == role)
        path = game / "source_derivatives/group4_completion_20261011" / model["file"]
        blob = path.read_bytes()
        h = hashes(blob)
        assert h["sha256"] == model["sha256"]
        family = "port_successor_002" if role == "guideway" else "receiving_module_003"
        original = "BlenderCatalogue/assets/group4_tram_connections_20261009/" + family + "/" + model["file"]
        assert h["git_blob_sha1"] == entries[original]["git_blob_sha1"]
        inputs["Game/" + str(path.relative_to(game))] = h
        triangles = read_glb(blob)
        for name in names:
            assert model["policies"][name] == "static_trimesh_candidate"
            all_tris = list(triangles(name))
            yy = [v[1] for _, tri in all_tris for v in tri]
            witness = None
            for i, tri in all_tris:
                radii = [math.hypot(v[0], v[2] + 72) for v in tri]
                if not all(52.55 < v[1] < 56.55 for v in tri) or max(radii) >= 2:
                    continue
                a = [tri[1][j] - tri[0][j] for j in range(3)]
                b = [tri[2][j] - tri[0][j] for j in range(3)]
                cross = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
                assert sum(x*x for x in cross) > 1e-20
                witness = {"triangle_zero_based": i, "vertices_world_xyz": tri,
                           "centroid_world_xyz": [sum(v[j] for v in tri)/3 for j in range(3)],
                           "maximum_vertex_horizontal_radius_m": max(radii),
                           "all_vertices_strictly_inside_start_cylinder": True}
                break
            assert witness is not None, name
            cases.append({"model": model["file"], "mesh": name, "source_policy": model["policies"][name],
                          "mesh_y_bounds_m": [min(yy), max(yy)], "witness": witness})
    for path, h in inputs.items():
        assert hashes((game / path.removeprefix("Game/")).read_bytes()) == h
    result = {"status": "FIVE_FIXED_SOURCE_MEMBERS_PROVEN_INSIDE_UNCHANGED_D09_RESERVATION",
              "source_commit": COMMIT,
              "method": "Read retained GLB triangles; verify current source Git and manifest hashes, identity transforms and static contact policies. Every witness triangle has all three vertices strictly inside the convex cylinder. No engine test or new motion experiment.",
              "reservation": {"center_xz": [0, -72], "radius_m": 2, "min_y": 52.55, "max_y": 56.55,
                              "source": "Game/tests/validate_atrium_supports.gd:34-46"},
              "source_interface_and_travel_route_agree": True,
              "production_inputs_unchanged_before_after": True,
              "inputs": inputs, "fixed_witnesses": cases,
              "limits": ["Positive intersections only; not an exhaustive obstruction census or clearance pass.",
                         "Native Blender files are remotely retained and identified, but not downloaded or opened in this review.",
                         "No Godot, Blender, rendering, motion experiment, candidate geometry, production edits or publication."]}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
