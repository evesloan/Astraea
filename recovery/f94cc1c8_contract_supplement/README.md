# Exact frozen-source contract supplement

This repairs an omission in the f94cc1c8 editable handoff; it does not change the frozen source revision, selected main, manifest, geometry or import policy. The previous completeness claim checked tracked-file presence, not retention of every manifest input, and was insufficient.

282 exact .glb.import files (315,328 bytes) are supplied in imports/. All 2,868 missing PNGs (49,454,185 bytes) reconstruct byte-for-byte from embedded image bufferViews in128 original GLBs already present in frozen f94cc1c8. SUPPLEMENT.json lists every relative target, byte count, SHA-256 and either exact payload or retained GLB hash/byte range. These are exact bytes, not re-encoded images. Do not rely on fresh import to recreate exact .import UIDs/hashes.

1. Extract this archive into a new separate directory, not over the project. Keep the utility, SUPPLEMENT.json and imports/ together.
2. Before Godot import, run with Python3.9+:

    python repair.py --repo "C:\path\Astraea-f94cc1c8"
    python repair.py --repo "C:\path\Astraea-f94cc1c8" --apply
    python repair.py --repo "C:\path\Astraea-f94cc1c8"

Preflight checks the unchanged frozen manifest and every existing contract file. It refuses mismatches or unexpected missing files before writing. It writes missing paths only using exclusive creation; never overwrite a survivor to resolve an error. If interrupted, rerun: already correct files are preserved. Final output must report all17487contracts match before the single laptop owner begins import. No network, credentials, installation, engine change or source-manifest regeneration is performed.

Three case-colliding validation-document pairs remain retained in Git history but are outside the manifest, have no identified runtime references and lie under export-excluded docs/. They do not require Windows case-setting changes for this repair. Full ship launch, playability and performance remain unverified; this supplement fixes source delivery, not those acceptance gates.
