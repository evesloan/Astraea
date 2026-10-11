# Group 7 finite terminal/body seams — integration and engineering held

This additive source package continues independently verified checkpoint `9a32693e9ce5b5e7d86a12fb85d558dafba9cfb8`. Main, shared ship root and registries are not edited. The baseline, every prior source/native/export, protected luxury roofs, room IDs, capacity and aft crown sitting bays/lights are retained. Newer Group1 main `bc731d6d6d54bb2595331ee2f4368558d4d24fda` was read only: its actual foyer and Star Atlas GLB bounds are separate from both terminal seam windows.

## Implemented

The selected editable native is `source/natives/G7_FiniteSeams_r004b.blend`: 64 closed authored parts, four fresh spatial export cells and 800 triangles. Four continuous corner weather spines cover Y61..106.5 at Z±510, with fitted lower-terminal and upper-headwall sections. They preserve the retained exterior profiles and bridge finite source material at both body and terminal receivers. Headwall foot/head roof laps tie these spines to the exact retained wing roof, headwall grid and exterior head-band source. Exposed upper laps rise 60mm above the source roof tops; original roofs are unchanged.

Two D18 landing assemblies join the raised neck to its retained headwall feet and cap through additive jambs, headers and roof laps. The central protected route X±4 and original open neck aperture X±6 stay clear: new jamb inner faces are X±6.4, and the lowest new central overhead is Y110.3, 3.8m above the original Y106.5 floor. The cap extends only 0.7m into the main body. This does not close the remaining body-route roof toward the crown.

The four models append to the existing Group7 opt-in runtime data, bringing its model count to 78. The previous 74 model definitions, four original doors, nineteen light definitions, IDs, source transforms and eight-source shadow budget remain unchanged. No new floor, room, capacity, door or light is introduced.

## Source receiving contracts

`docs/SEAM_PLAN.json` pins the exact sources and scopes all vertices. `qa/ACTUAL_RECEIVERS.json` records actual r003 native receiver meshes and retained terminal source records corroborated against decoded immutable GLBs. The retained terminal natives use `BLENDER17-01v0501`, unsupported by the provided Blender4.3.2; their hashes and files are retained without conversion or resave. Their recorded receiver vertices are matched to the actual exported geometry. The compatibility failure and first survey syntax failure are retained.

`qa/SEAM_SECTION_CHECK.json` passes 756 finite horizontal contacts and shared spine-plane checks, including sections around source tile/joint heights. New weather joints contact both original body and terminal material; each successive spine segment has nonzero common contact area. These are geometric receiving and material-continuity results. They do not establish pressure integrity, joint detailing, corrosion/drainage specification, primary load paths, receiver strength or capacity.

`qa/MIDDLE_FRAME_SEAT_CHECK.json` independently decodes the retained middle-frame GLBs. All four new lower weather feet meet actual Y61 horizontal head faces, with contact areas0.41766..0.43008m². `docs/RECEIVING_INTERFACES.json` names the actual source receivers for all64 new parts and the four lower seats. This completes the local geometric receiving contract; downstream primary load/capacity evidence is still held.

The independent native audit passes 3,834 checks: all 64 parts are closed/manifold with positive volume, finite UVs and nonzero triangles; original packed texture bytes are exact. All four fresh GLBs decode independently, retain embedded images and match native positions within0.1mm. The selected native is not resaved during audit/export. `qa/RUNTIME_CHECK.json` passes241 focused actual-main checks, including imported new static contacts, retained74 model definitions/hashes and door/light definitions, D18 floor/capsule/headroom probes, and four normal-player legs across the two joins. Two explicit terminal fixtures seed those walks; there are no position writes between legs. Targeted new-mesh rays exclude overlapping retained candidate collider RIDs to identify the new shapes; ordinary route/floor/capsule and walking collision excludes none and is unchanged. Both earlier held runs also retain their valid four-leg walking records. The initial nominal-position misses and subsequent retained-receiver first hits are recorded, not erased.

## Integration

The existing `group7_completion.gd` opt-in call is unchanged. Shared activation remains owned by construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b`:

1. Verify the branch manifest and exact source pins; preserve newer Group1 and protected roof work. Adopt only owned additions and the updated owned `GROUP7_COMPLETION.json`.
2. Install the Group7 opt-in once after `ShipSpace/Districts` and `ShipSystems` exist, preferably before lighting-budget configuration. The existing call is `load("res://scripts/group7_completion.gd").build(self)`. Never install old R002 model variants or retained prior cells twice.
   Restart the review scene after updating model data: the idempotent call preserves an existing candidate and does not hot-append new cells.
3. Do not register collar/cap laps as compiler floors or change any room/capacity registry. Run `godot --headless --path Game --script res://tests/group7_finite_seams_check.gd` for this changed work. Its scene starts from the pinned baseline and explicitly adds the candidate; adapt the fixture if shared main already installs it.
4. Review actual graphical source/game appearance and shared-current-main route/roof interfaces before final adoption. Source contact proof is not engineering acceptance.

## Remaining

Local finite terminal/body weather contacts are constructed and tested. Full bodywide enclosure, conservative held source fields, interior roof closure, the remainder of the D18 route-to-crown roof, protected house/crown joins, complete primary support paths/capacity, the D02–D17 botanical hierarchy, inhabited gameplay and final graphical/CRT/hardware art remain open. Group7 is not accepted as a whole.

The Star Atlas13.2m transfer is explicitly held. The earlier source-rooted proposal at Z33.10/Z39.00 remains a coordination envelope, not built or activated primary structure and not evidence of capacity.

## Evidence retention and screenshot

The first seam native `G7_FiniteSeams_r004.blend` and its plan/source/contact receipts remain unselected revision evidence. Its geometry checks passed their stated scope; the selected revision adds the exposed roof-lap allowance. No original revision is overwritten.

The existing clear whole-body R003 source screenshot is saved in Library as `libfile_fd250e2280048191818dda2e342fc70b`, file `file_000000000eec81f7b8db6def538d2eff`. SHA256 `49b2806a2cc7e3b72ac2c1287719b73925843a85629e89ff3c7936a671b943ec`. No new render was launched for reporting. It depicts the prior whole-body construction context, not these newly authored R004 seams. R004 visual/final-art acceptance remains open.
