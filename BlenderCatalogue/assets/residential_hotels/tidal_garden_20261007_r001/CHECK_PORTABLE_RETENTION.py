from pathlib import Path
import bpy,json,hashlib,os
P=Path(__file__).resolve().parent;ST=Path(os.environ.get('ASTRAEA_PORTABLE_CHECK_OUTPUT','/tmp/tidal-portability-check'));ST.mkdir(parents=True,exist_ok=True);T=P/'residential-neighborhood-courts-20261007/tidal_garden_house';model=T/'outputs/house_r001/house.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(model)
app=json.loads((P/'CURRENT_TIDAL_APPLICATION.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(model));bpy.context.view_layer.update();libs=[]
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath));assert path.is_file(),path;libs.append({'stored':lib.filepath,'resolved_for_verification':str(path),'sha256':sha(path)})
rooms=[]
for r in app['units']:
 ob=bpy.context.scene.objects.get(r['rebuild_identity']);assert ob is not None and ob.instance_type=='COLLECTION' and len(ob.instance_collection.objects)>10
 x,y,z=r['source_origin_world_xyz'];err=max(abs(a-b) for a,b in zip(ob.location,(x,-z,y)));assert err<2e-5;assert abs(ob.rotation_euler.z-r['source_yaw_godot'])<1e-6
 assert json.loads(ob['rest_slot_ids'])==[a['unit_slot_key'] for a in r['anchor_bindings']]
 rooms.append({'source_index':r['census_source_index'],'unit_id':r['rebuild_identity'],'location_error_m':err,'members':len(ob.instance_collection.objects)})
assert len(rooms)==85 and sum(len(r['anchor_bindings']) for r in app['units'])==221
assert sha(model)==before
out={'status':'PASS_NATIVE_PORTABLE_SOURCE_REOPEN','portable_model_sha256':before,'actual_linked_rooms':85,'exact_rest_slot_ids_and_ordinals':221,'linked_libraries':libs,'room_checks':rooms,'production_files_saved_or_changed':False,'Game_or_Catalogue_writes':False,'scope':'Saved whole-house Blender reopening and linked instance identities only; no duplicate build, export or geometry suite'}
(ST/'NATIVE_PORTABILITY_PROOF.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rooms),len(libs),flush=True)
