"""Read-only source render proposal. Parent reserves a separate render slot.
No save, export, hidden walls, global ambient/fill, runtime mutation or overwrite.
"""
import bpy,bmesh,sys,argparse,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');R=Path(__file__).resolve().parent;SOURCE=R/'source/AST-CUL-005_firstpass_002.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--views',default='D11_main_arrival,D11_audience_stage,D11_backstage');ap.add_argument('--samples',type=int,default=32);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(args.output_dir)
 assert out.is_relative_to('/workspace/scratch/375c2e438292/theater_resume') and not out.exists();assert sha(SOURCE)==args.source_sha;assert 16<=args.samples<=128
 plan=json.loads((P/'source/firstpass_001/LIGHTING_ENCLOSURE_VIEW_PLAN.json').read_text());allowed={v['id']for v in plan['normal_eye_viewpoints']};views=args.views.split(',');assert set(views)<=allowed and len(set(views))==len(views)
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;assert scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value==0
 lighting=json.loads((R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json').read_text());active=set(lighting['first_arrival_eight_source_preview']);assert len(active)==8
 for ob in scene.objects:
  if ob.type=='LIGHT':ob.hide_render=ob.name not in active
 assert len([o for o in scene.objects if o.type=='LIGHT'and not o.hide_render])==8;
 assert all(not o.hide_render for o in scene.objects if o.type=='MESH')
 # Match current Compatibility's visible emissive surfaces without hidden emissive GI.
 # The review copies shader datablocks in this unsaved scene only.
 for original in list(bpy.data.materials):
  if not original.use_nodes:continue
  emitting=[n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED'and n.inputs.get('Emission Strength')and n.inputs['Emission Strength'].default_value>0]
  if not emitting:continue
  mat=original.copy();mat.name='REVIEW_CAMERA_ONLY_'+original.name
  for node in mat.node_tree.nodes:
   if node.type!='BSDF_PRINCIPLED'or not node.inputs.get('Emission Strength'):continue
   strength=node.inputs['Emission Strength'].default_value
   if strength<=0:continue
   lp=mat.node_tree.nodes.new('ShaderNodeLightPath');multiply=mat.node_tree.nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=strength;mat.node_tree.links.new(lp.outputs['Is Camera Ray'],multiply.inputs[0]);mat.node_tree.links.new(multiply.outputs[0],node.inputs['Emission Strength'])
  for ob in bpy.data.objects:
   if ob.type=='MESH':
    for i,m in enumerate(list(ob.data.materials)):
     if m==original:ob.data.materials[i]=mat
 # Exact approved D11 walking candidate, transient review geometry only.
 contract=P/'contracts/D11_FLAT_FLOOR_CANDIDATE.json';candidate=json.loads(contract.read_text());verts=[];faces=[];y=candidate['floor_y'];th=candidate['thickness']
 for tri in candidate['triangles']:
  b=len(verts);verts.extend((x,-z,h)for h in [y,y-th]for x,z in tri);faces.extend([[b,b+1,b+2],[b+5,b+4,b+3],[b,b+3,b+4,b+1],[b+1,b+4,b+5,b+2],[b+2,b+5,b+3,b]])
 me=bpy.data.meshes.new('REVIEW_ONLY_APPROVED_D11_COMPILER_CANDIDATE');me.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 mat=next(m for m in bpy.data.materials if m.name.split('.')[0]=='warm_stone');me.materials.append(mat);uv=me.uv_layers.new(name='metric_material_uv');scale=json.loads((P.parents[1]/'materials/material_manifest.json').read_text())['materials']['warm_stone']['meters_per_tile_uv']
 for face in me.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
 ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);ob['review_only_no_save_export']=True
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=False;scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4;scene.cycles.transmission_bounces=6
 scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=768;scene.render.resolution_y=432;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.exposure=0
 out.mkdir();records=[]
 for view in views:
  camera=bpy.data.objects['FP_VIEW_'+view];assert abs(camera.get('eye_height_m',0)-1.65)<1e-6;scene.camera=camera;path=out/(view+'.png');assert not path.exists();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  records.append({'view':view,'png':str(path),'sha256':sha(path),'camera_eye_world':[camera.location.x,camera.location.z,-camera.location.y]})
 assert sha(SOURCE)==args.source_sha
 report={'status':'Normal-eye source-only review images, not runtime/GPU/performance acceptance','source_sha256':args.source_sha,'original_saved_source_unchanged':True,'world_strength':0,'active_analytic_source_count':8,'active_analytic_sources':sorted(active),'camera_only_emission_for_native_budget_honesty':True,'samples':args.samples,'denoising':False,'resolution':[768,432],'engine':'Cycles CPU','transient_compiler_candidate_sha256':sha(contract),'candidate_saved_or_exported':False,'renders':records}
 with (out/'render_receipt.json').open('x')as f:json.dump(report,f,indent=2)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
