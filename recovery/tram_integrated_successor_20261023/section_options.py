"""Bounded arithmetic from retained section contracts; no geometry or guard edits."""
from pathlib import Path
import hashlib,json,struct
R=Path(__file__).resolve().parents[2]
P=Path(__file__).resolve().parent
H=R/'recovery/tram_clearance_conflict_20261023'
interface=json.loads((H/'retained-inputs/port_successor_002/SUCCESSOR_INTERFACE.json').read_text())
module=json.loads((H/'retained-inputs/receiving_module_003/MODULE_INTERFACE.json').read_text())
witness=json.loads((H/'GEOMETRY_WITNESSES.json').read_text())
guide=interface['guideway'];top=witness['reservation']['max_y'];clearance=0.01
shift=round(top+clearance-guide['soffit_y'],6)
boarding=round(guide['floor_y']+shift,6)
undersides={round(x['xyz'][1],4) for x in module['receiver_bindings'] if str(x.get('owner','')).startswith('D10')}
assert undersides=={60.76},undersides
ceiling=next(iter(undersides));upper_clearance=4.0
# These fixed source values are quoted in the prior decision and authored in
# plan_receiving.py, lines 24-28 /45. They remain criteria, not edited constants.
header=[60.18,60.50]
boarding_plan=json.loads((R/'Game/data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json').read_text())
car=next(x for x in boarding_plan['models'] if x['role']=='vehicle')
car_path=R/'Game'/boarding_plan['model_root'].removeprefix('res://')/car['file']
raw=car_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==car['sha256']
size=struct.unpack_from('<I',raw,12)[0];glb=json.loads(raw[20:20+size])
assert not any(any(k in n for k in ['matrix','translation','rotation','scale']) for n in glb['nodes'] if 'mesh' in n or n.get('children'))
car_roof=max(glb['accessors'][p['attributes']['POSITION']]['max'][1] for m in glb['meshes'] for p in m['primitives'])
result={'status':'NO_COMPLETE_LEGAL_SECTION_SELECTED','source_inputs':{'retained_interface_sha256':hashlib.sha256((H/'retained-inputs/port_successor_002/SUCCESSOR_INTERFACE.json').read_bytes()).hexdigest(),'body_file':str(car_path.relative_to(R)),'body_sha256':car['sha256']},'protected_lower_band':witness['reservation'],'existing':{'soffit_y':guide['soffit_y'],'rail_head_y':guide['rail_head_y'],'boarding_y':guide['floor_y'],'upper_running_clearance_m':upper_clearance,'header_y':header,'D10_actual_receiving_underside_y':ceiling,'body_local_roof_y':car_roof},'vertical_raise_preserving_lower_test':{'clearance_margin_m':clearance,'raise_m':shift,'soffit_y':round(guide['soffit_y']+shift,6),'rail_head_y':round(guide['rail_head_y']+shift,6),'boarding_y':boarding,'required_4m_running_top_y':boarding+upper_clearance,'running_band_above_D10_m':round(boarding+upper_clearance-ceiling,6),'raised_header_top_y':header[1]+shift,'header_above_D10_m':round(header[1]+shift-ceiling,6),'status':'INFEASIBLE_WITH_BOTH_4M_BANDS_AND_EXISTING_D10'},'reduced_upper_envelope_not_selected':{'body_roof_y':boarding+car_roof,'space_to_original_header_m':round(header[0]-(boarding+car_roof),6),'available_envelope_to_original_header_m':round(header[0]-boarding,6),'reason':'Would reduce the retained upper 4m clearance; forbidden as an unapproved test/criterion reduction.'},'lateral_option_not_selected':{'straight_section_minimum_separation_m':2+3.5/2,'additional_margin_m':clearance,'reason':'This 3.75m is only two non-overlapping plan-strip widths. Curvature, shoes, stations, rail body sweep and receiving owners require more; no complete legal adjacent corridor is established. Master chapter32 body564 protects the six-point alignment. Earlier alternative screen explicitly retained that protected route and did not certify a replacement.','retained_actual_north_dock':[-5.6,56.1,-241],'retained_north_catchment_z':-216},'implementation_boundary':'Keep current geometry, source pins, stationary-frame witness and all operation admission holds. A named coordinated rail/boarding/support successor must satisfy both bands and retained receiving geometry before adoption. No construction or motion acceptance from this arithmetic.'}
(P/'SECTION_OPTIONS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','vertical_raise_preserving_lower_test']},indent=2))
