"""UNRUN. Separate Blender invocation; reopen saved derivative, export actual mesh bytes.
blender --background --factory-startup --python THIS -- --blend NEW_BLEND --output NEW_JSON
Does not import the authoring builder or copy proposal vertices. Original source never opened.
"""
from pathlib import Path
import bpy,sys,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert a.blend.resolve().is_relative_to(Path('/workspace/scratch/375c2e438292')) and a.output.resolve().is_relative_to(Path('/workspace/scratch/375c2e438292')) and not a.output.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.blend)
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;bpy.context.view_layer.update()
assert scene.get('catalogue_family')=='AST-CUL-005' and len(scene.objects)==8 and len(bpy.data.objects)==8
rows=[]
for ob in sorted(scene.objects,key=lambda o:o.name):
    assert ob.type=='MESH' and not ob.modifiers and ob.parent is None and len(ob.data.vertices)==8 and len(ob.data.polygons)==12 and ob.hide_render
    vertices=[]
    for vert in ob.data.vertices:
        v=ob.matrix_world@vert.co;vertices.append([float(v.x),float(v.z),-float(v.y)])
    rows.append({'id':ob.name,'vertices_world':vertices,'faces':[list(p.vertices)for p in ob.data.polygons],'properties':{k:ob[k]for k in ['catalogue_family','source_flight_id','walking_contact_approximation','collision_only','collision_margin_m','vertical_thickness_m','original_meshes_and_contacts_retained','compiler_floor_credit','load_certification','source_lower_receiver_ids','source_upper_receiver_ids','proposal_sha256']},'hide_render':ob.hide_render})
assert sha(a.blend)==before
result={'status':'REOPENED_ACTUAL_MESH_EXPORT_QA_PENDING','blend_sha256':before,'reopen_exporter_sha256':sha(__file__),'coordinate_system':'Godot world X right Y up Z aft','objects':rows}
a.output.write_text(json.dumps(result,indent=2)+'\n')
