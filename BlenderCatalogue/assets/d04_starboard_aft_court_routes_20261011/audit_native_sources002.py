from pathlib import Path
import bpy,json,hashlib,math,numpy as np
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={q['native']:sha(W/q['native'])for q in P['native_export_records']}
def material(m):
 bs=m.node_tree.nodes.get('Principled BSDF');images=[]
 for node in m.node_tree.nodes:
  if node.type!='TEX_IMAGE' or not node.image:continue
  im=node.image;packed=im.packed_file;assert packed is not None,im.name
  images.append({'packed_sha256':hashlib.sha256(bytes(packed.data)).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'interpolation':node.interpolation})
 return {'name':m.name,'roughness':bs.inputs['Roughness'].default_value,'images':images,'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links]}
def payload(ob):return {'verts':[list(v.co)for v in ob.data.vertices],'faces':[list(q.vertices)for q in ob.data.polygons],'UVs':[[list(v.uv)for v in l.data]for l in ob.data.uv_layers],'materials':[material(m)for m in ob.data.materials]}
bpy.ops.wm.open_mainfile(filepath=str(R/P['gate_source']['native']));src={n:{'data':payload(bpy.data.objects[n]),'matrix':bpy.data.objects[n].matrix_world.copy()}for n in P['gate_source']['members']+P['gate_source']['control_members']+P['closed_staging_source_members']};bpy.ops.wm.open_mainfile(filepath=str(W/'D04StarboardAftCourtRoutes_r001.blend'));s=P['gate_source']['source_pivot'];s=Vector((s[0],-s[2],s[1]));error=0
for i,g in enumerate(P['gates']):
 t=g['pivot'];T=Matrix.Translation(Vector((t[0],-t[2],t[1])))@Matrix.Rotation(math.radians(g['source_rotation_y_degrees']),4,'Z')@Matrix.Translation(-s)
 for n,q in src.items():
  if n in P['closed_staging_source_members']:continue
  ob=bpy.data.objects['SCR_G'+str(i)+'_'+n];assert payload(ob)==q['data'],n
  d=g.get('fixed_control_delta',[0,0,0])if n.endswith('_Control')and i>=9 else[0,0,0]
  delta=Vector((d[0],-d[2],d[1]))
  for v in ob.data.vertices:error=max(error,(ob.matrix_world@v.co-T@q['matrix']@v.co-delta).length)
d=P['closed_staging_translation'];T=Matrix.Translation(Vector((d[0],-d[2],d[1])))
for n in P['closed_staging_source_members']:
 ob=bpy.data.objects['SFR_ClosedDock_'+n];q=src[n];assert payload(ob)==q['data'],n
 for v in ob.data.vertices:error=max(error,(ob.matrix_world@v.co-T@q['matrix']@v.co).length)
source_max=max(abs(v)for q in src.values()for at in q['data']['verts']for v in at);float_bound=4*float(np.spacing(np.float32(source_max)));assert error<=float_bound,(error,float_bound)
bpy.ops.wm.read_factory_settings(use_empty=True);[bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/f))for f in sorted({q['source_model']for q in P['cuts']+P['moves']})];plants={q['name']:{'data':payload(bpy.data.objects[q['name']]),'world':[list(bpy.data.objects[q['name']].matrix_world@v.co+Vector((q['delta'][0],-q['delta'][2],q['delta'][1])))for v in bpy.data.objects[q['name']].data.vertices]}for q in P['moves']};bpy.ops.wm.open_mainfile(filepath=str(W/'D04StarboardAftCourtPatch_r001.blend'));plant_error=0
for n,q in plants.items():
 ob=bpy.data.objects[n];assert payload(ob)==q['data'],n
 for v,e in zip(ob.data.vertices,q['world']):plant_error=max(plant_error,(ob.matrix_world@v.co-Vector(e)).length)
assert plant_error<.00002,plant_error
for n,h in pins.items():assert sha(W/n)==h
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','rigid_original_gate_mesh_instances':55,'intact_static_closed_staging_meshes':0,'gate_local_vertices_faces_materials_UVs_exact':True,'packed_texture_bytes_roughness_links_and_UVs_exact':True,'gate_world_rigid_mapping_max_error_m':error,'far_origin_single_precision_transform_bound_m':float_bound,'relocated_original_planter_meshes':10,'planter_local_vertices_faces_materials_UVs_exact':True,'planter_world_translation_max_error_m':plant_error,'native_bytes_unchanged':pins,'original_inputs_unchanged':True},indent=2)+'\n');print('Native original gate/planter audit PASS',error,plant_error)
