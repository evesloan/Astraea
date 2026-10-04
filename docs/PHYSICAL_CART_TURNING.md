# Physical cart turning through starboard house returns

The geometric perimeter clearance test covered564 cart/load/operator poses, but did not establish physical steering. The first driven route failed: the single rear-point force grip pushed the cart sideways toward the south wall rather than reliably turning its nose.

The cart now applies a bounded two-handed handle yaw couple while held and grounded. It uses a spring/damper error against the driver's horizontal facing:60Nm/radian stiffness,14Nm damping and55Nm maximum torque. No body orientation is snapped; pitch, roll, translation, collisions and the four loose products remain physical. Releasing the handle removes this steering input. The common loose-object tether is unchanged.

The new test moves the actual collision capsule at1m/s and steers its view through the planned turns. The cart follows through applied forces and torque. After initial setup, the test never sets the cart or product transforms. Forward pushing and backward pulling both pass onD14 andD16, retain allfour products and end near the expected route endpoints. This is a bounded scripted physical route, not freehand mouse/keyboard feel or ship-wide clearance acceptance.

The lower torque trial did not fully align the cart at the destination; the final spring/damper configuration passes both directions. Existing cleaning, pickup/release, loaded boarding and lift carry checks remain required in aggregate regression.

Final aggregate check on2026-10-04: all46 current regression groups passed142.6821seconds fixed60. Both forward/backward D14 andD16 physical steering routes are included. No rendering-performance or freehand-input claim follows from this timing.
