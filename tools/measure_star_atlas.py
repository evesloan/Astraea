"""Measure editable Star Atlas source and its runtime export without changing geometry."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
def bounds():
 pts=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
for family,aid,markers in [('star_atlas_architecture','AST-LIB-011',['DATUM_light_'+str(i) for i in range(10)]),('commons_lift_cabin','AST-CIR-003_three_stop',[]),('library_structure','AST-LIB-STR-003_start',[])]:
 r=root/'assets'/family;source=r/'source'/(aid+'.blend');export=r/'exports'/(aid+'.glb')
 bpy.ops.wm.open_mainfile(filepath=str(source));lo,hi=bounds()
 assert all(o.data.uv_layers for o in bpy.context.scene.objects if o.type=='MESH')
 assert all(bpy.data.objects.get(n) is not None for n in markers)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(export));elo,ehi=bounds()
 deviation=max(abs(a-b) for arr,brr in [(lo,elo),(hi,ehi)] for a,b in zip(arr,brr))
 assert deviation<.002,(aid,deviation)
 triangles=sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)
 result={'asset':aid,'source_bounds_blender_xyz_m':[lo,hi],'dimensions_blender_xyz_m':[hi[i]-lo[i] for i in range(3)],'export_triangles':triangles,'all_source_meshes_have_uvs':True,'required_source_markers':markers,'roundtrip_max_deviation_m':deviation,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'scope':'Source/export geometry checks. No final art, species ergonomics or performance claim.'}
 (r/(aid+'_geometry_checks.json')).write_text(json.dumps(result,indent=2)+'\n');print(aid,triangles,deviation)
