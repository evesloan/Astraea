# Group4 port successor002, source construction delivery

This separately versioned batch is uninstalled construction work. Group4 remains open. The protected first batch and all installed Game sources are unchanged. Root owns integration and publication.

## Selected source layout

Outside the central arrival, the trunk is X−5.6, from Z−466 to+466. The protected central authority stays exactly `(0,−72),(0,−56),(40,−52),(40,52),(0,56),(0,72)`. Source rail fillets, R2.2m, stay within its retained4m strip. Group7 X43..46.5/Z−25..−19 and all four floor reservations are preserved.

Five stations keep Z−432,−216,−72,+216,+432. Forward/aft use reflected upper core connectors and starboard doors. Aft-midship uses a starboard platform/access. Fore-midship alone uses an outer-port platform X−13.2..−7.8, retaining original2.4m emergency stairs and moving the local lift toX−11.2/Z−200. This avoids retained Thread&Shell `TAIL_PromenadeCanopy`/`TAIL_PorchBearing_-231` and Orchard Exchange. The rejected starboard fore-midship access is not exported. Central keeps the axial catchment and port platform; its previous upper port-core connector is omitted, with access instead through the retained lower apron to a new local lift/stair.

## Receiving interfaces

See SUCCESSOR_INTERFACE.json for exact coordinates, stops, gate side, bridge and missing-only floor proposals. No lower slab, cut, cabin, moving bridge/gate/door, transport controller or cart is exported.

- Central recess X−7.8..−3.4/Z−68.4..−64.4,17.6m², actual retained owner `D09_atrium_circulation`. Root must perform the bounded receiving cut.
- Forward/aft/aft-midship recesses overlap the installed axial slab by2.4m² each.
- Fore-midship17.6m² recess is entirely in its new outer-port annex. Existing-slab cut area is0. Its missing-only annex is wider, X−13.4..−4/Z−240.5..−196.2; foundation/fill receiving is held.
- Reuse AST-CIR-003 and commons_lift.gd, local gate(0,0),52.5/56.1, distinct local IDs on D09. Existing lift stops and timing remain untouched.
- Nominal portal post spacing2.4m is only2.22m clear after posts. Vehicle doorway is2.33m clear. The root-owned retractable bridge proposal is2.18m wide and1.0926m reach, not the historical0.9m reach.
- Guideway has166 named D09/D10 receiving witnesses. Four exact core-end roof interfaces have non-unique boundary ownership and are explicitly held. Tie/central-bypass receiving frame and secondary central-stair receiving are unfinished. Geometry witnesses do not prove load capacity.

## Vehicle/interior

Exterior2.3m, unchanged4.88m length,1.72m gauge and3m bogie chord. Usable pocket-to-pocket interior2.104m. Both portals are open source apertures, with powered doors still required. Recessed mounting channels do not obstruct caster entry; operating restraints are absent.

Existing cart compound/casters width0.82m;25 bounded turn poses show≥0.257m side clearance. DockZ0.15 and rear operatorZ1.77 match the existing0.95m physical handle reach. A0.3m-radius rear stance has0.15m end-wall clearance; front stanceZ−0.95 has0.25m cart and0.29m perch clearance. Loaded four bottles at nominal cart locations reach1.21m, below the2.51m door header. Existing cart/product IDs and E/RMB controls are preserved.

## Verified scope and limits

Seven GLBs have finite/index/bounds checks, zero degenerate triangles and per-part native/world export agreement. All five stations have zero bounded adjacent-source AABB contacts. Existing lower4m axis has no source intrusion below the3.05m soffit.

201 bogie-chord poses per tie clear at0.20m horizontal margin.804 bounded poses around the four protected corners clear at0.15m margin;0.20m fails by6.3mm and is recorded as failed. The retained-source screen uses35,057 triangle AABBs from44 named source instances, including eight atrium bearing/fan positions. Whole stair-headroom reservations clear using oriented-body checks. This is not an exact continuous collision, steering, whole-world or runtime certificate.

Six native source studio views were reviewed. Their geometry signature matches final exports; texture sources are retained and packed in the editable blend. No Godot/import/full builds were run. Further traversal, species fit, secondary narrow stairs/upper connector local pinches, final material/lighting, CRT and hardware checks wait for installation.

## Reproduction

Use the existing installed Blender: `blender -b --threads 1 --python build_successor.py`. Then `OPENBLAS_NUM_THREADS=1 python validate_successor.py`. Rendering uses `render_source_review.py` and does not save changes to native/exports. The builder reads the protected first batch at the exact retained project path and asserts its receipt hashes; bundled route reports and GLB reader make this successor independent of changing comparison drafts.

Freeze/hash list: FROZEN_SUCCESSOR_BATCH.json. Root must check the source pins before integration; do not register these source-only assets as completed stations or Group4.
