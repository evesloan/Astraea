from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];U=json.load(open(R/'Game/data/architecture/STAR_ATLAS_UNITS.json'));rows=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();result={}
for idx in [545,551,557,563]:
 row=next(r for r in rows if r['source_envelope_index']==idx);u=next(x for x in U['units']if x['deck']=='D14'and x['allocation_x']==row['allocation_x']and x['allocation_z']==row['allocation_z']);p=next(x for x in U['prototypes']if x['key']==u['source_recipe_key']);native=R/p['editable_source'];assert sha(native)==p['editable_source_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(native),link=False)as(a,b):b.objects=[n for n in a.objects if n.startswith('SUI_Ceiling_')]
 assert len(b.objects)==6
 triangles=[];cy,sy=math.cos(u['source_yaw_godot']),math.sin(u['source_yaw_godot']);origin=u['source_origin_world_xyz']
 for ob in b.objects:
  bpy.context.collection.objects.link(ob);ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   vs=[]
   for vi in t.vertices:
    v=ob.matrix_local@ob.data.vertices[vi].co;x,y,z=v.x,v.z,-v.y;vs.append([origin[0]+x*cy+z*sy,origin[1]+y,origin[2]-x*sy+z*cy])
   triangles.append({'name':ob.name,'vertices':vs})
 assert sha(native)==p['editable_source_sha256'];result[str(idx)]={'native_source':p['editable_source'],'native_sha256':p['editable_source_sha256'],'runtime_source':p['model_file'],'runtime_sha256':p['sha256'],'triangles':triangles}
(W/'ROOF_SOURCE_TRIANGLES.json').write_text(json.dumps({'status':'PASS','read_only_native_sources':True,'rooms':result},indent=2)+'\n');print('EXACT_NATIVE_ROOFS',len(result))
