"""Independent reopen geometry/preservation check for the composed scratch derivative."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_001'))
from firstpass_common import *
BASE=P/'source/AST-CUL-005_firstpass_001.blend';SOURCE=R/'source/AST-CUL-005_firstpass_002.blend';REPORT=R/'SOURCE_REOPEN_REPORT_002.json';assert not REPORT.exists();assert sha(BASE)=='a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce';sourcehash=sha(SOURCE);build=read(R/'SOURCE_BUILD_REPORT_002.json');assert build['source_sha256']==sourcehash
lighting=read(R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json');garden=read(R/'PLANTED_COURT_GEOMETRY_002.json');bpy.ops.wm.open_mainfile(filepath=str(BASE));expected=baseline_snapshot(bpy)
for name in build['allowed_existing_object_records_excluded']:assert name in expected['objects'];expected['objects'].pop(name)
# Preserve every material used by original mesh/curve objects; separately record any unused source orphan.
unused=[]
for mat in list(bpy.data.materials):
 if mat.users==0 and not mat.use_fake_user and not any(slot.material==mat for ob in bpy.data.objects for slot in ob.material_slots):unused.append({'name':mat.name,'sha256':expected['materials'].pop(mat.name)})
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.view_layer.update();errors=compare_subset(expected,baseline_snapshot(bpy));assert not errors,errors[:25]
maxpos=0.;names=[]
for spec in lighting['objects']+garden['objects']:
 ob=bpy.data.objects.get(spec['name']);assert ob and ob.type=='MESH';assert ob.get('semantic_id')==spec['name'];assert len(ob.data.vertices)==len(spec['vertices_world']);assert len(ob.data.polygons)==len(spec['faces'])
 e=max((Vector(wvec(ob.matrix_world@v.co))-Vector(p)).length for v,p in zip(ob.data.vertices,spec['vertices_world']));maxpos=max(maxpos,e);assert e<.000045,(ob.name,e)
 assert [list(p.vertices)for p in ob.data.polygons]==spec['faces'];names.append(ob.name)
checks=verify_new_geometry(bpy,names);plantchecks=[]
for row in garden['plant_instances']:
 ob=bpy.data.objects[row['id']];assert ob.instance_type=='COLLECTION'and ob.instance_collection;assert list(ob.scale)==[1.,1.,1.];assert (Vector(wvec(ob.matrix_world.translation))-Vector(row['position_world'])).length<.00003;assert abs(ob.rotation_euler.z-row['yaw_radians'])<.000002
 soil=bpy.data.objects[row['root_receiver']];top=max((soil.matrix_world@v.co).z for v in soil.data.vertices);root=(ob.matrix_world.translation).z;assert abs((top-root)-.003)<.00004,(row['id'],top,root);plantchecks.append({'instance':row['id'],'root_embed_m':top-root,'receiver':soil.name})
for row in garden['furniture_pose_changes']:
 ob=bpy.data.objects['FP_'+row['id']];assert (Vector(wvec(ob.matrix_world.translation))-Vector(row['position_world'])).length<.00003;assert abs(ob.rotation_euler.z-row['yaw_radians'])<.000002
for spec in lighting['physical_bank_light_candidates']:
 ob=bpy.data.objects[spec['id']];assert ob.type=='LIGHT'and ob['physical_fixture']==spec['fixture_name'];assert bpy.data.objects.get(spec['fixture_name']);assert (Vector(wvec(ob.matrix_world.translation))-Vector(spec['position_world'])).length<.00003;assert abs(ob.data.energy-spec['initial_source_watts'])<.01
assert len(lighting['first_arrival_eight_source_preview'])==8 and len(set(lighting['first_arrival_eight_source_preview']))==8
assert len([o for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003'])==2200;assert sha(SOURCE)==sourcehash
result={'status':'Reopened composed source preservation/mesh/instance checks passed; budgeted visual and native route/lighting checks remain','source_sha256':sourcehash,'base_source_sha256':sha(BASE),'preserved_object_records':len(expected['objects']),'preserved_original_material_graphs':len(expected['materials']),'unused_orphan_materials_separately_recorded':unused,'allowed_furniture_pose_changes':len(garden['furniture_pose_changes']),'new_mesh_checks':checks,'maximum_new_vertex_error_m':maxpos,'plant_root_checks':plantchecks,'physical_bank_candidates':len(lighting['physical_bank_light_candidates']),'arrival_eight_sources':lighting['first_arrival_eight_source_preview'],'authored_original_chairs':2200,'pending':['Same-camera eight-source visual review','Seated/normal-walking local-budget views','Actual fixture exit/receiver and full-source internal contact review','Native Godot visibility-selection/import/collision/operation gates']}
with REPORT.open('x')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps({k:result[k]for k in ['status','source_sha256','maximum_new_vertex_error_m','authored_original_chairs']}))
