"""Bounded current-native floor topology repair; no room shell/fitout rebuilding."""
from pathlib import Path
import bpy,bmesh,json,hashlib
P=Path(__file__).resolve().parents[1];source=json.loads((P/'qa/source_geometry.json').read_text());receipts=[]
for path in sorted((P/'source/natives').glob('*.blend')):
 before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));sc=bpy.context.scene
 protected={o.name:hashlib.sha256(str([(tuple(v.co)) for v in o.data.vertices]).encode()).hexdigest() for o in sc.objects if o.type=='MESH' and o.get('layer')!='floor'}
 floors=[o for o in sc.objects if o.type=='MESH' and o.get('layer')=='floor'];groups={};details=[]
 for ob in floors:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),(ob.name,'floor is not closed');bm.to_mesh(ob.data);bm.free();ob.data.update()
  top=[f for f in ob.data.polygons if all(abs(ob.data.vertices[i].co.z)<1e-6 for i in f.vertices)];assert top and all(f.normal.z>.999 for f in top),(ob.name,'Top face orientation');groups.setdefault(ob['chunk_id'],[]).append(ob);details.append({'part':ob.name,'closed_manifold':True,'top_faces_up':True})
 assert protected=={o.name:hashlib.sha256(str([(tuple(v.co)) for v in o.data.vertices]).encode()).hexdigest() for o in sc.objects if o.type=='MESH' and o.get('layer')!='floor'}
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 for ident,obs in groups.items():
  root=obs[0].parent;old=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update();vs=[];faces=[];uvs=[]
  source[ident+'__floor']=[]
  for ob in obs:
   source[ident+'__floor'].append({'part':ob.name,'vertices_xyz':[[float(v.co.x),float(v.co.z),float(-v.co.y)] for v in ob.data.vertices],'material':ob['material_role']});start=len(vs);vs.extend(tuple(ob.matrix_world@v.co) for v in ob.data.vertices)
   for f in ob.data.polygons:faces.append(tuple(start+i for i in f.vertices));uvs.extend(tuple(ob.data.uv_layers.active.data[i].uv) for i in f.loop_indices)
  me=bpy.data.meshes.new(ident+'__floor__warm_stone');me.from_pydata(vs,[],faces);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='metric_material_uv')
  for i,p in enumerate(uvs):uv.data[i].uv=p
  cp=bpy.data.objects.new(me.name,me);sc.collection.objects.link(cp);cp['chunk_id']=ident;cp['layer']='floor';cp['source_parts_json']=json.dumps([o.name for o in obs]);cp['collision_kind']='precise_floor';bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp
  bpy.ops.export_scene.gltf(filepath=str(P/'exports'/(ident+'__floor.glb')),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False);bpy.data.objects.remove(cp,do_unlink=True);root.location=old
 receipts.append({'native':path.name,'before_sha256':before,'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'unchanged_non_floor_parts':len(protected),'repaired_floor_meshes':len(floors),'floors':details})
 print('FLOOR_ONLY_REPAIR',path.name,len(floors),flush=True)
(P/'qa/source_geometry.json').write_text(json.dumps(source,indent=2)+'\n');(P/'qa/floor_winding_repair.json').write_text(json.dumps(receipts,indent=2)+'\n')
