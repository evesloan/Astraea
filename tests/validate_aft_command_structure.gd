extends SceneTree
# Geometric construction contacts in the real main scene, never load certification.
# Parent is responsible for refreshed Godot imports and executing this regression.
const CONTRACT := "res://data/architecture/AFT_COMMAND_RUNTIME.json"
const ASSET := "res://assets/models/AST-CMD-002.glb"
const SOURCE_EXPORT_SHA256 := "c7543f3c9bb6e1284511175f33dd559b5f2ca5eaf025899e66ac2d2230f962ce"
const IMPORTED_TRIANGLE_SHA256 := "b06b0c131258b880515e344e94e7acba0e3018b19d86aa8fdca1f9c3692ea129"
const SOURCE_CONTRACT_SHA256 := "67d51cfd88bfafbaf18b896ceb66e980892ea01d382ce405e9dd3a0b9602e6af"
const SOURCE_PARTS_SHA256 := "0a45051363fb93baa9b6e33cc7d979fe8693da2059fd3c4c716d1b726707bed0"
const EXPECTED_BATCHES := 196
const EXPECTED_TRIANGLES := 12216
const EXPECTED_STRUCTURAL_PARTS := 542
const MAX_RESULTS := 256
const EPS := 0.001
const FLOOR_Y := 106.5
const SLAB_BOTTOM := 106.26
const FLOOR_IDS := ["D18_aft_command_port_floor", "D18_aft_command_starboard_floor"]
const LINK_X := [-35.5, -32.0, -5.04, 0.0, 5.04, 32.0, 35.5]
const HANGER_X := [-35.5, -5.04, 5.04, 35.5]
const BEARER_Z := [82.0, 86.0, 90.0, 94.0, 98.0, 101.7]
# FROZEN_STRUCTURAL_PARTS_BEGIN
# Replaced only after source/export equivalence review. Each row is name/group/AABB.
const STRUCTURAL_PARTS_JSON := """[
["AFC_RoofCeiling","roof",[-36,-24,111,111.16,64,72]],
["AFC_RoofCeiling.001","roof",[-36,-24,111,111.16,72,84]],
["AFC_RoofCeiling.002","roof",[-36,-24,111,111.16,84,96]],
["AFC_RoofCeiling.003","roof",[-36,-24,111,111.16,96,102]],
["AFC_RoofCeiling.004","roof",[-24,-12,111,111.16,64,72]],
["AFC_RoofCeiling.005","roof",[-24,-12,111,111.16,72,84]],
["AFC_RoofCeiling.006","roof",[-24,-12,111,111.16,84,96]],
["AFC_RoofCeiling.007","roof",[-24,-12,111,111.16,96,102]],
["AFC_RoofCeiling.008","roof",[-12,0,111,111.16,64,72]],
["AFC_RoofCeiling.009","roof",[-12,0,111,111.16,72,84]],
["AFC_RoofCeiling.010","roof",[-12,0,111,111.16,84,96]],
["AFC_RoofCeiling.011","roof",[-12,0,111,111.16,96,102]],
["AFC_RoofCeiling.012","roof",[0,12,111,111.16,64,72]],
["AFC_RoofCeiling.013","roof",[0,12,111,111.16,72,84]],
["AFC_RoofCeiling.014","roof",[0,12,111,111.16,84,96]],
["AFC_RoofCeiling.015","roof",[0,12,111,111.16,96,102]],
["AFC_RoofCeiling.016","roof",[12,24,111,111.16,64,72]],
["AFC_RoofCeiling.017","roof",[12,24,111,111.16,72,84]],
["AFC_RoofCeiling.018","roof",[12,24,111,111.16,84,96]],
["AFC_RoofCeiling.019","roof",[12,24,111,111.16,96,102]],
["AFC_RoofCeiling.020","roof",[24,36,111,111.16,64,72]],
["AFC_RoofCeiling.021","roof",[24,36,111,111.16,72,84]],
["AFC_RoofCeiling.022","roof",[24,36,111,111.16,84,96]],
["AFC_RoofCeiling.023","roof",[24,36,111,111.16,96,102]],
["AFC_SteppedRoofSkin","roof",[-12,0,114.24,114.44,64,72]],
["AFC_SteppedRoofSkin.001","roof",[-12,0,114.24,114.44,72,84]],
["AFC_SteppedRoofSkin.002","roof",[-12,0,114.24,114.44,84,96]],
["AFC_SteppedRoofSkin.003","roof",[-12,0,114.24,114.44,96,102]],
["AFC_SteppedRoofSkin.004","roof",[0,12,114.24,114.44,64,72]],
["AFC_SteppedRoofSkin.005","roof",[0,12,114.24,114.44,72,84]],
["AFC_SteppedRoofSkin.006","roof",[0,12,114.24,114.44,84,96]],
["AFC_SteppedRoofSkin.007","roof",[0,12,114.24,114.44,96,102]],
["AFC_SteppedRoofSkin.008","roof",[-24,-12,114.06,114.26,64,72]],
["AFC_SteppedRoofSkin.009","roof",[-24,-12,114.06,114.26,72,84]],
["AFC_SteppedRoofSkin.010","roof",[-24,-12,114.06,114.26,84,96]],
["AFC_SteppedRoofSkin.011","roof",[-24,-12,114.06,114.26,96,102]],
["AFC_RoofStepReturn","roof",[-12.08,-12,114.06,114.44000000000001,64,72]],
["AFC_RoofStepReturn.001","roof",[-12.08,-12,114.06,114.44000000000001,72,84]],
["AFC_RoofStepReturn.002","roof",[-12.08,-12,114.06,114.44000000000001,84,96]],
["AFC_RoofStepReturn.003","roof",[-12.08,-12,114.06,114.44000000000001,96,102]],
["AFC_RoofStepReturn.004","roof",[-12,-11.92,114.06,114.44000000000001,64,72]],
["AFC_RoofStepReturn.005","roof",[-12,-11.92,114.06,114.44000000000001,72,84]],
["AFC_RoofStepReturn.006","roof",[-12,-11.92,114.06,114.44000000000001,84,96]],
["AFC_RoofStepReturn.007","roof",[-12,-11.92,114.06,114.44000000000001,96,102]],
["AFC_SteppedRoofSkin.012","roof",[12,24,114.06,114.26,64,72]],
["AFC_SteppedRoofSkin.013","roof",[12,24,114.06,114.26,72,84]],
["AFC_SteppedRoofSkin.014","roof",[12,24,114.06,114.26,84,96]],
["AFC_SteppedRoofSkin.015","roof",[12,24,114.06,114.26,96,102]],
["AFC_RoofStepReturn.008","roof",[11.92,12,114.06,114.44000000000001,64,72]],
["AFC_RoofStepReturn.009","roof",[11.92,12,114.06,114.44000000000001,72,84]],
["AFC_RoofStepReturn.010","roof",[11.92,12,114.06,114.44000000000001,84,96]],
["AFC_RoofStepReturn.011","roof",[11.92,12,114.06,114.44000000000001,96,102]],
["AFC_RoofStepReturn.012","roof",[12,12.08,114.06,114.44000000000001,64,72]],
["AFC_RoofStepReturn.013","roof",[12,12.08,114.06,114.44000000000001,72,84]],
["AFC_RoofStepReturn.014","roof",[12,12.08,114.06,114.44000000000001,84,96]],
["AFC_RoofStepReturn.015","roof",[12,12.08,114.06,114.44000000000001,96,102]],
["AFC_SteppedRoofSkin.016","roof",[-36,-24,113.84,114.04,64,72]],
["AFC_SteppedRoofSkin.017","roof",[-36,-24,113.84,114.04,72,84]],
["AFC_SteppedRoofSkin.018","roof",[-36,-24,113.84,114.04,84,96]],
["AFC_SteppedRoofSkin.019","roof",[-36,-24,113.84,114.04,96,102]],
["AFC_RoofStepReturn.016","roof",[-24.08,-24,113.84,114.22000000000001,64,72]],
["AFC_RoofStepReturn.017","roof",[-24.08,-24,113.84,114.22000000000001,72,84]],
["AFC_RoofStepReturn.018","roof",[-24.08,-24,113.84,114.22000000000001,84,96]],
["AFC_RoofStepReturn.019","roof",[-24.08,-24,113.84,114.22000000000001,96,102]],
["AFC_RoofStepReturn.020","roof",[-24,-23.92,113.84,114.22000000000001,64,72]],
["AFC_RoofStepReturn.021","roof",[-24,-23.92,113.84,114.22000000000001,72,84]],
["AFC_RoofStepReturn.022","roof",[-24,-23.92,113.84,114.22000000000001,84,96]],
["AFC_RoofStepReturn.023","roof",[-24,-23.92,113.84,114.22000000000001,96,102]],
["AFC_SteppedRoofSkin.020","roof",[24,36,113.84,114.04,64,72]],
["AFC_SteppedRoofSkin.021","roof",[24,36,113.84,114.04,72,84]],
["AFC_SteppedRoofSkin.022","roof",[24,36,113.84,114.04,84,96]],
["AFC_SteppedRoofSkin.023","roof",[24,36,113.84,114.04,96,102]],
["AFC_RoofStepReturn.024","roof",[23.92,24,113.84,114.22000000000001,64,72]],
["AFC_RoofStepReturn.025","roof",[23.92,24,113.84,114.22000000000001,72,84]],
["AFC_RoofStepReturn.026","roof",[23.92,24,113.84,114.22000000000001,84,96]],
["AFC_RoofStepReturn.027","roof",[23.92,24,113.84,114.22000000000001,96,102]],
["AFC_RoofStepReturn.028","roof",[24,24.08,113.84,114.22000000000001,64,72]],
["AFC_RoofStepReturn.029","roof",[24,24.08,113.84,114.22000000000001,72,84]],
["AFC_RoofStepReturn.030","roof",[24,24.08,113.84,114.22000000000001,84,96]],
["AFC_RoofStepReturn.031","roof",[24,24.08,113.84,114.22000000000001,96,102]],
["AFC_RoofOuterFascia","roof",[-36,-35.84,111.16,113.84,64,72]],
["AFC_RoofOuterFascia.001","roof",[-36,-35.84,111.16,113.84,72,84]],
["AFC_RoofOuterFascia.002","roof",[-36,-35.84,111.16,113.84,84,96]],
["AFC_RoofOuterFascia.003","roof",[-36,-35.84,111.16,113.84,96,102]],
["AFC_RoofOuterFascia.004","roof",[35.84,36,111.16,113.84,64,72]],
["AFC_RoofOuterFascia.005","roof",[35.84,36,111.16,113.84,72,84]],
["AFC_RoofOuterFascia.006","roof",[35.84,36,111.16,113.84,84,96]],
["AFC_RoofOuterFascia.007","roof",[35.84,36,111.16,113.84,96,102]],
["AFC_RoofAftFascia","roof",[-12,0,111.16,114.24,101.84,102]],
["AFC_RoofAftFascia.001","roof",[0,12,111.16,114.24,101.84,102]],
["AFC_RoofAftFascia.002","roof",[-24,-12,111.16,114.06,101.84,102]],
["AFC_RoofAftFascia.003","roof",[12,24,111.16,114.06,101.84,102]],
["AFC_RoofAftFascia.004","roof",[-36,-24,111.16,113.84,101.84,102]],
["AFC_RoofAftFascia.005","roof",[24,36,111.16,113.84,101.84,102]],
["AFC_Pier_Port_Web_00","pier",[-35.82,-35.18,-3.2,0,85.48,86.52]],
["AFC_Pier_Port_Chord","pier",[-35.9,-35.8,-3.2,0,85.4,86.6]],
["AFC_Pier_Port_Chord.001","pier",[-35.2,-35.1,-3.2,0,85.4,86.6]],
["AFC_Pier_Port_Collar_00","pier",[-35.9,-35.1,-3.2,-3.0,85.4,86.6]],
["AFC_Pier_Port_Web_01","pier",[-35.82,-35.18,0,6,85.48,86.52]],
["AFC_Pier_Port_Chord.002","pier",[-35.9,-35.8,0,6,85.4,86.6]],
["AFC_Pier_Port_Chord.003","pier",[-35.2,-35.1,0,6,85.4,86.6]],
["AFC_Pier_Port_Collar_01","pier",[-35.9,-35.1,0,0.2,85.4,86.6]],
["AFC_Pier_Port_Web_02","pier",[-35.82,-35.18,6,12,85.48,86.52]],
["AFC_Pier_Port_Chord.004","pier",[-35.9,-35.8,6,12,85.4,86.6]],
["AFC_Pier_Port_Chord.005","pier",[-35.2,-35.1,6,12,85.4,86.6]],
["AFC_Pier_Port_Collar_02","pier",[-35.9,-35.1,6,6.2,85.4,86.6]],
["AFC_Pier_Port_Web_03","pier",[-35.82,-35.18,12,16.5,85.48,86.52]],
["AFC_Pier_Port_Chord.006","pier",[-35.9,-35.8,12,16.5,85.4,86.6]],
["AFC_Pier_Port_Chord.007","pier",[-35.2,-35.1,12,16.5,85.4,86.6]],
["AFC_Pier_Port_Collar_03","pier",[-35.9,-35.1,12,12.2,85.4,86.6]],
["AFC_Pier_Port_Web_04","pier",[-35.82,-35.18,16.5,21,85.48,86.52]],
["AFC_Pier_Port_Chord.008","pier",[-35.9,-35.8,16.5,21,85.4,86.6]],
["AFC_Pier_Port_Chord.009","pier",[-35.2,-35.1,16.5,21,85.4,86.6]],
["AFC_Pier_Port_Collar_04","pier",[-35.9,-35.1,16.5,16.7,85.4,86.6]],
["AFC_Pier_Port_Web_05","pier",[-35.82,-35.18,21,24,85.48,86.52]],
["AFC_Pier_Port_Web_05.001","pier",[-35.82,-35.18,24,27,85.48,86.52]],
["AFC_Pier_Port_Chord.010","pier",[-35.9,-35.8,21,24,85.4,86.6]],
["AFC_Pier_Port_Chord.011","pier",[-35.9,-35.8,24,27,85.4,86.6]],
["AFC_Pier_Port_Chord.012","pier",[-35.2,-35.1,21,24,85.4,86.6]],
["AFC_Pier_Port_Chord.013","pier",[-35.2,-35.1,24,27,85.4,86.6]],
["AFC_Pier_Port_Collar_05","pier",[-35.9,-35.1,21,21.2,85.4,86.6]],
["AFC_Pier_Port_Web_06","pier",[-35.82,-35.18,27,35.5,85.48,86.52]],
["AFC_Pier_Port_Chord.014","pier",[-35.9,-35.8,27,35.5,85.4,86.6]],
["AFC_Pier_Port_Chord.015","pier",[-35.2,-35.1,27,35.5,85.4,86.6]],
["AFC_Pier_Port_Collar_06","pier",[-35.9,-35.1,27,27.2,85.4,86.6]],
["AFC_Pier_Port_Web_07","pier",[-35.82,-35.18,35.5,36,85.48,86.52]],
["AFC_Pier_Port_Web_07.001","pier",[-35.82,-35.18,36,44,85.48,86.52]],
["AFC_Pier_Port_Chord.016","pier",[-35.9,-35.8,35.5,36,85.4,86.6]],
["AFC_Pier_Port_Chord.017","pier",[-35.9,-35.8,36,44,85.4,86.6]],
["AFC_Pier_Port_Chord.018","pier",[-35.2,-35.1,35.5,36,85.4,86.6]],
["AFC_Pier_Port_Chord.019","pier",[-35.2,-35.1,36,44,85.4,86.6]],
["AFC_Pier_Port_Collar_07","pier",[-35.9,-35.1,35.5,35.7,85.4,86.6]],
["AFC_Pier_Port_Web_08","pier",[-35.82,-35.18,44,48,85.48,86.52]],
["AFC_Pier_Port_Web_08.001","pier",[-35.82,-35.18,48,52.5,85.48,86.52]],
["AFC_Pier_Port_Chord.020","pier",[-35.9,-35.8,44,48,85.4,86.6]],
["AFC_Pier_Port_Chord.021","pier",[-35.9,-35.8,48,52.5,85.4,86.6]],
["AFC_Pier_Port_Chord.022","pier",[-35.2,-35.1,44,48,85.4,86.6]],
["AFC_Pier_Port_Chord.023","pier",[-35.2,-35.1,48,52.5,85.4,86.6]],
["AFC_Pier_Port_Collar_08","pier",[-35.9,-35.1,44,44.2,85.4,86.6]],
["AFC_Pier_Port_Web_09","pier",[-35.82,-35.18,52.5,60,85.48,86.52]],
["AFC_Pier_Port_Web_09.001","pier",[-35.82,-35.18,60,61,85.48,86.52]],
["AFC_Pier_Port_Chord.024","pier",[-35.9,-35.8,52.5,60,85.4,86.6]],
["AFC_Pier_Port_Chord.025","pier",[-35.9,-35.8,60,61,85.4,86.6]],
["AFC_Pier_Port_Chord.026","pier",[-35.2,-35.1,52.5,60,85.4,86.6]],
["AFC_Pier_Port_Chord.027","pier",[-35.2,-35.1,60,61,85.4,86.6]],
["AFC_Pier_Port_Collar_09","pier",[-35.9,-35.1,52.5,52.7,85.4,86.6]],
["AFC_Pier_Port_Web_10","pier",[-35.82,-35.18,61,69.5,85.48,86.52]],
["AFC_Pier_Port_Chord.028","pier",[-35.9,-35.8,61,69.5,85.4,86.6]],
["AFC_Pier_Port_Chord.029","pier",[-35.2,-35.1,61,69.5,85.4,86.6]],
["AFC_Pier_Port_Collar_10","pier",[-35.9,-35.1,61,61.2,85.4,86.6]],
["AFC_Pier_Port_Web_11","pier",[-35.82,-35.18,69.5,72,85.48,86.52]],
["AFC_Pier_Port_Web_11.001","pier",[-35.82,-35.18,72,78,85.48,86.52]],
["AFC_Pier_Port_Chord.030","pier",[-35.9,-35.8,69.5,72,85.4,86.6]],
["AFC_Pier_Port_Chord.031","pier",[-35.9,-35.8,72,78,85.4,86.6]],
["AFC_Pier_Port_Chord.032","pier",[-35.2,-35.1,69.5,72,85.4,86.6]],
["AFC_Pier_Port_Chord.033","pier",[-35.2,-35.1,72,78,85.4,86.6]],
["AFC_Pier_Port_Collar_11","pier",[-35.9,-35.1,69.5,69.7,85.4,86.6]],
["AFC_Pier_Port_Web_12","pier",[-35.82,-35.18,78,84,85.48,86.52]],
["AFC_Pier_Port_Chord.034","pier",[-35.9,-35.8,78,84,85.4,86.6]],
["AFC_Pier_Port_Chord.035","pier",[-35.2,-35.1,78,84,85.4,86.6]],
["AFC_Pier_Port_Collar_12","pier",[-35.9,-35.1,78,78.2,85.4,86.6]],
["AFC_Pier_Port_Web_13","pier",[-35.82,-35.18,84,88.5,85.48,86.52]],
["AFC_Pier_Port_Chord.036","pier",[-35.9,-35.8,84,88.5,85.4,86.6]],
["AFC_Pier_Port_Chord.037","pier",[-35.2,-35.1,84,88.5,85.4,86.6]],
["AFC_Pier_Port_Collar_13","pier",[-35.9,-35.1,84,84.2,85.4,86.6]],
["AFC_Pier_Port_Web_14","pier",[-35.82,-35.18,88.5,93,85.48,86.52]],
["AFC_Pier_Port_Chord.038","pier",[-35.9,-35.8,88.5,93,85.4,86.6]],
["AFC_Pier_Port_Chord.039","pier",[-35.2,-35.1,88.5,93,85.4,86.6]],
["AFC_Pier_Port_Collar_14","pier",[-35.9,-35.1,88.5,88.7,85.4,86.6]],
["AFC_Pier_Port_Web_15","pier",[-35.82,-35.18,93,96,85.48,86.52]],
["AFC_Pier_Port_Web_15.001","pier",[-35.82,-35.18,96,97.5,85.48,86.52]],
["AFC_Pier_Port_Chord.040","pier",[-35.9,-35.8,93,96,85.4,86.6]],
["AFC_Pier_Port_Chord.041","pier",[-35.9,-35.8,96,97.5,85.4,86.6]],
["AFC_Pier_Port_Chord.042","pier",[-35.2,-35.1,93,96,85.4,86.6]],
["AFC_Pier_Port_Chord.043","pier",[-35.2,-35.1,96,97.5,85.4,86.6]],
["AFC_Pier_Port_Collar_15","pier",[-35.9,-35.1,93,93.2,85.4,86.6]],
["AFC_Pier_Port_Web_16","pier",[-35.82,-35.18,97.5,102,85.48,86.52]],
["AFC_Pier_Port_Chord.044","pier",[-35.9,-35.8,97.5,102,85.4,86.6]],
["AFC_Pier_Port_Chord.045","pier",[-35.2,-35.1,97.5,102,85.4,86.6]],
["AFC_Pier_Port_Collar_16","pier",[-35.9,-35.1,97.5,97.7,85.4,86.6]],
["AFC_Pier_Port_Web_17","pier",[-35.82,-35.18,102,106.5,85.48,86.52]],
["AFC_Pier_Port_Chord.046","pier",[-35.9,-35.8,102,106.5,85.4,86.6]],
["AFC_Pier_Port_Chord.047","pier",[-35.2,-35.1,102,106.5,85.4,86.6]],
["AFC_Pier_Port_Collar_17","pier",[-35.9,-35.1,102,102.2,85.4,86.6]],
["AFC_Pier_Port_Web_18","pier",[-35.82,-35.18,106.5,108,85.48,86.52]],
["AFC_Pier_Port_Web_18.001","pier",[-35.82,-35.18,108,111,85.48,86.52]],
["AFC_Pier_Port_Chord.048","pier",[-35.9,-35.8,106.5,108,85.4,86.6]],
["AFC_Pier_Port_Chord.049","pier",[-35.9,-35.8,108,111,85.4,86.6]],
["AFC_Pier_Port_Chord.050","pier",[-35.2,-35.1,106.5,108,85.4,86.6]],
["AFC_Pier_Port_Chord.051","pier",[-35.2,-35.1,108,111,85.4,86.6]],
["AFC_Pier_Port_Collar_18","pier",[-35.9,-35.1,106.5,106.7,85.4,86.6]],
["AFC_Pier_Port_Web_19","pier",[-35.82,-35.18,111,114,85.48,86.52]],
["AFC_Pier_Port_Chord.052","pier",[-35.9,-35.8,111,114,85.4,86.6]],
["AFC_Pier_Port_Chord.053","pier",[-35.2,-35.1,111,114,85.4,86.6]],
["AFC_Pier_Port_Collar_19","pier",[-35.9,-35.1,111,111.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_00","pier",[35.18,35.82,-3.2,0,85.48,86.52]],
["AFC_Pier_Starboard_Chord","pier",[35.1,35.2,-3.2,0,85.4,86.6]],
["AFC_Pier_Starboard_Chord.001","pier",[35.8,35.9,-3.2,0,85.4,86.6]],
["AFC_Pier_Starboard_Collar_00","pier",[35.1,35.9,-3.2,-3.0,85.4,86.6]],
["AFC_Pier_Starboard_Web_01","pier",[35.18,35.82,0,6,85.48,86.52]],
["AFC_Pier_Starboard_Chord.002","pier",[35.1,35.2,0,6,85.4,86.6]],
["AFC_Pier_Starboard_Chord.003","pier",[35.8,35.9,0,6,85.4,86.6]],
["AFC_Pier_Starboard_Collar_01","pier",[35.1,35.9,0,0.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_02","pier",[35.18,35.82,6,12,85.48,86.52]],
["AFC_Pier_Starboard_Chord.004","pier",[35.1,35.2,6,12,85.4,86.6]],
["AFC_Pier_Starboard_Chord.005","pier",[35.8,35.9,6,12,85.4,86.6]],
["AFC_Pier_Starboard_Collar_02","pier",[35.1,35.9,6,6.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_03","pier",[35.18,35.82,12,16.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.006","pier",[35.1,35.2,12,16.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.007","pier",[35.8,35.9,12,16.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_03","pier",[35.1,35.9,12,12.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_04","pier",[35.18,35.82,16.5,21,85.48,86.52]],
["AFC_Pier_Starboard_Chord.008","pier",[35.1,35.2,16.5,21,85.4,86.6]],
["AFC_Pier_Starboard_Chord.009","pier",[35.8,35.9,16.5,21,85.4,86.6]],
["AFC_Pier_Starboard_Collar_04","pier",[35.1,35.9,16.5,16.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_05","pier",[35.18,35.82,21,24,85.48,86.52]],
["AFC_Pier_Starboard_Web_05.001","pier",[35.18,35.82,24,27,85.48,86.52]],
["AFC_Pier_Starboard_Chord.010","pier",[35.1,35.2,21,24,85.4,86.6]],
["AFC_Pier_Starboard_Chord.011","pier",[35.1,35.2,24,27,85.4,86.6]],
["AFC_Pier_Starboard_Chord.012","pier",[35.8,35.9,21,24,85.4,86.6]],
["AFC_Pier_Starboard_Chord.013","pier",[35.8,35.9,24,27,85.4,86.6]],
["AFC_Pier_Starboard_Collar_05","pier",[35.1,35.9,21,21.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_06","pier",[35.18,35.82,27,35.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.014","pier",[35.1,35.2,27,35.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.015","pier",[35.8,35.9,27,35.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_06","pier",[35.1,35.9,27,27.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_07","pier",[35.18,35.82,35.5,36,85.48,86.52]],
["AFC_Pier_Starboard_Web_07.001","pier",[35.18,35.82,36,44,85.48,86.52]],
["AFC_Pier_Starboard_Chord.016","pier",[35.1,35.2,35.5,36,85.4,86.6]],
["AFC_Pier_Starboard_Chord.017","pier",[35.1,35.2,36,44,85.4,86.6]],
["AFC_Pier_Starboard_Chord.018","pier",[35.8,35.9,35.5,36,85.4,86.6]],
["AFC_Pier_Starboard_Chord.019","pier",[35.8,35.9,36,44,85.4,86.6]],
["AFC_Pier_Starboard_Collar_07","pier",[35.1,35.9,35.5,35.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_08","pier",[35.18,35.82,44,48,85.48,86.52]],
["AFC_Pier_Starboard_Web_08.001","pier",[35.18,35.82,48,52.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.020","pier",[35.1,35.2,44,48,85.4,86.6]],
["AFC_Pier_Starboard_Chord.021","pier",[35.1,35.2,48,52.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.022","pier",[35.8,35.9,44,48,85.4,86.6]],
["AFC_Pier_Starboard_Chord.023","pier",[35.8,35.9,48,52.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_08","pier",[35.1,35.9,44,44.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_09","pier",[35.18,35.82,52.5,60,85.48,86.52]],
["AFC_Pier_Starboard_Web_09.001","pier",[35.18,35.82,60,61,85.48,86.52]],
["AFC_Pier_Starboard_Chord.024","pier",[35.1,35.2,52.5,60,85.4,86.6]],
["AFC_Pier_Starboard_Chord.025","pier",[35.1,35.2,60,61,85.4,86.6]],
["AFC_Pier_Starboard_Chord.026","pier",[35.8,35.9,52.5,60,85.4,86.6]],
["AFC_Pier_Starboard_Chord.027","pier",[35.8,35.9,60,61,85.4,86.6]],
["AFC_Pier_Starboard_Collar_09","pier",[35.1,35.9,52.5,52.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_10","pier",[35.18,35.82,61,69.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.028","pier",[35.1,35.2,61,69.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.029","pier",[35.8,35.9,61,69.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_10","pier",[35.1,35.9,61,61.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_11","pier",[35.18,35.82,69.5,72,85.48,86.52]],
["AFC_Pier_Starboard_Web_11.001","pier",[35.18,35.82,72,78,85.48,86.52]],
["AFC_Pier_Starboard_Chord.030","pier",[35.1,35.2,69.5,72,85.4,86.6]],
["AFC_Pier_Starboard_Chord.031","pier",[35.1,35.2,72,78,85.4,86.6]],
["AFC_Pier_Starboard_Chord.032","pier",[35.8,35.9,69.5,72,85.4,86.6]],
["AFC_Pier_Starboard_Chord.033","pier",[35.8,35.9,72,78,85.4,86.6]],
["AFC_Pier_Starboard_Collar_11","pier",[35.1,35.9,69.5,69.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_12","pier",[35.18,35.82,78,84,85.48,86.52]],
["AFC_Pier_Starboard_Chord.034","pier",[35.1,35.2,78,84,85.4,86.6]],
["AFC_Pier_Starboard_Chord.035","pier",[35.8,35.9,78,84,85.4,86.6]],
["AFC_Pier_Starboard_Collar_12","pier",[35.1,35.9,78,78.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_13","pier",[35.18,35.82,84,88.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.036","pier",[35.1,35.2,84,88.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.037","pier",[35.8,35.9,84,88.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_13","pier",[35.1,35.9,84,84.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_14","pier",[35.18,35.82,88.5,93,85.48,86.52]],
["AFC_Pier_Starboard_Chord.038","pier",[35.1,35.2,88.5,93,85.4,86.6]],
["AFC_Pier_Starboard_Chord.039","pier",[35.8,35.9,88.5,93,85.4,86.6]],
["AFC_Pier_Starboard_Collar_14","pier",[35.1,35.9,88.5,88.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_15","pier",[35.18,35.82,93,96,85.48,86.52]],
["AFC_Pier_Starboard_Web_15.001","pier",[35.18,35.82,96,97.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.040","pier",[35.1,35.2,93,96,85.4,86.6]],
["AFC_Pier_Starboard_Chord.041","pier",[35.1,35.2,96,97.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.042","pier",[35.8,35.9,93,96,85.4,86.6]],
["AFC_Pier_Starboard_Chord.043","pier",[35.8,35.9,96,97.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_15","pier",[35.1,35.9,93,93.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_16","pier",[35.18,35.82,97.5,102,85.48,86.52]],
["AFC_Pier_Starboard_Chord.044","pier",[35.1,35.2,97.5,102,85.4,86.6]],
["AFC_Pier_Starboard_Chord.045","pier",[35.8,35.9,97.5,102,85.4,86.6]],
["AFC_Pier_Starboard_Collar_16","pier",[35.1,35.9,97.5,97.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_17","pier",[35.18,35.82,102,106.5,85.48,86.52]],
["AFC_Pier_Starboard_Chord.046","pier",[35.1,35.2,102,106.5,85.4,86.6]],
["AFC_Pier_Starboard_Chord.047","pier",[35.8,35.9,102,106.5,85.4,86.6]],
["AFC_Pier_Starboard_Collar_17","pier",[35.1,35.9,102,102.2,85.4,86.6]],
["AFC_Pier_Starboard_Web_18","pier",[35.18,35.82,106.5,108,85.48,86.52]],
["AFC_Pier_Starboard_Web_18.001","pier",[35.18,35.82,108,111,85.48,86.52]],
["AFC_Pier_Starboard_Chord.048","pier",[35.1,35.2,106.5,108,85.4,86.6]],
["AFC_Pier_Starboard_Chord.049","pier",[35.1,35.2,108,111,85.4,86.6]],
["AFC_Pier_Starboard_Chord.050","pier",[35.8,35.9,106.5,108,85.4,86.6]],
["AFC_Pier_Starboard_Chord.051","pier",[35.8,35.9,108,111,85.4,86.6]],
["AFC_Pier_Starboard_Collar_18","pier",[35.1,35.9,106.5,106.7,85.4,86.6]],
["AFC_Pier_Starboard_Web_19","pier",[35.18,35.82,111,114,85.48,86.52]],
["AFC_Pier_Starboard_Chord.052","pier",[35.1,35.2,111,114,85.4,86.6]],
["AFC_Pier_Starboard_Chord.053","pier",[35.8,35.9,111,114,85.4,86.6]],
["AFC_Pier_Starboard_Collar_19","pier",[35.1,35.9,111,111.2,85.4,86.6]],
["AFC_TransferGirder_Web","transfer",[-35.5,-24,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Web.001","transfer",[-24,-12,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Web.002","transfer",[-12,0,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Web.003","transfer",[0,12,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Web.004","transfer",[12,24,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Web.005","transfer",[24,35.5,111.4,113.82,85.82,86.18]],
["AFC_TransferGirder_Flange","transfer",[-35.5,-24,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.001","transfer",[-24,-12,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.002","transfer",[-12,0,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.003","transfer",[0,12,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.004","transfer",[12,24,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.005","transfer",[24,35.5,111.25,111.43,85.45,86.55]],
["AFC_TransferGirder_Flange.006","transfer",[-35.5,-24,113.82,114.0,85.45,86.55]],
["AFC_TransferGirder_Flange.007","transfer",[-24,-12,113.82,114.0,85.45,86.55]],
["AFC_TransferGirder_Flange.008","transfer",[-12,0,113.82,114.0,85.45,86.55]],
["AFC_TransferGirder_Flange.009","transfer",[0,12,113.82,114.0,85.45,86.55]],
["AFC_TransferGirder_Flange.010","transfer",[12,24,113.82,114.0,85.45,86.55]],
["AFC_TransferGirder_Flange.011","transfer",[24,35.5,113.82,114.0,85.45,86.55]],
["AFC_Longitudinal_Web","transfer",[-35.66,-35.34,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.001","transfer",[-35.66,-35.34,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.002","transfer",[-35.66,-35.34,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.003","transfer",[-35.66,-35.34,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange","transfer",[-35.8,-35.2,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.001","transfer",[-35.8,-35.2,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.002","transfer",[-35.8,-35.2,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.003","transfer",[-35.8,-35.2,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.004","transfer",[-35.8,-35.2,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.005","transfer",[-35.8,-35.2,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.006","transfer",[-35.8,-35.2,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.007","transfer",[-35.8,-35.2,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.004","transfer",[-32.16,-31.84,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.005","transfer",[-32.16,-31.84,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.006","transfer",[-32.16,-31.84,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.007","transfer",[-32.16,-31.84,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.008","transfer",[-32.3,-31.7,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.009","transfer",[-32.3,-31.7,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.010","transfer",[-32.3,-31.7,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.011","transfer",[-32.3,-31.7,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.012","transfer",[-32.3,-31.7,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.013","transfer",[-32.3,-31.7,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.014","transfer",[-32.3,-31.7,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.015","transfer",[-32.3,-31.7,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.008","transfer",[-5.2,-4.88,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.009","transfer",[-5.2,-4.88,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.010","transfer",[-5.2,-4.88,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.011","transfer",[-5.2,-4.88,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.016","transfer",[-5.34,-4.74,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.017","transfer",[-5.34,-4.74,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.018","transfer",[-5.34,-4.74,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.019","transfer",[-5.34,-4.74,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.020","transfer",[-5.34,-4.74,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.021","transfer",[-5.34,-4.74,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.022","transfer",[-5.34,-4.74,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.023","transfer",[-5.34,-4.74,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.012","transfer",[-0.16,0,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.013","transfer",[-0.16,0,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.014","transfer",[-0.16,0,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.015","transfer",[-0.16,0,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Web.016","transfer",[0,0.16,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.017","transfer",[0,0.16,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.018","transfer",[0,0.16,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.019","transfer",[0,0.16,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.024","transfer",[-0.3,0,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.025","transfer",[-0.3,0,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.026","transfer",[-0.3,0,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.027","transfer",[-0.3,0,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.028","transfer",[0,0.3,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.029","transfer",[0,0.3,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.030","transfer",[0,0.3,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.031","transfer",[0,0.3,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.032","transfer",[-0.3,0,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.033","transfer",[-0.3,0,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.034","transfer",[-0.3,0,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.035","transfer",[-0.3,0,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Flange.036","transfer",[0,0.3,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.037","transfer",[0,0.3,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.038","transfer",[0,0.3,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.039","transfer",[0,0.3,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.020","transfer",[4.88,5.2,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.021","transfer",[4.88,5.2,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.022","transfer",[4.88,5.2,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.023","transfer",[4.88,5.2,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.040","transfer",[4.74,5.34,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.041","transfer",[4.74,5.34,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.042","transfer",[4.74,5.34,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.043","transfer",[4.74,5.34,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.044","transfer",[4.74,5.34,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.045","transfer",[4.74,5.34,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.046","transfer",[4.74,5.34,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.047","transfer",[4.74,5.34,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.024","transfer",[31.84,32.16,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.025","transfer",[31.84,32.16,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.026","transfer",[31.84,32.16,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.027","transfer",[31.84,32.16,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.048","transfer",[31.7,32.3,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.049","transfer",[31.7,32.3,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.050","transfer",[31.7,32.3,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.051","transfer",[31.7,32.3,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.052","transfer",[31.7,32.3,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.053","transfer",[31.7,32.3,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.054","transfer",[31.7,32.3,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.055","transfer",[31.7,32.3,113.7,113.9,96,101.84]],
["AFC_Longitudinal_Web.028","transfer",[35.34,35.66,111.1,113.8,70.8,72]],
["AFC_Longitudinal_Web.029","transfer",[35.34,35.66,111.1,113.8,72,84]],
["AFC_Longitudinal_Web.030","transfer",[35.34,35.66,111.1,113.8,84,96]],
["AFC_Longitudinal_Web.031","transfer",[35.34,35.66,111.1,113.8,96,101.84]],
["AFC_Longitudinal_Flange.056","transfer",[35.2,35.8,111.1,111.3,70.8,72]],
["AFC_Longitudinal_Flange.057","transfer",[35.2,35.8,111.1,111.3,72,84]],
["AFC_Longitudinal_Flange.058","transfer",[35.2,35.8,111.1,111.3,84,96]],
["AFC_Longitudinal_Flange.059","transfer",[35.2,35.8,111.1,111.3,96,101.84]],
["AFC_Longitudinal_Flange.060","transfer",[35.2,35.8,113.7,113.9,70.8,72]],
["AFC_Longitudinal_Flange.061","transfer",[35.2,35.8,113.7,113.9,72,84]],
["AFC_Longitudinal_Flange.062","transfer",[35.2,35.8,113.7,113.9,84,96]],
["AFC_Longitudinal_Flange.063","transfer",[35.2,35.8,113.7,113.9,96,101.84]],
["AFC_ForwardPurlinSaddle","transfer",[-32.22,-31.78,113.05,113.85,65.72,66.28]],
["AFC_ForwardPurlinSaddle.001","transfer",[-0.22,0,113.05,113.85,65.72,66.28]],
["AFC_ForwardPurlinSaddle.002","transfer",[0,0.22,113.05,113.85,65.72,66.28]],
["AFC_ForwardPurlinSaddle.003","transfer",[31.78,32.22,113.05,113.85,65.72,66.28]],
["AFC_RoofPurlin","roof",[-35.84,-24,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.001","roof",[-24,-12,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.002","roof",[-12,0,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.003","roof",[0,12,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.004","roof",[12,24,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.005","roof",[24,35.84,113.76,114.27,65.9,66.1]],
["AFC_RoofPurlin.006","roof",[-35.84,-24,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.007","roof",[-24,-12,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.008","roof",[-12,0,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.009","roof",[0,12,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.010","roof",[12,24,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.011","roof",[24,35.84,113.76,114.27,73.9,74.1]],
["AFC_RoofPurlin.012","roof",[-35.84,-24,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.013","roof",[-24,-12,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.014","roof",[-12,0,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.015","roof",[0,12,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.016","roof",[12,24,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.017","roof",[24,35.84,113.76,114.27,81.9,82.1]],
["AFC_RoofPurlin.018","roof",[-35.84,-24,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.019","roof",[-24,-12,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.020","roof",[-12,0,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.021","roof",[0,12,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.022","roof",[12,24,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.023","roof",[24,35.84,113.76,114.27,89.9,90.1]],
["AFC_RoofPurlin.024","roof",[-35.84,-24,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.025","roof",[-24,-12,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.026","roof",[-12,0,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.027","roof",[0,12,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.028","roof",[12,24,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.029","roof",[24,35.84,113.76,114.27,97.9,98.1]],
["AFC_RoofPurlin.030","roof",[-35.84,-24,113.76,114.27,101.7,101.89999999999999]],
["AFC_RoofPurlin.031","roof",[-24,-12,113.76,114.27,101.7,101.89999999999999]],
["AFC_RoofPurlin.032","roof",[-12,0,113.76,114.27,101.7,101.89999999999999]],
["AFC_RoofPurlin.033","roof",[0,12,113.76,114.27,101.7,101.89999999999999]],
["AFC_RoofPurlin.034","roof",[12,24,113.76,114.27,101.7,101.89999999999999]],
["AFC_RoofPurlin.035","roof",[24,35.84,113.76,114.27,101.7,101.89999999999999]],
["AFC_Hanger_X-35p5_Z86","hanger",[-35.6,-35.4,106.05,108,85.82,86.18]],
["AFC_Hanger_X-35p5_Z86.001","hanger",[-35.6,-35.4,108,113.82,85.82,86.18]],
["AFC_Hanger_X-35p5_Z98","hanger",[-35.6,-35.4,106.05,108,97.82,98.18]],
["AFC_Hanger_X-35p5_Z98.001","hanger",[-35.6,-35.4,108,113.82,97.82,98.18]],
["AFC_Hanger_X-5p04_Z86","hanger",[-5.14,-4.94,106.05,108,85.82,86.18]],
["AFC_Hanger_X-5p04_Z86.001","hanger",[-5.14,-4.94,108,113.82,85.82,86.18]],
["AFC_Hanger_X-5p04_Z98","hanger",[-5.14,-4.94,106.05,108,97.82,98.18]],
["AFC_Hanger_X-5p04_Z98.001","hanger",[-5.14,-4.94,108,113.82,97.82,98.18]],
["AFC_Hanger_X5p04_Z86","hanger",[4.94,5.14,106.05,108,85.82,86.18]],
["AFC_Hanger_X5p04_Z86.001","hanger",[4.94,5.14,108,113.82,85.82,86.18]],
["AFC_Hanger_X5p04_Z98","hanger",[4.94,5.14,106.05,108,97.82,98.18]],
["AFC_Hanger_X5p04_Z98.001","hanger",[4.94,5.14,108,113.82,97.82,98.18]],
["AFC_Hanger_X35p5_Z86","hanger",[35.4,35.6,106.05,108,85.82,86.18]],
["AFC_Hanger_X35p5_Z86.001","hanger",[35.4,35.6,108,113.82,85.82,86.18]],
["AFC_Hanger_X35p5_Z98","hanger",[35.4,35.6,106.05,108,97.82,98.18]],
["AFC_Hanger_X35p5_Z98.001","hanger",[35.4,35.6,108,113.82,97.82,98.18]],
["AFC_FloorEdgeGirder_Web","platform_support",[-35.62,-35.38,105.84,106.27,79.8,84]],
["AFC_FloorEdgeGirder_Web.001","platform_support",[-35.62,-35.38,105.84,106.27,84,96]],
["AFC_FloorEdgeGirder_Web.002","platform_support",[-35.62,-35.38,105.84,106.27,96,102]],
["AFC_FloorEdgeGirder_Flange","platform_support",[-35.78,-35.22,105.84,105.96000000000001,79.8,84]],
["AFC_FloorEdgeGirder_Flange.001","platform_support",[-35.78,-35.22,105.84,105.96000000000001,84,96]],
["AFC_FloorEdgeGirder_Flange.002","platform_support",[-35.78,-35.22,105.84,105.96000000000001,96,102]],
["AFC_FloorEdgeGirder_Flange.003","platform_support",[-35.78,-35.22,106.16,106.28,79.8,84]],
["AFC_FloorEdgeGirder_Flange.004","platform_support",[-35.78,-35.22,106.16,106.28,84,96]],
["AFC_FloorEdgeGirder_Flange.005","platform_support",[-35.78,-35.22,106.16,106.28,96,102]],
["AFC_FloorEdgeGirder_Web.003","platform_support",[-5.16,-4.92,105.84,106.27,79.8,84]],
["AFC_FloorEdgeGirder_Web.004","platform_support",[-5.16,-4.92,105.84,106.27,84,96]],
["AFC_FloorEdgeGirder_Web.005","platform_support",[-5.16,-4.92,105.84,106.27,96,102]],
["AFC_FloorEdgeGirder_Flange.006","platform_support",[-5.32,-4.76,105.84,105.96000000000001,79.8,84]],
["AFC_FloorEdgeGirder_Flange.007","platform_support",[-5.32,-4.76,105.84,105.96000000000001,84,96]],
["AFC_FloorEdgeGirder_Flange.008","platform_support",[-5.32,-4.76,105.84,105.96000000000001,96,102]],
["AFC_FloorEdgeGirder_Flange.009","platform_support",[-5.32,-4.76,106.16,106.28,79.8,84]],
["AFC_FloorEdgeGirder_Flange.010","platform_support",[-5.32,-4.76,106.16,106.28,84,96]],
["AFC_FloorEdgeGirder_Flange.011","platform_support",[-5.32,-4.76,106.16,106.28,96,102]],
["AFC_FloorEdgeGirder_Web.006","platform_support",[4.92,5.16,105.84,106.27,79.8,84]],
["AFC_FloorEdgeGirder_Web.007","platform_support",[4.92,5.16,105.84,106.27,84,96]],
["AFC_FloorEdgeGirder_Web.008","platform_support",[4.92,5.16,105.84,106.27,96,102]],
["AFC_FloorEdgeGirder_Flange.012","platform_support",[4.76,5.32,105.84,105.96000000000001,79.8,84]],
["AFC_FloorEdgeGirder_Flange.013","platform_support",[4.76,5.32,105.84,105.96000000000001,84,96]],
["AFC_FloorEdgeGirder_Flange.014","platform_support",[4.76,5.32,105.84,105.96000000000001,96,102]],
["AFC_FloorEdgeGirder_Flange.015","platform_support",[4.76,5.32,106.16,106.28,79.8,84]],
["AFC_FloorEdgeGirder_Flange.016","platform_support",[4.76,5.32,106.16,106.28,84,96]],
["AFC_FloorEdgeGirder_Flange.017","platform_support",[4.76,5.32,106.16,106.28,96,102]],
["AFC_FloorEdgeGirder_Web.009","platform_support",[35.38,35.62,105.84,106.27,79.8,84]],
["AFC_FloorEdgeGirder_Web.010","platform_support",[35.38,35.62,105.84,106.27,84,96]],
["AFC_FloorEdgeGirder_Web.011","platform_support",[35.38,35.62,105.84,106.27,96,102]],
["AFC_FloorEdgeGirder_Flange.018","platform_support",[35.22,35.78,105.84,105.96000000000001,79.8,84]],
["AFC_FloorEdgeGirder_Flange.019","platform_support",[35.22,35.78,105.84,105.96000000000001,84,96]],
["AFC_FloorEdgeGirder_Flange.020","platform_support",[35.22,35.78,105.84,105.96000000000001,96,102]],
["AFC_FloorEdgeGirder_Flange.021","platform_support",[35.22,35.78,106.16,106.28,79.8,84]],
["AFC_FloorEdgeGirder_Flange.022","platform_support",[35.22,35.78,106.16,106.28,84,96]],
["AFC_FloorEdgeGirder_Flange.023","platform_support",[35.22,35.78,106.16,106.28,96,102]],
["AFC_PlatformCrossBearer","platform_support",[-36,-24,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.001","platform_support",[-24,-12,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.002","platform_support",[-12,-4,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.003","platform_support",[4,12,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.004","platform_support",[12,24,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.005","platform_support",[24,36,105.88,106.28,81.88,82.12]],
["AFC_PlatformCrossBearer.006","platform_support",[-36,-24,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.007","platform_support",[-24,-12,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.008","platform_support",[-12,-4,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.009","platform_support",[4,12,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.010","platform_support",[12,24,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.011","platform_support",[24,36,105.88,106.28,85.88,86.12]],
["AFC_PlatformCrossBearer.012","platform_support",[-36,-24,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.013","platform_support",[-24,-12,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.014","platform_support",[-12,-4,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.015","platform_support",[4,12,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.016","platform_support",[12,24,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.017","platform_support",[24,36,105.88,106.28,89.88,90.12]],
["AFC_PlatformCrossBearer.018","platform_support",[-36,-24,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.019","platform_support",[-24,-12,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.020","platform_support",[-12,-4,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.021","platform_support",[4,12,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.022","platform_support",[12,24,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.023","platform_support",[24,36,105.88,106.28,93.88,94.12]],
["AFC_PlatformCrossBearer.024","platform_support",[-36,-24,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.025","platform_support",[-24,-12,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.026","platform_support",[-12,-4,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.027","platform_support",[4,12,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.028","platform_support",[12,24,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.029","platform_support",[24,36,105.88,106.28,97.88,98.12]],
["AFC_PlatformCrossBearer.030","platform_support",[-36,-24,105.88,106.28,101.58,101.82000000000001]],
["AFC_PlatformCrossBearer.031","platform_support",[-24,-12,105.88,106.28,101.58,101.82000000000001]],
["AFC_PlatformCrossBearer.032","platform_support",[-12,-4,105.88,106.28,101.58,101.82000000000001]],
["AFC_PlatformCrossBearer.033","platform_support",[4,12,105.88,106.28,101.58,101.82000000000001]],
["AFC_PlatformCrossBearer.034","platform_support",[12,24,105.88,106.28,101.58,101.82000000000001]],
["AFC_PlatformCrossBearer.035","platform_support",[24,36,105.88,106.28,101.58,101.82000000000001]],
["AFC_ApronTie_X-35p5","tie",[-35.72,-35.28,106.08,106.4,79.8,80.25]],
["AFC_ApronTie_X-5p04","tie",[-5.26,-4.82,106.08,106.4,79.8,80.25]],
["AFC_ApronTie_X5p04","tie",[4.82,5.26,106.08,106.4,79.8,80.25]],
["AFC_ApronTie_X35p5","tie",[35.28,35.72,106.08,106.4,79.8,80.25]]
]"""
# FROZEN_STRUCTURAL_PARTS_END
var failures: Array[String] = []
var space: PhysicsDirectSpaceState3D
var ship: Node3D
var crown: Node3D
var shell: Node3D
var old_shell: Node3D
var floors: Node3D
var crown_exclusions: Array[RID] = []
var own_exclusions: Array[RID] = []
var shell_only_exclusions: Array[RID] = []
var dynamic_exclusions: Array[RID] = []
var all_faces := PackedVector3Array()
var vertex_triangles: Dictionary = {}
var structural_parts: Array[Dictionary] = []
var support_count := 0
var slice_count := 0
var opening_count := 0
var floor_contact_count := 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, detail: String) -> bool:
	if not condition:
		failures.append(detail)
		push_error("AFT COMMAND STRUCTURE FAIL: " + detail)
	return condition

