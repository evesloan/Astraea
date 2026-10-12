"""Create exact-preimage adapter patch; preserve every earlier source file."""
import pathlib,json,hashlib,difflib,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
path='Game/scripts/group2_vip_dry_club/package.gd';raw=(ROOT/path).read_bytes();old=raw.decode();assert hashlib.sha256(raw).hexdigest()=='c8c66a60905d79135e308aa8c31f1630e89660a6679d1f79372d2611429b62e7'
lines=old.splitlines(keepends=True);assert lines[3].startswith('\tvar data:')
adapter='''static func build_on_current_receiver(receiver: Node3D)->Node3D:
	assert(receiver.name=="D15_D17_StarAtlasUpper_WIP")
	assert(receiver.transform.is_equal_approx(Transform3D.IDENTITY),"Retained models use zero-origin world coordinates")
	assert("D17_directory_03" in receiver.get_meta("programme_keys",[]))
	assert(int(receiver.get_meta("source_part_count",-1))==514)
	assert(receiver.get_node_or_null("VIPDryClub_Source")==null,"One retained fitout, no duplicates")
	assert(FileAccess.get_sha256("res://assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb")=="f6fe84992dfb8cb22beee696959f77b8f8b4f91261e46d77c9cf36719303c888")
	assert(FileAccess.get_sha256("res://assets/group2_vip_dry_club/VIP_DRY_CLUB_r002.glb")=="95cc7e8279e993a2b919a2229b4001d215b8146807be9d8d1b306865b50d0800")
	assert(FileAccess.get_sha256("res://data/group2_vip_dry_club/COMPONENT_r002.json")=="cb5902beb0a8cb39f4ac125b7b1bb0a9354ea5e83aa3751372929791bd806c4a")
	var section:=_build_contents(receiver)
	section.set_meta("construction_installed",true)
	section.set_meta("existing_parent_programme","D17_directory_03")
	section.set_meta("food_service_membership_booking_and_capacity_accepted",false)
	return section

static func _build_contents(parent: Node3D)->Node3D:
'''
updated=''.join(lines[:3])+'\treturn _build_contents(parent)\n\n'+adapter+''.join(lines[3:])
assert updated.split('static func _build_contents(parent: Node3D)->Node3D:\n',1)[1]==''.join(lines[3:])
preview=P/'preview/package.gd';preview.parent.mkdir(exist_ok=True);preview.write_text(updated)
patch=''.join(difflib.unified_diff(old.splitlines(True),updated.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
(P/'STAR_ATLAS_DRY_CONSTRUCTION_ADAPTER.patch').write_text(patch)
data_path=ROOT/'Game/data/group2_integration_admission/STAR_ATLAS_DRY_ADMISSION.json';d=json.loads(data_path.read_text());d['needed_runtime_delta']={'path':path,'preimage_sha256':hashlib.sha256(raw).hexdigest(),'postimage_sha256':hashlib.sha256(updated.encode()).hexdigest(),'patch_file':str((P/'STAR_ATLAS_DRY_CONSTRUCTION_ADAPTER.patch').relative_to(ROOT)),'fixture_guard_preserved':True,'original_contents_body_exactly_unchanged':True,'integrator_call':'load("res://scripts/group2_vip_dry_club/package.gd").build_on_current_receiver(existing_star_atlas_upper_receiver)','runtime_validation':'Not executed here;Group1 is sole current combined build owner'}
first=json.loads((ROOT/'Game/data/group2_completion/contracts/781.json').read_text());floors=json.loads((ROOT/'Game/data/group2_completion/FLOOR_INTERFACE.json').read_text());row=next(v for v in floors['summary']if v['key']=='781_lower');floor_rows=[v for v in floors['rows']if v['source_owner']=='781']
d['next_single_home_choice']={'source_key':'781','tier':'Deluxe','lower_floor_world_xz':first['reservation']['proposed_floor_boundary'],'source_door_world_xyz':next(v['world_xyz']for v in first['markers']if v['name']=='DATUM_entry'),'existing_compiler_floor_preimage':floors['structural_preimage_sha256'],'unchanged_original_lower_floor_interface':floor_rows,'wanted_lower_floor_m2':row['wanted_m2'],'existing_compiler_covered_m2':row['already_supported_floor_m2'],'source_floor_interface_not_adopted':True,'choice_required':'Bind the240m2 single-level floor to actual lower receiving/bearing and a supported private arrival before calling completion.build_section(receiver,"781"). The outboard entryX-95.1/Z-42.7 is beyond the installed commons, unlike the ready dry fitout. Do not copy all91 old floor rows or route through the installed standard-room interiors','upper_private_lift_or790_changes_required':False,'new_units_or_capacity':0}
d['Group8_dining_receipts_distinct_programmes']=['D10_directory_01','D10_directory_02','D10_directory_03'];d['Group8_dining_place_credit_added']=0
data_path.write_text(json.dumps(d,indent=2)+'\n')
(P/'evidence/ADAPTER_SOURCE_PASS.json').write_text(json.dumps({'pass':True,'original_source_package_bytes_unchanged':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==hashlib.sha256(raw).hexdigest(),'preimage_sha256':hashlib.sha256(raw).hexdigest(),'postimage_sha256':hashlib.sha256(updated.encode()).hexdigest(),'original_contents_body_exactly_preserved':True,'old_fixture_guard_retained':True,'preview_only_no_shared_patch_applied':True,'new_engine_run':False},indent=2)+'\n')
shutil.copy2('/workspace/group2-current-star-atlas-measurement002.log',P/'evidence/MEASUREMENT002.log')
print('Prepared exact source adapter;four materializations,zero floor/capacity changes;Group1 current-build validation required')
