#!/usr/bin/env python3
"""Read installed Game and emit SCRATCH patches/proofs/routes only.
This must be rerun/reviewed against the post-theater bytes before adoption.
"""
from pathlib import Path
import copy,difflib,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
V2=ROOT.parent/'engineering-harmless-controls-labels-v2-20261006'
REV='engineering_controls_runtime_v3_20261006'
LISTENER_LINE='\tworld_view.audio_listener_enable_3d = true\n'
LISTENER_ANCHOR='\tworld_view.own_world_3d = true\n'
BUILD_LINE='\tload("res://scripts/engineering_calibration_builder.gd").build(wrapper,visual,ship)\n'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def emit(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def patch(path,before,after):
    (ROOT/'integration'/path).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+('scripts/presentation.gd' if 'listener' in path else 'scripts/secondary_engineering_cell.gd'),tofile='b/'+('scripts/presentation.gd' if 'listener' in path else 'scripts/secondary_engineering_cell.gd'))))
def main():
    pins= json.loads((ROOT/'provenance/labels_v2_bundle_hashes.json').read_text())
    for path,h in pins['files'].items():assert sha(V2/path)==h,path
    head=subprocess.check_output(['git','-C',str(GAME),'rev-parse','HEAD'],text=True).strip()
    presentation=(GAME/'scripts/presentation.gd').read_text();cell=(GAME/'scripts/secondary_engineering_cell.gd').read_text()
    assert presentation.count(LISTENER_ANCHOR)==1 and LISTENER_LINE not in presentation
    assert cell.endswith('\treturn data\n') and BUILD_LINE not in cell
    new_presentation=presentation.replace(LISTENER_ANCHOR,LISTENER_ANCHOR+LISTENER_LINE)
    new_cell=cell[:-len('\treturn data\n')]+BUILD_LINE+'\treturn data\n'
    assert new_presentation.replace(LISTENER_LINE,'')==presentation
    assert new_cell.replace(BUILD_LINE,'')==cell
    patch('presentation_listener_prerequisite.patch',presentation,new_presentation)
    patch('secondary_engineering_cell_controls.patch',cell,new_cell)
    # Future integration snapshots are SCRATCH evidence, not live replacements.
    (ROOT/'integration/presentation.listener_candidate.gd').write_text(new_presentation)
    (ROOT/'integration/secondary_engineering_cell.controls_candidate.gd').write_text(new_cell)
    chain=json.loads((GAME/'docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json').read_text())
    successor=chain['explicit_runtime_pin_successors']['scripts/presentation.gd']
    assert digest(presentation)==successor['section_sha256'], 'Unknown presentation successor; parent review required, do not reset predecessor pins.'
    proof={'revision':REV,'status':'DRAFT_FOR_POST_THEATER_REBASE_AND_PARENT_REVIEW','adoption_approved':False,
        'base_game_head':head,'target':'scripts/presentation.gd','historical_caller_sha256':successor['historical_sha256'],
        'predecessor_sha256':digest(presentation),'candidate_sha256':digest(new_presentation),
        'original_section_predecessor_sha256':successor['section_sha256'],
        'exact_added_line':LISTENER_LINE,'anchor_line':LISTENER_ANCHOR,'exact_addition_count':1,
        'all_other_bytes_restored_by_reversal':True,
        'shared_guard_action':'After existing section-byte case, before theater-only path allowlist, call separate exact listener successor guard. Do not replace historical callers or theater/floor proofs.',
        'listener_scope':'3D audio in existing World360 only; no bus/gain/UI/input/camera change','listening_accepted':False}
    emit(ROOT/'docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json',proof)
    d=json.loads((V2/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text())
    d['runtime_revision']=REV
    d['runtime_prerequisites']={'base_game_head':head,'post_theater_rebase_required':True,'deferred_original_player_binding':True,
        'actor_path_from_ship':'ShipSpace/PersistentActors/Player','viewport_name':'World360','audio_listener_enable_3d_required':True,
        'camera_voice_same_viewport_and_world_required':True,'actual_engine_checks':'UNRUN','listening_accepted':False}
    emit(ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json',d)
    by_panel={}
    for row in d['controls']:by_panel.setdefault(row['panel'],[]).append(row)
    # Explicit waypoints inherit the successfully checked staff circulation spine.
    # New panel connections are still candidates pending ordinary-player walking.
    control_order=['C1L','C1R','C2L','C2R','C3L','C3R']
    segments=[]
    for i,panel in enumerate(control_order):
        first=by_panel[panel][0]['proposed_approach_xyz'];segments.append({'panel':panel,'waypoints_xyz':[[30,6,-461.475]] if i==0 else [],'first_approach_xyz':first})
    spine=[[30,6,-459],[30,6,-452.8],[38,6,-452.8],[38,6,-445],[45.5,6,-445],[45.5,6,-432],[51,6,-432],[51,6,-411.2],[30,6,-411.2],[30,6,-407.7],[25.26,6,-407.7]]
    for panel,waypoints in [
        ('TEST_RACK_REMOTE_R',spine),
        ('TEST_RACK_REMOTE_L',[]),
        ('MORALE',[[23.76,6,-407.7],[28.6,6,-407.7],[28.6,6,-402.624]]),
        ('SCOPE',[[28.2,6,-402.624],[25,6,-402.624]])]:
        segments.append({'panel':panel,'waypoints_xyz':waypoints,'first_approach_xyz':by_panel[panel][0]['proposed_approach_xyz']})
    route={'revision':REV,'status':'FULL_SCENE_WALK_UNRUN','initial_supported_arrival_xyz':[30,6,-459],
        'allowed_diagnostic_arrivals':1,'floor_owner':'D02_secondary_engineering_floor','segments':segments,
        'source_route_reference':'tests/validate_secondary_engineering_cell.gd::retained_routes',
        'source_route_reference_sha256':sha(GAME/'tests/validate_secondary_engineering_cell.gd'),
        'source_screen_revision':'002: north-side shelf detour at z-407.7 and east turn x28.6; failed 001 retained',
        'connection_claim':'The staff spine has prior actual-world proof; new panel-to-panel links must pass this candidate original-player run. No source-only ray result substitutes for them.'}
    emit(ROOT/'data/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json',route)
    watched=['scripts/presentation.gd','scripts/secondary_engineering_cell.gd','scripts/player.gd','scripts/physics_tether.gd','scripts/service_door.gd','scripts/engineering_cell_gate.gd','scripts/engineering_cell_gate_target.gd','scripts/lighting_budget.gd','scripts/commons_lift.gd','scripts/lift_button.gd','scripts/lift_gate.gd','scripts/ship.gd','tests/secondary_engineering_additive_guard.gd','docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json']
    emit(ROOT/'reports/runtime_v3_preflight.json',{'revision':REV,'base_game_head':head,'base_pins':{p:sha(GAME/p) for p in watched},
        'candidate_modified_game_files':{'scripts/presentation.gd':digest(new_presentation),'scripts/secondary_engineering_cell.gd':digest(new_cell)},
        'listener_proof_sha256':sha(ROOT/'docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json'),
        'game_writes':False,'engines_run':False,'imports':False,'legacy_guard_modified':False,
        'post_theater_rebase_required':True,'original_labels_and_audio_unchanged':True})
    print('Prepared scratch-only runtime v3 patches, separate listener proof and connected route candidate from',head)
if __name__=='__main__':main()
