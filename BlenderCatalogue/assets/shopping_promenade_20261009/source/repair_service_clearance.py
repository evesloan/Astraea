"""Bounded saved-source service-clearance and storefront-glyph repair. One-time journal."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];plan=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());geometry=json.loads((P/'qa/source_geometry.json').read_text());receipt=[]
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
 bpy.ops.wm.open_mainfile(filepath=str(path));sc=bpy.context.scene;before=sha(path);protected={o.name:mesh_digest(o) for o in sc.objects if o.type=='MESH'};changed=[];tasks=set();roots={o.get('chunk_id'):o for o in sc.objects if o.type=='EMPTY' and o.get('chunk_id')}
 for ob in sc.objects:
  if ob.type!='MESH':continue
  row=next((r for r in plan['rooms'] if r['chunk_id']==ob.get('chunk_id')),None)
  if not row:continue
  du=None
  if '__orbit_rest_' in ob.name:du=2.8
  if '__parcel_cubbies_' in ob.name:du=3.1
  if '_curio_care_' in ob.name:du=3.0
  if du is not None:
   for v in ob.data.vertices:v.co.y-=du
   ob.data.update();changed.append(ob.name);tasks.add((row['chunk_id'],'fitout'))
  if row['front_sign_x']==1 and ('__front_address' in ob.name or '__brand_front' in ob.name):
   for v in ob.data.vertices:v.co.y=-v.co.y
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();changed.append(ob.name);tasks.add((row['chunk_id'],'shell'))
 for name,h in protected.items():
  if name not in changed:assert mesh_digest(bpy.data.objects[name])==h,name
 if tasks:
  bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
  for ident,layer in sorted(tasks):export(ident,layer,roots[ident],[o for o in sc.objects if o.type=='MESH' and o.get('chunk_id')==ident and o.get('layer')==layer])
 receipt.append({'native':path.name,'before_sha256':before,'after_sha256':sha(path),'changed_parts':changed,'unrelated_source_meshes_unchanged':len(protected)-len(changed),'export_layers_changed':sorted(tasks)})
 print('SERVICE_GLYPH_REPAIR',path.name,len(tasks),flush=True)
interfaces=json.loads((P/'docs/FITTED_COMPONENT_INTERFACES.json').read_text())
for r in interfaces:
 if r['instance']=='curio_care':r['origin_uvh'][0]+=3
(P/'docs/FITTED_COMPONENT_INTERFACES.json').write_text(json.dumps(interfaces,indent=2)+'\n')
(P/'qa/source_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
(P/'qa/service_clearance_glyph_repair.json').write_text(json.dumps(receipt,indent=2)+'\n')
