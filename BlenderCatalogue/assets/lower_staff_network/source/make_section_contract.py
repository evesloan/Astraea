"""Deterministic floor-union and service-boundary contract. No geometry editing."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
# Exact axis-aligned union: keeps coordinates stable without extra libraries.
def union_polygons(rects):
 xs=sorted({r[k]for r in rects for k in [0,1]});zs=sorted({r[k]for r in rects for k in [2,3]})
 filled={(i,j)for i in range(len(xs)-1)for j in range(len(zs)-1)if any(r[0]<=(xs[i]+xs[i+1])/2<=r[1] and r[2]<=(zs[j]+zs[j+1])/2<=r[3]for r in rects)}
 edges={}
 for i,j in filled:
  a,b,c,d=(xs[i],zs[j]),(xs[i+1],zs[j]),(xs[i+1],zs[j+1]),(xs[i],zs[j+1])
  for neighbour,e in [((i,j-1),(a,b)),((i+1,j),(b,c)),((i,j+1),(c,d)),((i-1,j),(d,a))]:
   if neighbour not in filled:edges[e[0]]=e[1]
 rings=[]
 while edges:
  start=min(edges);p=start;ring=[]
  while True:
   ring.append(p);p=edges.pop(p)
   if p==start:break
  simple=[]
  for k,p in enumerate(ring):
   a=ring[k-1];b=ring[(k+1)%len(ring)]
   if (p[0]-a[0])*(b[1]-p[1])!=(p[1]-a[1])*(b[0]-p[0]):simple.append(p)
  rings.append(simple)
 return rings
base=[[-23.2,-18.8,-496,-484],[-22.8,-19.2,-500,-490],[-58.8,-19.2,-501.8,-498.2]]
decks=[]
for number,y,tail in [(1,0,[[-58.8,-55.2,-500,-58.2],[-57,-46,-61.8,-58.2]]),(2,6,[[-58.8,-55.2,-500,-430.2],[-57,-54,-433.8,-430.2]]),(3,12,[[-58.8,-55.2,-500,-214.2],[-57,-54,-433.8,-430.2],[-54,-48,-435,-429],[-57,-54,-433.8+216,-430.2+216],[-54,-48,-219,-213]])]:
 rects=base+tail;row={'deck':number,'floor_y':y,'floor_union_rectangles_x0_x1_z0_z1':rects,'floor_union_polygons_xz':union_polygons(rects),'floor_slab_thickness':.24,'ceiling_bottom_y':y+3.2,'ceiling_top_y':y+3.34,'boundary_apertures':[{'name':'lift_shaft_connection','plane_axis':'x','plane':-23.2,'range_axis':'z','range':[-492.2,-487.8],'bottom_y':y,'top_y':y+3.2,'mode':'omit_full_boundary_wall_existing_shaft_fills'}]}
 if number==1:row['boundary_apertures'].append({'name':'D01_existing_port_service_spine','plane_axis':'x','plane':-46,'range_axis':'z','range':[-61.8,-58.2],'bottom_y':y,'top_y':y+3.2,'mode':'open_existing_supported_destination'})
 if number==2:row['boundary_apertures'].append({'name':'D02_existing_fusion_service_opening','plane_axis':'x','plane':-54,'range_axis':'z','range':[-433.8,-430.2],'bottom_y':y,'top_y':y+3.2,'mode':'open_existing_supported_destination'});row['existing_floor_overlap_rectangles']=[[-59.5,-54,-435,-429]]
 if number==3:row['thresholds']=[{'name':'home_threshold','rectangle':[-54,-48,-435,-429],'status':'bounded_unfurnished_threshold_no_beds_no_identity','existing_cover':'D03_protected_crew_cover'},{'name':'depot_threshold','rectangle':[-54,-48,-219,-213],'status':'bounded_unfurnished_threshold_no_stock','existing_cover':None}]
 if number==1:
  row['existing_floor_overlap_rectangles']=[[-48,-46,-61.8,-58.2]]
  for z in [-61.8,-58.2]:row['boundary_apertures'].append({'name':'D01_existing_spine_sidewall_omission_'+str(z),'plane_axis':'z','plane':z,'range_axis':'x','range':[-48,-46],'bottom_y':0,'top_y':3.2,'mode':'omit_return_inside_existing_longitudinal_street'})
 decks.append(row)
d={'schema':1,'catalogue_id':'AST-STF-009','family':'lower_staff_network','coordinate_system':'Godot world XYZ metres; exported at world origin, Blender source maps (X,-Z,Y)','scope':'One screened D01/D02/D03 staff lift enclosure and connected lower staff corridor architecture. No general floors, dynamic cabin/gates, beds, job/species assignments or finished rooms.','deck_stops_y':[0,6,12],'decks':decks,'corridor':{'gross_width':3.6,'wall_thickness':.12,'bumper_projection':.025,'minimum_straight_clear_width':3.31,'clear_height':3.015,'ceiling_underside_height':3.2,'fixture_minimum_underside_height':3.015,'corner_turn_square_clear':3.31,'cart_envelope_screen':'Parent to drive existing loaded physical cart; static planar square is not dynamic acceptance.'},'lift':{'parent_position':[-25,0,-490],'parent_rotation_y_radians':3.141592653589793,'controller':'commons_lift.gd','gate_origin_xz_local':[-1.8,0],'cabin_file':'AST-CIR-003_three_stop.glb','gate_file':'AST-DOR-003.glb','reserved_shaft_rectangle':[-27.2,-22.8,-492.2,-487.8],'floor_shaft_exclusion':[-27.2,-23.18,-492.2,-487.8],'ceiling_shaft_exclusion':[-27.2,-23.18,-492.2,-487.8],'ceiling_contact_tolerance_note':'All corridor ceilings subtract the same shaft reservation; 0.02 m clearance beyond moving cabin roof front X−23.20. Whole moving cabin swept AABB checked with 5 mm inflation.','floor_contact_tolerance_east_m':.02,'floor_contact_tolerance_note':'Reserve 0.02 m beyond cabin front X−23.20; existing fixed sill bridges this clearance. Authored enclosure and portal geometry unchanged.','shaft_outer_rectangle':[-27.12,-22.84,-492.2,-487.8],'shaft_inner_rear_x':-26.96,'shaft_inner_z':[-492.04,-487.96],'pit_pan_bottom_top_y':[-.24,-.2],'top_cap_bottom_top_y':[15.1,15.24],'landing_gate_centres':[[-23.08,y,-490]for y in [0,6,12]],'moving_gate_x':-23.32,'cabin_floor_x':[-26.8,-23.2],'cabin_floor_z':[-492,-488],'dynamic_clear_aperture':{'width_z':2.4,'height_y':2.65},'east_wall_aperture':{'plane_x':[-23,-22.84],'z':[-491.9,-488.1],'height_from_stop':[0,2.85]},'minimum_cabin_side_clearance':.04,'minimum_cabin_rear_clearance':.16,'minimum_cabin_top_clearance':.16,'pit_to_cabin_bottom_clearance':.02},'render_batch_max_cell_m':20,'wall_policy':'Walls and bumpers entirely inside union floor polygons. Boundary apertures open at supported existing interfaces only. D03 threshold east ends and outer walls closed. No D01 Arrivals spur.','light_markers':[],'floor_owner':'Godot structural floor builder, parent task; union and subtract overlaps before slab compilation','reference':'Godot docs/reference_register/staff_lift_reference_20261003.jpg: actual pixels reviewed; use service grey enamel, restrained dark bumper, cool task strip housing. Preserve shared working cabin.'}
d['decks'][1]['interface_extensions']=[{'id': 'D02_fusion_service_transition_collar', 'mesh_name_prefix': 'STF_D02_FusionCollar_', 'supported_plan_rectangle': [-54.12, -53.77, -434.02, -429.98], 'height_y': [6, 9.345], 'existing_floor_owner': 'D02_fusion_screened_service', 'new_floor_required': False, 'clear_passage_z': [-433.8, -430.2], 'minimum_headroom_m': 3.2, 'header_bottom_y': 9.205, 'jamb_top_y': 9.225, 'reason': 'Close20cm side slots and5cm axial gap between existing4m fusion opening and new3.6m gross corridor without narrowing the route. Overlap old wall ends by20mm; header is5mm above existing undersides to avoid coplanar flicker.', 'measured_existing_asset': 'assets/arrivals_fusion/exports/AST-ARR-002.glb', 'measured_existing_asset_sha256': '938a20eae3eec4a164e8822368b6776d534216bb6f438153e10aa60aa67f1d9e', 'measured_existing_mesh_aabbs': [{'name': 'ARR_WestServiceEnclosure_-465.85', 'world_aabb': [-53.95000076293945, -53.75, 6.0, 11.760000228881836, -465.8499984741211, -434.0]}, {'name': 'ARR_WestServiceEnclosure_-430', 'world_aabb': [-53.95000076293945, -53.75, 6.0, 11.760000228881836, -430.0, -398.1500015258789]}, {'name': 'ARR_ServiceEntryHeader', 'world_aabb': [-53.95000076293945, -53.75, 9.199999809265137, 11.760000228881836, -434.0, -430.0]}], 'permitted_parts': ['STF_D02_FusionCollar_North_Wainscot', 'STF_D02_FusionCollar_North_Enamel', 'STF_D02_FusionCollar_South_Wainscot', 'STF_D02_FusionCollar_South_Enamel', 'STF_D02_FusionCollar_Header']}]
(R/'section_contract.json').write_text(json.dumps(d,indent=2)+'\n')
print(R/'section_contract.json')
