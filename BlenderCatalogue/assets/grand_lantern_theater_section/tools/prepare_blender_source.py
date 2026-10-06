"""Reserved serial Blender slot only. Not executed during source planning.
Usage: blender --background --python tools/prepare_blender_source.py
Creates editable family-labelled mesh groups; no engine import/export/registration.
"""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
g=json.loads((R/'source/geometry.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Merge pure parts by ownership, retaining provenance custom properties.
groups={}
for o in g['objects']:
 if o['role']=='preview_only':continue
 key=(o.get('surface_region') or o['name'].split('_')[0],o['material_family'],o['role'])
 vs,fs,names=groups.setdefault(key,([],[],[]));base=len(vs)
 vs.extend((x,-z,y) for x,y,z in o['vertices_world']);fs.extend([base+i for i in f] for f in o['faces']);names.append(o['name'])
for (owner,material,role),(vs,fs,names) in groups.items():
 mesh=bpy.data.meshes.new(owner);mesh.from_pydata(vs,[],fs);mesh.update()
 obj=bpy.data.objects.new(owner+'__'+material,mesh);bpy.context.collection.objects.link(obj)
 obj['catalogue_id']='AST-CUL-005';obj['ownership_region']=owner;obj['material_family_required']=material;obj['collision_role']=role;obj['pure_part_names']=json.dumps(names)
 # Parent must link approved shared material library, never invent substitute palette.
for s in json.loads((R/'contracts/place_instances.json').read_text())['places']:
 obj=bpy.data.objects.new(s['id'],None);bpy.context.collection.objects.link(obj)
 x,y,z=s['position'];obj.location=(x,-z,y);obj['existing_family']='AST-CUL-003';obj['instance_marker_only']=True;obj['godot_yaw']=s['orientation_yaw_radians']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/AST-CUL-005.blend'))
