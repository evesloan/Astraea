# Group3 port2 physical riser and clinical transfer

Additive successor to retained Group3 commit `28e32333ba9c8c20aa673b1fa01812efc68c769e`. Frozen batches001..015, original rooms/IDs/capacities, D01 shared circulation and D04 neighborhood/riser3 work remain unchanged. Group3 remains unfinished.

## Implemented

Batch016 constructs 1,435.58m² of missing-only floors at the seventeen original port2 landing datums, including the bounded D05 clinical/header approach. It reuses the frozen port2 shaft and header, original seventeen-stop cabin, telescoping landing gates and four unscaled service doors. Twenty-six source fixture profiles use the existing light budget.

Five new native sources/exports:

- AST-STF-G3-030: seventeen missing-only landing floors. D05 also supports the original midship clean/used headers and bounded clinical street selection. Existing compiled floors and source sill footprints are excluded.
- AST-STF-G3-031: original-payload source assembly of seventeen landing gates, one cabin/cabin gate at D03 and four clinical service doors. No persistent identity is assigned. This static source assembly is omitted when original controllers are bound, preventing duplicate fittings.
- AST-STF-G3-032: exactly27 original riser native batch replacements. The other68 original batches remain unchanged. Tiny source notches provide2mm clearance around the original gate's3.84m upper trim. Seventeen call backings mount behind the actual original button spheres on the native gate-front skins, outside moving pockets. Total source shaft trim removal is0.004790464m³. Originals remain immutable.
- AST-MED-G3-005: missing-only head/side infills around the four actual service fittings, plus the1m roof-height closure between the original3.2m lobby and4.2m clinical header.
- AST-MED-G3-006: bounded clinical street geometry at X[−63.1,−53], Z[−312,−278], with the frozen port2 partial receiver successor. Only an additional22mm high frame-clearance cut is made at the four exact frame rectangles. The original ten clinical junctions and all other clinical source remain retained.

The original controller keeps its fixed-sill boxes. Fifty-one exact native-sill remainder contacts supplement those boxes without replacing them or duplicating contact ownership. No full requested floor is overlaid.

The scoped crossing supervisor sequences existing service-door lifecycles. It closes the other axis before opening clean or sealed-return passage, rejects mode changes while the buffer is occupied and rejects sealed return without an owner-supplied dispatch predicate. It supplies no inventory, sterilization or new transport simulation.

## Tested

- Independent native geometry:1,024 checks pass, including all five actual exports, upward floor faces, seventeen supported worker footprints, no previous-floor duplication at1mm precision, exact disclosed source sections, native batch omission/replacement agreement and mounted original-button geometry. Original fitting meshes retain their vertex/UV/material payloads and scale.
- Five fresh native exports repeat byte-identically.
- Staged actual main:7,178 checks pass. The original player calls, boards and rides port2 from D03 to D05 using normal RMB/E. Sixteen walk legs use the original controller, one initial fixture setup and zero subsequent position/velocity writes.
- All seventeen authored empty-cabin stop endpoints and landing/cabin gate interlocks pass.373 sampled empty-cabin motion poses check actual cabin contacts against fixed scene geometry. This is separate from the single player ride; it does not establish seventeen normal arrivals or loaded/species boarding.
- The player uses clean and sealed-return crossing gates with normal input. Opposing axes remain exclusive, and an occupied buffer blocks switching. The test uses a **synthetic sealed-load predicate** and temporary validation labels; these are not operational dispatch proof or authoritative persistent IDs. They are never saved or registered.

The full repository suite, loaded carts, species envelopes, clinical sterility, stock/returns, pressure/fire/egress, primary engineering, CRT and target-hardware acceptance remain open.

## Identity evidence and C036 proposal

The directly read archived `DesignArchive/Historical_Design/Editable_Source/project_docs/architecture/whole_ship_coverage.json` matches its recorded SHA256 `3b02b1fdea59ec9ddd7cb66e39bbcfbd6492e0d3e37647eeb6d38b3d370edefe` through independent remote baseline readback. It contains the original C001..C200 architectural room IDs:199 double-room capacity records and C036's singleton, plus the separate employee/player-home single, totaling400 historically. Historical implementation screens are not current gameplay acceptance.

That archive contains no concrete person/berth anchor keys, current save schema or atlas coordinates. The184 unresolved atlas joins remain held. Retained archive registry-pin files are asset-hash checks, not missing person/berth registries. The current Player node name is not a persistent person or berth key.

`source/C036_EXISTING_KEY_MIGRATION_PROPOSAL.json` supplies a fail-closed transaction proposal, exact original room evidence, source pins, preconditions, unchanged-key/count checks and rollback obligations. It preserves C036 and D03_employee_cabin0 and proposes moving only the existing C036 singleton's anchor/home association into the other compatible existing shared-home slot. It creates no key, actor, species assignment or current registry change. Concrete original records and suitability proof remain required.

## Owner integration contract

1. Apply only this successor's new scoped files after the retained28e32333 checkpoint. Shared ship root, catalogues, ledgers, floor compilers and prior manifests are untouched.
2. The builder is deliberately uncalled by the default ship root. `physical_package.gd.build(ship)` gives a closed static source preview. Operation requires a supplied dictionary containing an authoritative lift ID/prefix and all four gate IDs. No production defaults are provided. **Do not reuse the validation labels from the test as production IDs.**
3. Preserve source models and hashes. Do not overlay original riser batches listed in `riser_native_meshes_to_omit` with AST-STF-G3-032. The module omits exactly those27 native nodes and preserves the other68. Preserve original sill visuals and controller-owned contacts; supplement only the disclosed native remainders.
4. Do not overlay this bounded clinical selection with the full frozen clinical street source. Compose its selection, old port2 receiver omission contract and explicit22mm cuts into an owner-controlled full derivative when expanding. Keep all ten existing clinical junctions.
5. Recompute missing-only floors against the owner's current actual/compiler sources and support geometry before live adoption. The original D01 circuit and D04 riser3/routes remain separate. Port2 is centred at[−25,−283]; the existing D04 riser3 is at[−25,−90]. No D18 stop is added. Preserve original forward lift keys/stops, its46.2m wet datum and D04..D07 blank shaft rule.
6. Bind the existing commons lift with the exact seventeen-stop source, original canonical elevations and explicit gate origin. Bind real sealed-load dispatch validation to `ClinicalCrossing.sealed_load_ready` before enabling return traffic. The shared lift lobby and crossing remain sequential buffers; simultaneous segregation or sterile flow is not certified.
7. Run `Game/tests/group3_port2_clinical_20261011/validate_physical.gd` on staged actual main under an external600-second timeout. Inspect its receipt in `Game/artifacts/group3_port2_clinical_20261011/physical.json`. Revalidate changed source/scene dependencies and keep full-group acceptance false.

## Visual and remaining acceptance

The existing clear wide crew source screenshot is reused for user delivery: Library `libfile_8ac946a9b5c48191baafa859c0e97bfd`. No reporting-only render was made. This new riser/clinical package has geometric and in-game physics/input evidence, but has not had graphical visual acceptance. Final normal-game source composition, lighting, CRT and hardware review remain unfinished.

Six other wholly unbuilt reservations, the first-starboard source adoption/correction, upper obligations above existing D04 riser3, remaining district/house connections and D18 needs remain open. Whole clinical transfer still requires the original ten junctions, actual medical receiver doors, sealed-load/stock policy, safe maintenance/egress and all species/load acceptance. The400-berth identity migration remains unapplied. Failed or rejected source candidates and earlier bounded passing receipts are retained honestly in batch QA.
