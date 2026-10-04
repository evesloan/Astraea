"""Verify fitted source/export bounds; gameplay acceptance is separate."""
from pathlib import Path
import bpy,json
from mathutils import Vector
r=Path(__file__).resolve().parents[1]/'assets/arrivals_reception_alcove';aid='AST-ARR-004'
def bounds():
 points=[o.matrix_world@Vector(v)for o in bpy.context.scene.objects if o.type=='MESH'for v in o.bound_box]
 return [[min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)]]
bpy.ops.wm.open_mainfile(filepath=str(r/'source'/(aid+'.blend')));lo,hi=bounds();assert abs(lo[2])<1e-5 and hi[2]<3.8;assert lo[0]>-7 and hi[0]<7 and lo[1]>-1 and hi[1]<7
assert all(o.data.uv_layers for o in bpy.context.scene.objects if o.type=='MESH')
for i in range(3):assert bpy.data.objects.get('DATUM_light_'+str(i))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(r/'exports'/(aid+'.glb')));elo,ehi=bounds();assert max(abs(lo[i]-elo[i])for i in range(3))<.002 and max(abs(hi[i]-ehi[i])for i in range(3))<.002
result={'source_floor_origin':True,'all_mesh_uvs':True,'roundtrip_bounds_match':True,'three_light_datums':True,'fits_below_existing_3_8m_canopy':True,'scope':'Source component envelope only; in-game clearance, receiver lighting and composition require separate verification'}
(r/'geometry_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
