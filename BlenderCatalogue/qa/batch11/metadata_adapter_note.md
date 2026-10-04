# Catalogue metadata adapter

The first lead aggregation stopped before publishing because the staff author schema uses `title` and `bounds_blender_z_up.dimensions_m`, while the guest schema also supplies `name` and `dimensions_blender_xyz_m`. The lead adapter now recognizes those exact two documented schemas. Original independently reviewed manifests and source/export hashes remain unchanged; no image or source rebuild is needed. Unknown schemas still fail rather than inventing a name or dimension.

The first index-promotion command named a corrections file not emitted by this review, and stopped before writing the canonical index. This batch uses the actual independently produced `independent_interface_coverage_map.json` as its normalization/evidence mapping. That file contains the source/native marker checks and bindings; no additional declaration correction is invented. The successful promotion verifies all183 current source/export/manifest bindings.
