from pathlib import Path
import bpy,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[1]
reference=json.loads((ROOT/'qa/source_geometry.json').read_text());stage=ROOT/'qa/source_only_stage_collision_refined/catalogue/assets/aquatic_towel_use'
rows=[]
for asset,expected in reference.items():
 path=stage/'source'/f'{asset}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();checks=[]
 for p in expected['parts']:
  ob=bpy.data.objects.get(p['name']);assert ob is not None;eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();v=np.array([list(ob.matrix_world@x.co) for x in me.vertices]);f=np.array([list(t.vertices) for t in me.loop_triangles]);error=float(np.abs(v-np.array(p['vertices'])).max())
  checks.append({'part':p['name'],'vertices_max_difference_m':error,'triangle_indices_equal':np.array_equal(f,np.array(p['triangles'])),'material_role':ob['semantic_role'],'passed':error<1e-7 and np.array_equal(f,np.array(p['triangles'])) and ob['semantic_role']==p['role']});eo.to_mesh_clear()
 packed=[{'image':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.source=='FILE']
 rows.append({'asset':asset,'fresh_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'parts':checks,'images':packed,'passed':all(x['passed'] for x in checks) and all(x['packed'] for x in packed)})
(ROOT/'qa/fresh_source_reload.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passed'] for r in rows)},indent=2)+'\n');print('FRESH_SOURCES_RELOAD_PASS',all(r['passed'] for r in rows))
