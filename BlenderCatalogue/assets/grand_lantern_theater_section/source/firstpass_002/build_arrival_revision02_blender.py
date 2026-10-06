"""Add coherent arrival lighting/planting into a NEW scratch derivative only."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_001'))
from firstpass_common import *
import build_firstpass_assembly as source_tools
BASE=P/'source/AST-CUL-005_firstpass_001.blend';BASEHASH='a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce';OUT=R/'source/AST-CUL-005_firstpass_002.blend';REPORT=R/'SOURCE_BUILD_REPORT_002.json'
assert sha(BASE)==BASEHASH and not OUT.exists() and not REPORT.exists();bpy.ops.wm.open_mainfile(filepath=str(BASE))
lighting=read(R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json');garden=read(R/'PLANTED_COURT_GEOMETRY_002.json');before=baseline_snapshot(bpy);allowed=[];moved=[]
root=bpy.data.objects.new('AST_CUL005_FIRSTPASS_002',None);bpy.context.collection.objects.link(root);root['source_only']=True;root['base_sha256']=BASEHASH;root['runtime_installed']=False
source_tools.ROOT=root;source_tools.BASE_MATS=list(bpy.data.materials)
# Explicitly move only first-pass informal furnishings, keeping their complete mesh definitions.
for row in garden['furniture_pose_changes']:
 ob=bpy.data.objects['FP_'+row['id']];allowed.append(ob.name);ob.location=bvec(row['position_world']);ob.rotation_euler.z=row['yaw_radians'];moved.append({'name':ob.name,'position_world':row['position_world'],'yaw':row['yaw_radians']})
# Move the actual tabletop pot/rosette pair with its parent table, with its support unchanged.
surface=read(P/'source/firstpass_001/SURFACE_CONTENTS_AND_FINISH_PLAN.json');moves={r['id']:r for r in garden['furniture_pose_changes']}
for item in surface['surface_contents']:
 if item['support_instance']not in moves:continue
 move=moves[item['support_instance']];delta=[move['position_world'][k]-move['before_position'][k]for k in range(3)]
 assert move['yaw_radians']==move['before_yaw'],'Rotated table contents need explicit transformed anchors'
 for kind in ['pot','plant']:
  ob=bpy.data.objects['FP_'+item['id']+'_'+kind];allowed.append(ob.name);ob.location+=Vector(bvec(delta));moved.append({'name':ob.name,'world_translation':delta})
# The rotated rehearsal bench faces the real shielded cue/notes stand; light follows its aperture.
cue=moves['D11_backstage_09'];pos=cue['position_world'];angle=cue['yaw_radians'];ob=bpy.data.objects['FP_PRACTICAL_D11_backstage_09_task_light'];allowed.append(ob.name);ob.location=bvec([pos[0]-.015*math.sin(angle),pos[1]+1.547,pos[2]-.015*math.cos(angle)])
for name in allowed:before['objects'].pop(name)
# Retain family sources; use existing prototype if already present, otherwise append exact original.
measurements=garden['retained_asset_measurements'];definitions={}
for asset,row in measurements.items():
 col=bpy.data.collections.get('FP_RETAINED_'+asset)
 if col is not None:definitions[asset]=(col,{}, {'asset':asset,'reuse_saved_definition':True,'source_sha256':row['source_sha256']})
 else:definitions[asset]=source_tools.load_definition(asset,measurements)
plants=[]
for row in garden['plant_instances']:
 ob=source_tools.instance(definitions[row['asset']][0],row['id'],row['position_world'],row['yaw_radians']);ob['retained_family']=row['asset'];ob['root_receiver']=row['root_receiver'];plants.append(ob.name)
CAT=P.parents[1];specs={}
for rel in ['materials/material_manifest.json','materials/auditorium/manifest.json','materials/staff/manifest.json']:
 for role,spec in read(CAT/rel)['materials'].items():specs[role]={**spec,'manifest_dir':str(Path(rel).parent)}
geometry=lighting['objects']+garden['objects'];materials={}
for role in {r['material_family']for r in geometry}:
 if role=='hospitality_opal':
  original=next(m for m in source_tools.BASE_MATS if m.name.split('.')[0]=='GardenOpalLens');mat=original.copy();mat.name='FP2_PublicOpal';bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.91,.80,1);bs.inputs['Emission Strength'].default_value=1.5;mat['source_material_family']='GardenOpalLens';mat['preview_emission_not_extra_runtime_light']=True;materials[role]=mat
 else:materials[role]=source_tools.existing_or_new_material(role,definitions,specs)
new_names=source_tools.add_architecture({'objects':geometry},materials,specs)
for spec in geometry:
 ob=bpy.data.objects[spec['name']];ob['semantic_id']=spec['name'];assert ob.name==spec['name'] and len(ob.name.encode())<64
# Physical Omni bank anchors are inside actual visible fixture apertures.
new_lights=[]
for spec in lighting['physical_bank_light_candidates']:
 data=bpy.data.lights.new(spec['id'],'SPOT'if spec['type']=='SPOT'else'POINT');data.energy=spec['initial_source_watts'];data.color=spec['color_linear'];data.shadow_soft_size=.12
 ob=bpy.data.objects.new(spec['id'],data);bpy.context.collection.objects.link(ob);ob.parent=root;ob.location=bvec(spec['position_world']);ob['physical_fixture']=spec['fixture_name'];ob['proposed_godot_range_m']=spec['range_m'];ob['represented_fixtures']=json.dumps(spec['represented_fixtures']);ob['source_only']=True;ob['source_budget_bank']=True;new_lights.append(ob.name)
 if spec['type']=='SPOT':
  data.spot_size=math.radians(spec['full_cone_degrees']);data.spot_blend=.35;ob.rotation_euler=Vector(bvec(spec['aim_world'])).to_track_quat('-Z','Y').to_euler();ob['illumination_anchor']=spec['illumination_anchor']
# Additional honest eye positions; original arrival camera remains byte-exact.
for ident,position,target,height,kind in [('D11_seated_west',[-91,70.7,-136.85],[-89.5,71.2,-142],1.2,'seated review scenario, not all-species acceptance'),('D11_walk_to_ushers',[-63.5,71.15,-137],[-70.5,71.2,-140],1.65,'normal walking review')]:
 data=bpy.data.cameras.new('FP2_VIEW_'+ident);ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=bvec(position);ob.rotation_euler=(Vector(bvec(target))-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=24;ob['eye_height_m']=height;ob['view_kind']=kind
root['bank_preview_ids']=json.dumps(lighting['first_arrival_eight_source_preview']);bpy.context.scene['arrival_revision_status']='Composed planted courts and mounted luminous architecture. Eight-source same-camera visual and native budget/route gates pending.'
errors=compare_subset(before,baseline_snapshot(bpy));assert not errors,errors[:20];assert len([o for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003'])==2200
checks=verify_new_geometry(bpy,new_names);textures=source_tools.texture_audit(specs);assert sha(BASE)==BASEHASH
report={'status':'New source derivative authored; independent reopen and eight-source visual acceptance pending','base_source_sha256':BASEHASH,'source':str(OUT),'source_sha256':None,'allowed_existing_instance_pose_changes':moved,'allowed_existing_object_records_excluded':allowed,'preservation_snapshot':before,'new_geometry_checks':checks,'new_plant_instances':plants,'retained_definitions':[r[2]for r in definitions.values()],'new_physical_bank_candidates':new_lights,'first_arrival_active_direct_sources':lighting['first_arrival_eight_source_preview'],'authored_original_chairs':2200,'material_texture_checks':textures,'input_hashes':{p.name:sha(p)for p in [Path(__file__),R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json',R/'PLANTED_COURT_GEOMETRY_002.json',R/'FURNITURE_STANCE_SCREEN.json']},'pending':['Independent reopened preservation/geometry/roots/fixture exits','Eight-source same-arrival view and normal/seated views','Actual Godot visibility/range selection and collision/import fidelity','Remaining first-pass visual refinement based on images']}
json.dumps(report,allow_nan=False);OUT.parent.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(OUT));report['source_sha256']=sha(OUT)
with REPORT.open('x')as f:json.dump(report,f,indent=2,allow_nan=False)
assert sha(BASE)==BASEHASH;print(json.dumps({k:report[k]for k in ['status','source','source_sha256','authored_original_chairs']}))
