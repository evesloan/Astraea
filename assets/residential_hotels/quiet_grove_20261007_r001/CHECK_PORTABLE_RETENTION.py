from pathlib import Path
import bpy,json,hashlib,math,os
P=Path(__file__).resolve().parent;REPORT=Path(os.environ.get('ASTRAEA_REOPEN_REPORT','/tmp/quiet_grove_portable_reopen.json'));Q=P/'residential-neighborhood-courts-20261007/quiet_grove_interiors';model=Q/'outputs/context_r002/quiet_grove_house_83.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(model)
app=json.loads((Q/'QUIET_GROVE_83_CURRENT_APPLICATION.json').read_text());port=json.loads((P/'RETENTION_PORTABILITY.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(model));bpy.context.view_layer.update();libraries=[]
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath));assert path.is_file(),path;libraries.append({'stored':lib.filepath,'resolved_for_verification':str(path),'sha256':sha(path)})
rooms=[]
for row in app['units']:
 ob=bpy.context.scene.objects.get(row['rebuild_identity']);assert ob is not None and ob.instance_type=='COLLECTION'and len(ob.instance_collection.objects)>10
 x,y,z=row['source_origin_world_xyz'];error=max(abs(a-b)for a,b in zip(ob.location,(x,-z,y)));assert error<2e-5;assert abs(ob.rotation_euler.z-row['source_yaw_godot'])<1e-6
 rooms.append({'source_index':row['census_source_index'],'unit_id':row['rebuild_identity'],'location_error_m':error,'members':len(ob.instance_collection.objects)})
assert len(rooms)==83 and sum(len(r['bed_anchors'])for r in app['units'])==215
assert sha(model)==before
report={'status':'PASS_NATIVE_PORTABLE_SOURCE_REOPEN','portable_model_sha256':before,'actual_linked_rooms':len(rooms),'retained_rest_slots':215,'linked_libraries':libraries,'room_checks':rooms,'production_files_saved_or_changed':False,'Game_or_Catalogue_writes':False,'scope':'Actual Blender reopen and library/83instance resolution after fixed-field path repair. Existing geometry and source family checks are not rerun.'}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rooms),len(libraries),flush=True)
