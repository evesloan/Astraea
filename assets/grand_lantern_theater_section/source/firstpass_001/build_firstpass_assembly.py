"""New editable first-pass derivative only. Run in parent's reserved source slot.
No runtime export, registry mutation, render, or overwrite of an existing Blend.
"""
import argparse,json,math,sys,hashlib
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from firstpass_common import *
import build_mechanism_package_compact as mechanisms
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PACKAGE=CAT/'assets/grand_lantern_theater_section'
BASE=PACKAGE/'source/AST-CUL-005.blend'
EXPECTED_BASE='c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5'

def check_pins():
 pins=read(HERE/'FIRSTPASS_BUILD_INPUT_PINS.json')
 for path,h in pins['input_sha256'].items():assert sha(Path(path))==h,('Input changed',path)
 assert sha(BASE)==EXPECTED_BASE
 return pins

def trim_cap_ranges(removal):
 found=[]
 for ob in list(bpy.data.objects):
  if 'pure_part_ranges' not in ob:continue
  ranges=json.loads(ob['pure_part_ranges']);cut=[r for r in ranges if r['name'] in removal]
  if not cut:continue
  old=ob.data;verts=[];faces=[];kept=[];polys=[];uvs={l.name:[]for l in old.uv_layers}
  for r in ranges:
   if r['name'] in removal:found.append(r['name']);continue
   vs=len(verts);fs=len(faces);verts.extend(tuple(v.co)for v in list(old.vertices)[r['vertex_start']:r['vertex_start']+r['vertex_count']])
   for p in list(old.polygons)[r['face_start']:r['face_start']+r['face_count']]:
    faces.append([vs+i-r['vertex_start']for i in p.vertices]);polys.append((p.material_index,p.use_smooth))
    for layer in old.uv_layers:uvs[layer.name].extend(tuple(layer.data[i].uv)for i in p.loop_indices)
   kept.append({**r,'vertex_start':vs,'face_start':fs})
  me=bpy.data.meshes.new(old.name+'_six_cap_removal');me.from_pydata(verts,[],faces);me.update()
  for mat in old.materials:me.materials.append(mat)
  for p,(mi,smooth)in zip(me.polygons,polys):p.material_index=mi;p.use_smooth=smooth
  for olduv in old.uv_layers:
   layer=me.uv_layers.new(name=olduv.name);layer.active_render=olduv.active_render
   assert len(layer.data)==len(uvs[olduv.name])
   for x,v in zip(layer.data,uvs[olduv.name]):x.uv=v
  ob.data=me;ob['pure_part_ranges']=json.dumps(kept);ob['pure_part_names']=json.dumps([r['name']for r in kept])
 assert sorted(found)==sorted(removal),(found,removal)
 return found

def world_matrix(ob):
 if ob.parent:return world_matrix(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis
 return ob.matrix_basis.copy()

def load_definition(asset,measurements):
 row=measurements[asset];path=CAT/row['source'];assert sha(path)==row['source_sha256']
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):
  requested=tuple(src.objects);dst.objects=list(requested)
 pairs=list(zip(requested,dst.objects));root=next((ob for name,ob in pairs if name==asset),None)
 def belongs(ob):
  if root is None:return True
  while ob:
   if ob==root:return True
   ob=ob.parent
  return False
 members=[ob for _,ob in pairs if ob and ob.type in {'MESH','EMPTY','CURVE','FONT'} and belongs(ob)]
 assert any(ob.type=='MESH'for ob in members),asset
 collection=bpy.data.collections.new('FP_RETAINED_'+asset)
 names={}
 for source_name,ob in pairs:
  if ob in members:
   names[source_name]=ob;collection.objects.link(ob);ob['firstpass_retained_source_object']=source_name
 # Collections remain unlinked; explicit instances own placement. No source root scale edits.
 points=[wvec(world_matrix(ob)@v.co)for ob in members if ob.type=='MESH'for v in ob.data.vertices]
 bounds={'min':[min(p[k]for p in points)for k in range(3)],'max':[max(p[k]for p in points)for k in range(3)]}
 maximum=max(abs(bounds[edge][k]-row['bounds_gltf'][edge][k])for edge in ['min','max']for k in range(3))
 assert maximum<.003,('Retained definition differs from measured export',asset,bounds,row['bounds_gltf'],maximum)
 return collection,names,{'asset':asset,'source':str(path),'source_sha256':row['source_sha256'],'source_objects':list(names),'raw_source_vs_export_bounds_error_m':maximum,'retained_mesh_uv_fingerprints':{name:digest(mesh_record(ob.data)) for name,ob in names.items() if ob.type=='MESH'}}

