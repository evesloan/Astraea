# Orchard chair rendering review

This is a bounded runtime drawing change for the existing static AST-DIN-002 chairs in Orchard. The editable Blender source and all ten original contact-bearing part nodes remain intact. The explicit opt-in helper joins those ten visible meshes into one chair-local ArrayMesh with two original material surfaces, shared between the240 instances. It preserves each chair's independent bounds, persistent identity, seat marker and all ten collision shapes. It is not cross-room batching, new seating gameplay or ship-wide streaming.

## Comparison
The paired current-scene graphical review used Godot4.6.3 Compatibility on llvmpipe, the same prescribed cameras and existing eight-source shadow budget. Normal arrival changed from2751 to1217 reported draw calls; effects-off arrival changed from2743 to1209. The communal view changed from1892 to1189. The upper court remained322. Complete counters are in docs/ORCHARD_RENDER_COMPARISON.json.

Coarser chair-local culling increases the normal arrival primitive counter from170362 to171430 while reducing submissions. This is an explicit tradeoff; the change is not a triangle reduction. Normal and effects-off arrival images were inspected. Their average channel differences against the preceding captures were0.0000521 and0.0000338 on the0–255 scale. The two captures are practically identical at these views; this does not certify every angle or hardware configuration.

The regression verifies the original transformed vertex/UV/material multiset, normal directions within a0.999999 dot-product tolerance for Godot normal repacking, shared joined-mesh ownership and all original contacts. The existing240-seat support/standing-position and actual public/service route checks remain in place. An initial exact four-decimal normal-string comparison failed because normal repacking perturbed the last digit; that was replaced with the explicit angular comparison rather than removing normal verification.

The first full regression execution was interrupted before it wrote a final result. It was confirmed absent before a fresh full run. Only the final completed report may be cited as full acceptance. No target-GPU frame-rate result, full ship streaming, occupied seating or service simulation is implied.

Reference: Godot4.6 SurfaceTool append_from/commit API, https://docs.godotengine.org/en/4.6/classes/class_surfacetool.html . Master chapter25's truth/presentation separation remains governing; its historical implementation statements are not claims about this reconstruction.

Final full regression:54/54 groups passed in203.9126seconds with fixed60 simulation. Graphical queue orchard-chair-visual-001 passed in135.703seconds; normal and effects-off arrival images were inspected after completion. These are execution timings, not frame-rate results.
