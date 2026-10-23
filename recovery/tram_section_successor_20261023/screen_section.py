#!/usr/bin/env python3
"""Bounded central detour evidence. Read source geometry; never alter production.

The two complete tangent detours preserve the existing 4 m reservation. A source
screen is deliberately insufficient to admit a replacement route or new station.
"""
from pathlib import Path
import argparse, hashlib, json, math, struct
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GAME = ROOT / "Game"
PINS = {}


def read(path):
    raw = path.read_bytes()
    PINS[str(path.relative_to(ROOT))] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return raw


def fillet(corners, radius=4.0):
    points = [np.array(corners[0], float)]
    for a, b, c in zip(corners, corners[1:], corners[2:]):
        a, b, c = map(lambda v: np.array(v, float), (a, b, c))
        incoming = (b-a)/np.linalg.norm(b-a)
        outgoing = (c-b)/np.linalg.norm(c-b)
        assert abs(float(incoming@outgoing)) < 1e-8
        start, end = b-incoming*radius, b+outgoing*radius
        center = start+outgoing*radius
        points.append(start)
        va, vb = start-center, end-center
        angle = math.atan2(float(np.cross(va, vb)), float(va@vb))
        angle0 = math.atan2(va[1], va[0])
        points.extend(center+radius*np.array([math.cos(angle0+angle*i/32), math.sin(angle0+angle*i/32)]) for i in range(1, 33))
    points.append(np.array(corners[-1], float))
    return np.array(points)


def distances(points, route):
    result = np.full(len(points), np.inf)
    for a, b in zip(route, route[1:]):
        delta = b-a
        if delta@delta < 1e-16:
            continue
        t = np.clip((points-a)@delta/(delta@delta), 0, 1)
        result = np.minimum(result, np.linalg.norm(points-(a+t[:, None]*delta), axis=1))
    return result


def glb_vertices(file, origin=(0, 0, 0), yaw=0.0):
    raw = read(GAME / "assets/models" / file)
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20+length])
    blength, bkind = struct.unpack_from("<II", raw, 20+length)
    assert bkind == 0x004E4942
    binary = raw[28+length:28+length+blength]

    def matrix(node):
        if "matrix" in node:
            return np.array(node["matrix"]).reshape(4, 4).T
        x, y, z, w = node.get("rotation", [0, 0, 0, 1])
        rot = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
        out = np.eye(4)
        out[:3, :3] = rot@np.diag(node.get("scale", [1, 1, 1]))
        out[:3, 3] = node.get("translation", [0, 0, 0])
        return out

    world = np.eye(4)
    world[:3, :3] = [[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0], [-math.sin(yaw), 0, math.cos(yaw)]]
    world[:3, 3] = origin

    def visit(index, parent):
        node = doc["nodes"][index]
        transform = parent@matrix(node)
        if "mesh" in node:
            for primitive in doc["meshes"][node["mesh"]]["primitives"]:
                a = doc["accessors"][primitive["attributes"]["POSITION"]]
                assert a["componentType"] == 5126 and a["type"] == "VEC3" and "sparse" not in a
                v = doc["bufferViews"][a["bufferView"]]
                assert v.get("buffer", 0) == 0
                points = np.ndarray((a["count"], 3), dtype="<f4", buffer=binary,
                                    offset=v.get("byteOffset", 0)+a.get("byteOffset", 0),
                                    strides=(v.get("byteStride", 12), 4)).astype(float)
                yield node.get("name", str(index)), points@transform[:3, :3].T+transform[:3, 3]
        for child in node.get("children", []):
            yield from visit(child, transform)

    for index in doc["scenes"][doc.get("scene", 0)]["nodes"]:
        yield from visit(index, world)


def clip(poly, axis, value, above):
    result = []
    for a, b in zip(poly, poly[1:]+poly[:1]):
        aa = a[axis] >= value if above else a[axis] <= value
        bb = b[axis] >= value if above else b[axis] <= value
        if aa:
            result.append(a)
        if aa != bb:
            t = (value-a[axis])/(b[axis]-a[axis])
            result.append([a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])])
    return result


