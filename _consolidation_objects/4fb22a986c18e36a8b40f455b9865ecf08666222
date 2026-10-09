# Exact original ZIP recovery

Original: `WP13_D11_directory_02_FULL_CANDIDATE.zip`
Bytes: 49287596
SHA-256: `e93522b3af28553648c86a3ff0551f74de491c338a5c6462c32474b92676788c`

These are unmodified raw byte parts, each at most 18,000,000 bytes (18 decimal MB). They are not standalone ZIP files. Concatenate in the exact numeric order below. No recompression or source rebuild is involved.

Run from this folder in a fresh location. The no-clobber subshell refuses to replace an existing original ZIP.

```sh
sha256sum -c PARTS_SHA256SUMS
(set -C; cat WP13_D11_directory_02_FULL_CANDIDATE.zip.part001 WP13_D11_directory_02_FULL_CANDIDATE.zip.part002 WP13_D11_directory_02_FULL_CANDIDATE.zip.part003 > WP13_D11_directory_02_FULL_CANDIDATE.zip)
sha256sum -c ORIGINAL_SHA256SUMS
```

Check that all commands pass before extraction. Extract only into a new empty directory, preserving surviving workspaces. Keep these parts and their manifests until recovery is verified. `PARTS_MANIFEST.json` records exact offsets, byte counts, ordered names, all part hashes, and the verified original hash.

Validation at packaging: source expected SHA-256, source ZIP CRCs, each written part SHA-256, and concatenated SHA-256 all passed.
