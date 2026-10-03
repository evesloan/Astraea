# Production status — 3 October 2026

Godot cloud restart, not recovered original code.

Implemented: single main entry and 640x360 world with native HUD; restrained ordered dithering and optional scanlines; F4 toggles display effects including glow/SSAO; first-person movement/slight RMB zoom; 18 structural datum outlines and provisional atrium strips; one provisional D09 terrace footprint; imported cove/day-use/plant assets; actual fixture lights; source-preserving static contact meshes.

Verified: Godot4.6.3 Compatibility runs on cloud desktop using llvmpipe software OpenGL. Source assets render; native640x360 captures saved. Headless tests confirm supported D09 spawn, source cove mate offset,18datums and viewport size. No target GPU performance or audio acceptance (dummy audio fallback).

Not complete: hull shell, real district/room allocation, connected18deck traversal, final terrace architecture, ceilings/doors/glass, cart/cleaning/persistence/guests. Structural ribbons are planning representation, not finished balconies. Temporary boundary guards keep the currently supported floor bounded. No room counted complete.

Next: finish source review and author structural fit/connected circulation before propagating rooms. Remove generic datum overlaps as each authored surface takes ownership. Expand Blender catalogue from actual missing component needs.

Backup: source baseline9caa948 is independently retained in Library and clean-restore tested; newer scene work requires another checkpoint. Automatic Workshop copy not yet established. Unity changeset3 retained separately.