def footprint_owners(xz, regions):
    x, z = xz
    owners = []
    for region in regions:
        area = 0.0
        for triangle in region["triangles"]:
            poly = [list(p) for p in triangle]
            for axis, value, above in [(0, x-.12, True), (0, x+.12, False), (1, z-.18, True), (1, z+.18, False)]:
                poly = clip(poly, axis, value, above) if poly else []
            if len(poly) > 2:
                area += abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(poly, poly[1:]+poly[:1])))*.5
        if area > 1e-9:
            owners.append({"owner": region["id"], "overlap_m2": round(area, 9), "underside_y": region["floor_y"]-region["thickness"]})
    return owners


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    read(GAME / "tests/validate_atrium_supports.gd")
    read(GAME / "scripts/atrium_lighting.gd")
    read(GAME / "scripts/group4_integrated_receiving.gd")
    read(GAME / "docs/master_source/MASTER_FULL_CONTENT_INDEX.json")
    interface = json.loads(read(ROOT / "recovery/tram_clearance_conflict_20261023/retained-inputs/port_successor_002/SUCCESSOR_INTERFACE.json"))
    layout = json.loads(read(GAME / "data/generated/structural_meshes.json"))
    regions = [r for r in layout["regions"] if r["floor_y"] == 61]
    protected = np.array(interface["protected_polyline_xz"])
    meshes = []
    core = json.loads(read(GAME / "data/architecture/PRIMARY_ATRIUM_CORE.json"))
    meshes.extend(("central_core/"+name, pts) for name, pts in glb_vertices(core.get("enclosure_file", "AST-CIR-005.glb"), core["origin"]))
    meshes.extend(("atrium/"+name, pts) for name, pts in glb_vertices("AST-ATR-001.glb"))
    for x, z in [(-31, -18), (-31, 18), (31, -18), (31, 18), (-18, -46), (18, -46), (-18, 46), (18, 46)]:
        yaw = (0 if x > 0 else math.pi) if abs(x) > abs(z) else (math.pi/2 if z < 0 else -math.pi/2)
        for file in ["AST-STR-001-H826.glb", "AST-STR-002-H826.glb"]:
            meshes.extend((f"{file}@{x},{z}/"+name, pts) for name, pts in glb_vertices(file, (x, 52.5, z), yaw))
    results = []
    for side, x in [("starboard_outboard", 44.5), ("port_outboard", -44.5)]:
        route = fillet([[-5.6, -85.3], [-5.6, -78], [x, -78], [x, 78], [-5.6, 78], [-5.6, 92]])
        # Dense sampling gives a lower-bound witness only, never a swept-clearance PASS.
        sample = np.concatenate([np.linspace(a, b, max(2, math.ceil(np.linalg.norm(b-a)*10))) for a, b in zip(route, route[1:])])
        nearest = float(distances(sample, protected).min())
        hits = []
        for name, pts in meshes:
            near = pts[(pts[:, 1] > 55.55+1e-5)&(pts[:, 1] < 60.1-1e-5)]
            if not len(near):
                continue
            dd = distances(near[:, [0, 2]], route)
            inside = np.flatnonzero(dd < 2-1e-5)
            if len(inside):
                i = int(inside[0])
                hits.append({"mesh": name, "vertex_inside_running_envelope": near[i].tolist(), "distance_to_route_m": float(dd[i])})
        receiver_samples = []
        for z in [-78, -64, -48, -24, 0, 24, 48, 64, 78]:
            for dx in [-1.7, 1.7]:
                pt = [x+dx, z]
                owners = footprint_owners(pt, regions)
                receiver_samples.append({"pad_center_xz": pt, "owners": owners,
                                         "full_unique_pad": len(owners) == 1 and abs(owners[0]["overlap_m2"]-.0864) < 1e-6})
        # Approaches between core and atrium are necessary, not inferred from midspan owners.
        for z in [-78, 78]:
            for xx in [-5.6, (x-5.6)/2, x]:
                owners = footprint_owners([xx, z], regions)
                receiver_samples.append({"approach_pad_center_xz": [xx, z], "owners": owners,
                                         "full_unique_pad": len(owners) == 1 and abs(owners[0]["overlap_m2"]-.0864) < 1e-6})
        results.append({"option": side, "sampled_route_centerline_xz": route.round(9).tolist(),
                        "corner_radius_m": 4, "running_y": 56.1, "envelope_y": [55.55, 60.1],
                        "protected_centerline_separation_sample_min_m": nearest,
                        "positive_source_vertex_intersections": hits, "receiver_samples": receiver_samples,
                        "entire_corridor_admitted": False})
    report = {"status": "BOUNDED_SECTION_OPTIONS_NOT_ADMITTED", "options": results,
              "protected_lower_envelope_y": [52.55, 56.55], "protected_width_and_height_m": [4, 4],
              "source_pins": PINS,
              "limits": ["Positive vertices prove intersection with the proposed swept band; absence does not prove a clear scene.",
                         "Selected actual core/atrium/bearings only; all later district details are not included.",
                         "Full positive-area pads are source contacts, not load/capacity approval.",
                         "A continuous admissible guideway, station and support interface has not been established.",
                         "No production, native geometry, engine, collision guard or admission mutation."]}
    output = json.dumps(report, indent=2)+"\n"
    if args.output:
        assert args.output.resolve().parent == HERE and not args.output.exists()
        args.output.write_text(output)
    else:
        print(output, end="")
    print(json.dumps({r["option"]: {"positive_intersection_meshes": len(r["positive_source_vertex_intersections"]),
                                      "receiver_samples_without_unique_full_pad": sum(not x["full_unique_pad"] for x in r["receiver_samples"]),
                                      "minimum_sampled_separation_m": r["protected_centerline_separation_sample_min_m"]} for r in results}))


if __name__ == "__main__":
    main()
