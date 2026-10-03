# Rendering direction

Owner requested more refined light/glow while preserving early-2000s low-poly/pixel presentation (2026-10-03). Keep Godot4.6.3 Compatibility baseline. Version4.6 provides simplified SSAO (radius/intensity) and Compatibility glow (limited controls). Use actual direct lights at fixtures; emission/glow is not room illumination. Start with bounded adjustable glow and contact shading, inspect moving silhouettes and effects-off captures; do not imply feature enablement is visual acceptance.

References: https://docs.godotengine.org/en/4.6/tutorials/3d/environment_and_post_processing.html and https://docs.godotengine.org/en/4.6/classes/class_environment.html

Current status: direction verified in documentation, not yet authored or visually tested in the empty production entry scene.

## Local identity (owner update 2026-10-03)

Guest lighting varies by purpose and supported species needs: calm residential approaches, warm social gathering, focused library tasks and gentle aquatic light. Avoid a ship-wide yellow grade. Cold staff work areas use clinical controlled light and economical infrastructure; Aperture Science is an architectural/lighting inspiration, not a requirement to reproduce assets or make spaces unusably dark. Keep activity visibility and accessibility. Expose fixture color, energy, range, shadows and zone ambience independently; glow is restrained and optional. Species-specific biological lighting needs remain undefined unless supported by canon.
