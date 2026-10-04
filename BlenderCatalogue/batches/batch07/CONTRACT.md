# Batch07 — hospitality service components

Six original editable Blender designs extend the catalogue into guest-facing dining service. This is independent component work while the original game remains unavailable. No replacement room, working food system or player cart is built.

## Actual reference guidance

Inspect references/hospitality/public_reference.png and vibe_dining_edge.jpg, plus the existing premium-space suite reference where useful. The public blueprint establishes meaningful dining/support purpose; old labels/counts do not override later canon. The dining image contributes continuous rounded joinery, ribbed timber privacy and service/display integration. Translate its warmth through coordinated material roles and useful forms, not amber scene tint or dozens of tiny luminous trim strips.

## Six designs and ownership

- AST-HSP-001 fitted pantry counter; AST-HSP-002 compatible corner/return: assets/hospitality_counters
- AST-HSP-003 countertop beverage station; AST-HSP-004 dirty-dish return: assets/hospitality_stations
- AST-HSP-005 plate/tray storage; AST-HSP-006 compact dining service trolley: assets/hospitality_serviceware

Separate local generators, sources, exports, manifests and QA in each owner folder. Existing assets, textures and helpers are frozen. Shared modifications require lead coordination. Author new assets from deliberate shapes, not old missing source or unverified external kit.

## Common placement contract

Metres. Blender source +Z up, guest front −Y, staff/work rear +Y. GLB mapping (x,y,z) → (x,z,−y), with actual imported node hierarchy authoritative. Normal counter height 0.90 m and nominal depth 0.78 m; exact ends and corner interfaces are authored by the counter owner and published before the final assembly. Catalogue dimensions are proposed component sizes, not an approved room fit.

The beverage station is a countertop component with support plane Z0, proposed footprint about 0.65×0.45 m, installed on the 0.90 m worktop; cups/drains/spouts must have real distinct support and release spaces. Dirty return is a separate floor-standing component around 1.10 m wide and0.78 m deep, with a usable approximately 0.90 m drop surface and a real receiving compartment. Avoid an indiscriminate full-body collider across openings.

Storage is a floor-standing companion with actual accessible plate/tray storage. Trolley is a distinct compact service furnishing with two purposeful tiers, castor/support geometry and a real push-grip. It is not the existing player cart, and proposed articulation/contact metadata does not implement rolling, cargo physics or controls. Use a common proposed tray envelope 0.45×0.32 m where needed; contextual stock groups and repeated trays are parts/derivatives, not additional counted designs.

## Material and source craft

Reuse appropriate guest roles from standards/materials.py: ivory enamel, walnut, warm stone, champagne metal and dark rubber. Washable staff-side equipment can use the existing neutral staff metal/label roles, explicitly scoped to that work surface. Do not globally recolor old roles. New original local graphics are permitted when they convey useful function. Keep material roles semantic and metric UV scale/grain direction intentional.

Shaped profiles, load support, fascia returns, recessed practical storage, coherent handles and clean joints must read at first-person scale. Preserve editable semantic objects/modifiers; join evaluated static exports by material role within functional group, leaving doors, shelves/caddies or controls separately named where motion is proposed. Normalize export UV layer names and inspect actual GLB pixels. Keep repeated details economical and report actual triangles/primitives; no arbitrary polygon-count certification.

## Evidence and gate

Reload every .blend, inspect actual exports, packed texture/material references, transforms, dimensions, normals and UVs. Measure real floor/support contacts, defined mating joints, work/guest approaches and any proposed moving-part sweep with sensitive blocked/wrong-axis controls. Conservative collision proposals must preserve meaningful service/opening space and identify their source/export frame. No universal species/accessibility or food/structural/electrical certification.

Use standards/qa_frame.py before heavy actual-GLB renders; neutral three-quarter, ordinary standing/use and a purposeful detail view. Serialize heavy renders through the lead. A small joined neutral fixture will inspect service-side and guest-side relationships without constructing a restaurant. Independent source/visual review is followed by commit, full archive, complete compact source-family ZIPs, actual offline restoration and durable Library backup before any next batch.
