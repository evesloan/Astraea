"""Independent read-only reopened-source QA. No scene save/export/render."""
import argparse,sys,json,math,struct
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from firstpass_common import *
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');PACKAGE=CAT/'assets/grand_lantern_theater_section';BASE=PACKAGE/'source/AST-CUL-005.blend';SOURCE=PACKAGE/'source/AST-CUL-005_firstpass_001.blend';BASE_HASH='c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--report',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(args.report);assert out.parent==PACKAGE/'qa' and not out.exists()
 assert sha(BASE)==BASE_HASH;basehash=sha(BASE);sourcehash=sha(SOURCE);pins=read(HERE/'FIRSTPASS_BUILD_INPUT_PINS.json')
 for path,h in pins['input_sha256'].items():assert sha(path)==h,('Changed input',path)
 specs={}
 for rel in ['materials/material_manifest.json','materials/auditorium/manifest.json','materials/staff/manifest.json']:specs.update(read(CAT/rel)['materials'])
 mech=read(HERE/'mechanism_package_compact.json');arch=read(HERE/'ARCHITECTURE_ADDITIONS_GEOMETRY.json');lighting=read(HERE/'LIGHTING_ENCLOSURE_VIEW_PLAN.json');removal=mech['baseline_removal_by_parent_only']
 # Derive preservation expectations afresh from immutable original, not its report.
 bpy.ops.wm.open_mainfile(filepath=str(BASE));expected=baseline_snapshot(bpy,removal);assert len(expected['parts'])==6962
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));actual=baseline_snapshot(bpy,removal);errors=compare_subset(expected,actual);assert not errors,errors[:25]
 assert all(not any(r['name'] in removal for r in json.loads(ob['pure_part_ranges']))for ob in bpy.data.objects if 'pure_part_ranges'in ob)
 bpy.context.view_layer.update();checks=[];maxpos=0.;maxuv=0.
 for spec in arch['objects']+mech['objects']:
  ob=bpy.data.objects.get(spec['name']);assert ob and ob.type=='MESH',spec['name'];me=ob.data;assert len(me.vertices)==len(spec['vertices_world']);assert len(me.polygons)==len(spec['faces'])
  err=max((Vector(wvec(ob.matrix_world@v.co))-Vector(target)).length for v,target in zip(me.vertices,spec['vertices_world']));maxpos=max(maxpos,err);assert err<.000045,(ob.name,'world-coordinate error',err)
  for face,wanted in zip(me.polygons,spec['faces']):assert list(face.vertices)==wanted,(ob.name,'face order')
  if 'uv_faces'not in spec:
   scale=specs.get(spec['material_family'],{}).get('meters_per_tile_uv',[1,1])
   for face in me.polygons:
    axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
    for li in face.loop_indices:
     v=me.vertices[me.loops[li].vertex_index].co
     maxuv=max(maxuv,*(abs(me.uv_layers.active.data[li].uv[k]-v[axes[k]]/scale[k])for k in [0,1]))
  if 'uv_faces'in spec:
   for face,values in zip(me.polygons,spec['uv_faces']):
    for li,value in zip(face.loop_indices,values):maxuv=max(maxuv,*(abs(me.uv_layers.active.data[li].uv[k]-value[k])for k in [0,1]))
  checks.append(ob.name)
 assert maxuv<.00006,('Material UV storage error',maxuv)
 newchecks=verify_new_geometry(bpy,checks);chair_instances=[o for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003'];assert len(chair_instances)==2200
 fixtures=[]
 for spec in lighting['fixtures']:
  ob=bpy.data.objects.get('FP_PRACTICAL_'+spec['id']);assert ob and ob.type=='LIGHT';assert bpy.data.objects.get(ob['physical_fixture']),spec['id'];err=(Vector(wvec(ob.matrix_world.translation))-Vector(spec['emitter_world'])).length;assert err<.00003,(spec['id'],err)
  assert abs(ob.data.energy-spec['initial_source_preview_watts'])<1e-5
  fixtures.append({'id':spec['id'],'actual_world':wvec(ob.matrix_world.translation),'fixture_model':ob['physical_fixture'],'emitter_position_error_m':err})
 assert len(fixtures)==134;lights=[o for o in bpy.context.scene.objects if o.type=='LIGHT'];assert len(lights)==134 and all(o.name.startswith('FP_PRACTICAL_')for o in lights)
 assert bpy.context.scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value==0
 # Every actual mesh material, including unlinked retained chair/furniture definitions.
 texture_rows=[]
 for mat in sorted({m for o in bpy.data.objects if o.type=='MESH'for m in o.data.materials if m},key=lambda m:m.name):
  ims=[]
  for n in image_nodes(mat.node_tree if mat.use_nodes else None):
   assert n.image.packed_file,(mat.name,n.image.name,'Not packed')
   role=mat.get('astraea_material_role','')
   if role in specs:assert hashlib.sha256(n.image.packed_file.data).hexdigest()==specs[role]['sha256'],('Texture mismatch',mat.name)
   ims.append({'name':n.image.name,'sha256':hashlib.sha256(n.image.packed_file.data).hexdigest(),'bytes':len(n.image.packed_file.data)})
  texture_rows.append({'material':mat.name,'images':ims})
 # Verify actual endpoints for each motion group from reopened mesh world vertices.
 motion_results=[]
 for spec in mech['motion_groups']:
  root=bpy.data.objects[spec['id']];assert list(root.scale)==[1,1,1]
  actualspec=json.loads(root['mechanism_spec']);assert actualspec==spec
  names=[o['name']for o in mech['objects']if o.get('motion_group')==spec['id']];points=[wvec(bpy.data.objects[name].matrix_world@v.co)for name in names for v in bpy.data.objects[name].data.vertices]
  if points:motion_results.append({'id':spec['id'],'part_count':len(names),'rest_bounds':{'min':[min(p[k]for p in points)for k in range(3)],'max':[max(p[k]for p in points)for k in range(3)]},'spec':spec})
 assert len(mech['motion_groups'])==39
 # Independently reopen the retained head family, reconstruct expected local vertices,
 # and compare every actual derivative part, face and UV before testing six exits.
 source_path=CAT/'assets/auditorium_use/source/AST-CUL-004.blend'
 with bpy.data.libraries.load(str(source_path),link=False)as(src,dst):
  original_names=tuple(src.objects);dst.objects=list(original_names)
 source_objects=dict(zip(original_names,dst.objects));hinge=source_objects['LIGHT_AIM_X']
 def source_matrix(ob):return source_matrix(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis.copy()
 def moving(ob):
  while ob:
   if ob==hinge:return True
   ob=ob.parent
  return False
 pivot=source_matrix(hinge).translation;selected=[];headerr=0.
 for name,ob in source_objects.items():
  fixed=name=='light_yoke_crossbar' or any(t in name for t in ['_light_yoke_upright','_fixed_aim_stub','_retained_aim_pin','_aim_pin_inner_retainer'])
  if ob.type!='MESH' or not(fixed or moving(ob)):continue
  actual_head=bpy.data.objects['FP_HEAD_'+name];expected_matrix=Matrix.Translation(-pivot)@source_matrix(ob)
  if moving(ob):expected_matrix=Matrix.Rotation(-math.atan(.25),4,'X')@expected_matrix
  assert len(actual_head.data.vertices)==len(ob.data.vertices)
  for a,v in zip(actual_head.data.vertices,ob.data.vertices):headerr=max(headerr,(a.co-expected_matrix@v.co).length)
  assert [list(p.vertices)for p in actual_head.data.polygons]==[list(p.vertices)for p in ob.data.polygons]
  assert {u.name:[list(x.uv)for x in u.data]for u in actual_head.data.uv_layers}=={u.name:[list(x.uv)for x in u.data]for u in ob.data.uv_layers}
  selected.append(actual_head.name)
 assert len(selected)==34 and headerr<.000003,(len(selected),headerr)
 head_ray_results=[]
 for spec in lighting['fixtures']:
  if spec['group']!='stage':continue
  inst=bpy.data.objects['FP_FIXTURE_'+spec['id']];verts=[];faces=[]
  for name in selected:
   ob=bpy.data.objects[name];offset=len(verts);verts.extend(inst.matrix_world@v.co for v in ob.data.vertices);faces.extend([offset+i for i in p.vertices]for p in ob.data.polygons)
  tree=BVHTree.FromPolygons(verts,faces,all_triangles=False);origin=Vector(bvec(spec['emitter_world']));direction=Vector(bvec(spec['aim_world']));hit=tree.ray_cast(origin,direction,2.0)
  assert hit[0] is None,('Actual stage head self-block',spec['id'],hit)
  # The original stage top is an actual retained mesh part, located from semantic ranges.
  stage_ob,stage_range=next((ob,r)for ob in bpy.data.objects if 'pure_part_ranges'in ob for r in json.loads(ob['pure_part_ranges'])if r['name']=='stage_36x14')
  vertices=[stage_ob.matrix_world@v.co for v in stage_ob.data.vertices];polygons=[list(p.vertices)for p in list(stage_ob.data.polygons)[stage_range['face_start']:stage_range['face_start']+stage_range['face_count']]]
  receiver=BVHTree.FromPolygons(vertices,polygons,all_triangles=False).ray_cast(origin,direction,40)
  assert receiver[0] is not None,('Actual stage receiver missing',spec['id'])
  head_ray_results.append({'fixture':spec['id'],'actual_head_self_block':False,'stage_hit_world':wvec(receiver[0]),'distance_m':receiver[3]})
 assert sha(BASE)==basehash and sha(SOURCE)==sourcehash
 result={'status':'Independent reopened geometry/material/instance QA passed; no visual or imported-operation acceptance','source_sha256':sourcehash,'preserved_base_sha256':basehash,'preserved_unaffected_parts':len(expected['parts']),'preserved_original_object_records':len(expected['objects']),'preserved_original_material_records':len(expected['materials']),'chair_instances':len(chair_instances),'new_mesh_checks':newchecks,'maximum_new_world_vertex_error_m':maxpos,'maximum_mechanism_uv_storage_error':maxuv,'fixture_records':fixtures,'actual_material_texture_checks':texture_rows,'actual_motion_roots':motion_results,'retained_stage_head_parts_checked':selected,'maximum_retained_stage_head_vertex_error_m':headerr,'actual_stage_head_receiver_rays':head_ray_results,'world_strength':0,'pending':['Actual internal mechanism contacts and rotating-bearing phases','Actual complete light head/contact/ray checks','Normal-eye visual review','Import/physics collision margins and full vertical/leaf sweeps','Loaded traversal and external receiving routes','Compiler adoption and runtime installation']}
 with out.open('x')as f:json.dump(result,f,indent=2,allow_nan=False)
 print(json.dumps({k:result[k]for k in ['status','source_sha256','preserved_unaffected_parts','chair_instances','maximum_new_world_vertex_error_m']}))
if __name__=='__main__':main()
