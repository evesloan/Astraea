# WP09 Custodial depot — isolated source candidate

Blender4.3.2; CPU12threads. All paths resolve inside this unpacked package. Bundled exact native dependencies and original texture files are SHA-checked before authoring. No Game, catalogue, global registry or runtime writes.

Build: `blender --background --factory-startup --threads 12 --python source/build_section.py`

Independent reopen/export checks: `blender --background --threads 12 --python source/review_section.py`

Eye-level source renders: `blender --background --threads 12 --python source/review_section.py -- --render 01_arrival,03_cart_spine,04_cart_work,05_ready_stock,06_textile_receiving,07_used_carriers,08_overhead_support --samples 24`

Build and review require the coordinator's serialized heavy-job slot. Runtime adoption remains pending. See docs/BRIEF.md, plan_contract.json, reference_evidence.json and dependencies.json. Source floor and parking paint are excluded from GLB; receiving floor/contact adoption belongs Higgins.
