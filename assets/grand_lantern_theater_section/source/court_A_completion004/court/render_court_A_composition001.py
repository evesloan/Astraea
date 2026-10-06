"""One normal-eye source composition study. No save, new fill, exposure increase or hidden walls."""
from pathlib import Path
import bpy,bmesh,sys,json,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');G=Path('/workspace/shared/astraea-godot-production-20261003');sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import baseline_snapshot,compare_subset
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());composition=read(R/'composed_review001/COMPOSITION_REPORT.json');source=Path(composition['source']);assert sha(source)==composition['sha256'];out=R/'composition_view001';out.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);scene=bpy.context.scene;assert not compare_subset(composition['preserved_base_snapshot'],baseline_snapshot(bpy));assert scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value==0
# These are the exact eight source identities selected by the native Court A
# front capture. Native energy and Cycles wattage are recorded separately.
active=['FP2_D11_BANK_0','FP2_D11_BANK_1','FP2_D11_BANK_2','FP2_D11_BANK_3','FP2_D11_BANK_4','FP2_D11_BANK_5','FP2_D12_BANK_3','FP2_D12_BANK_4'];data=read(G/'data/architecture/THEATER_RUNTIME_STAGE001.json');fixtures={r['id']:r for r in data['fixtures']};lights=[]
def bv(p):return Vector((p[0],-p[2],p[1]))
for ob in scene.objects:
 if ob.type=='LIGHT':ob.hide_render=ob.name not in active
for name in active:
 ob=bpy.data.objects[name];entry=fixtures[name];assert ob.type=='LIGHT'and not ob.hide_render and(ob.location-bv(entry['position_world'])).length<.001
 before={'energy_watts':ob.data.energy,'full_cone_degrees':math.degrees(ob.data.spot_size)if ob.data.type=='SPOT'else None}
 if entry['type']=='SPOT':
  assert ob.data.type=='SPOT';ob.data.spot_size=math.radians(entry['full_cone_degrees']);ob.rotation_euler=bv(entry['aim_world']).to_track_quat('-Z','Y').to_euler()
 else:assert ob.data.type=='POINT'
 lights.append({'id':name,'source_watts_unchanged':ob.data.energy,'native_energy':entry['initial_native_energy'],'native_range_m':entry['range_m'],'native_full_cone_degrees':entry.get('full_cone_degrees'),'source_position_world':entry['position_world'],'before_source_optic':before})
assert sum(o.type=='LIGHT'and not o.hide_render for o in scene.objects)==8
assert all(not o.hide_render for o in scene.objects if o.type=='MESH')
# Native Compatibility has visible emissive lenses but no emissive GI; retain
# their camera appearance without introducing unbudgeted analytic/area fills.
for original in list(bpy.data.materials):
 if not original.use_nodes or not any(n.type=='BSDF_PRINCIPLED'and n.inputs.get('Emission Strength')and n.inputs['Emission Strength'].default_value>0 for n in original.node_tree.nodes):continue
 mat=original.copy();mat.name='VIEW_CAMERA_ONLY_'+original.name
 for node in mat.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED'and node.inputs.get('Emission Strength')and node.inputs['Emission Strength'].default_value>0:
   strength=node.inputs['Emission Strength'].default_value;lp=mat.node_tree.nodes.new('ShaderNodeLightPath');mul=mat.node_tree.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=strength;mat.node_tree.links.new(lp.outputs['Is Camera Ray'],mul.inputs[0]);mat.node_tree.links.new(mul.outputs[0],node.inputs['Emission Strength'])
 for ob in bpy.data.objects:
  if ob.type=='MESH':
   for i,m in enumerate(list(ob.data.materials)):
    if m==original:ob.data.materials[i]=mat
# Source package excludes compiler-owned D11 floor. Display the exact current
# installed compiler record as temporary review geometry, never a new floor.
compiled=read(G/'data/generated/structural_meshes.json');floor=next(r for r in compiled['regions']if r['id']=='D11_theater_flat_00');verts=[];faces=[];face_uv=[];face_materials=[];fy=float(floor['floor_y']);bottom=fy-float(floor['thickness'])
def emit(points,normal,material):
 points=[Vector(p)for p in points];normal=Vector(normal)
 if(points[1]-points[0]).cross(points[2]-points[0]).dot(normal)<0:points[1],points[2]=points[2],points[1]
 base=len(verts);verts.extend([bv(p)for p in points]);faces.append([base,base+1,base+2]);face_materials.append(material)
 face_uv.append([[p.x*.3,p.z*.3]if abs(normal.y)>.9 else[(p.x+p.z)*.3,p.y*.3]for p in points])
