"""Read-only independent native inspection of already pinned special components."""
import bpy,pathlib,json,hashlib,sys
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;out=[]
for rel in ['inputs_9311/BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003.blend','inputs_9311/BlenderCatalogue/assets/low_nesting_rest_20261009/AST-RST-LN-001.blend']:
 p=R/rel;bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();rows=[];markers=[]
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','FONT','CURVE']:
   if ob.type=='EMPTY':markers.append({'name':ob.name,'xyz_blender':list(ob.matrix_world.translation),'properties':{k:str(v) for k,v in ob.items()}})
   continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices]
  if vs:rows.append({'name':ob.name,'type':ob.type,'bounds_blender':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],'UV_layers':[u.name for u in me.uv_layers],'triangles':len(me.loop_triangles),'preview':'preview' in ob.name.lower(),'hidden_render':ob.hide_render})
  ev.to_mesh_clear()
 out.append({'source_path':rel,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_rows':rows,'markers':markers,'images':[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.type!='RENDER_RESULT']})
(R/'SPECIAL_COMPONENT_NATIVE_INSPECTION.json').write_text(json.dumps(out,indent=2));print('Independent special source native inspection complete',flush=True)
