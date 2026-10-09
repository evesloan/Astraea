# Shared crew home construction successor

9 October 2026. Additive enclosure, return connector, linen shelving and wash basin for the existing D03 employee home programme. Two retained AST-CRW-001 rest frames, AST-CRW-002 privacy curtains, AST-CRW-003 personal stores and AST-CRW-004 reading shelves are placed by Game/scripts/shared_crew_home.gd. Their original editable Blender sources remain in crew_rest and crew_personal.

The installed dogleg's actual exit is north-facing at Z=-423, X[-42.8,-39.2]. A new north/east return reaches the proposed bedroom without cutting that retained source. All new construction uses the existing D03_protected_crew_cover at Y12; no floor is exported or duplicated. Ceiling underside is Y15.2, top Y15.34. New walls subtract retained wall footprints; roof excludes retained cap footprints. No below-floor plumbing penetrations are created.

source/prepare_shared_home.py regenerates the new geometry specification using Shapely 2.1.2. source/build_shared_home.py builds editable semantic solids and exports the enclosure with Blender 4.3.2. Both derive paths from the retained project layout. Staff materials are the unchanged catalogue materials. Geometry and fixture datums use world Godot metres, converted to Blender Z-up for authoring.

Two physical resting places are constructed. No NPC, person, berth key, save assignment or capacity migration is invented. The selected eventual C036 migration still requires the actual retained person/berth keys. This does not complete 400 crew berths.

Static curtain and drawer states are installed. Live privacy controls, drawers, wet fixture operation, enclosed shower/toilet facilities, species suitability, sound insulation, complete traversal and final visual acceptance remain unfinished. Shelves use their source-specified bed mount (-0.26,0.88,-2.14) in Godot coordinates.
