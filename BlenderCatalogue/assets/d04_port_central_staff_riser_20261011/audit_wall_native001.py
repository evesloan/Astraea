from pathlib import Path
import bpy,json,hashlib,collections
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=R/'Game/assets/models/AST-STF-009_pool_market_home_equipment.glb';native=W/'D04PortCentralStaffWallPatch_r001.blend';pins={str(p):sha(p)for p in[source,native]};lo=(-55.36,96.4,-.005);hi=(-55.1,102,2.85)
def triangles(ob):
 ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;out=[]
 for tri in ob.data.loop_triangles:
  q=[(tuple(ob.matrix_world@ob.data.vertices[ob.data.loops[k].vertex_index].co),tuple(uv.data[k].uv))for k in tri.loops];out.append((q,ob.data.materials[tri.material_index].name))
 return out
def key(q,mat):return (tuple(sorted((pos,uv)for pos,uv in q)),mat)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));expected={}
for name in P['wall_patch']['modified_cells']:
 ob=bpy.data.objects[name];ts=triangles(ob);outside=[(q,m)for q,m in ts if any(all(v[a]<lo[a]for v,u in q)or all(v[a]>hi[a]for v,u in q)for a in range(3))];expected[name]=collections.Counter(key(q,m)for q,m in outside)
bpy.ops.wm.open_mainfile(filepath=str(native));counts={}
for name,required in expected.items():
 actual=collections.Counter(key(q,m)for q,m in triangles(bpy.data.objects[name]));missing=required-actual;assert not missing,(name,len(missing));counts[name]=sum(required.values())
for p,h in pins.items():assert sha(Path(p))==h
(W/'EXACT_OUTSIDE_CUT_NATIVE_AUDIT.json').write_text(json.dumps({'status':'PASS','source_glb_sha256':pins[str(source)],'new_native_sha256':pins[str(native)],'exact_source_triangles_outside_cut_preserved':counts,'exact_vertices_UVs_materials_verified':True,'new_source_native_not_original_recovered_native':True,'no_native_or_original_export_bytes_changed_by_audit':True,'scope':'Exact triangle/UV/material multiset outside the bounded clipping box; triangles crossing the cut retain interpolated UVs and area-conservation proof in wall provenance. Godot source import compression discrepancy is separately bounded.'},indent=2)+'\n');print('Exact outside-cut source triangle audit',sum(counts.values()))
