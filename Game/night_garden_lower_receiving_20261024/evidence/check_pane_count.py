"""Close only the recorded pane-count expectation error; no engine or fixture."""
from pathlib import Path
import hashlib
import json

EVIDENCE = Path(__file__).resolve().parent
GAME = EVIDENCE.parents[1]


def main():
    decision = json.loads((EVIDENCE / "INTEGRATION_DECISION.json").read_text())
    for name, digest in decision["raw_evidence"].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name
    source = (GAME / "night_garden_lower_bank_20261022/PACKAGE.json").read_bytes()
    assert hashlib.sha256(source).hexdigest() == decision["source_package_sha256"]
    package = json.loads(source)
    observed = json.loads((EVIDENCE / "INTEGRATION.json").read_text())
    expected = sum(sum(part.get("category") == "window" for part in room["parts"])
                   for room in package["rooms"])
    # Same source-derived aggregate predicate as the corrected Godot check.
    rests = [identity for room in package["rooms"]
             for identity in room["allocation"]["proposed_rest_slot_ids"]]
    doors = [door["persistent_id"] for room in package["rooms"] for door in room["doors"]]
    assert len(set(rests)) == len(rests) == observed["reserved_rests"] == 19
    assert len(set(doors)) == len(doors) == observed["door_ids"] == 53
    assert expected == observed["privacy_panes"] == 26
    assert observed["failures"] == ["19rests53doors17privacy panes"]
    assert observed["status"] == "FAIL" and observed["checks"] == 456
    corrected = (GAME / "tests/validate_night_garden_lower_receiving_20261024.gd").read_text()
    assert 'windows==expected_windows' in corrected and 'windows==17' not in corrected
    assert 'part.get("category","")=="window"' in corrected
    result = {
        "status": "CORRECTED_PANE_COUNT_CHECK_PASS",
        "expected_from_protected_source": expected,
        "observed_in_preserved_actual_ship_run": observed["privacy_panes"],
        "reserved_rest_ids": 19, "unique_door_ids": 53,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "raw_runtime_result_unchanged": True,
        "raw_runtime_status": "FAIL", "raw_runtime_exit_code": 1,
        "new_runtime_run": False,
        "scope": "One source-derived aggregate count check, using preserved actual-ship observations. Not a new full-suite or visual pass.",
    }
    (EVIDENCE / "PANE_COUNT_CORRECTION_CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
