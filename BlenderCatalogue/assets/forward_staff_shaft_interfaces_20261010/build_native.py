from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'SHAFT_INTERFACE_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);assert next(q for q in json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))['assets']if q['catalogue_id']=='AST-STF-009')['family']=='lower_staff_network'
def save(blend,glb):
 bpy.ops.wm.save_as_mainfile(filepath=str(W/blend));bpy.ops.export_scene.gltf(filepath=str(W/glb),export_format='GLB',export_extras=True);h=sha(W/glb);count=sum(o.type=='MESH'for o in bpy.context.scene.objects);bpy.ops.wm.open_mainfile(filepath=str(W/blend));bpy.ops.export_scene.gltf(filepath=str(W/glb),export_format='GLB',export_extras=True);assert sha(W/glb)==h;return {'native':blend,'native_sha256':sha(W/blend),'export':glb,'export_sha256':h,'meshes':count,'fresh_native_repeat_identical':True}
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/AST-STF-G3-003.blend'));keep={p['name']for p in P['retained_shaft_parts']}
assert all(n in bpy.data.objects for n in keep)
for o in list(bpy.context.scene.objects):
 if o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
mat=next(o.data.materials[0]for o in bpy.context.scene.objects)
def box(spec):
 b=spec['aabb'];vs=[B((x,y,z))for z in [b[4],b[5]]for y in [b[2],b[3]]for x in [b[0],b[1]]];fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];me=bpy.data.meshes.new(spec['name']);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)if abs(f.normal.z)>.5 else(v.x+v.y,v.z)
 o=bpy.data.objects.new(spec['name'],me);bpy.context.collection.objects.link(o)
box(P['new_missing_only_top_cap'])
for q in P['sill_gate_interfaces']:box(q)
envelope=save('ForwardStaffUpperEnvelope.blend','AST-STF-009_upper_tidal_envelope_r001.glb')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-STF-009_pool_market_home_equipment.glb'));bpy.context.view_layer.update();wanted={q['mesh']for q in P['cap_exact_triangle_removals']};worlds={o:o.matrix_world.copy()for o in bpy.data.objects if o.name in wanted}
for o in list(bpy.data.objects):
 if o not in worlds:bpy.data.objects.remove(o,do_unlink=True)
lo=P['cap_predecessor_object']['min'];hi=P['cap_predecessor_object']['max'];changes=[]
for o,m in worlds.items():
 o.parent=None;o.matrix_world=m;old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;vs=[];fs=[];uvs=[];mis=[];removed=0
 for tri in old.loop_triangles:
  vv=[o.matrix_world@old.vertices[i].co for i in tri.vertices];pts=[Vector((v.x,v.z,-v.y))for v in vv];normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized();inside=all(lo[a]-1e-5<=v[a]<=hi[a]+1e-5 for v in pts for a in range(3));hit=inside and any(all(abs(v[a]-val)<1e-5 for v in pts)and normal[a]*sign>.999 for a in range(3)for val,sign in [(lo[a],-1),(hi[a],1)])
  if hit:removed+=1;continue
  k=len(vs);vs.extend(vv);fs.append((k,k+1,k+2));uvs.extend(tuple(uv.data[i].uv)for i in tri.loops);mis.append(tri.material_index)
 expected=next(q['removed_triangles']for q in P['cap_exact_triangle_removals']if q['mesh']==o.name);assert removed==expected,(o.name,removed,expected)
 me=bpy.data.meshes.new(o.name+'_CapOnlySuccessor');me.from_pydata(vs,[],fs);me.update()
 for material in old.materials:me.materials.append(material)
 layer=me.uv_layers.new(name='ExactRetainedUV')
 for f,mi in zip(me.polygons,mis):
  f.material_index=mi
  for li in f.loop_indices:layer.data[li].uv=uvs[me.loops[li].vertex_index]
 o.data=me;o.matrix_world.identity();changes.append({'mesh':o.name,'removed_cap_triangles':removed,'retained_triangle_count':len(fs)})
patch=save('ForwardStaffLowerCapOnlySuccessor.blend','AST-STF-009_lower_cap_only_successor_r001.glb');assert all(sha(W/"predecessors/lower_staff_network.gd" if p=="Game/scripts/lower_staff_network.gd" else R/p)==h for p,h in P['source_pins'].items());result={'status':'PASS','blender_version':bpy.app.version_string,'envelope':envelope,'cap_patch':patch,'cap_named_replacements':changes,'retained_native_shaft_parts':37,'new_top_cap':1,'fixed_sills':5,'source_pins_unchanged':True,'upper_travel_enabled':False};(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print('SHAFT_NATIVE_PASS',json.dumps(result))
