# Reproduction and archive tools

The source was authored with Blender 4.3.2 and Python. The original tile generator uses Pillow 12.3.0; Blender includes its own Python/bpy. No downloaded model code, cloud generation service or paid asset is required.

Run from a separate writable copy of this catalogue if preserving the exact delivered binaries. Regeneration changes Blender file hashes even when the measured geometry is identical.

```sh
python3 tools/generate_materials.py
blender --background --threads 4 --python assets/furniture/build_furniture.py
blender --background --threads 4 --python assets/view_reveal/source/build_reveal.py -- --no-render
```

Each asset family includes its own documented inspection/render commands. Shared QA tools independently inspect GLB bytes and saved Blender source. `qa/render_combined_components.py` imports the evaluated GLBs into a plainly labelled component arrangement; it does not construct a room or implement the game.

For a reviewed, committed batch, `package_batch.py` makes a versioned ZIP outside the working source tree. It embeds a file hash manifest and portable Git bundle, checks archive CRCs and every source hash, and verifies that source bytes did not change during packaging. It refuses an existing output file or an uncommitted source snapshot. A verified local ZIP still requires a separate durable Library upload.

```sh
python3 tools/package_batch.py /absolute/delivery/path/Astraea_Catalogue_Batch01_v1.zip
```

The complete original game, runtime shaders, physics, saves and player controls are not contained here. They remain part of the original-workspace recovery process.

## Later catalogue checkpoints

`package_batch.py` accepts `--prefix`, `--incremental-base` and `--base-library-file-id`. The full ZIP still contains all current tracked source/evidence files; only optional Git history becomes incremental from the stated backed-up commit. Verify restoration from that base plus the new bundle before delivery.

`package_small_delivery.py` takes an already verified full ZIP, a new output directory and `--label`. With `--base-zip` and `--base-library-file-id`, it omits unchanged prior review/reference copies from current delivery while listing their exact hashes and backup dependency. Complete current editable source, textures and generator dependencies remain together. Review ZIPs are ordinary archives; only optional history uses byte segments and a checksum-verifying join helper. Payloads use7.5MB and every finished file must be below8MB.

For a larger catalogue, add `--family-sources`. The ownership map in `standards/source_package_groups.json` produces independently extractable family source ZIPs. Each contains its own editable assets plus all shared textures, material helpers and source tooling. Common bytes are identical across packages, so the ZIPs can also be extracted together. The full catalogue index remains included, with `FAMILY_CONTENTS_<name>.json` stating exactly which assets are present in that package. Unknown asset directories, missing exports and duplicate ownership fail closed; no source files are dropped to reach the size limit. An oversized family must be deliberately split into smaller coherent dependency groups.

Source family delivery is independent of optional QA media and Git history. Continue storing the complete unsplit archive durably. User delivery can contain the compact source family set and one labelled representative preview rather than every optional review/history package.
