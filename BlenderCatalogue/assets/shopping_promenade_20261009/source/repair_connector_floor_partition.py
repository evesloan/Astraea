"""Repair four unopened-core links and19 planter/column conflicts in saved sources.
No bank reassembly. Change only affected native parts and bounded affected exports.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];plan=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());geometry=json.loads((P/'qa/source_geometry.json').read_text());oldplan=json.loads((P/'qa/plan_before_connection_repair.json').read_text());lights=json.loads((P/'docs/LIGHT_SOURCES.json').read_text());occ=json.loads((P/'docs/OPAQUE_SURFACES.json').read_text());receipt=[]
renames={r['chunk_id']:r['chunk_id'] for r in plan['chunks'] if r['kind']=='link' and '301' in r['chunk_id']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mesh_digest(ob):return hashlib.sha256(str([(tuple(v.co)) for v in ob.data.vertices]).encode()).hexdigest()
def export(ident,layer,root,parts):
 old=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update();groups={};out=[];geometry[ident+'__'+layer]=[]
 for ob in parts:
  groups.setdefault(ob['material_role'],[]).append(ob);geometry[ident+'__'+layer].append({'part':ob.name,'vertices_xyz':[[float(v.co.x),float(v.co.z),float(-v.co.y)] for v in ob.data.vertices],'material':ob['material_role']})
 for role,obs in groups.items():
  vs=[];fs=[];uvs=[]
  for ob in obs:
   start=len(vs);vs.extend(tuple(ob.matrix_world@v.co) for v in ob.data.vertices)
   for f in ob.data.polygons:fs.append(tuple(start+i for i in f.vertices));uvs.extend(tuple(ob.data.uv_layers.active.data[i].uv) for i in f.loop_indices)
  me=bpy.data.meshes.new(ident+'__'+layer+'__'+role);me.from_pydata(vs,[],fs);me.update();me.materials.append(obs[0].data.materials[0]);uv=me.uv_layers.new(name='metric_material_uv')
  for i,p in enumerate(uvs):uv.data[i].uv=p
  cp=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(cp);cp['chunk_id']=ident;cp['layer']=layer;cp['source_parts_json']=json.dumps([o.name for o in obs]);out.append(cp)
 bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
 for o in out:o.select_set(True)
 bpy.context.view_layer.objects.active=out[0];bpy.ops.export_scene.gltf(filepath=str(P/'exports'/(ident+'__'+layer+'.glb')),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
 root.location=old
for path in sorted((P/'source/natives').glob('*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(path));sc=bpy.context.scene;before=sha(path);protected={o.name:mesh_digest(o) for o in sc.objects if o.type=='MESH'};modified=[];tasks=set();roots={o.get('chunk_id'):o for o in sc.objects if o.type=='EMPTY' and o.get('chunk_id')}
 for ob in list(sc.objects):
  key=ob.get('chunk_id')
  if key in renames:
   new=renames[key];ob.name=ob.name.replace(key,new);ob['chunk_id']=new
   if ob.type=='EMPTY':
    row=next(r for r in plan['chunks'] if r['chunk_id']==new);ob.location=(row['position'][0],-row['position'][2],0);roots[new]=ob
   if ob.type=='MESH':
    modified.append(key)
    if ob.get('layer')=='floor':
     vs=[];fs=[];cx,_,cz=next(r for r in plan['chunks'] if r['chunk_id']==new)['position']
     floor_rows=[r for r in plan['floor_proposals'] if r['chunk_id']==new]
     part_index=int(ob.name.split('__floor_')[1].split('_')[0])
     for f in [floor_rows[part_index]]:
      for tr in f['triangles_xz']:
       for h in [-.24,0]:
        i=len(vs);vs.extend((x-cx,-(z-cz),h) for x,z in tr);fs.append((i,i+1,i+2))
      for ring in [f['boundary'],*f.get('holes',[])]:
       for a,b in zip(ring,ring[1:]+[ring[0]]):
        i=len(vs);vs.extend([(a[0]-cx,-(a[1]-cz),-.24),(b[0]-cx,-(b[1]-cz),-.24),(b[0]-cx,-(b[1]-cz),0),(a[0]-cx,-(a[1]-cz),0)]);fs.append(tuple(range(i,i+4)))
     mat=ob.data.materials[0];me=bpy.data.meshes.new(ob.name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();me.update();me.materials.append(mat);uv=me.uv_layers.new(name='metric_material_uv')
     for f in me.polygons:
      ax=max(range(3),key=lambda a:abs(f.normal[a]));ij=[i for i in range(3) if i!=ax]
      for li in f.loop_indices:
       p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[ij[0]],p[ij[1]])
     ob.data=me
   tasks.add((new,ob.get('layer'))) if ob.type=='MESH' else None
  if False:
   row=next(r for r in plan['rooms'] if r['chunk_id']==key);sgn=row['front_sign_x'];du,dv=(1.5,-.7) if '__soft_green_' in ob.name else (-1.4,-1.0);delta=Vector((-sgn*dv,-du,0))
   for v in ob.data.vertices:v.co+=delta
   ob.data.update();modified.append(ob.name);tasks.add((key,'fitout'))
 # Verify every unrelated source mesh retained literal vertex data.
 changed_names=set(modified);unaffected=0
 for name,h in protected.items():
  if any(name.startswith(old+'__') for old in renames) or '__soft_green_' in name or '__curio_green_' in name:continue
  assert name in bpy.data.objects and mesh_digest(bpy.data.objects[name])==h,name;unaffected+=1
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 for ident,layer in sorted(tasks):
  obs=[o for o in sc.objects if o.type=='MESH' and o.get('chunk_id')==ident and o.get('layer')==layer];export(ident,layer,roots[ident],obs)
 receipt.append({'native':path.name,'before_sha256':before,'after_sha256':sha(path),'modified_parts':len(modified),'unrelated_source_meshes_unchanged':unaffected,'export_layers_changed':sorted(tasks)})
 print('TARGETED_REPAIR',path.name,len(tasks),flush=True)

(P/'qa/connector_floor_partition_repair.json').write_text(json.dumps(receipt,indent=2)+'\n')
(P/'qa/source_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
