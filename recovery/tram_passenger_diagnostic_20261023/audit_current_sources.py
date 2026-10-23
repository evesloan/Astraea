#!/usr/bin/env python3
"""Read-only source inspection. Does not import Godot, simulate, launch or edit Game.

Writes this candidate's JSON evidence only. The PCK is used as a retained byte
store, not as authority: each selected model must match the CURRENT plan hash.
"""
import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
GAME = BASE / "recovery-only-current-448eab12/Game"
COMMIT = "448eab129169f3c205e7db0662fcf774b869a346"
PINS = {}
for name in ("CURRENT_SCRIPTS_RECOVERY", "CURRENT_SCENES_RECOVERY", "CURRENT_GAME_ROOT_RECOVERY"):
    for item in json.loads((BASE / f"recovery_inventory/{name}.json").read_text()):
        PINS[item["repository_path"]] = item["git_blob_sha1"]
for line in (BASE / "acquisition/current-gap-files/acquisition-ledger.jsonl").read_text().splitlines():
    item = json.loads(line)
    if item.get("status") == "verified" and item.get("commit") == COMMIT:
        for path in item["paths"]:
            PINS[path] = item["observed"]["git_blob_sha1"]


def inspect(path):
    data = (GAME / path).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    expected = PINS.get("Game/" + path)
    assert expected == blob, (path, expected, blob)
    return {"path": "Game/" + path, "bytes": len(data), "git_blob_sha1": blob,
            "sha256": hashlib.sha256(data).hexdigest(), "current_git_verified": True}


def read(path):
    inspect(path)
    return (GAME / path).read_text()


