# Astraea — integrated construction delivery

This package runs the existing default ship with all 83 received section keys, all 80 retained Group 2 homes, the 177 shopping chunks (99 shops and 78 connections), and 88 Group 7 models registered in one scene. Major physical packages across all eight groups and the protected Family D13–D15 and Quiet Grove D13–D16 connections are included. Distant destinations use the existing residency and streaming systems; they are not all rendered at once.

## Run

Extract the entire ZIP to a normal local folder. On Windows x64, double-click `Launch-Astraea.cmd`. On Linux x64, run `sh Launch-Astraea.sh`; if your archive tool drops executable permissions, make the bundled Linux engine executable first. Both launchers run the included Godot 4.6.3 engine and `Astraea.pck`; no editor import or project reconstruction is required. Keep the engine folder and PCK together.

Startup loads substantial construction data and can take several minutes. The measured headless scene uses roughly 12 GiB of memory; target-device graphical memory and performance have not been accepted. This is a construction build, not an optimized game release.

## Controls

WASD moves, mouse looks, Space jumps, right mouse focuses, and E interacts with supported aimed objects. Escape releases the mouse. M opens the existing express directory; F4 toggles the existing visual effects. Existing inactive or locked systems remain inactive or locked.

## What is unfinished

Inclusion is separate from finished architecture and gameplay. D17's proposed identity/placement allocation remains unapproved. The unfinished Family D16 survey was preserved but is not installed construction. Structural/pressure/load acceptance, some shared service interfaces, staff/private authorizations and authoritative room mappings, tram/water operations, loaded carts, species interactions, stock/save workflows, and final lighting/art remain open. No capacity or room identity was created for this delivery. No new pixel review or Windows hardware acceptance is claimed.

## Sources and evidence

Production source is retained in the private evesloan/Astraea repository on `construction/group1-tidal-d15-20261010`. The construction baseline is `32268435ecbb5380f81e96e695c5103212a07139`. The delivery checkpoint adds the inclusion audit, packaging preset and evidence; original native models remain retained in Git. The package contains runtime data, not duplicated native-source archives.

`DELIVERY_MANIFEST.json` records hashes of the delivered runtime and engines. Validation receipts distinguish source-scene inclusion from the same check run against the exported PCK. These checks do not establish full physics, gameplay, graphical performance or final visual acceptance.

## Rebuilding the package

The ordinary export alone is insufficient for this project: startup integrity guards require raw GLB/texture bytes, original import parameters and selected retained validation receipts. The recorded `export_pack.py` and `repack_with_sources.gd` procedure preserves the exported resource paths and model payloads, then adds those exact dependencies. `PACK_SOURCE_PINS.json`, `EXPORTED_RESOURCE_PINS.json` and `IMPORT_METADATA_PINS.json` record the package inputs. `verify_pack.gd` verifies them before loading the default scene. The scripts record the production workspace paths used for this delivery. Do not bypass guards to make a standard stripped export start.
