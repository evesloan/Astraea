# Group 4 steering, terminal protection and source travel

Additive construction following independently retained `943c20d694e405a4deac54e62cbede05c71bc183`. Original source011/024 bodies, source016 guideway, stations, protected six-point bypass, source019 bridge, original four wheel meshes, all prior revisions and shared Game source remain immutable. Source28/29 IDs are locally reserved and unregistered. Production, north-stop and shared-pit adoption flags remain false. This is a checkpoint in the continuing Group4 programme, not whole-group completion.

## Physical construction

`Group4_Steering_Bogies_and_EndBuffers_r002.blend` contains46 editable closed meshes. Source028 has28 fixed floor/slide receivers, steering truck frames, axle/bearing and bounded sliding-bolster parts. The four original source024 wheels are reused at runtime, never exported or duplicated. Original3m kingpin chord,1.72m gauge,0.16m nominal wheel radius, standing floorY56.1 and rail headY55.74 stay unchanged. Source029 has18 terminal buffer feet/columns/crossheads/rubber pads positively received into the retained guideway web. Ordinary body travel stops at Z±462, inside the original rail endpoints±466. Impact absorption, mechanical/hull load capacity and species requirements remain unaccepted.

The exact source route has379 points and1003.703093m length. Source-bound fitting contains9964 poses. The immutable central dock requires a rear truck traverse of0.17446m; the complete selected approach stays below0.18104m within a0.20m source fitting. A rejected4m alignment blend demanded0.34436m and is retained. The selected0.5m alignment pocket and bidirectional acceleration/braking profile keep the body at its original central X0/Z−72/yaw0 while both trucks follow the original rail references. This does not certify the sliding bearing, wheel forces, fatigue or loaded dynamics.

`group4_tram_source_actuator.gd` is one optional actuator on one root-supplied `AnimatableBody3D`, with a duplicate-motor guard and external-pose fault detection. It has no input handler, cart/product spawn, guest simulation, global transport controller or shared registration. Existing root controls may call `request_stop` or `request_distance`. Its standalone vehicle factory is for construction tests. It refuses movement while original source door/bridge clearance is unavailable and respects protected terminal limits. Default production build is refused until active, north adoption and pit adoption are all explicitly satisfied by the shared owner.

## Corrected physical representations

The published bridge adapter's initial `fraction0` did not establish a physical stow: synchronized initialization left the panel horizontal. `group4_bridge_pose_diagnostic.json` and `BRIDGE_POSE_DIAGNOSTIC001.log` read the actual PhysicsServer transforms. `initialize_bridge_physics(safety)` applies the proper original source019 rotation during empty, closed construction assembly and uses manual physics-step transforms. **Apply this instance correction even when adopting only boarding, before admitting a player/cart.** It asserts empty thresholds; it is not a repair to perform during occupancy. Original source and published scripts are untouched. The former initial-stow-only acceptance is superseded; source state/fraction checks alone are insufficient.

The original car's fixed gate frames are hollow compound geometry. Whole-frame convex hulls would fill the doorway; concave-vs-concave queries are unsupported by the installed physics engine. `prepare_gate_contacts.py` proves nine closed convex original components per gate with126 checks. The actuator uses the **exact existing runtime face vertices** for18 contact components across both original portals. Every original contact vertex is bit-identical (maximum error0); no bounding-box fill or looser tolerance is used. A separately recomputed global-to-local candidate differed97.16µm and is retained as rejected. Source meshes/materials and the original `lift_gate.gd` remain unchanged.

## Evidence and limits

