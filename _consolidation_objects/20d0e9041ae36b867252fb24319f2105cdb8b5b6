# Remaining-section receiver and recovered-original packages

This tree contains two complete existing receiver derivative packages and byte-exact split copies of two recovered original full-candidate ZIPs. Packaging did not run Blender or a game engine, construct sources, edit geometry, or change the input files. Publication is the responsibility of the root publisher; this preparation performed no remote upload.

## Receiver derivatives

Each ZIP in `receivers/` stores all existing files under their full `BlenderCatalogue/assets/...` project-relative paths, plus a hash inventory under `PUBLICATION_METADATA/`. External `.manifest.json` files hash every ZIP entry, including embedded metadata, and pin the complete ZIP. `.zip.sha256` files are compatible with `sha256sum -c` when run inside `receivers/`.

Extract receiver ZIPs only into a new empty staging directory, then compare destination hashes before integrating. Do not extract over a surviving project. Paths under `PUBLICATION_METADATA/` are packaging evidence, not source assets.

The medical package retains historical `qa/RECEIVING_BUILD.json` unchanged and preserves `qa/first_unapplied_modifiers.glb`. The stale build `export_sha256` correctly identifies that first attempt rather than the final export. An additive `qa/RECEIVING_BUILD_EXPORT_HASH_CORRECTION_20261009.json` receipt identifies the final export SHA-256 `c7cfb577d2bbc01c6058d77a02a87b6087b45c53022f568e9145f595d918e742`, corroborated by the retained `RECEIVING_EXPORT_VERIFICATION.json`. The same receipt is available separately under `receivers/receipts/`.

## Original full-candidate ZIPs

`recovered_originals/` contains raw parts of the exact original WP13 D11 directory 02 and WP06 D12 directory 02 ZIPs. All parts are at most 18,000,000 bytes. Each directory supplies `RECOVER.md`, ordered part metadata, part SHA-256 sums, and the original ZIP hash. Concatenate parts; do not unzip individual parts. Preserve existing workspaces.

## Verification scope

All original input file hashes were rechecked unchanged. All receiver ZIP entry bytes, entry hashes, and CRCs passed. Original full-candidate ZIP CRCs and reassembled raw-part hashes passed. This is packaging integrity evidence, not a fresh source, scene, runtime, or engine QA pass.
