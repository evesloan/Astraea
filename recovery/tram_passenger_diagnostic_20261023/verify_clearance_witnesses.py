#!/usr/bin/env python3
"""Read exact restored GLB triangles; no Godot import or physics execution."""
import hashlib
import json
import math
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parent / "recovery-only-current-448eab12/Game"
COMPLETION = json.loads((GAME / "data/architecture/GROUP4_COMPLETION_CANDIDATE.json").read_text())
BOARDING = json.loads((GAME / "data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json").read_text())
CASES = [
    (BOARDING, "vehicle", "source_derivatives/group4_boarding_safety_20261011/",
     "V2__Tram_Floor", 4, (0.0, 56.1, -72.0), "moving_vehicle"),
    (COMPLETION, "guideway", "source_derivatives/group4_completion_20261011/",
     "V2_Continuous_Web", 819, (0.0, 0.0, 0.0), "fixed_infrastructure"),
    (COMPLETION, "guideway_receivers", "source_derivatives/group4_completion_20261011/",
     "M003_UnderwebGirder_-1.25", 449, (0.0, 0.0, 0.0), "fixed_infrastructure"),
]


def witness(plan, role, prefix, mesh_name, triangle_index, translation, kind):
    model = next(m for m in plan["models"] if m["role"] == role)
    path = prefix + model["file"]
    blob = (GAME / path).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == model["sha256"]
    assert struct.unpack_from("<4sII", blob) == (b"glTF", 2, len(blob))
    json_length, json_type = struct.unpack_from("<II", blob, 12)
    assert json_type == 0x4E4F534A
    gltf = json.loads(blob[20:20 + json_length])
    bin_header = 20 + json_length
    bin_length, bin_type = struct.unpack_from("<II", blob, bin_header)
    assert bin_type == 0x004E4942 and bin_header + 8 + bin_length == len(blob)
    bin_start = bin_header + 8

    def element(accessor_index, element_index):
        accessor = gltf["accessors"][accessor_index]
        assert "sparse" not in accessor and element_index < accessor["count"]
        view = gltf["bufferViews"][accessor["bufferView"]]
        assert view["buffer"] == 0
        code = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}[accessor["componentType"]]
        count = {"SCALAR": 1, "VEC3": 3}[accessor["type"]]
        fmt = "<" + code * count
        stride = view.get("byteStride", struct.calcsize(fmt))
        offset = bin_start + view.get("byteOffset", 0) + accessor.get("byteOffset", 0) + element_index * stride
        return struct.unpack_from(fmt, blob, offset)

    node_index, node = next((i, n) for i, n in enumerate(gltf["nodes"]) if n.get("name") == mesh_name)
    assert node_index in gltf["scenes"][gltf.get("scene", 0)]["nodes"]
    assert not any(k in node for k in ("matrix", "translation", "rotation", "scale"))
    policy = model["policies"][mesh_name]
    assert policy != "no_collision_detail"
    if kind == "fixed_infrastructure":
        assert policy == "static_trimesh_candidate"
    primitives = gltf["meshes"][node["mesh"]]["primitives"]
    assert len(primitives) == 1 and primitives[0].get("mode", 4) == 4
    primitive = primitives[0]
    pos_accessor = primitive["attributes"]["POSITION"]
    assert gltf["accessors"][pos_accessor]["componentType"] == 5126
    vertices = []
    for corner in range(3):
        vertex_index = element(primitive["indices"], 3 * triangle_index + corner)[0]
        local = element(pos_accessor, vertex_index)
        vertices.append(tuple(local[axis] + translation[axis] for axis in range(3)))
    centroid = tuple(sum(v[axis] for v in vertices) / 3 for axis in range(3))
    radius = math.hypot(centroid[0], centroid[2] + 72)
    assert radius < 2 and 52.55 < centroid[1] < 56.55
    return {"path": "Game/" + path, "sha256": model["sha256"], "kind": kind,
            "mesh": mesh_name, "policy": policy, "triangle_zero_based": triangle_index,
            "world_vertices": vertices, "centroid": centroid,
            "distance_from_guard_axis_m": radius, "inside_central_start_guard": True}


if __name__ == "__main__":
    guard = (GAME / "tests/validate_atrium_supports.gd").read_bytes()
    guard_blob = hashlib.sha1(b"blob " + str(len(guard)).encode() + b"\0" + guard).hexdigest()
    assert guard_blob == "b609552edbd560a0cc8d645f8b11abf0d6755cdb"
    result = {"guard_git_blob_sha1": guard_blob, "guard_radius_m": 2, "guard_height_m": 4,
              "guard_d09_y_range_m": [52.55, 56.55], "guard_start_xz": [0, -72],
              "witnesses": [witness(*case) for case in CASES],
              "scope": "Source-triangle intrusion, not a Godot runtime test. Fixed obstructions remain even if moving vehicle occupancy is considered separately.",
              "godot_executed": False}
    (HERE / "CLEARANCE_WITNESSES.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"source_witnesses_verified": len(result["witnesses"]), "fixed_infrastructure_witnesses": 2, "godot_executed": False}))
