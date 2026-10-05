#!/usr/bin/env python3
"""Read actual derivative GLB bytes; write only the two named QA receipts.

No builder or builder-produced geometry receipt is imported. Geometry tests use
resolved GLB world-space triangles in native glTF Y-up metres. This is an exchange
geometry check, not a Godot import, physics, collision or performance claim.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("independent_glb_reader", ROOT / "qa/inspect_glb_independent.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
FLOORS = [0, 6, 12, 16.5, 21, 27, 35.5, 44, 52.5, 61, 69.5, 78, 84, 88.5, 93, 97.5, 102]
TOL = 2e-5


def resolved_geometry(glb):
    """Resolve every live scene node; do not assume node-local positions are global."""
    triangles, materials, node_rows = [], [], []
    doc = glb.doc

    def visit(index, parent, ancestors):
        assert index not in ancestors, "Hierarchy cycle"
        node = doc["nodes"][index]
        world = parent @ glb.matrix(node)
        row = {"name": node.get("name", str(index)), "index": index,
               "world_position_gltf_xyz_m": world[:3, 3].tolist(),
               "mesh_index": node.get("mesh"), "extras": node.get("extras", {})}
        if "mesh" in node:
            row["primitives"] = []
            for primitive in doc["meshes"][node["mesh"]]["primitives"]:
                assert primitive.get("mode", 4) == 4
                pos = glb.accessor(primitive["attributes"]["POSITION"])
                world_pos = (np.column_stack((pos, np.ones(len(pos)))) @ world.T)[:, :3]
                indices = (glb.accessor(primitive["indices"]).ravel().astype(int)
                           if "indices" in primitive else np.arange(len(pos)))
                tri = world_pos[indices.reshape(-1, 3)]
                material = doc["materials"][primitive["material"]]["name"]
                triangles.append(tri)
                materials.extend([material] * len(tri))
                row["primitives"].append({"material": material, "triangles": len(tri),
                                           "vertices": len(pos),
                                           "min_gltf_xyz_m": world_pos.min(axis=0).tolist(),
                                           "max_gltf_xyz_m": world_pos.max(axis=0).tolist()})
        node_rows.append(row)
        for child in node.get("children", []):
            visit(child, world, ancestors | {index})

    for index in doc["scenes"][doc.get("scene", 0)].get("nodes", []):
        visit(index, np.eye(4), set())
    return np.concatenate(triangles), np.array(materials), node_rows


def clip_polygon(poly, axis, bound, keep_greater):
    """Sutherland-Hodgman half-space clipping, retaining actual surface pieces."""
    if not len(poly):
        return []
    out = []
    previous = poly[-1]
    d_previous = (previous[axis] - bound) * (1 if keep_greater else -1)
    for current in poly:
        d_current = (current[axis] - bound) * (1 if keep_greater else -1)
        if (d_current >= 0) != (d_previous >= 0):
            out.append(previous + (current - previous) * d_previous / (d_previous - d_current))
        if d_current >= 0:
            out.append(current)
        previous, d_previous = current, d_current
    return out


def surface_in_box(triangles, lo, hi):
    """Exact clipped triangle surface area, not AABB-overlap approximation."""
    lo, hi = np.asarray(lo), np.asarray(hi)
    indices = np.flatnonzero(np.all(triangles.max(axis=1) >= lo, axis=1)
                             & np.all(triangles.min(axis=1) <= hi, axis=1))
    area = 0.0
    hit_count = 0
    for index in indices:
        polygon = list(triangles[index])
        for axis in range(3):
            polygon = clip_polygon(polygon, axis, lo[axis], True)
            polygon = clip_polygon(polygon, axis, hi[axis], False)
        if len(polygon) >= 3:
            p = np.asarray(polygon)
            value = np.linalg.norm(np.cross(p[1:-1] - p[0], p[2:] - p[0]), axis=1).sum() / 2
            if value > 1e-10:
                hit_count += 1
                area += value
    return {"clipped_surface_m2": float(area), "intersecting_triangles": hit_count}


def ray_hits(triangles, origin, direction, max_distance):
    """Moller-Trumbore hits against the raw material-batched triangle surfaces."""
    origin, direction = np.asarray(origin), np.asarray(direction)
    e1 = triangles[:, 1] - triangles[:, 0]
    e2 = triangles[:, 2] - triangles[:, 0]
    p = np.cross(direction, e2)
    determinant = np.einsum("ij,ij->i", e1, p)
    valid = np.abs(determinant) > 1e-10
    inverse = np.divide(1.0, determinant, out=np.zeros_like(determinant), where=valid)
    tvec = origin - triangles[:, 0]
    u = np.einsum("ij,ij->i", tvec, p) * inverse
    q = np.cross(tvec, e1)
    v = q @ direction * inverse
    distance = np.einsum("ij,ij->i", e2, q) * inverse
    valid &= (u >= -1e-7) & (v >= -1e-7) & (u + v <= 1 + 1e-7)
    valid &= (distance >= 0) & (distance <= max_distance)
    return sorted(set(float(round(x, 6)) for x in distance[valid]))


def add_check(report, name, condition, evidence=None):
    entry = {"check": name, "passed": bool(condition)}
    if evidence is not None:
        entry["evidence"] = evidence
    report["checks"].append(entry)


def base_report(path):
    glb = reader.GLB(path)
    generic = glb.inspect()
    triangles, materials, nodes = resolved_geometry(glb)
    report = {"asset": path.stem, "export_path": str(path.relative_to(ROOT)),
              "export_sha256": hashlib.sha256(glb.data).hexdigest(),
              "verifier_path": str(Path(__file__).relative_to(ROOT)),
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "frame": "Resolved native glTF Y-up XYZ metres, before runtime placement",
              "raw_counts": {"scene_nodes": len(nodes), "mesh_nodes": sum(n["mesh_index"] is not None for n in nodes),
                             "meshes": len(glb.doc.get("meshes", [])), "materials": len(glb.doc.get("materials", [])),
                             "embedded_images": sum("bufferView" in im for im in glb.doc.get("images", [])),
                             "triangles": len(triangles), "bytes": len(glb.data)},
              "bounds_gltf_xyz_m": [triangles.min(axis=(0, 1)).tolist(), triangles.max(axis=(0, 1)).tolist()],
              "material_triangle_counts": {str(m): int((materials == m).sum()) for m in sorted(set(materials))},
              "resolved_nodes": nodes, "generic_raw_glb_inspection": generic, "checks": [],
              "scope": "Actual GLB visual surfaces, materials, UVs and marker checks only. Source-piece equivalence has a separate verifier. No engine, physics, collision construction, ergonomics or performance certification."}
    add_check(report, "independent_parser_has_no_geometry_or_uv_issues", not generic["issues"], generic["issues"])
    primitives = [p for n in generic["nodes"] for p in n["primitives"]]
    add_check(report, "all_primitives_have_normals_and_uv0", all(p["normals_present"] and p["uv_present"] for p in primitives))
    add_check(report, "all_images_embedded", all(im["embedded"] for im in generic["images"]))
    return report, triangles, materials, nodes


def verify_forward():
    path = ROOT / "assets/primary_atrium_core/exports/AST-CIR-005_forward_core.glb"
    report, triangles, materials, nodes = base_report(path)
    report["expected_floor_y_m"] = FLOORS
    report["expected_portal_levels"] = [0, 1]
    report["expected_portal_sides"] = [-1]
    add_check(report, "four_material_batches", report["raw_counts"]["meshes"] == report["raw_counts"]["materials"] == report["raw_counts"]["mesh_nodes"] == 4)
    add_check(report, "core_has_10140_actual_triangles_and_51_markers", report["raw_counts"]["triangles"] == 10140 and sum(n["mesh_index"] is None for n in nodes) == 51)
    markers = {n["name"]: n["world_position_gltf_xyz_m"] for n in nodes if n["name"].startswith("DATUM_landing_")}
    expected_names = {f"DATUM_landing_{i+1:02d}" for i in range(17)}
    add_check(report, "exactly_17_landing_markers", set(markers) == expected_names, markers)
    add_check(report, "landing_marker_heights_match_all_17_floors", set(markers) == expected_names and all(abs(markers[f"DATUM_landing_{i+1:02d}"][1] - y) < TOL for i, y in enumerate(FLOORS)))
    lights = [n for n in nodes if n["name"].startswith("DATUM_light_")]
    add_check(report, "exactly_34_light_markers", len(lights) == 34, [n["name"] for n in lights])
    bounds = np.asarray(report["bounds_gltf_xyz_m"])
    add_check(report, "overall_bounds_match_enclosure_and_end_guard_extensions", np.allclose(bounds, [[-7.88, -.24, -13.04], [7.88, 105.9, 20.04]], atol=TOL, rtol=0), bounds.tolist())

    ivory = triangles[materials == "ivory_enamel"]
    cap_evidence = []
    for y in [105.78, 105.9]:
        horizontal = ivory[np.all(np.abs(ivory[:, :, 1] - y) < TOL, axis=1)]
        # Coplanar wall and shaft top faces also occur at these heights. The
        # actual full-width/full-depth cap triangles have the four plan corners.
        at_x_edge = np.abs(np.abs(horizontal[:, :, 0]) - 7.88) < TOL
        at_z_edge = (np.abs(horizontal[:, :, 2] + 13) < TOL) | (np.abs(horizontal[:, :, 2] - 20) < TOL)
        cap = horizontal[np.all(at_x_edge & at_z_edge, axis=1)]
        area = surface_in_box(cap, [-7.881, y - TOL, -13.001], [7.881, y + TOL, 20.001])
        area["y_m"] = y
        area["full_plan_corner_triangles"] = len(cap)
        area["other_coplanar_wall_shaft_triangles_excluded"] = len(horizontal) - len(cap)
        cap_evidence.append(area)
    add_check(report, "top_cap_has_full_15_76_by_33_faces_at_105_78_and_105_9", all(e["full_plan_corner_triangles"] == 2 and abs(e["clipped_surface_m2"] - 15.76 * 33) < .003 for e in cap_evidence), cap_evidence)

    side_checks = []
    for level, floor in enumerate(FLOORS):
        for side in [-1, 1]:
            portal = level in [0, 1] and side == -1
            x0, x1 = sorted([side * 7.60, side * 7.90])
            opening = surface_in_box(triangles, [x0, floor + .001, -2.999], [x1, floor + 3.199, 2.999])
            # Full outer wall plane area proves that the absent six metres have
            # not become a convex filled face, and intact levels are continuous.
            outer = ivory[np.all(np.abs(ivory[:, :, 0] - side * 7.88) < TOL, axis=1)]
            outer_area = surface_in_box(outer, [x0, floor + .01, -13], [x1, floor + 3.19, 20])["clipped_surface_m2"]
            expected_area = (27 if portal else 33) * 3.18
            probes = []
            for z in [-2.99, -1.27, 0, 1.63, 2.99]:
                for dy in [.4, 1.57, 3.19]:
                    hit = ray_hits(triangles, [side * 7.59, floor + dy, z], [side, 0, 0], .32)
                    probes.append({"z_m": z, "height_above_floor_m": dy, "distances_m": hit})
            lintel_hits = ray_hits(ivory, [side * 7.70, floor + 3.201, 0], [side, 0, 0], .2)
            flank_hits = [ray_hits(ivory, [side * 7.70, floor + .4, z], [side, 0, 0], .2) for z in [-3.001, 3.001]]
            row = {"level_index": level, "floor_y_m": floor, "side": side, "expected_portal": portal,
                   "opening_box_surface": opening, "outer_wall_plane_area_m2": outer_area,
                   "expected_outer_wall_plane_area_m2": expected_area, "ray_probes": probes,
                   "lintel_probe_hits": lintel_hits, "flank_probe_hits": flank_hits}
            passed = abs(outer_area - expected_area) < .003 and bool(lintel_hits) and all(bool(x) for x in flank_hits)
            if portal:
                passed &= opening["intersecting_triangles"] == 0 and all(not p["distances_m"] for p in probes)
                jambs = []
                for z_edge in [-3, 3]:
                    jamb = ivory[np.all(np.abs(ivory[:, :, 2] - z_edge) < TOL, axis=1)]
                    jambs.append(surface_in_box(jamb, [x0, floor, z_edge - TOL], [x1, floor + 3.2, z_edge + TOL]))
                lintel = ivory[np.all(np.abs(ivory[:, :, 1] - (floor + 3.2)) < TOL, axis=1)]
                lintel_area = surface_in_box(lintel, [x0, floor + 3.2 - TOL, -3], [x1, floor + 3.2 + TOL, 3])
                row["exact_z_minus3_plus3_jamb_surfaces"] = jambs
                row["exact_floor_plus3_2_lintel_underside"] = lintel_area
                passed &= all(abs(e["clipped_surface_m2"] - .16 * 3.2) < .0001 for e in jambs)
                passed &= abs(lintel_area["clipped_surface_m2"] - .16 * 6) < .0001
                walnut = triangles[materials == "warm_walnut"]
                dado_left = surface_in_box(walnut, [x0, floor + .121, -3.05], [x1, floor + .779, -3.001])
                dado_right = surface_in_box(walnut, [x0, floor + .121, 3.001], [x1, floor + .779, 3.05])
                row["dado_flank_surfaces"] = [dado_left, dado_right]
                passed &= all(e["intersecting_triangles"] > 0 for e in [dado_left, dado_right])
            else:
                passed &= opening["intersecting_triangles"] > 0 and all(bool(p["distances_m"]) for p in probes)
            row["passed"] = bool(passed)
            side_checks.append(row)
    report["sidewall_surface_checks"] = side_checks
    add_check(report, "only_port_D01_D02_have_6m_by_3_2m_lateral_openings_and_no_dado_bridge", all(r["passed"] for r in side_checks if r["expected_portal"]))
    add_check(report, "starboard_all_levels_and_port_D03_D17_are_continuous", all(r["passed"] for r in side_checks if not r["expected_portal"]))

    ends = []
    metal = triangles[materials == "champagne_metal"]
    for level, floor in enumerate(FLOORS):
        for z in [-13, 20]:
            central = surface_in_box(triangles, [-3.999, floor + .001, z - .045], [3.999, floor + 3.199, z + .045])
            wings = []
            for a, b in [(-7.8, -4), (4, 7.8)]:
                area = surface_in_box(metal, [a, floor + 1.061, z - .045], [b, floor + 1.139, z + .045])
                wings.append(area)
            passed = central["intersecting_triangles"] == 0 and all(w["intersecting_triangles"] > 0 for w in wings)
            ends.append({"level_index": level, "z_m": z, "central_8m_opening": central, "wing_guard_surfaces": wings, "passed": passed})
    report["end_spine_surface_checks"] = ends
    add_check(report, "both_8m_spine_openings_and_both_wing_guards_exist_every_level", all(r["passed"] for r in ends))

    # The negative control is an artificial wall triangle that crosses a portal
    # although none of its vertices lies inside that portal's small inner box.
    artificial = np.array([[[-7.88, 0, -4], [-7.88, 4, 0], [-7.88, 0, 4]]], dtype=float)
    negative = surface_in_box(artificial, [-7.89, 1, -.25], [-7.87, 2, .25])
    add_check(report, "surface_clipper_detects_convex_bridge_negative_control", negative["clipped_surface_m2"] > .1, negative)
    return report


def verify_cabin():
    path = ROOT / "assets/commons_lift_cabin/exports/AST-CIR-003_seventeen_stop.glb"
    report, triangles, materials, nodes = base_report(path)
    buttons = [n for n in nodes if n["name"].startswith("DATUM_floor_button_")]
    names = [n["name"] for n in buttons]
    expected = {f"DATUM_floor_button_{i}" for i in range(17)}
    add_check(report, "exactly_markers_0_through_16_without_17", len(names) == 17 and set(names) == expected, buttons)
    positions = [tuple(np.round(n["world_position_gltf_xyz_m"], 6)) for n in buttons]
    add_check(report, "all_17_button_positions_distinct", len(set(positions)) == 17)
    add_check(report, "seven_material_batches", report["raw_counts"]["meshes"] == report["raw_counts"]["materials"] == report["raw_counts"]["mesh_nodes"] == 7)
    add_check(report, "cabin_has_312_actual_triangles", report["raw_counts"]["triangles"] == 312)
    add_check(report, "cabin_bounds_match_4m_width_3_6m_depth_and_3_12m_height", np.allclose(report["bounds_gltf_xyz_m"], [[-2, -.18, -3.6], [2, 2.94, 0]], atol=TOL, rtol=0))
    # The front opening remains a clear passage at standing body height.
    doorway = surface_in_box(triangles, [-1.87, .01, -.13], [1.87, 2.62, .01])
    add_check(report, "material_batches_preserve_open_cabin_threshold", doorway["intersecting_triangles"] == 0, doorway)
    add_check(report, "extra_button_17_negative_control_is_rejected", set(names + ["DATUM_floor_button_17"]) != expected)
    return report


def main():
    reports = [(verify_forward(), ROOT / "assets/primary_atrium_core/qa/forward_core_glb_bytes.json"),
               (verify_cabin(), ROOT / "assets/commons_lift_cabin/qa/seventeen_stop_glb_bytes.json")]
    for report, path in reports:
        report["all_checks_passed"] = all(c["passed"] for c in report["checks"])
        report["failed_checks"] = [c["check"] for c in report["checks"] if not c["passed"]]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"asset": report["asset"], "counts": report["raw_counts"], "passed": report["all_checks_passed"], "failed": report["failed_checks"], "report": str(path.relative_to(ROOT))}))
    return 0 if all(r[0]["all_checks_passed"] for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
