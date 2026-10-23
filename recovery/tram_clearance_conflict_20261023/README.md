# Tram clearance review r001

Read `CONSTRUCTION_DECISION.md` first. The retained sources contain incompatible
vertical clearance interpretations. A support-only repair preserving the current
rails cannot clear the current D09 reservation, so no geometry candidate was
authored or adopted.

Files:

- `CONSTRUCTION_DECISION.md`: governing evidence, distinction between geometric
  obstruction and unresolved requirement interpretation, and smallest safe next
  construction options.
- `GEOMETRY_WITNESSES.json`: five exact fixed-geometry intersections, current
  source pins and integration evidence. Positive examples only, not a full audit.
- `inspect_retained_geometry.py`: read-only reproducible witness extraction.
- `INPUT_RECEIPT.json`: verified recovered text and remote native identities.
- `CURRENT_CONTENT_PINS.json`, `SOURCE_DIRECTORY_PINS.json`: checkpoint metadata,
  without private download URLs or credentials.
- `retained-inputs/`: unchanged source recipes/interfaces at the checkpoint.
- `VERIFICATION_ATTEMPTS.json`: bounded preparation failure history and outcome.
- `PACKAGE_MANIFEST.json`: final file sizes and SHA-256 hashes, excluding itself.

Reproduce the static source observation with:

    python inspect_retained_geometry.py --game-root /path/to/recovered/Game

It reads the existing source files and prints JSON. It does not run Blender or
Godot, edit production, regenerate geometry or relax any clearance requirement.

This revision is additive and unadopted. Preserve it; write a new revision for a
future design decision. Root owns publication and independent retention.