for tri in floor['triangles']:
 emit([[x,fy,z]for x,z in tri],[0,1,0],0);emit([[x,bottom,z]for x,z in tri],[0,-1,0],1)
for ring in floor['rings']:
 for a,b in zip(ring,ring[1:]+ring[:1]):
  aa=[a[0],fy,a[1]];bb=[b[0],fy,b[1]];ba=[a[0],bottom,a[1]];bt=[b[0],bottom,b[1]];normal=[b[1]-a[1],0,-(b[0]-a[0])];emit([aa,bb,bt],normal,1);emit([aa,bt,ba],normal,1)
me=bpy.data.meshes.new('VIEW_ONLY_INSTALLED_D11_COMPILER_FLOOR');me.from_pydata(verts,[],faces);me.update();floor_material_records=[]
for role in ['warm_stone','ivory_enamel']:
 path=G/('assets/textures/'+role+'.png');mat=bpy.data.materials.new('VIEW_NATIVE_FLOOR_'+role);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.83;image=bpy.data.images.load(str(path),check_existing=False);node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.interpolation='Closest';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);me.materials.append(mat);floor_material_records.append({'role':role,'native_texture_sha256':sha(path),'roughness':.83,'uv_cycles_per_m':.3,'nearest_filter_source_approximation':True})
uv=me.uv_layers.new(name='ExactNativeFloorUV')
for face,coords,mi in zip(me.polygons,face_uv,face_materials):
 face.material_index=mi
 for li,uvpoint in zip(face.loop_indices,coords):uv.data[li].uv=uvpoint
ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob)
# Match the normal native camera pose AND vertical72-degree FOV. Earlier24mm
# source studies used a narrower horizontal FOV and are not a matched baseline.
eye=[-69.5,71.15,-131.7];target=[-69.5,71.3,-143];camdata=bpy.data.cameras.new('VIEW_COURT_A_NATIVE_POSE');camera=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(camera);camera.location=bv(eye);camera.rotation_euler=(bv(target)-camera.location).to_track_quat('-Z','Y').to_euler();camdata.sensor_fit='VERTICAL';camdata.sensor_height=24;camdata.lens=12/math.tan(math.radians(72)*.5);camdata.clip_start=.05;camdata.clip_end=1600;scene.camera=camera
assert abs(math.degrees(camdata.angle_y)-72)<.00002
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4;scene.cycles.transmission_bounces=6;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=768;scene.render.resolution_y=432;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.exposure=0;scene.render.filepath=str(out/'D11_Court_A_composition.png')
pre={'status':'SOURCE_COMPOSITION_STUDY_NOT_NATIVE_LIGHTING_ACCEPTANCE','source_sha256':sha(source),'base_source_sha256':composition['base_source_sha256'],'standalone_source_sha256':composition['standalone_source_sha256'],'camera_eye_world':eye,'camera_target_world':target,'camera_vertical_fov_degrees':72,'camera_horizontal_fov_degrees':math.degrees(2*math.atan(math.tan(math.radians(72)*.5)*16/9)),'native_camera_reference':'https://docs.godotengine.org/en/stable/classes/class_camera3d.html#class-camera3d-property-fov','source_wattage_not_native_energy_equivalence':True,'analytic_lights':lights,'no_new_fill_lights':True,'world_strength':0,'exposure':0,'camera_only_emission':True,'temporary_floor_materials':floor_material_records,'current_compiled_sha256':sha(G/'data/generated/structural_meshes.json'),'runtime_contract_sha256':sha(G/'data/architecture/THEATER_RUNTIME_STAGE001.json'),'resolution':[768,432],'samples':24,'denoising':False,'existing_geometry_hidden':False,'saved_or_exported':False};(out/'SETTINGS.json').write_text(json.dumps(pre,indent=2)+'\n');bpy.ops.render.render(write_still=True);assert sha(source)==composition['sha256'];pre.update(status='CAPTURED_SOURCE_COMPOSITION_REVIEW_PENDING',png=str(out/'D11_Court_A_composition.png'),png_sha256=sha(out/'D11_Court_A_composition.png'));(out/'RECEIPT.json').write_text(json.dumps(pre,indent=2)+'\n');print(json.dumps({'status':pre['status'],'png':pre['png'],'png_sha256':pre['png_sha256']}))
