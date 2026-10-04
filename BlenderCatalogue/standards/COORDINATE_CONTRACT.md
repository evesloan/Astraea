# Source and exchange coordinates

This contract applies across the catalogue. Numeric records must identify their frame and datum. Existing contact/collision/connection proposals documented as Blender coordinates remain in the asset's source frame; they are not silently reinterpreted as engine coordinates.

## Axes and units

All lengths are metres. Blender source uses right +X, depth +Y and up +Z. The catalogue's stated front is normally −Y unless an individual asset explicitly states another direction. Standard glTF/GLB exchange is Y-up. The source-to-exchange geometric mapping is:

- Source point (x, y, z) → GLB point (x, z, −y)
- Source up +Z → GLB up +Y
- Source front −Y → GLB front +Z
- Source right +X → GLB right +X

The mapping is a proper −90° rotation about X, not a reflection. Its inverse is (x, y, z) in GLB → (x, −z, y) in Blender. A receiving engine whose camera/controller forward is −Z must use an explicit placement rotation where appropriate; it must not assume these asset fronts already face −Z.

Homogeneous basis C:

    [ 1  0  0  0 ]
    [ 0  0  1  0 ]
    [ 0 -1  0  0 ]
    [ 0  0  0  1 ]

## Points, pivots and poses

The asset's stated pivot remains its datum: floor origin for ordinary furniture, soil origin for plants, deck surface for coping/entry, and explicitly proposed design datum for a float. A float design waterline is not a solved buoyant equilibrium. A pose centre may lie in an intentional opening; it must be distinguished from adjacent physical support/contact points.

For a source-frame point p, the intended exchange-world point is C·p. Named source-part local points must first be transformed through their source object hierarchy into the asset source frame. Do not transform already-exported GLB vertex or node coordinates a second time.

The exporter may bake basis changes into vertices or represent them through node transforms. The actual GLB node hierarchy is authoritative. Resolve node matrices/TRS and parents, then transform local vertex positions through that hierarchy. Validation must compare these actual file positions with converted source records, rather than assuming every individual node contains an identical basis rotation.

If expressing the same abstract world transform in the other coordinate basis, use T_glb = C·T_source·C⁻¹. Rotations are transformed as bases/quaternions, not by swapping Euler components. Directions and normals omit translation. Under non-uniform placement scale, normals require the inverse-transpose linear transform; the basis C itself is orthonormal.

## Collision and connection proposals

Collision files are proposals in the frame stated by their file or asset manifest. Convert capsule endpoints, centres, vertices, grip/mount points and connector normals with the same basis as the visual geometry. Transform all eight corners when deriving a bounding box; do not assume source AABB bounds remain valid after arbitrary placement rotation. Preserve positive radii/lengths and recompute world bounds.

Connection positions and tangents must be interpreted together. Source yaw about +Z maps to rotation about GLB +Y with the equivalent handedness under C. A mirrored derivative must bake and validate its geometry/normals explicitly; it is not a new artistic asset or permission to ignore negative-scale culling.

These records do not certify collisions, character fit, animation, water behavior or game-side interactions. Consumers must retain stable asset IDs, explicit frame labels and the imported node transforms. Never mix source-space contact values with GLB-space mesh values without conversion.

## Evidence

Batch05's independent coordinate checks bind representative pivot, seat/grip/mount and prior-family records to actual GLB node/mesh data, with wrong-axis negative controls. The report states whether each marker is a physical contact, an origin or a pose/opening datum. No engine scene is required for this exchange-level proof; engine adoption remains a later gate.

## Versioned staff cabinet metadata

The current AST-STF-007 cabinet uses metadata revision `hinge-frame-metadata-02` in its actual source and GLB hinge node. It has explicit `hinge_axis_blender_source` (+Z), `hinge_axis_gltf_yup` (+Y), and corresponding named pivot fields. The unqualified `axis` string has been removed. Both frames retain the same negative opening rotation sense.

The source pivot is (−0.837, −0.317, 0.200) m. The GLB pivot is (−0.837, 0.200, 0.317) m. Future consumers can read these explicit fields from the actual asset rather than depending on an external erratum. The generator reproduces the same metadata.

Earlier backed-up cabinet versions retained a descriptive `extras.axis` string saying “Local +Z, negative rotation opens outward”. That archived text described the Blender source frame, not the native GLB axis. `standards/coordinate_compatibility.json` identifies this historical interpretation for consumers of those older versions. Previous backups remain unchanged; the current source/export revision is versioned and has explicit metadata.

The metadata revision preserves all source geometry, material graphs, packed images, object transforms/modifiers and scene units, and preserves the GLB binary payload and JSON outside the intended node extras. Independent actual-node rotation checks establish the correct transformed axis. No new render or engine validation is implied.
