# Shared focus interaction foundation

Hold RMB for a slight zoom and pixel-cluster reticle, then press E at the actual target. The existing camera ray remains the single selection path, with a 2.5 m reach; it now includes authored Area3D controls as well as physical bodies. The first hit wins, so solid architecture blocks selection.

Implemented examples:
- D01 food-synthesis two-leaf service door, including occupied-sweep inhibition
- D09 salon shared-study task fixture, with a 36 mm-diameter selection volume at its imported POINT_toggle datum

The reading fixture changes both its local optical source and its instance-local diffuser emission. The shadow budget respects the fixture's power state and cannot turn a switched-off light back on. Source materials shared by other fixtures are not mutated. A source outside the shadow budget may remain unlit even when switched on; this remains an explicit preliminary rendering constraint.

The task fixture has the stable authored identity D09_salon5_shared_study_light. Current state is in memory only. This is not saved-game persistence, a complete electrical simulation, or permission to treat static furniture as usable.

Automated checks cover precise camera selection from a usable approach, RMB/E off, unfocused E rejection, diffuser state, repeated budget refreshes, power restoration and selection blocked by solid geometry. Graphical review captures the same player position with the reading light on and off. Focus blur/depth-of-field remains pending.
