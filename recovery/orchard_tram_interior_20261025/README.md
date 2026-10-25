# Orchard interior tram receiving — unfinished, unselected source

R003 authors an interior route through the retained two-level Orchard Exchange,
with a southern public arrival coordinated into Thread & Shell. It supersedes
the direction of the isolated D10 access candidate, not its preserved originals.
The selected main and its operating controllers are unchanged.

## Authored physical scope

- FORE_MIDSHIP identity and catchment retained; proposed dock X17.3, Y56.1,
  Z-236.1. Rail height remains 56.1. R4 approach and shallow eastward S turn
  return at Z-222; the central original body pose is preserved.
- 226 new native parts: continuous route rails/web, supported north opening,
  inhabited boarding landing, two-flight stair with guards, same-identity lift
  receiving shaft, raised retail arrival canopy and 30 source-floor receiver
  bindings. Receiver footprint coverage is not structural capacity approval.
- Retained Orchard switchback, lift, protected deck slab, retail entrance and
  bearing geometry remain unchanged. Original room GLBs are immutable.
- 60 recorded member operations fit receiving openings and retain/refit two
  fixtures. R003 canopy is Y60.55..60.75, below D10 underside60.76. R002's older
  PLAN canopy annotation was inconsistent with its build and is not authoritative.
- Blender editable sources are under
  `BlenderCatalogue/assets/orchard_tram_interior_20261025/r003`.
  Runtime candidates are `Game/orchard_tram_interior_20261025/r003`.

## Verified changed work

Native source verifies 414 untouched members' geometry, UVs and transforms.
Blender GLB roundtrip showed normal/material floating-point drift and triangle
ordering changes. Separate `*_receiving_exact.glb` successors therefore retain
the original untouched primitive/accessor/material/image bytes and transforms;
all414 oriented triangle/normal/UV and material comparisons now pass. Changed
members use the native export. Both raw exports and exact successors are retained.
The new guard glass exports with alphaMode BLEND and alpha0.28.

Attempt004 found support-shoe, north-opening top, retail ceiling edge and
platform corner conflicts. R003 lowers the shoes, enlarges the receiving cuts
and trims the platform corner without weakening the queried envelope. Attempt005
passes226 0.5m sampled 4m-wide x5.4m-long envelope queries, Y55.75..60.1,
against847 candidate triangle-contact meshes. All protected source members remain
queryable; only deliberate rolling rail/web contacts are excluded.

Attempt006 is NOT a complete pass: Godot warned that concave-vs-concave queries
are unsupported. Attempt007 encloses the12 affected portal query shapes in
conservative convex hulls, without modifying source/production contacts. It
passes279604 discrete queries across247 original vehicle, articulated bogie,
closed portal, restraint, console, cart and four-stock shapes. No conflicts,
warnings, assertions or script errors; exit0,1.101s fixture duration. The source
assembly is in a separate physics world, never driven or substituted for an
installed ship. The external3s sampler captured only one startup sample; its
memory reading is NOT the peak. No FPS or performance claim follows.

## Required before selection

1. Fit the relocated original boarding lift into the D09 floor: receiving pit
   X10.8..15.2/Z-231.96..-227.94, keeping real surrounding floor and circulation.
   Bind the original two-stop controller, cabin and persistent IDs once.
2. Bind the new route/stop/bridge/boarding pose coherently to the unchanged
   controllers. Retire only their explicitly superseded old physical receivers;
   do not duplicate stations or change stop identity.
3. Complete floor/support/guard continuity, door opening/boarding/cart circulation,
   structural capacity and lighting receiver checks. Fixture range9m for Orchard
   and10m for retail remain explicit runtime work, not completed by GLB authoring.
4. Installed whole-ship continuous vehicle/door/cart clearance and actual rider
   sightline/visual review. Current checks are discrete candidate-only evidence.
5. Aquatic grand-room integration, live-resource/RID correction, actual moving
   tram/player-camera performance and matching Windows delivery remain open.

No full-ship launch, import, gameplay input, Windows export or new screenshot was
performed for this checkpoint. Earlier selected source and packages are preserved.
