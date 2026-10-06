# Source preview spotlight convention correction

The first architectural preview used a cone too narrow to represent the project’s fixtures. Godot’s `spot_angle` is the cone’s angular radius, from its axis to its edge. [Official SpotLight3D documentation](https://docs.godotengine.org/en/stable/classes/class_spotlight3d.html).

Blender’s `spot_size` describes the full cone; its source gizmo uses `cos(0.5 * spotsize)`. [Official Blender source](https://github.com/blender/blender/blob/main/source/blender/editors/space_view3d/view3d_gizmo_light.cc).

The corrected source-preview expression is `math.radians(2 * source_angle_degrees)`. No source fixture contract, native runtime light, shared light selector, colour, energy or test tolerance is changed. The project’s actual physics/selection gates already used the correct cosine-of-angular-radius convention.

Preserve the first source PNGs and report as a rejected lighting-preview interpretation. They are not evidence that the in-game alcoves are correctly or incorrectly lit. The corrected render still uses an explicitly recorded Cycles watt mapping and all recorded source origins; it does not reproduce Godot’s eight-active-source selection or target hardware and cannot replace native review.
