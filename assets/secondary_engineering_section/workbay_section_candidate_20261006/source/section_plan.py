"""Pure early architecture proposal; no real compiler/runtime mutation."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R.parent
CELL=[21.9,-406.6,27.1,-403.65];parts=[]
def box(n,b,role='staff_zinc',kind='architecture'):
 assert all(b[i+3]>b[i] for i in range(3));parts.append(dict(name=n,bounds_xyz=b,material_role=role,kind=kind));return n
def build():
 # Honest section preview: upper slab is decomposed around the complete cell cut.
 # These are compiler-owner proposal surfaces, never exported to the Game as a second floor.
 for n,x,X,z,Z in [('west',8,21.9,-466,-398),('east',27.1,54,-466,-398),('north',21.9,27.1,-466,-406.6),('south',21.9,27.1,-403.65,-398)]:box('PREVIEW_UPPER_FLOOR_'+n,[x,5.76,z,X,6,Z],'staff_floor','compiler_floor_preview')
 box('PREVIEW_LOWER_FLOOR',[21.9,5.31,-406.6,27.1,5.55,-403.65],'staff_floor','compiler_lower_owner_preview')
 # Structural retaining faces have real thickness and sit on the lower slab.
 for n,b in [('north',[21.9,5.55,-406.6,27.1,6,-406.48]),('south',[21.9,5.55,-403.77,27.1,6,-403.65]),('east',[26.98,5.55,-406.48,27.1,6,-403.77]),('west_north',[21.9,5.55,-406.48,22.02,6,-405.1]),('west_south',[21.9,5.55,-403.9,22.02,6,-403.77])]:box('CellRetainer_'+n,b,'staff_bluegrey_paint')
 # Exact three150mm descending risers; step3 is the lower datum transition.
 for i,top in enumerate([5.85,5.70]):box('CellStep_'+str(i+1),[21.9+i*.3,5.31,-405.1,22.2+i*.3,top,-403.9],'staff_zinc','stair_structure')
 # Three supported vertical nose bands avoid coplanar tread overlays.
 for i,(x,y) in enumerate([(21.9,6.0),(22.2,5.85),(22.5,5.70)]):box('CellRiserNose_'+str(i+1),[x,y-.028,-405.1,x+.0025,y-.002,-403.9],'staff_label','nosing_pigment')
 # Low rim allows ordinary-eye view to the lowered machine and floor.
 for n,b in [('N',[21.9,6,-406.6,27.1,6.12,-406.48]),('S',[21.9,6,-403.77,27.1,6.12,-403.65]),('E',[26.98,6,-406.48,27.1,6.12,-403.77]),('WN',[21.9,6,-406.48,22.02,6.12,-405.1]),('WS',[21.9,6,-403.9,22.02,6.12,-403.77])]:box('CellLowUpstand_'+n,b,'staff_bluegrey_paint')
 # Framed full-height restricted glass, using the retained exact glass material.
 for side,x in [('W',21.96),('E',27.04)]:
  for z in [-406.54,-403.71]:box('CellPost_'+side+str(z),[x-.045,6,z-.045,x+.045,8.76,z+.045],'staff_zinc')
  box('CellTop_'+side,[x-.045,8.66,-406.54,x+.045,8.76,-403.71],'staff_bluegrey_paint')
 for side,z in [('N',-406.54),('S',-403.71)]:
  box('CellTop_'+side,[21.96,8.66,z-.045,27.04,8.76,z+.045],'staff_bluegrey_paint')
  for i,(lo,hi) in enumerate([(22.005,23.66),(23.74,25.29),(25.37,26.995)]):box('CellGlass_'+side+str(i),[lo,6.13,z-.013,hi,8.65,z+.013],'section_sealed_glass','glazing')
  for x in [23.70,25.33]:box('CellMullion_'+side+str(x),[x-.04,6.12,z-.03,x+.04,8.66,z+.03],'staff_zinc')
 # East overlook remains entirely atY6. Glass/transoms never intrude into the turn.
 for i,(lo,hi) in enumerate([(-406.495,-405.175),(-405.095,-403.755)]):box('CellGlass_E'+str(i),[27.027,6.13,lo,27.053,8.65,hi],'section_sealed_glass','glazing')
 box('CellMullion_E',[27.01,6.12,-405.175,27.07,8.66,-405.095],'staff_zinc')
 # West door is physically open in this study, leaf parked in a horizontal north pocket.
 box('CellGlass_WN',[21.947,6.13,-406.495,21.973,8.65,-405.145],'section_sealed_glass','glazing')
 for z in [-405.14,-403.86]:box('CellDoorJamb'+str(z),[21.915,6,z-.035,22.005,8.38,z+.035],'staff_zinc')
 box('CellDoorHeader',[21.915,8.34,-405.135,22.005,8.40,-403.865],'staff_bluegrey_paint')
 box('CellDoorTransom',[21.947,8.41,-405.10,21.973,8.65,-403.9],'section_sealed_glass','glazing')
 box('CellDoorOpenLeaf',[21.855,6.03,-406.32,21.881,8.33,-405.12],'section_sealed_glass','open_gate_proposal')
 for z in [-406.32,-405.12]:box('CellDoorLeafEdge'+str(z),[21.84,6.10,z-.02,21.895,8.35,z+.02],'staff_zinc')
 box('CellDoorLeafTop',[21.84,8.31,-406.34,21.895,8.36,-405.10],'staff_zinc')
 box('CellDoorTrack',[21.815,8.39,-406.36,22.01,8.45,-403.86],'staff_zinc')
 # Stair-side guards protect the lowered step edges and connect to the jambs.
 for z in [-405.14,-403.86]:
  for x,y in [(22.10,5.85),(22.70,5.55)]:box('CellStairGuardPost'+str((x,z)),[x-.024,y,z-.024,x+.024,y+1.0,z+.024],'staff_zinc')
  parts.append(dict(name='CellStairHandrail'+str(z),endpoints_xyz=[[21.9,6.95,z],[22.8,6.50,z]],radius=.027,material_role='staff_zinc',kind='handrail'))
 # Compact2.0x0.75machinery skid; all portable maintenance occurs on its clear south face.
 box('CellMachineSkid',[23.85,5.55,-406.25,25.85,5.67,-405.50],'staff_zinc','machine_support')
 for x in [24.30,25.20]:box('CellMachineBearing'+str(x),[x-.24,5.67,-406.16,x+.24,5.80,-405.66],'staff_bluegrey_paint','machine_support')
 # Supported transfer shelf outside cell, no claim that the cart goes down stairs.
 box('CellToolShelfLegA',[27.24,6,-407.00,27.31,6.88,-406.55],'staff_zinc')
 box('CellToolShelfLegB',[27.96,6,-407.00,28.03,6.88,-406.55],'staff_zinc')
 box('CellToolTransferShelf',[27.19,6.88,-407.03,28.08,6.94,-406.52],'staff_white_paint')
 # Stepped structural shoes and cap-seated yokes integrate the cell with the room.
 for side,x in [('W',21.96),('E',27.04)]:
  for z in [-406.54,-403.71]:
   box('CellProfileShoe_'+side+str(z),[x-.08,6,z-.08,x+.08,6.26,z+.08],'staff_white_paint')
   box('CellProfileCap_'+side+str(z),[x-.09,8.55,z-.09,x+.09,8.79,z+.09],'staff_white_paint')
   box('CellProfileFlange_'+side+str(z),[x-.064,6.26,z-.067,x+.064,8.55,z-.026],'staff_white_paint')
 box('CellSteppedEastHeader',[27.015,8.63,-406.58,27.15,8.80,-403.67],'staff_white_paint')
 for x in [23.70,25.33]:
  box('CellYoke_'+str(x),[x-.055,8.76,-405.975,x+.055,9.57,-405.865],'staff_zinc')
  box('CellCapAnchor_'+str(x),[x-.16,9.57,-406.08,x+.16,9.60,-405.76],'staff_white_paint')
 # Real door controls are separately identified, not counted as harmless calibration controls.
 box('CellGateOutsideHousing',[21.79,6.98,-405.31,21.916,7.22,-405.15],'staff_white_paint','door_control_housing')
 box('CellGateInsideHousing',[22.005,6.74,-403.86,22.085,6.98,-403.70],'staff_white_paint','door_control_housing')
 for name,a,b in [('Outside',[21.765,7.10,-405.23],[21.791,7.10,-405.23]),('Inside',[22.084,6.86,-403.78],[22.11,6.86,-403.78])]:parts.append(dict(name='CellGateButton'+name,endpoints_xyz=[a,b],radius=.045,material_role='staff_cable_blue',kind='real_door_control'))
 # An actual header-borne stair source makes the risers and lower landing legible.
 box('CellThresholdTaskHousing',[21.91,8.318,-404.78,22.08,8.34,-404.22],'staff_bluegrey_paint')
 box('CellThresholdTaskOpal',[21.98,8.296,-404.73,22.06,8.318,-404.27],'staff_opal','lens')
 # Source fixture and beam are mechanically supported by the cell perimeter frame.
 box('CellLightingCrossbeam',[21.96,8.67,-405.97,27.04,8.76,-405.87],'staff_zinc')
 box('CellTaskHousing',[24.18,8.56,-406.035,25.42,8.67,-405.805],'staff_bluegrey_paint')
 box('CellTaskOpal',[24.28,8.536,-406.005,25.32,8.56,-405.835],'staff_opal','lens')
 return dict(status='Early source architecture only; no compiler or Game edit',cell_cut_xz=CELL,upper_y=6,lower_y=5.55,lower_slab_underside_y=5.31,steps={'risers':3,'riser_m':.15,'tread_m':.30,'clear_z':[-405.1,-403.9],'run_x':[21.9,22.8]},lower_landing=[22.8,5.55,-405.1,24.0,5.55,-403.9],upper_landing=[20.7,6,-405.1,21.9,6,-403.9],retained_turn=[28.2,6,-406.8,31.8,8.7,-403.2],cart_parking_candidate={'bounds_xz':[29.0,-406.2,30.6,-403.8],'blocks_when_in_use':'parking inside turn volume is temporary operational occupancy, not static obstruction; actualcart check pending'},staff_workflow='Park on upper route, carry bounded portable tools via real three-step gate, use clear lower landing/south machine face; no loaded cart stair traversal',future_D01_reservation='lower slab underside5.31; D01 Cold provisions fit must retain this reserve before future architecture',glazing_material='exact retained ASTRAEA_bridge_pressure_glass, unchanged; only new visual panes are single sheets with separate26mm contact bounds',removed_upper_source_assemblies=['WEST_DIAGNOSTIC_WALL','WEST_FILTER_SKID','WEST_TASK_PROPOSAL'],machine_cylinder_reuse={'source':'engineering-dense-bays/source/AST-ENG-008_dense_bays.blend','donor_names':['FilterDrum0','FilterDrum1','FilterBand*'],'placements_centres_xyz':[[24.30,6.67,-405.91],[25.20,6.67,-405.91]],'floor_contact_y':5.80},source_light={'marker':'PROPOSAL_CellTask','position':[24.8,8.515,-405.92],'aim':[24.8,6.55,-405.85]},ordinary_eye=[30,7.6501565,-405],ordinary_yaw=1.5707963267948966,ordinary_pitch=0,vertical_fov=72,parts=parts)
if __name__=='__main__':
 p=build();(R/'source/section_plan.json').write_text(json.dumps(p,indent=2)+'\n');print('SECTION_PLAN',len(parts),'parts','lowerdatum',p['lower_y'],'three150mmsteps','no runtime writes')
