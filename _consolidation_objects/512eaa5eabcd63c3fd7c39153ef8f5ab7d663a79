# Exact original ZIP recovery

Original: `WP06_D12_directory_02_FULL_CANDIDATE.zip`
Bytes: 56800256
SHA-256: `e05c745f8672caf5e8937ad8bda1df2df2a02f67439065edfcdb63201e811fe4`

These are unmodified raw byte parts, each at most 18,000,000 bytes (18 decimal MB). They are not standalone ZIP files. Concatenate in the exact numeric order below. No recompression or source rebuild is involved.

Run from this folder in a fresh location. The no-clobber subshell refuses to replace an existing original ZIP.

```sh
sha256sum -c PARTS_SHA256SUMS
(set -C; cat WP06_D12_directory_02_FULL_CANDIDATE.zip.part001 WP06_D12_directory_02_FULL_CANDIDATE.zip.part002 WP06_D12_directory_02_FULL_CANDIDATE.zip.part003 WP06_D12_directory_02_FULL_CANDIDATE.zip.part004 > WP06_D12_directory_02_FULL_CANDIDATE.zip)
sha256sum -c ORIGINAL_SHA256SUMS
```

Check that all commands pass before extraction. Extract only into a new empty directory, preserving surviving workspaces. Keep these parts and their manifests until recovery is verified. `PARTS_MANIFEST.json` records exact offsets, byte counts, ordered names, all part hashes, and the verified original hash.

Validation at packaging: source expected SHA-256, source ZIP CRCs, each written part SHA-256, and concatenated SHA-256 all passed.
