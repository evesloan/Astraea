# D09 connected salon architectural checkpoint

Current species authority: [SPECIES_CANON.md](../SPECIES_CANON.md). Koblins, Mantelids, Humans, Baelins, Munkos and Mindos replace the prior roster. Existing eight habitat profiles are physical room/rest types and legacy implementation identifiers, not eight species. Baelin aquatic homes and Mantelid quiet cocoons must be represented; new demographic and numeric biological parameters remain open.

Approval update: the later D09 Composition04 direction is approved for propagation and substantial further refinement toward the refined, alive, filled yet pixelated ship. Earlier rejection or no-rollout statements below describe their dated revisions, not a withdrawal of this later direction approval. Final room and shipwide acceptance remain open.

Status: first architectural checkpoint inside the production main scene. This is one room and a 28 m terrace segment, not a completed ship-wide reauthoring.

## Protected live baseline

Godot 4.6.3, Compatibility renderer, metres, Y up; deck-local coordinates retain the active-deck origin. D09 is at +52.5 m; D10 at +61 m; usable height is 8.25 m. The current 640 × 360 SubViewport, CRT stage and native-resolution HUD remain the only rendering path. Player capsule diameter is 0.6 m; cart collider envelope is about 1.14 × 0.77 m. Automatic leaves now have independently verified closed/open transforms on all 18 decks.

D09_salon5 retains its ID, name, kind, centre (75,0,0), allocation X52..98/Z-34..34, front door (52,0,0), rear service door (98,0,0), and both operational sliding-door families. No accommodations, other registered destinations or room envelopes change. Social positions remain within the authored plan, with the existing centre-to-anchor approach kept free.

The terrace sample is the starboard garden-facing edge at Z-14..14. The entire tram strip X35..45 stays clear. The transverse route at Z0 stays clear and leads through the existing atrium portal at X48 to the room door at X52. The panoramic lift tower at (31.2,5) keeps its space and current decorative status. No floor holes are added.

## Plan decision

Replace the salon's rectangular enclosing walls with a continuous two-lobed perimeter. A narrow arrival neck opens into a broad conversation court. The north lobe is an acoustically sheltered reading/conversation recess; the south lobe is a more open planted social court. Both share the legible cross-axis leading to the rear service door. The perimeter bends around these uses, rather than clipping four decorative corners off a box.

The existing rectangular allocation remains metadata. A local authored profile provides a precise polygon and ceiling zones to the existing builder. Static wall segments have individually rotated, shallow box collision; the interior is never wrapped in a convex collider. Floor finish and ceiling silhouettes derive from the same profile. Residual allocation corners are enclosed structure/service depth, not newly registered guest rooms.

The linked terrace has two sheltered stopping pockets facing the garden, separated by the existing transparent lift landmark and clear transverse crossing. Their canopy edges, planting rims and rib rhythm share the salon threshold's vocabulary. This is a destination edge beside a working tram, not an added shop row.

## Section decision

The arrival neck has a 3.8 m soffit. The central conversation court opens to 7.4 m, below the real 8.25 m limit. The quiet north lobe has a lowered 4.3 m canopy with open access; the south court has a 5.2 m planted seating canopy. Visible ribs and stepped reveals join these volumes to the perimeter. This provides compression, reveal and intimacy without an invented double-height void or mezzanine.

Visible pendants and sconces provide local illumination under the current global light budget. Geometry must read with CRT disabled and under a neutral-material diagnostic. No new renderer or shader stack is introduced.

## Evidence and acceptance

Baseline four views are preserved in artifacts/d09-baseline with source copies and hashes. After views use the same cameras. Normal door states and all registered IDs remain active in the production scene. Required review: plan, section, cutaway, room entry/interior, terrace/across-atrium, CRT on/off, broad-body routes, loaded cart interfaces, tram strip clearance and floor support. Source counts alone are not visual acceptance. No propagation to other terraces or room families before this checkpoint is judged.

## Revision 02: response to independent architectural rejection

The first enclosing silhouette and ceiling zones were physically valid but still read as a sparse event hall. Both the parent review and independent visual review rejected that purposeful-use gate. The current revision adds four real nested edge bays, each about 9.2 m wide with a lower 3.65 m quiet or 3.95 m social canopy. Curved backs, side protection, a supported built-in bench, shared low table and two chairs establish the group. Quiet bays have 2.65 m screened backs and integrated book storage. Social bays have low open backs and planting. A backed tea recess anchors the social side. The shared arrival court retains its uninterrupted public/service axis; additional activity anchors route through the mouths of the bays, not through their walls.

The original four anchors remain valid. The registered allocation, ID, doors and capacity ledger remain unchanged. This revision is being judged in-engine before propagation. The existing D09 bridge endpoint was shortened by 0.5 m to remove a 0.14 m inherited guard overlap with the protected tram buffer; its actual vehicle envelope already passed, and the full buffer is being rechecked.

## Revision 03 implemented program reduction, pending user direction

The second pass makes the bays legible but leaves small pavilions under an oversized public hall. The next bounded correction reduces the *actual guest enclosure* to approximately 826 m² within the unchanged 46 × 68 m registry allocation. Its program is a 4–6 m arrival/service spine, two roughly 8 m quiet conversation/reading alcoves, one social garden court, and a directly adjoining tea-service edge. The outer allocation corners are behind enclosing bulkheads as service/acoustic depth, not exposed public carpet. The true room profile must contain all preserved original anchors, door turning landings and the central service route.

Low ceilings terminate into the enclosing walls. The social garden is a planted shared focal surface and view sequence, not a second atrium monument. This revision is intended to resolve scale and sequence, rather than adding more freestanding furniture. The successful 28 m terrace stays unchanged.

Revision03 current evidence: the independent reviewer confirms the eight activity-anchor approaches, two local cleaning stances, both terrace pockets,110 ordinary/broad room routes and7,990 sampled floor supports. The full X35..45 buffer is now clear after the bridge guard correction. These are geometry screens; the independently simulated loaded-cart crossing is recorded separately. Visual review says this is ready to show for user direction, while retaining open privacy, tea composition, material/detail and allocation-reserve work. No ship-wide architectural rollout is approved.

A real moving-platform regression now additionally passes upper-gallery cart recovery and the menu-close interaction latch, preserving all three loose doses. Current crew meal/break/changing collision checks also pass after removing generic partitions from those room types and closing the theater landing support gap. These are specific fixes, not a claim that every ship system is finished.
