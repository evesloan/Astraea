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