def instance(col,name,pos,yaw=0,rotation=None):
 assert not bpy.data.objects.get(name),name
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.instance_type='COLLECTION';ob.instance_collection=col;ob.location=bvec(pos)
 if rotation is not None:ob.rotation_euler=rotation.to_euler()
 else:ob.rotation_euler.z=yaw
 ob['firstpass_new_instance']=True;ob['source_only']=True
 return ob

def existing_or_new_material(role,definitions,specs):
 # Exact retained original graphs are preferred; no shader mutation in baseline materials.
 for mat in BASE_MATS:
  if mat.get('astraea_material_role')==role or mat.name in [role,'ASTRAEA_'+role]:return mat
 for col,names,_ in definitions.values():
  for ob in col.objects:
   if ob.type!='MESH':continue
   for mat in ob.data.materials:
    if mat and (mat.get('astraea_material_role')==role or mat.name.split('.')[0] in [role,'ASTRAEA_'+role]):return mat
 if role=='hospitality_opal':
  for ob in definitions['AST-LGT-001'][0].objects:
   if ob.type=='MESH':
    for mat in ob.data.materials:
     if mat and mat.name.split('.')[0]=='GardenOpalLens':return mat
  raise RuntimeError('Missing retained GardenOpalLens')
 spec=specs[role];path=CAT/spec['manifest_dir']/(spec.get('file')or spec['base_color_file']);assert sha(path)==spec['sha256']
 mat=bpy.data.materials.new('FP_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['meters_per_tile_uv']=spec['meters_per_tile_uv']
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=spec['roughness'];bs.inputs['Metallic'].default_value=spec['metallic']
 image=bpy.data.images.load(str(path),check_existing=False);image.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 return mat

def add_architecture(package,materials,specs):
 names=[]
 for row in package['objects']:
  me=bpy.data.meshes.new(row['name']);me.from_pydata([bvec(v)for v in row['vertices_world']],[],row['faces']);me.update()
  role=row['material_family'];me.materials.append(materials[role]);uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
  scale=specs[role]['meters_per_tile_uv'] if role in specs else[1,1]
  for face in me.polygons:
   axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
   for li in face.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
  ob=bpy.data.objects.new(row['name'],me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob['source_only']=True;ob['firstpass_new_geometry']=True;ob['material_family']=role;ob['collision_role']=row['role'];ob['source_spec']=json.dumps({k:v for k,v in row.items()if k not in ['vertices_world','faces']})
  names.append(ob.name)
 return names

def stage_head_definition(definition,angle):
 _,named,_=definition;hinge=named['LIGHT_AIM_X'];pivot=world_matrix(hinge).translation;col=bpy.data.collections.new('FP_RETAINED_CUL004_STAGE_HEAD');result=[]
 def under_hinge(ob):
  while ob:
   if ob==hinge:return True
   ob=ob.parent
  return False
 for source_name,ob in named.items():
  fixed=source_name=='light_yoke_crossbar' or any(s in source_name for s in ['_light_yoke_upright','_fixed_aim_stub','_retained_aim_pin','_aim_pin_inner_retainer'])
  if ob.type!='MESH' or not(fixed or under_hinge(ob)):continue
  new=ob.copy();new.data=ob.data.copy();new.name='FP_HEAD_'+source_name;new.parent=None;new.matrix_world=Matrix.Identity(4)
  transform=Matrix.Translation(-pivot)@world_matrix(ob)
  if under_hinge(ob):transform=Matrix.Rotation(angle,4,'X')@transform
  new.data.transform(transform);col.objects.link(new);new['source_derivative_part']=source_name;result.append(new.name)
 assert len(result)>=30,('Incomplete retained yoke/hood',len(result))
 return col,result

def make_practical_lenses_visible(definitions):
 # Only appended fixture definitions receive a local lamp-on derivative.
 # Preserve source texture nodes, UVs and roughness; no original datablock changes.
 records=[]
 for asset in ['AST-CUL-004','AST-STF-006']:
  replacements={}
  for ob in definitions[asset][0].objects:
   if ob.type!='MESH':continue
   for i,mat in enumerate(list(ob.data.materials)):
    if not mat or mat.get('astraea_material_role')!='staff_opal':continue
    if mat not in replacements:
     new=mat.copy();new.name='FP_PRACTICAL_'+asset+'_staff_opal';bs=next(n for n in new.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
     bs.inputs['Emission Color'].default_value=(1,.86,.65,1);bs.inputs['Emission Strength'].default_value=.45
     new['lamp_on_derivative_of']=mat.name;replacements[mat]=new;records.append({'asset':asset,'original_material':mat.name,'local_material':new.name,'emission_strength':.45})
    ob.data.materials[i]=replacements[mat]
 return records

def texture_audit(specs):
 used={mat for ob in bpy.data.objects if ob.type=='MESH'for mat in ob.data.materials if mat};rows=[]
 for mat in sorted(used,key=lambda m:m.name):
  images=[]
  for node in image_nodes(mat.node_tree if mat.use_nodes else None):
   im=node.image
   if not im.packed_file:im.pack()
   assert im.packed_file,('Unpacked image',im.name)
   actual_hash=hashlib.sha256(im.packed_file.data).hexdigest();role=mat.get('astraea_material_role','')
   if role in specs:assert actual_hash==specs[role]['sha256'],('Retained texture bytes mismatch',mat.name,im.name)
   images.append({'name':im.name,'packed_sha256':actual_hash,'bytes':len(im.packed_file.data)})
  rows.append({'name':mat.name,'role':mat.get('astraea_material_role',''),'images':images})
 return rows

def main():
 global ROOT,BASE_MATS
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--report',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(args.output);report_path=Path(args.report)
 assert out==PACKAGE/'source/AST-CUL-005_firstpass_001.blend';assert report_path.parent==PACKAGE/'qa';assert not out.exists() and not report_path.exists(),'Never overwrite a source or receipt'
 pins=check_pins();bpy.ops.wm.open_mainfile(filepath=str(BASE));BASE_MATS=list(bpy.data.materials)
 mech=read(HERE/'mechanism_package_compact.json');removal=mech['baseline_removal_by_parent_only'];baseline=baseline_snapshot(bpy,removal);assert len(baseline['parts'])==6962
 removed=trim_cap_ranges(removal);assert not compare_subset(baseline,baseline_snapshot(bpy,removal))
 ROOT=bpy.data.objects.new('AST-CUL-005_FIRSTPASS_001',None);bpy.context.collection.objects.link(ROOT);ROOT['source_only']=True;ROOT['base_source_sha256']=EXPECTED_BASE;ROOT['first_pass_visual_acceptance']=False
 additions=read(HERE/'FIRST_PASS_ADDITIONS_PLAN.json');lighting=read(HERE/'LIGHTING_ENCLOSURE_VIEW_PLAN.json');surface=read(HERE/'SURFACE_CONTENTS_AND_FINISH_PLAN.json');arch=read(HERE/'ARCHITECTURE_ADDITIONS_GEOMETRY.json');measurements=read(HERE/'RETAINED_MODULE_MEASUREMENTS.json')
 assets={r['asset']for r in additions['ground_modules']}|{'AST-LGT-001','AST-STF-006','AST-CUL-004'}|{r[k]for r in surface['surface_contents']for k in ['pot_asset','plant_asset']}
 definitions={asset:load_definition(asset,measurements)for asset in sorted(assets)}
 lens_derivatives=make_practical_lenses_visible(definitions)
 furniture=[]
 for row in additions['ground_modules']:
  ob=instance(definitions[row['asset']][0],'FP_'+row['id'],row['position_world'],row['yaw_radians']);ob['retained_family']=row['asset'];furniture.append(ob.name)
 for row in surface['surface_contents']:
  for kind in ['pot','plant']:
   ob=instance(definitions[row[kind+'_asset']][0],'FP_'+row['id']+'_'+kind,row[kind+'_origin_world']);ob['retained_family']=row[kind+'_asset'];furniture.append(ob.name)
 specs={}
 for rel in ['materials/material_manifest.json','materials/auditorium/manifest.json','materials/staff/manifest.json']:
  for role,spec in read(CAT/rel)['materials'].items():specs[role]={**spec,'manifest_dir':str(Path(rel).parent)}
 materials={role:existing_or_new_material(role,definitions,specs)for role in {r['material_family']for r in arch['objects']}}
 new_mesh_names=add_architecture(arch,materials,specs)
 mechanism_materials=mechanisms.load_retained_materials_for_blender(mech);mechanism_result=mechanisms.append_to_blender(mech,mechanism_materials,parent_root=ROOT);new_mesh_names+=mechanism_result['object_names']
 head_col,head_names=stage_head_definition(definitions['AST-CUL-004'],-math.atan(.25));new_mesh_names+=head_names
 fixture_records=[]
 for f in lighting['fixtures']:
  asset=f['asset'];group=f['group'];model=None
  if asset.startswith('AST-LGT-001'):
   if 'backplate_support_world'in f:
    support=Vector(bvec(f['backplate_support_world']));theta=0.0
    if group=='gallery_soffit':
     theta=math.radians(float(f['id'].rsplit('_a',1)[1]))
    rot=Matrix.Rotation(theta,3,'Z')@Matrix.Rotation(math.pi/2,3,'X');origin=support-rot@Vector((0,0,.45));model=instance(definitions['AST-LGT-001'][0],'FP_FIXTURE_'+f['id'],wvec(origin),rotation=rot)
   else:model=instance(definitions['AST-LGT-001'][0],'FP_FIXTURE_'+f['id'],f['origin_world'],f['yaw_radians'])
  elif group=='backstage':model=instance(definitions['AST-STF-006'][0],'FP_FIXTURE_'+f['id'],f['mount_world'])
  elif group=='stage':model=instance(head_col,'FP_FIXTURE_'+f['id'],f['head_pivot_world'],f['whole_mount_yaw_radians'])
  elif f['id']=='stage_cue_worklight':
   model=bpy.data.objects.get('FP_D11_stage_cue');assert model,'Original seventh cue stand absent'
  elif group=='backstage_rehearsal_cue':model=bpy.data.objects.get('FP_'+f['id'].removesuffix('_task_light'));assert model
  elif group=='cabin':model=bpy.data.objects.get(f['physical_mesh']);assert model
  elif group=='canopy_ring':model=bpy.data.objects.get('FP_ring_opal_segment_'+f['id'].rsplit('_',1)[-1]);assert model,('Ring lens missing',f['id'])
  else:raise RuntimeError('Fixture geometry mapping missing '+f['id'])
  ld=bpy.data.lights.new('FP_PRACTICAL_'+f['id'],'SPOT' if group in ['stage','backstage','backstage_rehearsal_cue','canopy_ring','cabin'] or f['id']=='stage_cue_worklight' else 'POINT');ld.energy=f['initial_source_preview_watts'];ld.color=(1.0,.80,.57) if group!='backstage'else(1.0,.91,.78);ld.shadow_soft_size=.002 if group in ['stage','backstage','backstage_rehearsal_cue'] or f['id']=='stage_cue_worklight'else .015
  ob=bpy.data.objects.new(ld.name,ld);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.location=bvec(f['emitter_world']);ob['physical_fixture']=model.name;ob['source_only']=True;ob['not_runtime_photometry']=True
  if ld.type=='SPOT':
   direction=Vector(bvec(f.get('aim_world',[0,-1,0])));ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();ld.spot_size=math.radians(f.get('cone_full_angle_degrees',100));ld.spot_blend=.35
  if group=='cabin':
   origin=next(m['closed_root_world']for m in mech['motion_groups']if m['id']==f['motion_parent']);ob.parent=bpy.data.objects[f['motion_parent']];ob.location=bvec([f['emitter_world'][k]-origin[k]for k in range(3)])
  fixture_records.append({'id':f['id'],'model':model.name,'light':ob.name,'position_world':f['emitter_world'],'watts_preview_trial':ld.energy})
 assert len(fixture_records)==134
 scene=bpy.context.scene;scene.world=bpy.data.worlds.new('FP_PRACTICAL_ONLY_WORLD');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0;scene.view_settings.exposure=0
 for view in lighting['normal_eye_viewpoints']:
  data=bpy.data.cameras.new('FP_VIEW_'+view['id']);ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=bvec(view['position']);ob.rotation_euler=(Vector(bvec(view['target']))-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=24;ob['eye_height_m']=1.65;ob['source_only']=True
  if view['id']=='D11_audience_stage':scene.camera=ob
 scene['firstpass_source_status']='Furnished source candidate. Reopen, normal-eye visual review, source/import operation and external route construction remain gates.'
 textures=texture_audit(specs);preservation=compare_subset(baseline,baseline_snapshot(bpy,removal));assert not preservation,preservation[:20]
 mesh_checks=verify_new_geometry(bpy,new_mesh_names);assert len([o for o in scene.objects if o.get('existing_family')=='AST-CUL-003'])==2200
 check_pins();report={'status':'Built source candidate; no visual/export/runtime acceptance','source':str(out),'source_sha256':None,'baseline_source_sha256':EXPECTED_BASE,'removed_only_parts':removed,'preserved_old_parts':len(baseline['parts']),'baseline_snapshot':baseline,'furniture_and_surface_instances':furniture,'fixture_records':fixture_records,'visible_lens_derivatives':lens_derivatives,'source_asset_definitions':[d[2]for d in definitions.values()],'mechanisms':mechanism_result,'new_mesh_checks':mesh_checks,'all_mesh_material_texture_checks':textures,'chair_instances':2200,'world_strength':0,'input_pins_sha256':sha(HERE/'FIRSTPASS_BUILD_INPUT_PINS.json'),'pending':['Independent reopened source QA','Actual fixture head/contact/ray checks','Normal-eye visual lighting/material/detail review','Imported triangle/collision fidelity','Door/lift operating sweeps and loaded traversal','Compiler/external route construction','Runtime placement and performance']}
 json.dumps(report,allow_nan=False);bpy.ops.wm.save_as_mainfile(filepath=str(out));assert sha(BASE)==EXPECTED_BASE;report['source_sha256']=sha(out)
 with report_path.open('x')as f:json.dump(report,f,indent=2,allow_nan=False)
 print(json.dumps({k:report[k]for k in ['status','source','source_sha256','preserved_old_parts','chair_instances']}))
if __name__=='__main__':main()
