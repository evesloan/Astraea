"""Future RESERVED SERIAL SLOT ONLY; never invoked by pure geometry builders.
Build editable source with approved retained materials and instanced original chair.
No engine import/export, controller authoring, registration or shared-source writes.
Cruise references: unchanged-volume static glazed shaft panels, same-depth warm_walnut soffits.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];CAT=R.parents[1]
g=json.loads((R/'source/geometry.json').read_text());mc=json.loads((R/'contracts/material_reuse_contract.json').read_text());pc=json.loads((R/'contracts/place_instances.json').read_text())
chair_path=CAT/'assets/auditorium_use/source/AST-CUL-003.blend'
assert hashlib.sha256(chair_path.read_bytes()).hexdigest()==pc['source_sha256']
mats={}
for rel,names in mc['sources'].items():
 with bpy.data.libraries.load(str(CAT/'assets'/rel),link=False) as (src,dst):
  missing=set(names)-set(src.materials)
  if missing:raise RuntimeError(f'Retained source missing required materials: {rel}: {missing}')
  dst.materials=names
 for name,mat in zip(names,dst.materials):mats[name]=mat
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
root=bpy.data.objects.new('AST-CUL-005',None);bpy.context.collection.objects.link(root);root['programme_keys']=json.dumps(['D11_directory_01','D12_directory_11','D13_directory_01'])
groups={}
for o in g['objects']:
 if o['role']=='preview_only':continue
 key=(o.get('surface_region') or o['name'].split('_')[0],o['material_family'],o['role'])
 vs,fs,names,fm=groups.setdefault(key,([],[],[],[]));base=len(vs)
 vs.extend((x,-z,y) for x,y,z in o['vertices_world']);fs.extend([base+i for i in f] for f in o['faces']);names.append(o['name']);fm.extend(o.get('face_material_families',[o['material_family']]*len(o['faces'])))
for (owner,material,role),(vs,fs,names,fm) in groups.items():
 me=bpy.data.meshes.new(owner);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 obj=bpy.data.objects.new(owner+'__'+material,me);bpy.context.collection.objects.link(obj);obj.parent=root;material_names=list(dict.fromkeys(fm))
 for mat_name in material_names:me.materials.append(mats[mat_name])
 for f,mat_name in zip(me.polygons,fm):f.material_index=material_names.index(mat_name)
 uv=me.uv_layers.new(name='metric_material_uv')
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 obj['catalogue_id']='AST-CUL-005';obj['ownership_region']=owner;obj['material_family']=material;obj['collision_role']=role;obj['pure_part_names']=json.dumps(names)
# Append untouched chair hierarchy once, instance it2200times; no new designs or seat behavior.
with bpy.data.libraries.load(str(chair_path),link=False) as (src,dst):dst.objects=list(src.objects)
loaded=[o for o in dst.objects if o];chair_root=next((o for o in loaded if o.name=='AST-CUL-003'),None)
if chair_root is None:raise RuntimeError('Exact retained chair root absent')
col=bpy.data.collections.new('Existing_AST-CUL-003_capacity_preview')
for obj in loaded:
 p=obj;selected=False
 while p:
  if p==chair_root:selected=True;break
  p=p.parent
 if selected:col.objects.link(obj)
for s in pc['places']:
 obj=bpy.data.objects.new(s['id'],None);bpy.context.collection.objects.link(obj);obj.parent=root;obj.instance_type='COLLECTION';obj.instance_collection=col
 x,y,z=s['position'];obj.location=(x,-z,y);obj.rotation_euler.z=s['orientation_yaw_radians'];obj['existing_family']='AST-CUL-003';obj['capacity_preview_only']=True;obj['seat_controller_authored']=False
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['status']='Source-only platform; source/export/runtime/species/doors/lift acceptance still gated'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/AST-CUL-005.blend'))
assert hashlib.sha256(chair_path.read_bytes()).hexdigest()==pc['source_sha256']
