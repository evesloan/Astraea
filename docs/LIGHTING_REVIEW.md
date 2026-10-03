# Atrium lighting integration review, October 3

The current renderer remains Godot 4.6.3 Compatibility. The world/post stack is unchanged except for a 32-bit positional-shadow atlas, selected for the current long-range court review. Its atlas resolution remains 2048. No target-PC frame-rate or memory acceptance is claimed.

## What was actually checked

Cloud llvmpipe captures compared lights on/off, shadow toggles, caster groups, shadow depth, and local versus high-mounted sources inside the running ship. These were diagnostic captures, not replacement scenes or final quality approvals. The initial high-mounted spotlights gave negligible dependable court illumination in these views. Increasing their energy, changing bias and raising per-object light limits did not resolve that appearance. The experimental per-object limit was reverted.

The broad artificial ceiling coffers now use two shadowed OmniLight3D sources with supported cubemap shadows. Their in-engine captures illuminate the court; 32-bit shadow depth and tuned bias reduced visible floor banding. Dual-paraboloid mode was rejected by the Compatibility renderer during a test and is not used. The exact cause of the prior spotlight behavior has not been established.

Ten original garden lanterns supply human-scale path lighting. Their emitters sit below the optical housing and clear the stem. Four requested shadowed approach lights and six explicitly unshadowed, short-range open-court sources form the initial arrangement. Four planted-island uplights have real housings inside the soil bed. They are not unexplained world lights.

A source budget selects at most eight requested shadowed lights around the player. Unselected shadowed sources are disabled rather than converted to wall-leaking unshadowed lights; their visible fixture geometry remains. This preliminary budget needs movement/fade and target-hardware review. It is not whole-ship sector streaming or a completed scalable lighting system.

The garden is readable, but upper terraces remain largely unfinished and their bright edges need integration with actual room fronts, ceilings and occupied destinations. The current result does not meet the final hospitality quality benchmark.

## Primary technical references

- Godot 4.6 lights/shadows, including Compatibility multipass appearance differences: https://docs.godotengine.org/en/4.6/tutorials/3d/lights_and_shadows.html
- Renderer feature differences: https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html

These references explain engine behavior generally; they do not prove the cause of this scene's diagnostic results.
