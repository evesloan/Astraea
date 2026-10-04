"""Measure editable Star Atlas source and its runtime export without changing geometry."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
def bounds():
 pts=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
for family,aid,markers in [('vesper_mezzanine','AST-DIN-004',['DATUM_light_'+str(i) for i in range(8)]+['DATUM_upper_stair_arrival','DATUM_lower_lift_stage']),('vesper_service_bay','AST-DIN-003',['DATUM_door','DATUM_clean_landing','DATUM_dirty_landing','DATUM_light_0','DATUM_light_1']),('vesper_watercourse','AST-AQU-015',['DATUM_outlet','DATUM_receiver_floor','DATUM_spillway_guard_crossing']),('vesper_dining_furniture','AST-DIN-001',['DATUM_table_surface']),('vesper_dining_furniture','AST-DIN-001_six',['DATUM_table_surface']),('vesper_dining_furniture','AST-DIN-002',['DATUM_seat_contact','DATUM_front_approach']),('nursery_pottery','AST-BOT-012',['DATUM_soil_surface']),('nursery_pottery','AST-BOT-012_low',['DATUM_soil_surface']),('living_gifts_interior','AST-RTL-006',['DATUM_flora_'+str(i) for i in range(4)]+['DATUM_light_'+str(i) for i in range(4)]),('aquatic_arrival','AST-AQU-014',['DATUM_arrival_light_'+str(i) for i in range(2)]+['DATUM_seat_'+str(i) for i in range(3)]),('aquatic_balcony_edges','AST-AQU-013',['DATUM_'+d+'_light_'+str(i) for d in ['D09','D10'] for i in range(4)]),('aquatic_ceiling','AST-AQU-012',['DATUM_ceiling_light_'+str(i) for i in range(4)]),('aquatic_lift_enclosure','AST-CIR-004',['DATUM_arrival_light_'+str(y) for y in [44,52.5,61]]),('star_atlas_architecture','AST-LIB-011',['DATUM_light_'+str(i) for i in range(10)]),('commons_lift_cabin','AST-CIR-003_three_stop',[]),('library_structure','AST-LIB-STR-003_start',[]),('library_arrival_counter','AST-LIB-012',['DATUM_'+side+'_'+role for side in ['west','lower','east'] for role in ['guest_approach','rear_approach','work_surface']])]:
 r=root/'assets'/family;source=r/'source'/(aid+'.blend');export=r/'exports'/(aid+'.glb')
 bpy.ops.wm.open_mainfile(filepath=str(source));lo,hi=bounds()
 assert all(o.data.uv_layers for o in bpy.context.scene.objects if o.type=='MESH')
 if aid=='AST-AQU-012':
  for name in ['AQU_HighCentralField','AQU_MiddleCove','AQU_PeripheralSoffit','AQU_VesperLiftRelief']:
   o=bpy.data.objects.get(name)
   if o is None:continue
   low=min(v.co.z for v in o.data.vertices)
   for face in o.data.polygons:
    zs=[o.data.vertices[i].co.z for i in face.vertices]
    if max(zs)-min(zs)<1e-5:
     expected=-1 if abs(zs[0]-low)<1e-5 else 1
     assert face.normal.z*expected>.99,(name,face.index,'inward level cap')

 assert all(p.normal.z>.99 for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('LIB_Finish') for p in o.data.polygons),'Floor finishes must face upward'
 assert all(bpy.data.objects.get(n) is not None for n in markers)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(export));elo,ehi=bounds()
 deviation=max(abs(a-b) for arr,brr in [(lo,elo),(hi,ehi)] for a,b in zip(arr,brr))
 assert deviation<.002,(aid,deviation)
 triangles=sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)
 result={'asset':aid,'source_bounds_blender_xyz_m':[lo,hi],'dimensions_blender_xyz_m':[hi[i]-lo[i] for i in range(3)],'export_triangles':triangles,'all_source_meshes_have_uvs':True,'required_source_markers':markers,'roundtrip_max_deviation_m':deviation,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'scope':'Source/export geometry checks. No final art, species ergonomics or performance claim.'}
 (r/(aid+'_geometry_checks.json')).write_text(json.dumps(result,indent=2)+'\n');print(aid,triangles,deviation)