- Geometry: **20,054** checks against actual exports and pose data.46 meshes /648 triangles total; correct kingpins, closed/nondegenerate geometry, original source pins, guideway receivers and protected lower axis/headroom.
- Native: **146** checks, all46 closed editable meshes, original UV/material bindings, two byte-identical fresh native re-exports.
- Material: **46** exact original graph/packed-texture/interpolation/color-space bindings.
- Accepted `TRAVEL_RUN007.log`: **120,614** checks without engine/script errors or warnings. One source car completes **1991.406187m** of uninterrupted unloaded bidirectional travel between the safe terminal limits, five unchanged dock alignments, pause, a travelled central bridge/door sequence and motor departure refusal while open. **676** nominal wheel-reference rays hit the real rail; **26,533** actual car-shape contact samples pass. Original four wheels remain reused. These are kinematic source tests, not friction/traction or arbitrary-speed impact tests.
- Two1920×1080 actual Godot Compatibility source views: [terminal buffer and station context](SOURCE_GAME_G4_TERMINAL_BUFFER_WIDE003.png), [steering corner and retained receiving frame](SOURCE_GAME_G4_STEERING_CORNER_WIDE002.png). They show original D09 floor/public-core sources and the selected guideway/station assembly without hiding/cutting geometry. Review lighting, static pose relocation and software OpenGL are disclosed. The car floor naturally occludes some small fittings; native/physical evidence is separate. Ordinary-main lighting, CRT and hardware/final art remain open. Failed exposure/crop/renderer attempts are retained.

The two source-game images are saved to Library as `libfile_6e764d644d308191b1039d83f3a28400` and `libfile_6819f85480288191b4df309b41f42db8`; exact metadata/byte hashes are in `LIBRARY_SCREENSHOT_DELIVERY.json`. Prior four Library image identities remain in `../boarding_safety_009/LIBRARY_SCREENSHOT_DELIVERY.json`.

## Integration and continuing obligations

Group1/shared integration thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b` owns activation, registry and root/compiler adoption. See the previous complete16-item checklist and the new scoped `../floor_receiving_patch_013/GROUP4_FLOOR_RECEIVING_PATCH.json`: four required pits, **three exact replacement floor owners**,24.8m² total. It includes exact region preimages, triangles/rings/render chunks and retains the protected4m axis and six-point bypass. Shared source is not edited here. The north physical dock−241 remains a distinct adoption hold; historical `FORE_MIDSHIP`/catchment−216 are stable.

Only after the owner verifies actual current receiving, explicit stop adoption and source/registry preimages may it supply the single canonical body and connect its existing controls to the actuator. Assemble `group4_completion.gd` and `group4_boarding_safety.gd`, apply the initial physical-stow correction, then attach this one actuator. The supplied motor predicate is **unloaded**. Loaded cart restraint/carry/release, original player carry, original E/RMB boarding, stock/consumption/save continuity, NPC finite-time transit, engineering/species and ordinary-main acceptance still require work and evidence. No extra cart or product exists in this fixture.

Group8's exact theater receiving contract is retained at `3bb45e93776919e458d5d85903e3a73c242f2178`; Group4 continues exterior approaches against its actual interfaces while protected interior/door/source ownership stays with Group8. Remaining neighborhood/destination/service joins retain their actual source-owner boundaries. The103 missing precise portals in the bounded received-section dataset are an input gap, not103 absent buildings. Neither indexing nor floor-component screening completes those routes.

Reproduction uses the unchanged installed Blender4.3.2 and Godot4.6.3 environment:

```sh
source /workspace/astraea-env/activate.sh
python BlenderCatalogue/assets/group4_completion_20261011/travel_hardware_012/audit_geometry.py
blender -b --threads 1 --python BlenderCatalogue/assets/group4_completion_20261011/travel_hardware_012/audit_native.py
blender -b --threads 1 --python BlenderCatalogue/assets/group4_completion_20261011/travel_hardware_012/audit_materials.py
godot --headless --path Game --fixed-fps 60 --script res://tests/validate_group4_source_travel.gd
```

Refresh new imports in a clean worktree first. Captures use the existing Xorg dummy driver with a temporary private display, no installation/credential/permission changes, and process-local Dummy audio. A successful source run never overrides an engine error/warning from a retained failed attempt. The full suite and normal production tram are not claimed. Continue construction and acceptance after this checkpoint; Group4 remains unfinished.
