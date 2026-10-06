# Pool source/export equivalence

`snapshot_source.py` opens each checked `.blend` read-only in Blender. It captures
the evaluated scene, including modifiers, world transforms, every triangle corner
position/UV/normal, source properties, the active material graph and packed image
hashes. It never saves a source, exports, renders or edits runtime files.

`check_glb.py` is independent pure Python (NumPy/SciPy). It decodes GLB accessors,
scene transforms, materials, samplers and embedded PNG bytes directly. Source
contract vertices are not substituted for the evaluated snapshot.

The checker enforces:

- Complete one-to-one triangle/corner correspondence, cyclic winding only. A
  KD-tree produces candidates, and maximum bipartite matching verifies a full
  bijection. There are no rounded-coordinate hash bins or nearest-surface tests.
- World positions within the existing 50 µm ceiling, unchanged local vertices
  within 1e-10 m float64 reconstruction noise, and checked source/export matrices.
  Snapshot 001 local arrays are reconstructed by inverting its recorded evaluated
  world matrix; measured error is at most 2.85e-14 m.
- Exact float32 export UV values after `V = 1 - source V`. No UV epsilon.
- Every corner normal within the existing 2e-6 normal limit.
- Actual Principled material factors, emission, opaque alpha, culling, precise
  image links, UV channel, texture wrap/filtering and exact embedded PNG bytes.
- Exact sign/media node hierarchy and source custom properties; excluded sign
  reference geometry cannot appear.
- Independently recomputed envelope batch membership, source-part inventory,
  collision/shadow metadata and physical light marker-to-batch mapping.

Blender's float32 parent inverse can add a tiny exported media child translation.
Decoded origins must round back to the **exact** saved source float32 origin;
the 50 µm world ceiling remains in force, and local mesh coordinates must remain
unchanged. Quaternion normalization is applied before decoding rotation matrices.

## Commands

After the parent clears the Blender job slot:

```sh
blender -b -t 2 --python snapshot_source.py -- \
  --kind envelope --source CHECKED.blend --output NEW_snapshot.json
```

`--kind wayfinding` and `--kind media` select the other exact inventories. Media
captures evaluated live bevel/weighted-normal modifiers. The source hashes must
still match when the pure checker runs.

```sh
python check_glb.py --snapshot envelope_snapshot001.json --glb NEW.glb \
  --batches EXPORT_BATCHES.json --contract finish_contract.json --report NEW.json
python check_glb.py --snapshot wayfinding_snapshot001.json --glb NEW.glb --report NEW.json
python check_glb.py --snapshot media_snapshot001.json --glb NEW.glb --report NEW.json
python test_checker.py
```

All output paths are write-once. Initial exports failed because Blender 4.3.2's
four-decimal normal rounding exceeded the 2e-6 normal gate. No checker tolerance
was broadened to accept that. Early checker-development reports 001/002 preserve
their errors for history; only a complete `status: PASS` report is an equivalence
result. Runtime adoption, physical collision/contact tests and rendered visual
acceptance remain separate gates.