def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    entry = ["project.godot", "scenes/bootstrap_star_atlas_living_20261022.tscn",
             "scripts/star_atlas_living_integration_20261022/bootstrap.gd",
             "scenes/launcher_star_atlas_living_20261022.tscn",
             "scripts/star_atlas_living_integration_20261022/launcher.gd",
             "scenes/main_star_atlas_living_20261022.tscn",
             "scripts/star_atlas_living_integration_20261022/presentation.gd",
             "scenes/ship_star_atlas_living_20261022.tscn",
             "scripts/delivery_shell_20261022/settings.gd"]
    chain = []
    path = "scripts/star_atlas_living_integration_20261022/ship.gd"
    while True:
        chain.append(path)
        match = re.match(r'extends\s+"res://([^"]+)"', read(path))
        if not match:
            break
        path = match[1]
        assert path not in chain
    focused = ["scripts/group4_integrated_receiving.gd", "scripts/group4_boarding_safety.gd",
               "scripts/group4_cart_restraint.gd", "scripts/group4_tram_source_actuator.gd",
               "scripts/group4_loaded_tram_actuator.gd", "scripts/group4_tram_operating_controls.gd",
               "scripts/player.gd", "scripts/group6_swimming_20261019/player.gd",
               "scripts/group6_float_20261019/player.gd",
               "scripts/group6_completion/player_water_seat_20261019.gd",
               "scripts/cleaning_cart.gd", "tests/validate_group4_source_travel.gd",
               "tests/validate_group4_received_player.gd", "tests/group4_exact_pit_successor_guard.gd",
               "tests/validate_group4_completion_candidate.gd", "tests/validate_atrium_supports.gd", "data/spatial_layout.json",
               "data/generated/structural_meshes.json", "docs/WHOLE_SHIP_SECTION_COORDINATION.md",
               "docs/master_source/MASTER_CURRENT_APPLICATION.json",
               "docs/master_source/MASTER_FULL_CONTENT_INDEX.json"]
    names = ["TRAVEL_SOURCE", "BOARDING_SAFETY", "COMPLETION", "LOADED_CART_SOURCE", "OPERATING_CONTROLS_SOURCE"]
    plans = {}
    for name in names:
        path = f"data/architecture/GROUP4_{name}_CANDIDATE.json"
        focused.append(path)
        plans[name] = json.loads(read(path))
    travel = plans["TRAVEL_SOURCE"]
    pose_path = travel["pose_file"].removeprefix("res://")
    pose_bytes = (GAME / pose_path).read_bytes()
    assert hashlib.sha256(pose_bytes).hexdigest() == travel["pose_sha256"]
    poses = json.loads(pose_bytes)
    assert all(len(row) == 11 and all(math.isfinite(v) for v in row) for row in poses)
    assert all(a[0] < b[0] for a, b in zip(poses, poses[1:]))
    assert [poses[0][0], poses[-1][0]] == travel["safe_body_cursor_range_m"]
    stops = sorted(travel["stops"], key=lambda stop: stop["distance_m"])
    stop_checks = []
    for stop in stops:
        distance = stop["distance_m"]
        a, b = next((a, b) for a, b in zip(poses, poses[1:]) if a[0] <= distance <= b[0])
        weight = (distance - a[0]) / (b[0] - a[0])
        xyz = [a[1] + weight * (b[1] - a[1]), 56.1, a[2] + weight * (b[2] - a[2])]
        error = math.dist(xyz, stop["world_xyz"])
        assert error < 0.005
        stop_checks.append({"station": stop["station"], "distance_m": distance,
                            "world_xyz": stop["world_xyz"], "interpolated_error_m": error})
    focused.extend([pose_path, travel["gate_contacts_file"].removeprefix("res://")])
    if (GAME / "data/design_contract.json").exists():
        focused.append("data/design_contract.json")
    script_tree = json.loads((BASE / "recovery_inventory/metadata/CURRENT_SCRIPTS_TREE.json").read_text())
    assert not script_tree["truncated"]
    source_files = [inspect(path) for path in dict.fromkeys(entry + chain + focused)]
    save("CURRENT_SOURCE_EVIDENCE.json", {
        "repository": "evesloan/Astraea", "commit": COMMIT,
        "selected_entry_chain": entry, "ship_inheritance_chain": chain,
        "current_scripts_tree_sha": script_tree["sha"], "scripts_tree_entry_count": len(script_tree["tree"]),
        "scripts_tree_truncated": False,
        "director_named_paths": [x["path"] for x in script_tree["tree"] if "director" in x["path"].lower()],
        "files": source_files,
        "scope": "Exact source/content evidence only; no runtime, collision, passenger, renderer or benchmark acceptance."
    })
    index = json.loads((BASE / "acquisition/PCK_INDEX_e3af0334.json").read_text())
    models = []
    with open(index["path"], "rb") as pack:
        for name, plan in plans.items():
            base = plan.get("model_root", "res://source_derivatives/group4_completion_20261011/").removeprefix("res://")
            for model in plan.get("models", plan.get("exports", [])):
                path = base + model["file"]
                item = index["entries"][path]
                pack.seek(item["offset"])
                data = pack.read(item["bytes"])
                assert len(data) == item["bytes"]
                assert hashlib.sha256(data).hexdigest() == model["sha256"]
                models.append({"path": "Game/" + path, "sha256": model["sha256"], "bytes": len(data),
                               "authority": f"current GROUP4_{name}_CANDIDATE.json model pin",
                               "retained_pck_entry": path, "offset": item["offset"],
                               "raw_source_present": (GAME / path).exists(), "pck_bytes_match_current_pin": True})
    save("EXACT_MODEL_RECOVERY_INPUTS.json", {"commit": COMMIT, "models": models,
          "scope": "Read-only byte validation. No files acquired or written into Game. Native Blender sources are separate prerequisites."})
    save("ROUTE_FACTS.json", {
        "commit": COMMIT, "pose_sha256": travel["pose_sha256"], "pose_rows": len(poses),
        "pose_columns": travel["pose_columns"], "safe_cursor_range_m": travel["safe_body_cursor_range_m"],
        "route_total_m": travel["source_route_total_m"], "stops": stop_checks,
        "source_motion_scope": travel["motion_scope"], "closed_loop": False,
        "station_span_m": stops[-1]["distance_m"] - stops[0]["distance_m"],
        "full_out_and_back_m": 2 * (stops[-1]["distance_m"] - stops[0]["distance_m"]),
        "max_speed_m_s": travel["maximum_speed_m_s"], "acceleration_m_s2": travel["acceleration_m_s2"],
        "curve_cap_m_s": travel["curve_speed_cap_m_s"],
        "central_alignment_cap_m_s": travel["central_alignment_speed_cap_m_s"],
        "protected_central_polyline_xz": plans["COMPLETION"]["protected_polyline_xz"],
        "named_pit_cuts": plans["COMPLETION"]["shared_floor_cuts"],
        "runtime_executed": False, "passenger_carry_verified": False, "full_route_collision_verified": False,
        "benchmark_runnable": False
    })
    print(json.dumps({"current_files_hash_verified": len(source_files), "current_model_pins_matched_in_retained_pack": len(models),
                      "pose_rows_inspected": len(poses), "station_pose_checks": len(stop_checks), "runtime_executed": False}))


if __name__ == "__main__":
    main()
