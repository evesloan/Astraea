from pathlib import Path
import bpy,json,hashlib,os
P=Path(__file__).resolve().parent;ST=Path(os.environ.get('ASTRAEA_PORTABLE_CHECK_OUTPUT','/tmp/aft-houses-portability-check'));ST.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();app=json.loads((P/'CURRENT_AFT_SOURCE_APPLICATION.json').read_text());result=[]
for house in app['houses']:
 source=P/house['current_editable_house']['package_relative'];before=sha(source);assert before==house['current_editable_house']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();libs=[]
 for lib in bpy.data.libraries:
  q=Path(bpy.path.abspath(lib.filepath));assert q.is_file(),q;libs.append({'stored':lib.filepath,'resolved_for_verification':str(q),'sha256':sha(q)})
 rows=[]
 for row in house['units']:
  ob=bpy.context.scene.objects.get(row['unit_id']);assert ob is not None and ob.instance_type=='COLLECTION'and len(ob.instance_collection.objects)>10
  x,y,z=row['origin_world_xyz'];error=max(abs(a-b)for a,b in zip(ob.location,(x,-z,y)));assert error<2e-5 and abs(ob.rotation_euler.z-row['yaw_godot'])<1e-6
  assert json.loads(ob['rest_slot_ids'])==[a['unit_slot_key']for a in row['slot_bindings']];rows.append({'unit_id':row['unit_id'],'source_index':row['source_index'],'location_error_m':error,'members':len(ob.instance_collection.objects)})
 assert len(rows)==house['new_source_interiors']and sum(len(r['slot_bindings'])for r in house['units'])==house['rest_slots'];assert sha(source)==before
 result.append({'house':house['house_folder'],'source_sha256':before,'new_linked_interiors':len(rows),'exact_rest_slot_IDs':house['rest_slots'],'libraries':libs,'instances':rows})
r={'status':'PASS_NATIVE_TWO_PORTABLE_HOUSE_REOPEN','new_linked_interiors':sum(x['new_linked_interiors']for x in result),'exact_rest_slot_IDs':sum(x['exact_rest_slot_IDs']for x in result),'houses':result,'geometry_material_lighting_or_source_files_changed':False,'Game_or_Catalogue_writes':False,'scope':'Actual saved whole-house source/library/identity reopening after reversible path-field edits. No geometry rebuild, render or broad repeated QA.'};assert r['new_linked_interiors']==165 and r['exact_rest_slot_IDs']==429;(ST/'NATIVE_PORTABILITY_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['new_linked_interiors'],r['exact_rest_slot_IDs'],flush=True)