func read_json(path: String) -> Dictionary:
	if not check(FileAccess.file_exists(path), "Required construction evidence absent: " + path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not check(parsed is Dictionary, "Invalid JSON object: " + path):
		return {}
	return parsed

func ray(start: Vector3, finish: Vector3, excluded: Array[RID]) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(start, finish)
	query.exclude = excluded
	return space.intersect_ray(query)

func box_hits(bounds: AABB, excluded: Array[RID], label: String) -> Array[Dictionary]:
	var shape := BoxShape3D.new()
	shape.size = bounds.size
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.margin = 0.0005
	query.transform.origin = bounds.get_center()
	query.exclude = excluded
	var hits := space.intersect_shape(query, MAX_RESULTS)
	check(hits.size() < MAX_RESULTS, label + ": collision result capacity saturated")
	return hits

func owner(hit: Dictionary) -> String:
	return "<no contact>" if hit.is_empty() else str(hit.collider.get_path())

func region_id(body: Node) -> String:
	var node := body
	while node != null:
		if node.has_meta("region_id"):
			return str(node.get_meta("region_id"))
		node = node.get_parent()
	return ""

func contract_box(values: Array) -> AABB:
	return AABB(Vector3(values[0], values[2], values[4]),
		Vector3(values[1] - values[0], values[3] - values[2], values[5] - values[4]))

func vertex_key(vertex: Vector3) -> String:
	return "%d,%d,%d" % [roundi(vertex.x * 1000), roundi(vertex.y * 1000), roundi(vertex.z * 1000)]

func geometry_signature(faces: PackedVector3Array) -> String:
	var triangles := PackedStringArray()
	for index in range(0, faces.size(), 3):
		var corners := PackedStringArray()
		for offset in range(3):
			corners.append(vertex_key(faces[index + offset]))
		corners.sort()
		triangles.append("|".join(corners))
	triangles.sort()
	return "\n".join(triangles).sha256_text()

func contact_extent(a: AABB, b: AABB) -> Vector3:
	return a.end.min(b.end) - a.position.max(b.position)

func has_face_contact(a: AABB, b: AABB) -> bool:
	# A line/point touch is insufficient. Face bearing or positive embed is required.
	var overlap := contact_extent(a, b)
	var positive_axes := int(overlap.x > EPS) + int(overlap.y > EPS) + int(overlap.z > EPS)
	return overlap.x >= -EPS and overlap.y >= -EPS and overlap.z >= -EPS and positive_axes >= 2

func validate_meshes() -> void:
	var minimum := Vector3(INF, INF, INF)
	var maximum := Vector3(-INF, -INF, -INF)
	var meshes := shell.find_children("AFC_CELL_*", "MeshInstance3D", true, false)
	check(meshes.size() == EXPECTED_BATCHES, "Source batch count changed: observed %d expected %d" % [meshes.size(), EXPECTED_BATCHES])
	check(shell.find_children("*", "MeshInstance3D", true, false).size() == EXPECTED_BATCHES,
		"Unexpected additional architecture meshes, possibly a duplicate source floor")
	for node in meshes:
		var mesh := node as MeshInstance3D
		if not check(mesh.mesh != null and mesh.is_visible_in_tree(), "Missing/hidden architecture batch " + str(mesh.name)):
			continue
		var local_faces := mesh.mesh.get_faces()
		check(not local_faces.is_empty() and local_faces.size() % 3 == 0, "Empty/invalid triangles in " + str(mesh.name))
		for vertex in local_faces:
			var world_vertex: Vector3 = mesh.global_transform * vertex
			all_faces.append(world_vertex)
			minimum = minimum.min(world_vertex)
			maximum = maximum.max(world_vertex)
		var contact := mesh.get_node_or_null("StaticContact/SharedShape") as CollisionShape3D
		if check(contact != null and not contact.disabled, "Missing active concave collision for " + str(mesh.name)):
			var body := contact.get_parent() as StaticBody3D
			check(body != null and body.collision_layer != 0, "Architecture contact needs an active static physics owner: " + str(mesh.name))
			check(contact.shape is ConcavePolygonShape3D, "Architecture contact must use real surface triangles: " + str(mesh.name))
			if contact.shape is ConcavePolygonShape3D:
				check(contact.shape.get_faces() == local_faces, "Render/contact triangle mismatch: " + str(mesh.name))
				check(contact.global_transform.is_equal_approx(mesh.global_transform), "Collision transform differs from source mesh: " + str(mesh.name))
	check(all_faces.size() == EXPECTED_TRIANGLES * 3, "Imported triangle count changed: %d" % (all_faces.size() / 3))
	check(geometry_signature(all_faces) == IMPORTED_TRIANGLE_SHA256,
		"Actual world-space triangles differ from final verified GLB; stale import, moved shell or changed source")
	check(minimum.distance_to(Vector3(-36.0, -3.2, 62.79)) < EPS, "Actual source minimum bounds changed: " + str(minimum))
	check(maximum.distance_to(Vector3(36, 114.44, 102)) < EPS, "Actual source maximum bounds changed: " + str(maximum))
	for index in range(0, all_faces.size(), 3):
		for offset in range(3):
			var key := vertex_key(all_faces[index + offset])
			if not vertex_triangles.has(key):
				vertex_triangles[key] = []
			vertex_triangles[key].append(index)

func face_is_complete(masks: Dictionary, corner_ids: Array[int]) -> bool:
	if corner_ids.size() != 4:
		return false
	# Natural bit order is A=(0,0), B=(0,1), C=(1,0), D=(1,1).
	# Only complementary diagonal halves cover a rectangle. Two triangles that
	# share an outside edge overlap and leave a hole even if their areas add up.
	var a := 1 << corner_ids[0]
	var b := 1 << corner_ids[1]
	var c := 1 << corner_ids[2]
	var d := 1 << corner_ids[3]
	return (masks.has(a | b | c) and masks.has(b | c | d)) or (masks.has(a | b | d) and masks.has(a | c | d))

func validate_coverage_predicate() -> void:
	var ids: Array[int] = [0, 1, 2, 3]
	check(face_is_complete({7: true, 14: true}, ids), "Coverage predicate must accept complete B-C diagonal halves")
	check(face_is_complete({11: true, 13: true}, ids), "Coverage predicate must accept complete A-D diagonal halves")
	check(not face_is_complete({7: true}, ids), "Coverage predicate must reject a missing triangle half")
	var duplicate_halves: Dictionary = {}
	for mask in [7, 7]:
		duplicate_halves[mask] = true
	check(not face_is_complete(duplicate_halves, ids), "Coverage predicate must reject duplicated copies of the same half")
	check(not face_is_complete({7: true, 11: true}, ids), "Coverage predicate must reject overlapping outside-edge halves")

func validate_real_box(bounds: AABB, label: String) -> bool:
	# Every frozen member is recovered from real imported triangles. A marker or
	# batch AABB never establishes construction. The final GLB signature remains
	# exact at the established 1mm corner precision, and contact triangles must
	# be identical to the imported render triangles.
	var corners: Dictionary = {}
	var candidates: Dictionary = {}
	for ix in range(2):
		for iy in range(2):
			for iz in range(2):
				var point := bounds.position + bounds.size * Vector3(ix, iy, iz)
				var key := vertex_key(point)
				corners[key] = {"position": point, "id": ix * 4 + iy * 2 + iz}
				for index in vertex_triangles.get(key, []):
					candidates[index] = true
	var used_corners: Dictionary = {}
	var face_masks: Array[Dictionary] = [{}, {}, {}, {}, {}, {}]
	var count := 0
	var maximum_corner_error := 0.0
	for index in candidates:
		var keys := [vertex_key(all_faces[index]), vertex_key(all_faces[index + 1]), vertex_key(all_faces[index + 2])]
		if not (corners.has(keys[0]) and corners.has(keys[1]) and corners.has(keys[2])):
			continue
		var corner_ids: Array[int] = []
		var triangle_mask := 0
		for offset in range(3):
			var corner: Dictionary = corners[keys[offset]]
			corner_ids.append(int(corner.id))
			triangle_mask |= 1 << int(corner.id)
			maximum_corner_error = maxf(maximum_corner_error, all_faces[index + offset].distance_to(corner.position))
		var on_surface := false
		for axis in range(3):
			var axis_bit := 1 << (2 - axis)
			for endpoint in range(2):
				var expected_bits := axis_bit * endpoint
				if (corner_ids[0] & axis_bit) == expected_bits and (corner_ids[1] & axis_bit) == expected_bits and (corner_ids[2] & axis_bit) == expected_bits:
					face_masks[axis * 2 + endpoint][triangle_mask] = true
					on_surface = true
		if on_surface:
			count += 1
			for key in keys:
				used_corners[key] = true
	# Import compression can move a coordinate by <1mm. For an 80mm-wide
	# return, that changes measured area proportionally much more than for a
	# broad panel. Test complete triangle coverage, not a fragile scalar-area
	# tolerance. Each plane still needs both actual complementary halves.
	var coverage: Array[bool] = []
	for axis in range(3):
		var axis_bit := 1 << (2 - axis)
		for endpoint in range(2):
			var face_corners: Array[int] = []
			for corner_id in range(8):
				if (corner_id & axis_bit) == axis_bit * endpoint:
					face_corners.append(corner_id)
			coverage.append(face_is_complete(face_masks[axis * 2 + endpoint], face_corners))
	return check(count >= 12 and used_corners.size() == 8 and not coverage.has(false) and maximum_corner_error < EPS,
		"Built member needs eight real corners and complementary triangles covering all six faces: %s got %d triangles/%d corners, face coverage %s, max corner error %.6fm" % [label, count, used_corners.size(), str(coverage), maximum_corner_error])

func validate_members_and_graph() -> void:
	var definitions: Array = JSON.parse_string(STRUCTURAL_PARTS_JSON)
	check(definitions.size() == EXPECTED_STRUCTURAL_PARTS, "Frozen structural member inventory changed")
	var groups: Dictionary = {}
	for definition in definitions:
		var bounds := contract_box(definition[2])
		var valid := validate_real_box(bounds, str(definition[0]))
		structural_parts.append({"name": str(definition[0]), "group": str(definition[1]), "bounds": bounds, "valid": valid})
		groups[str(definition[1])] = int(groups.get(str(definition[1]), 0)) + 1
	for group in ["pier", "transfer", "roof", "hanger", "platform_support", "tie"]:
		check(groups.has(group), "Missing real structural member family: " + group)
	var edges: Array = []
	var connected: Dictionary = {}
	var pending: Array[int] = []
	for index in range(structural_parts.size()):
		edges.append([])
		var part: Dictionary = structural_parts[index]
		if part.valid and part.group == "pier" and absf(part.bounds.position.y + 3.2) < EPS:
			connected[index] = true
			pending.append(index)
		for previous in range(index):
			if part.valid and structural_parts[previous].valid and has_face_contact(part.bounds, structural_parts[previous].bounds):
				edges[index].append(previous)
				edges[previous].append(index)
	check(not pending.is_empty(), "No actually constructed foundation members seed the contact graph")
	while not pending.is_empty():
		var index: int = pending.pop_back()
		for neighbour in edges[index]:
			if not connected.has(neighbour):
				connected[neighbour] = true
				pending.append(neighbour)
	for index in range(structural_parts.size()):
		check(connected.has(index), "No continuous real geometric member contact to a keel-bearing pier: " + str(structural_parts[index].name))

func required_family_contact(first: String, second: String, zone: AABB, label: String) -> void:
	var found := false
	for a in structural_parts:
		if not a.valid or not str(a.name).begins_with(first) or not has_face_contact(a.bounds, zone):
			continue
		for b in structural_parts:
			if b.valid and str(b.name).begins_with(second) and has_face_contact(b.bounds, zone) and has_face_contact(a.bounds, b.bounds):
				found = true
	check(found, "Required real member-to-member bearing/embed missing: " + label)

func validate_piers(data: Dictionary) -> void:
	var centres: Array = data.get("support", {}).get("pier_centres_xz", [])
	check(centres.size() == 2, "Exactly two audited pier centres X±35.5/Z86 required")
	var seen_centres: Dictionary = {}
	for centre in centres:
		if not check(centre is Array and centre.size() == 2, "Invalid pier-centre coordinate pair: " + str(centre)):
			continue
		var point := Vector2(float(centre[0]), float(centre[1]))
		var side_key := "port" if point.x < 0 else "starboard"
		var expected := Vector2(-35.5 if point.x < 0 else 35.5, 86.0)
		check(point.distance_to(expected) < EPS, "Audited pier centre changed: " + str(point))
		check(not seen_centres.has(side_key), "Duplicate audited pier centre: " + side_key)
		seen_centres[side_key] = true
	check(seen_centres.has("port") and seen_centres.has("starboard"), "Both distinct audited pier centres must remain present")
	for x in [-35.5, 35.5]:
		var side := "Port" if x < 0 else "Starboard"
		var intended: String = FLOOR_IDS[0 if x < 0 else 1]
		for segment in range(16):
			var low := lerpf(-3.19, 114.0, segment / 16.0)
			var high := lerpf(-3.19, 114.0, (segment + 1) / 16.0)
			var bounds := AABB(Vector3(x - 0.4, low, 85.4), Vector3(0.8, high - low, 1.2))
			var label := "%s pier slice %d [%.3f,%.3f]" % [side, segment, low, high]
			for hit in box_hits(bounds, own_exclusions, label):
				var allowed: bool = region_id(hit.collider) == intended and low < FLOOR_Y and high > SLAB_BOTTOM
				check(allowed, "Pier intersects unintended existing static/dynamic body: " + label + " -> " + owner(hit))
			var y := (low + high) * 0.5
			for direction in [-1.0, 1.0]:
				# Start immediately outside the chord so its fitted outer wall cannot
				# mask the real pier face in the upper occupied segment.
				var start := Vector3(x + direction * 0.45, y, 86)
				var hit := ray(start, Vector3(x, y, 86), shell_only_exclusions)
				if check(not hit.is_empty(), "Empty hypothetical pier envelope: " + label):
					check(shell.is_ancestor_of(hit.collider) and absf(hit.position.x - (x + direction * 0.4)) < EPS,
						"Pier outer chord must exist at audited full width: " + label + " -> " + owner(hit))
			slice_count += 1
		for offset in [Vector2.ZERO, Vector2(-0.4, -0.6), Vector2(-0.4, 0.6), Vector2(0.4, -0.6), Vector2(0.4, 0.6)]:
			var start := Vector3(x + offset.x, -3.0, 86 + offset.y)
			var hit := ray(start, start - Vector3.UP * 0.4, crown_exclusions)
			if check(not hit.is_empty(), "Keel support absent: " + side + str(offset)):
				check("HUL_KeelPan" in owner(hit) and absf(hit.position.y + 3.2) < EPS, "Pier must bear on actual keel top -3.2: " + owner(hit))
			support_count += 1
		required_family_contact("AFC_Pier_" + side, "AFC_TransferGirder_", AABB(Vector3(x - 0.5, 111.25, 85.4), Vector3(1, 2.75, 1.2)), side + " pier/new Z86 frame")
	check(slice_count == 32 and support_count == 10, "All 32 real pier slices and ten keel support rays must execute")

func validate_frame_and_roof() -> void:
	for x in LINK_X:
		var zone := AABB(Vector3(x - 0.31, 111.4, 70.82), Vector3(0.62, 2.4, 0.36))
		var found_old := false
		for hit in box_hits(zone, crown_exclusions, "old Z71 frame/new longitudinal link"):
			check(old_shell.is_ancestor_of(hit.collider), "Roof link intersects unintended old owner: " + owner(hit))
			found_old = found_old or old_shell.is_ancestor_of(hit.collider)
		check(found_old, "Roof link lacks actual old Z71 frame contact at X" + str(x))
		var hit := ray(Vector3(x, 112, 70.5), Vector3(x, 112, 71.5), crown_exclusions)
		if check(not hit.is_empty(), "Old Z71 frame witness absent at X" + str(x)):
			check(old_shell.is_ancestor_of(hit.collider) and absf(hit.position.z - 70.82) < EPS, "Old transfer-web face moved at X" + str(x) + " -> " + owner(hit))
		required_family_contact("AFC_Longitudinal_", "AFC_TransferGirder_", AABB(Vector3(x - 0.31, 111.25, 85.45), Vector3(0.62, 2.75, 1.1)), "longitudinal/new frame X" + str(x))
	for x in [-32.0, 0.0, 32.0]:
		var zone := AABB(Vector3(x - 0.22, 113.05, 65.72), Vector3(0.44, 0.8, 0.56))
		required_family_contact("AFC_ForwardPurlinSaddle", "AFC_RoofPurlin", zone, "forward purlin saddle X" + str(x))
		var contact := false
		for hit in box_hits(zone, crown_exclusions, "forward saddle/old roof beam"):
			check(old_shell.is_ancestor_of(hit.collider), "Forward saddle touches unexpected owner: " + owner(hit))
			contact = contact or old_shell.is_ancestor_of(hit.collider)
		check(contact, "Forward purlin saddle lacks actual old longitudinal bearing X" + str(x))
		var hit := ray(Vector3(x, 113.3, 66), Vector3(x, 112.9, 66), crown_exclusions)
		if check(not hit.is_empty(), "Old forward-saddle bearing surface absent X" + str(x)):
			check(old_shell.is_ancestor_of(hit.collider) and absf(hit.position.y - 113.15) < EPS, "Forward saddle must overlap actual old beam by 0.10m: " + owner(hit))
	for z in [74.0, 82.0, 90.0, 98.0, 101.8]:
		for x in LINK_X:
			required_family_contact("AFC_RoofPurlin", "AFC_Longitudinal_", AABB(Vector3(x - 0.31, 113.7, z - 0.11), Vector3(0.62, 0.57, 0.22)), "purlin/longitudinal X%s Z%s" % [x, z])
	for z in [66.0, 74.0, 82.0, 90.0, 98.0, 101.8]:
		for x in [-30.0, -18.0, -6.0, 6.0, 18.0, 30.0]:
			required_family_contact("AFC_SteppedRoofSkin", "AFC_RoofPurlin", AABB(Vector3(x - 0.1, 113.7, z - 0.11), Vector3(0.2, 0.75, 0.22)), "roof skin/purlin X%s Z%s" % [x, z])
	for x in HANGER_X:
		for z in [86.0, 98.0]:
			var zone := AABB(Vector3(x - 0.31, 106.05, z - 0.19), Vector3(0.62, 7.77, 0.38))
			required_family_contact("AFC_Hanger_", "AFC_Longitudinal_", zone, "hanger/roof link X%s Z%s" % [x, z])
			required_family_contact("AFC_Hanger_", "AFC_FloorEdgeGirder_", zone, "hanger/floor girder X%s Z%s" % [x, z])
		for z in BEARER_Z:
			required_family_contact("AFC_FloorEdgeGirder_", "AFC_PlatformCrossBearer", AABB(Vector3(x - 0.3, 105.84, z - 0.13), Vector3(0.6, 0.44, 0.26)), "girder/cross-bearer X%s Z%s" % [x, z])

func slab_witness(point: Vector2, expected_id: String, label: String) -> void:
	var top := ray(Vector3(point.x, 106.7, point.y), Vector3(point.x, 106.1, point.y), crown_exclusions)
	if check(not top.is_empty(), label + ": missing real slab top"):
		check(region_id(top.collider) == expected_id and absf(top.position.y - FLOOR_Y) < EPS, label + ": incorrect slab top owner/height -> " + owner(top))
	var bottom := ray(Vector3(point.x, 106.1, point.y), Vector3(point.x, 106.4, point.y), crown_exclusions)
	if check(not bottom.is_empty(), label + ": missing real slab underside"):
		check(region_id(bottom.collider) == expected_id and absf(bottom.position.y - SLAB_BOTTOM) < EPS, label + ": incorrect slab thickness/underside owner -> " + owner(bottom))

func validate_floor_chain() -> void:
	var layout := read_json("res://data/spatial_layout.json")
	var generated := read_json("res://data/generated/structural_meshes.json")
	if layout.is_empty() or generated.is_empty():
		return
	var owned: Array = layout.regions.filter(func(item: Dictionary) -> bool: return str(item.get("authoring_owner", "")) == "aft_command_extension")
	check(owned.size() == 2, "Exactly two regions and one aft_command_extension compiled floor owner required")
	for side in range(2):
		var id: String = FLOOR_IDS[side]
		var x0 := -36.0 if side == 0 else 4.0
		var x1 := -4.0 if side == 0 else 36.0
		var matches: Array = owned.filter(func(item: Dictionary) -> bool: return str(item.id) == id)
		if check(matches.size() == 1, "Missing/duplicate parent-owned floor region: " + id):
			check(matches[0].boundary == [[x0, 80], [x1, 80], [x1, 102], [x0, 102]] or _same_rectangle(matches[0].boundary, x0, x1, 80, 102), "New floor must preserve central X±4 spine: " + id)
		var compiled: Array = generated.regions.filter(func(item: Dictionary) -> bool: return str(item.id) == id)
		if check(compiled.size() == 1, "Missing/duplicate compiled floor: " + id):
			check(absf(float(compiled[0].floor_y) - FLOOR_Y) < EPS and absf(float(compiled[0].thickness) - 0.24) < EPS and absf(float(compiled[0].structural_area_m2) - 704.0) < EPS, "Compiled floor datum/thickness/net area changed: " + id)
		# One-sided concave surfaces require an exterior-centred query. A box
		# centred inside the slab can be backface-culled even across both faces.
		# Probe each real face separately, overlapping it by 5mm from outside.
		for face in [["top", FLOOR_Y + 0.005], ["underside", SLAB_BOTTOM - 0.005]]:
			var owned_surface := AABB(Vector3(x0 + 0.002, float(face[1]) - 0.01, 80.002), Vector3(x1 - x0 - 0.004, 0.02, 21.996))
			var found_owner := false
			for hit in box_hits(owned_surface, crown_exclusions, id + " whole slab " + str(face[0]) + " ownership"):
				check(region_id(hit.collider) == id, "Duplicate or unintended physical owner at new slab " + str(face[0]) + ": " + id + " -> " + owner(hit))
				found_owner = found_owner or region_id(hit.collider) == id
			check(found_owner, "New platform has no actual compiled owner contact at " + str(face[0]) + ": " + id)
		var slab := floors.get_node_or_null(id) as Node3D
		if not check(slab != null, "Actual compiled slab absent: " + id):
			continue
		var actual_faces := PackedVector3Array()
		var actual_min := Vector3(INF, INF, INF)
		var actual_max := Vector3(-INF, -INF, -INF)
		for node in slab.find_children("*", "CollisionShape3D", true, false):
			var shape := node as CollisionShape3D
			if not check(shape.shape is ConcavePolygonShape3D and not shape.disabled, "New slab needs active triangle collision: " + id):
				continue
			for vertex in shape.shape.get_faces():
				var world_vertex: Vector3 = shape.global_transform * vertex
				actual_faces.append(world_vertex)
				actual_min = actual_min.min(world_vertex)
				actual_max = actual_max.max(world_vertex)
		check(actual_faces.size() == 36 and actual_min.distance_to(Vector3(x0, SLAB_BOTTOM, 80)) < EPS and actual_max.distance_to(Vector3(x1, FLOOR_Y, 102)) < EPS, "Actual rectangular slab bounds/12 triangles changed: " + id)
		var visuals := PackedVector3Array()
		for node in slab.find_children("*", "MeshInstance3D", true, false):
			var mesh := node as MeshInstance3D
			if check(mesh.mesh != null and mesh.is_visible_in_tree(), "New floor render absent/hidden: " + id):
				for vertex in mesh.mesh.get_faces():
					visuals.append(mesh.global_transform * vertex)
		check(geometry_signature(visuals) == geometry_signature(actual_faces), "New floor render/contact triangles disagree: " + id)
		for x in [x0 + 0.1, (x0 + x1) * 0.5, x1 - 0.1]:
			for z in [80.1, 85.0, 91.0, 97.0, 101.9]:
				slab_witness(Vector2(x, z), id, id + " X%s Z%s" % [x, z])
	# Inspect every real support touching the slab, not an empty declared envelope.
	var spine_boundary_count := 0
	for part in structural_parts:
		if not part.valid or part.group != "platform_support" or part.bounds.end.y < SLAB_BOTTOM:
			continue
		var expected_id: String = FLOOR_IDS[0 if part.bounds.get_center().x < 0 else 1]
		var boundary_member: bool = str(part.name).begins_with("AFC_PlatformCrossBearer") and spine_boundary_only(part.bounds)
		if boundary_member:
			validate_spine_boundary_witness(part)
			spine_boundary_count += 1
		var contact := false
		for hit in box_hits(part.bounds, crown_exclusions, str(part.name)):
			var actual := region_id(hit.collider)
			var apron_ok: bool = actual == "D18_aft_apron" and part.bounds.position.z < 80
			var spine_boundary_ok: bool = actual == "D18_aft_route" and boundary_member
			check(actual == expected_id or apron_ok or spine_boundary_ok, "Floor support intersects unintended owner or penetrates protected spine: " + str(part.name) + " -> " + owner(hit))
			contact = contact or actual == expected_id
		check(contact, "Built girder/cross-bearer lacks actual new slab underside embed: " + str(part.name))
		floor_contact_count += 1
	check(floor_contact_count == 60, "All 24 web/top-flange plus 36 cross-bearer slab contacts must execute")
	check(spine_boundary_count == 12, "All twelve inner cross-bearer ends need independent zero-overlap spine seam witnesses")
	for z in [80.1, 86.0, 98.0, 101.9]:
		slab_witness(Vector2(0, z), "D18_aft_route", "Preserved central floor owner Z" + str(z))

func spine_boundary_only(bounds: AABB) -> bool:
	# This is a zero-material-overlap seam in the frozen, triangle-proven member.
	# Query margin may report the adjacent spine, but positive X overlap is never
	# accepted as an intended support. 10 micrometres accommodates float arithmetic.
	var material_overlap := minf(bounds.end.x, 4.0) - maxf(bounds.position.x, -4.0)
	if material_overlap > 0.00001:
		return false
	var member_edge := bounds.end.x if bounds.get_center().x < 0 else bounds.position.x
	var expected_edge := -4.0 if bounds.get_center().x < 0 else 4.0
	return absf(member_edge - expected_edge) < 0.00001 and bounds.position.z >= 80.0 and bounds.end.z <= 102.0

func validate_spine_boundary_predicate() -> void:
	check(spine_boundary_only(AABB(Vector3(-12, 105.88, 81.88), Vector3(8, 0.4, 0.24))), "Port bearer may meet the spine only at X-4")
	check(spine_boundary_only(AABB(Vector3(4, 105.88, 81.88), Vector3(8, 0.4, 0.24))), "Starboard bearer may meet the spine only at X+4")
	check(not spine_boundary_only(AABB(Vector3(-12, 105.88, 81.88), Vector3(8.01, 0.4, 0.24))), "Port bearer with positive spine penetration must be rejected")
	check(not spine_boundary_only(AABB(Vector3(3.99, 105.88, 81.88), Vector3(8.01, 0.4, 0.24))), "Starboard bearer with positive spine penetration must be rejected")
	check(not spine_boundary_only(AABB(Vector3(-12, 105.88, 81.88), Vector3(7.99, 0.4, 0.24))), "A disconnected bearer is not a shared spine-boundary contact")

func validate_spine_boundary_witness(part: Dictionary) -> void:
	var bounds: AABB = part.bounds
	var edge := -4.0 if bounds.get_center().x < 0 else 4.0
	var z := bounds.get_center().z
	# Independently identify the real old slab's lateral face and new bearer's
	# end face, excluding the opposite geometry from each witness.
	var inside := edge - signf(edge) * 0.15
	var outside := edge + signf(edge) * 0.15
	var slab := ray(Vector3(outside, 106.35, z), Vector3(inside, 106.35, z), _exclude_new_slabs())
	var bearer := ray(Vector3(inside, 106.0, z), Vector3(outside, 106.0, z), shell_only_exclusions)
	if not check(not slab.is_empty() and not bearer.is_empty(), "Shared spine boundary needs two real independent faces: " + str(part.name)):
		return
	check(region_id(slab.collider) == "D18_aft_route" and absf(slab.position.x - edge) < EPS,
		"Protected spine's actual lateral boundary moved: " + str(part.name) + " -> " + owner(slab))
	check(shell.is_ancestor_of(bearer.collider) and absf(bearer.position.x - edge) < EPS,
		"Cross-bearer's actual end face changed: " + str(part.name) + " -> " + owner(bearer))
	# Exact authored zero overlap above plus measured alignment at the existing
	# sub-mm import precision. This does not permit a designed intrusion.
	check(absf(bearer.position.x - slab.position.x) < EPS,
		"Actual bearer/spine seam is separated or penetrates beyond import precision: " + str(part.name))

func _same_rectangle(boundary: Array, x0: float, x1: float, z0: float, z1: float) -> bool:
	if boundary.size() != 4:
		return false
	var expected := {Vector2(x0, z0): true, Vector2(x1, z0): true, Vector2(x1, z1): true, Vector2(x0, z1): true}
	for point in boundary:
		expected.erase(Vector2(point[0], point[1]))
	return expected.is_empty()

func validate_apron_ties(data: Dictionary) -> void:
	var ties: Array = data.get("support", {}).get("authored_ties", [])
	check(ties.size() == 4, "Four intended apron ties required")
	var unique: Dictionary = {}
	for tie in ties:
		var bounds := contract_box(tie.world_aabb)
		var x := bounds.get_center().x
		var intended: String = FLOOR_IDS[0 if x < 0 else 1]
		check(not unique.has(x) and (absf(absf(x) - 35.5) < EPS or absf(absf(x) - 5.04) < EPS), "Duplicate/unexpected apron tie X" + str(x))
		unique[x] = true
		check(bounds.size.distance_to(Vector3(0.44, 0.32, 0.45)) < EPS and absf(bounds.position.z - 79.8) < EPS and absf(bounds.end.y - 106.4) < EPS, "Tie must embed old apron 0.20m and stay 0.10m below walking level: " + str(tie.name))
		validate_real_box(bounds, str(tie.name))
		var old_contact := false
		var new_contact := false
		for hit in box_hits(bounds, crown_exclusions, str(tie.name)):
			var actual := region_id(hit.collider)
			check(actual == "D18_aft_apron" or actual == intended, "Apron tie touches unintended old/new floor: " + owner(hit))
			old_contact = old_contact or actual == "D18_aft_apron"
			new_contact = new_contact or actual == intended
		check(old_contact and new_contact, "Apron tie needs positive old apron and new slab contact: " + str(tie.name))
		var edge := ray(Vector3(x, 106.35, 80.1), Vector3(x, 106.35, 79.7), _exclude_new_slabs())
		if check(not edge.is_empty(), "Actual Z80 apron edge missing: " + str(tie.name)):
			check(region_id(edge.collider) == "D18_aft_apron" and absf(edge.position.z - 80) < EPS, "Tie's intended old edge must be actual apron Z80: " + owner(edge))
		slab_witness(Vector2(x, 79.9), "D18_aft_apron", "Apron tie old floor X" + str(x))
		required_family_contact("AFC_ApronTie_", "AFC_FloorEdgeGirder_", bounds, "apron tie/girder X" + str(x))

func _exclude_new_slabs() -> Array[RID]:
	var excluded: Array[RID] = crown_exclusions.duplicate()
	for body in floors.find_children("*", "CollisionObject3D", true, false):
		if region_id(body) in FLOOR_IDS:
			excluded.append(body.get_rid())
	return excluded

func validate_protected_routes() -> void:
	# Keep closed door leaves in these queries; a clear static-only belt is insufficient.
	var excluded: Array[RID] = []
	for body in ship.find_children("*", "CollisionObject3D", true, false):
		if body is CharacterBody3D or body is RigidBody3D:
			excluded.append(body.get_rid())
	for index in range(12):
		var bounds := AABB(Vector3(-48 + index * 8 + 0.002, 106.52, 60.002), Vector3(7.996, 2.1, 5.996))
		for hit in box_hits(bounds, excluded, "Protected six-metre public belt"):
			check(false, "Wall/frame/pier/closed leaf enters protected Z60–66 public belt: " + owner(hit))
	for index in range(7):
		var bounds := AABB(Vector3(-3.998, 106.52, 60.002 + index * 6), Vector3(7.996, 2.1, 5.996))
		for hit in box_hits(bounds, excluded, "Protected X±4 longitudinal route"):
			check(false, "Architecture/door enters protected X±4 public route: " + owner(hit))
	for x in [-47.0, -35.5, -20.0, -7.5, 0.0, 7.5, 20.0, 35.5, 47.0]:
		for z in [60.1, 63.0, 65.9]:
			var intended := "D18_atrium_structural_cap" if z < 64 else "D18_aft_apron"
			slab_witness(Vector2(x, z), intended, "Protected belt floor X%s Z%s" % [x, z])

func validate_door_sweep_routes() -> void:
	# Inspect actual moving render vertices and their real contact boxes at every
	# coordinated door pose. This supplements the separate operation/cart tests.
	var belt := AABB(Vector3(-48, 106.52, 60.001), Vector3(96, 2.1, 5.998))
	var spine := AABB(Vector3(-3.999, 106.52, 60), Vector3(7.998, 2.1, 42))
	var door_count := 0
	for district in [crown, old_shell.get_parent()]:
		for door in district.get_children():
			if not door.has_method("_apply_pose"):
				continue
			# Only doors adjoining this aft interface are in this regression's scope.
			if door.global_position.z < 59.0:
				continue
			door_count += 1
			var saved_fraction := float(door.open_fraction)
			for leaf in door.leaves:
				leaf.sync_to_physics = false
			for step in range(91):
				door.open_fraction = step / 90.0
				door._apply_pose()
				for leaf in door.leaves:
					for node in leaf.find_children("*", "MeshInstance3D", true, false):
						var mesh := node as MeshInstance3D
						if mesh.mesh == null:
							continue
						var minimum := Vector3(INF, INF, INF)
						var maximum := Vector3(-INF, -INF, -INF)
						for vertex in mesh.mesh.get_faces():
							var point: Vector3 = mesh.global_transform * vertex
							minimum = minimum.min(point)
							maximum = maximum.max(point)
						var bounds := AABB(minimum, maximum - minimum)
						check(not bounds.intersects(belt) and not bounds.intersects(spine), "Actual moving door mesh enters protected belt/spine: %s pose%d/%s" % [door.name, step, mesh.name])
					for node in leaf.find_children("*", "CollisionShape3D", true, false):
						var shape := node as CollisionShape3D
						if shape.disabled or not shape.shape is BoxShape3D:
							continue
						var bounds: AABB = shape.global_transform * AABB(-shape.shape.size * 0.5, shape.shape.size)
						check(not bounds.intersects(belt) and not bounds.intersects(spine), "Actual moving door contact enters protected belt/spine: %s pose%d/%s" % [door.name, step, shape.name])
			door.open_fraction = saved_fraction
			door._apply_pose()
			for leaf in door.leaves:
				leaf.sync_to_physics = true
	check(door_count == 6, "Exactly four new and two old aft-interface doors require 91 protected-route poses")

func validate_core_openings() -> void:
	var exclusions: Array[RID] = []
	for body in ship.find_children("*", "CollisionObject3D", true, false):
		if not floors.is_ancestor_of(body) and not crown.is_ancestor_of(body) and not old_shell.is_ancestor_of(body):
			exclusions.append(body.get_rid())
	var layout := read_json("res://data/spatial_layout.json")
	if layout.is_empty():
		return
	var expected := {
		"primary_atrium_core": [-106.0, -90.65, 18], "forward_public_core": [-438.0, -422.65, 17],
		"fore_midship_public_core": [-278.0, -262.65, 17], "aft_midship_public_core": [266.0, 281.35, 17],
		"aft_public_core": [426.0, 441.35, 17], "aft_crown_link": [113.0, 128.35, 2]}
	for prefix in expected:
		for kind in ["lift", "stairs"]:
			var id: String = str(prefix) + "_" + str(kind)
			var matches: Array = layout.voids.filter(func(item: Dictionary) -> bool: return str(item.id) == id)
			if not check(matches.size() == 1, "Protected core opening absent/duplicated: " + id):
				continue
			var opening: Dictionary = matches[0]
			var centre_z := float(expected[prefix][0 if kind == "lift" else 1])
			var half := Vector2(1.82, 2.02) if kind == "lift" else Vector2(3.1, 5.35)
			var count := int(expected[prefix][2]) - (1 if kind == "stairs" else 0)
			check(opening.decks.size() == count, "Protected core opening deck count changed: " + id)
			check(_same_rectangle(opening.boundary, -half.x, half.x, centre_z - half.y, centre_z + half.y), "Protected core opening bounds changed: " + id)
			for deck in opening.decks:
				var index := int(str(deck).substr(1)) - 1
				var y := float(ship.deck_y[index])
				var bounds := AABB(Vector3(-half.x + 0.02, y - 0.6, centre_z - half.y + 0.02), Vector3(half.x * 2.0 - 0.04, 0.7, half.y * 2.0 - 0.04))
				for hit in box_hits(bounds, exclusions, id + "/" + str(deck)):
					check(false, "Protected core/deck opening filled: " + id + "/" + str(deck) + " -> " + owner(hit))
				opening_count += 1
	check(opening_count == 170, "All 170 protected core/deck openings must execute")

func validate_fixtures_and_signs(data: Dictionary) -> void:
	var markers: Array = data.get("light_markers", [])
	check(markers.size() == 30, "Source contract must retain 30 fixtures")
	check(shell.find_children("DATUM_light_*", "Node3D", true, false).size() == 30, "Actual imported fixture-marker count changed")
	check(crown.find_children("AftCommandSource_*", "SpotLight3D", true, false).size() == 30, "Actual runtime source-light count changed")
	var unique: Dictionary = {}
	for item in markers:
		var name := str(item.name)
		check(not unique.has(name), "Duplicated fixture marker " + name)
		unique[name] = true
		var marker := shell.find_child(name, true, false) as Node3D
		var light := crown.find_child("AftCommandSource_" + name, true, false) as SpotLight3D
		if not check(marker != null and light != null, "Missing actual fixture marker/light: " + name):
			continue
		var position := Vector3(item.position[0], item.position[1], item.position[2])
		check(marker.global_position.distance_to(position) < EPS and light.global_position.distance_to(position) < EPS, "Actual fixture/light placement changed: " + name)
		check((-light.global_basis.z).dot(Vector3.DOWN) > 0.999, "Light must emit downward: " + name)
		var exit_hit := ray(position, position + Vector3.DOWN * 0.25, dynamic_exclusions)
		check(exit_hit.is_empty(), "Physical fixture exit obstructed: " + name + " -> " + owner(exit_hit))
		var lens := ray(position, position + Vector3.UP * 0.08, dynamic_exclusions)
		check(not lens.is_empty() and shell.is_ancestor_of(lens.collider), "Fixture has no physical source lens immediately above marker: " + name)
	check(crown.find_children("AftCommandSign_*", "Label3D", true, false).size() == 2, "Two physically backed programme signs required")
	var programmes: Array = data.get("programmes", [])
	check(programmes.size() == 2, "Exactly the two assigned aft programmes required")
	var seen: Dictionary = {}
	for programme in programmes:
		var key := str(programme.programme_key)
		check(key in ["D18_directory_08", "D18_directory_10"] and not seen.has(key), "Unexpected/duplicate aft programme " + key)
		seen[key] = true
		var sign := crown.find_child("AftCommandSign_" + key, true, false) as Label3D
		if not check(sign != null and sign.is_visible_in_tree(), "Missing visible programme sign: " + key):
			continue
		var x := -9.98 if key == "D18_directory_08" else 9.98
		check(sign.global_position.distance_to(Vector3(x, 109.65, 82)) < EPS, "Sign must remain at real room-front solid-header datum: " + key)
		check(not sign.text.strip_edges().is_empty(), "Programme sign text empty: " + key)
		for offset in [-0.5, 0.0, 0.5]:
			var start := sign.global_position + Vector3(0, 0, offset)
			var backing := ray(start, start + Vector3(signf(x) * 0.08, 0, 0), dynamic_exclusions)
			if check(not backing.is_empty(), "Sign has no real header backing: " + key):
				check(shell.is_ancestor_of(backing.collider) and absf(absf(backing.position.x) - 10) < EPS, "Wrong sign backing owner/plane: " + key + " -> " + owner(backing))

func run() -> void:
	var data := read_json(CONTRACT)
	if data.is_empty():
		quit(1)
		return
	check(FileAccess.get_sha256(ASSET) == SOURCE_EXPORT_SHA256 and str(data.get("export_sha256", "")) == SOURCE_EXPORT_SHA256,
		"Aft export changed; renew source/export equivalence and frozen contact witnesses before updating test pins")
	var main_scene := load("res://scenes/main.tscn") as PackedScene
	if not check(main_scene != null, "Main scene missing"):
		quit(1)
		return
	var main := main_scene.instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	ship = main.get_node_or_null("World360/Astraea") as Node3D
	if not check(ship != null, "Main scene ship missing"):
		quit(1)
		return
	crown = ship.get_node_or_null("ShipSpace/Districts/AftCommandCrown_WIP") as Node3D
	if not check(crown != null, "Actual main scene has no adopted aft command root"):
		quit(1)
		return
	shell = crown.get_node_or_null("AftCommandArchitecture") as Node3D
	old_shell = ship.get_node_or_null("ShipSpace/Districts/CentralCommandCrown_WIP/CentralCrownArchitecture") as Node3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms", true, false) as Node3D
	if not check(shell != null and old_shell != null and floors != null, "New/old architecture or real compiled floor root missing"):
		quit(1)
		return
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*", "CollisionObject3D", true, false):
		var permanent: bool = body is StaticBody3D and not body is AnimatableBody3D
		if not permanent:
			dynamic_exclusions.append(body.get_rid())
		if crown.is_ancestor_of(body):
			own_exclusions.append(body.get_rid())
		if crown.is_ancestor_of(body) or not permanent:
			crown_exclusions.append(body.get_rid())
		if not shell.is_ancestor_of(body):
			shell_only_exclusions.append(body.get_rid())
	validate_meshes()
	validate_coverage_predicate()
	validate_members_and_graph()
	validate_piers(data)
	validate_frame_and_roof()
	validate_spine_boundary_predicate()
	validate_floor_chain()
	validate_apron_ties(data)
	validate_protected_routes()
	validate_door_sweep_routes()
	validate_core_openings()
	validate_fixtures_and_signs(data)
	if not failures.is_empty():
		print("AFT COMMAND STRUCTURE: %d recorded failures" % failures.size())
		quit(1)
		return
	print("AFT COMMAND STRUCTURE PASS: real imported member/contact equality; 2 constructed piers, 32 envelope slices, 10 keel rays; roof/frame/saddle/hanger/girder chain, 60 slab contacts, 4 old/new apron ties; protected belt/spine and 170 core openings; 30 clear fixture exits and 2 backed signs. Geometric construction contacts only, no structural load certification.")
	main.queue_free()
	await process_frame
	quit()
