# Authored architecture and asset pipeline

The surviving master document, blueprints and reference archives supply design intent. data/design_contract.json records later owner decisions that override older counts/engine assumptions. Historical allocation rectangles are evidence, not mandatory box interiors.

## Geometry ownership
- Edit data/spatial_layout.json deliberately. Floor datums remain separate from local offsets, ceilings and voids.
- Compile with tools/compile_layout.py and the pinned geometry dependencies. Ownership is evaluated at absolute elevation, so mezzanines do not erase lower floors.
- The 96 × 128 m atrium rectangle is a structural slab cut-out. Authored terraces occupy part of it. Explicit atrium-terrace records and the separately constrained D02 garden-base records may exempt that structural cut-out; the theater reservation remains protected.
- Run tools/validate_atrium_routes.py for continuous four-metre support around the reserved service route. This is not actual loaded-cart or tram acceptance.
- Floor rendering can use 24 m cells while physics remains one continuous contact mesh per authored region. This supports local lighting without adding collision seams.

## Blender catalogue
The catalogue is maintained separately with editable .blend sources, GLB exports, manifests and authoring scripts. Do not regenerate over someone else's manual edits. Review local changes before rebuilding a source asset.

Repeated construction profiles and fitted variants are not additional unique designs. The atrium guard network is one profile family fitted to sixteen levels. Column height variants preserve the foot and capital while changing the shaft span; they are not globally stretched props.

For guard changes, run tools/export_atrium_guard_paths.py with an explicit output path to the catalogue's atrium_guard_network/source/atrium_paths.json, then run that family's Blender generator. Keep the floor and guard source paths coordinated. The D06 standalone floor/soffit retains its identity; the fitted network owns its guard and fascia to avoid duplicates.

Import only the current manifest exports. Record hashes and support files. Original materials and Blender sources remain available independently of Godot's import cache.

## Contacts, controls and lights
Static model contacts share immutable shapes through weak references. Moving door leaves use separate simple contacts and authored hinges. The service door's stable ID is independent of its scene-tree name. Save serialization remains future work.

RMB focus and E use one camera-targeted interaction path. Keep future buttons/pickups on this path. Depth-of-field is not implemented yet.

Light sources belong at fixture datums or verified source lens geometry. Profiles are artistic tuning, not species biological requirements. Large render meshes need deliberate spatial grouping: Godot's Compatibility renderer has default per-mesh light limits. See the official renderer overview: https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html

## Evidence and backups
Run tools/validate.py for import, baseline, world, stairs, doors, contact-cache, garden, salon, principal-bearing and activity-placement checks. Use its --only option during focused debugging; a full run is required for a milestone.

The fixed cloud capture runner is session-scoped. It is not an OS startup service, an autonomous coding agent or a target-GPU benchmark. It records in-engine views, camera settings and errors. Inspect the actual images, including native-resolution effects-off views.

A local Git commit is not an independent backup. Retain verified source archives and hashes, perform clean restores, and separately verify Workshop copies. Automatic Workshop delivery is not established. Keep engine installers, authentication state and disposable import caches out of project backups.

Use Blender --python-exit-code 1 for scripted authoring so a Python failure cannot be mistaken for a successful export. Source IDs must be checked against the entire current catalogue before allocation.

Opaque structural slabs and selected room walls/ceilings now provide occluders copied from actual surfaces. Glass, fixtures and door openings are excluded. Paired stationary-view diagnostics are available through the fixed review request helper; they are not target-device benchmarks. Animated ornamental water receives light but does not cast an opaque moving shadow, and unchanged light-budget state is not reapplied on every refresh.
