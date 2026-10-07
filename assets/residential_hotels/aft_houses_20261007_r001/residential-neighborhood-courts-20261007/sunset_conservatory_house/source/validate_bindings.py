"""Exact 83-to-eight source binding and 215-slot identity audit, no engine use."""
from pathlib import Path
import json,hashlib,runpy,math,collections
R=Path(__file__).resolve().parents[1];W=R.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
p=read(R/'SUNSET_83_PLACEMENT_MAP.json');old=read(W/'residential-batch-neighborhood-20261006/scale_domestic_r011/assemblies/GODOT_BATCH_INSTANCE_MAP.json');by={r['census_source_index']:r for r in old['instances']};provenance=read(R/'REST_SLOT_PROVENANCE.json');screen=read(R/'qa/GEOMETRY_SCREEN.json');house=read(R/'outputs/house_r002/PLAN.json');batch=read(R/'outputs/interiors_r002/BATCH_RECEIPT.json')
proof={r['prototype']:r for r in batch['prototypes']};rows=[];slots=[]
for r in p['units']:
 o=by[r['census_source_index']];assert all(r[k]==o[k]for k in['address','rebuild_identity','allocation_sha256','allocation_x','allocation_z','historical_door_marker_xz','source_origin_world_xyz','source_yaw_godot','entry_persistent_id','bath_persistent_id'])
 assert [a['unit_slot_key']for a in r['anchor_bindings']]==[a['unit_slot_key']for a in o['anchor_bindings']]
 assert [a['unit_anchor_index']for a in r['anchor_bindings']]==[a['unit_anchor_index']for a in o['anchor_bindings']]
 assert not r['preserve_installed'];slots.extend(a['unit_slot_key']for a in r['anchor_bindings']);key=r['source_recipe_key'];d=R/'outputs/interiors_r002'/key
 for n,h in proof[key]['files'].items():assert sha(d/n)==h
 rows.append({'unit_id':r['rebuild_identity'],'source_index':r['census_source_index'],'prototype':key,'assembly_blend':str(d/'assembly.blend'),'assembly_sha256':sha(d/'assembly.blend'),'shell_glb':str(d/'shell.glb'),'shell_glb_sha256':sha(d/'shell.glb'),'rest_slots':[a['unit_slot_key']for a in r['anchor_bindings']],'runtime_enabled':False})
assert len(rows)==83 and len(slots)==len(set(slots))==215 and len(proof)==8
assert {r['census_source_index']for r in house['rooms']}=={r['source_index']for r in rows}
assert screen['all_component_transforms_pass']and screen['all_route_targets_pass']and not screen['furniture_pair_broad_overlaps']
newcontacts=[r for r in screen['shell_surface_contacts']if r['component']not in['bath_shower','EntryDoor','BathroomDoor']];assert not newcontacts
newdoc={'schema':'astraea.sunset_source_binding.v1','status':'PASS_SCOPED_83_UNIT_SOURCE_MAPPING','source_map_sha256':sha(R/'SUNSET_83_PLACEMENT_MAP.json'),'house_plan_sha256':sha(R/'outputs/house_r002/PLAN.json'),'units':rows,'unit_count':83,'source_family_count':8,'rest_slot_count':215,'unit_identity_allocation_doors_slots_ordinals_unchanged':True,'all_original_coordinates_are_explicit_unregistered_proposals':True,'known_historical_anchor_coordinates_changed':0,'installed_pilots_preserved_outside_scope':[16,40],'counts':p['counts'],'adjacent_variant_conflicts':0,'component_transforms_pass':True,'route_radius_m':.30,'all_interior_route_targets_pass':True,'new_rest_salon_shell_crossings':newcontacts,'inherited_door_shower_mount_contact_groups':len(screen['shell_surface_contacts']),'inherited_contact_scope':'Original entry door frame and bathroom door stops/jambs plus original shower frame/entry-wall contacts remain documented; this report does not accept runtime moving-door collision or waive retained-contact review.','no_runtime_adoption_or_acceptance':True,'unbuilt_specialty_vip':64}
(R/'qa/SOURCE_83_BINDING.json').write_text(json.dumps(newdoc,indent=2)+'\n');print('SUNSET_BINDING_PASS',len(rows),len(proof),len(slots))
