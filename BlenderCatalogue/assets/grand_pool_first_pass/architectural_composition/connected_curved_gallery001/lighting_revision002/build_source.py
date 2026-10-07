from pathlib import Path
import bpy,bmesh,json,hashlib,importlib.util,sys
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True;B=Path(__file__).parent;P=B.parent
spec=importlib.util.spec_from_file_location('parent_source_methods',P/'build_source.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sha=m.sha;core=m.core;OUT=B/'source_build002'
def main():
 pins=json.loads((B/'SOURCE_JOB_PINS.json').read_text())['inputs']
 for p,h in pins.items():assert sha(p)==h,p
 assert not OUT.exists();OUT.mkdir();(OUT/'qa').mkdir();(OUT/'source').mkdir()
 plan=json.loads((B/'CORE_PLAN.json').read_text());proof=json.loads((B/'RECEIVER_PROOF.json').read_text());assert proof['status']=='PASS_PAIRED_PHYSICAL_FIXTURE_RECEIVER_PLAN'and proof['plan_sha256']==sha(B/'CORE_PLAN.json');tris=json.loads((B/'SOURCE_TRIANGLES.json').read_text());assert tris['plan_sha256']==sha(B/'CORE_PLAN.json');assert sha(plan['source_base'])==plan['source_base_sha256']
 bpy.ops.wm.open_mainfile(filepath=plan['source_base']);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2;before={o.name:m.retained.fingerprint(o)for o in scene.objects};modified=set(plan['modified_existing_parts']);markers={r['name']for r in plan['fixture_reservations']}
 for r in plan['parts']:
  if r['name']not in modified:continue
  o=bpy.data.objects[r['name']];material=o.data.materials[0];me=bpy.data.meshes.new(r['name']+'_paired_optics002');me.from_pydata([core.B(v)for v in r['vertices_xyz']],[],tris['parts'][r['name']]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();me.materials.append(material);o.data=me;o['source_plan_sha256']=sha(B/'CORE_PLAN.json');o['support_json']=json.dumps(r['support']);o['semantic_role']=r['semantic'];o['paired_optics_revision']='002';uv=me.uv_layers.new(name='MetreScaled_SourceRole');tile=material.get('meters_per_tile_uv',[1,1]);axis=core.B(r.get('grain_axis_xyz',[1,0,0]))
  for face in me.polygons:
   n=face.normal.normalized();u=axis-n*axis.dot(n)
   if u.length<.01:a=Vector((0,0,1))if abs(n.z)<.9 else Vector((0,1,0));u=a-n*a.dot(n)
   u.normalize();v=n.cross(u).normalized()
   for li in face.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/tile[0],p.dot(v)/tile[1])
 for r in plan['fixture_reservations']:
  o=bpy.data.objects[r['name']];o.location=core.B(r['position_xyz']);o['marker_json']=json.dumps(r);o['paired_optics_revision']='002'
 bpy.context.view_layer.update();after={o.name:m.retained.fingerprint(o)for o in scene.objects};assert set(before)==set(after)
 for n,h in before.items():
  if n not in modified|markers:assert after[n]==h,('Unrelated source mutation',n)
 actual=dict(plan,parts=core.snapshot(scene,plan));m.newjson(OUT/'qa/BUILD_EVALUATED_CORE.json',actual);m.newjson(OUT/'qa/OBJECT_PRESERVATION.json',{'status':'PASS_PAIRED_LIGHT_ONLY_SOURCE_REVISION','before':before,'after':after,'modified_meshes':sorted(modified),'updated_markers':sorted(markers),'unchanged_objects':len(before)-len(modified|markers),'architecture_palette_programme_exact':True})
 scene['status']='Connected curved gallery with paired physical uplights/downlights; native balance and visual acceptance pending';scene['source_plan_sha256']=sha(B/'CORE_PLAN.json');scene['paired_optics_proof_sha256']=sha(B/'RECEIVER_PROOF.json');source=OUT/'source/AST-AQU-016_connected_curved_gallery_lighting_r02.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);m.newjson(OUT/'qa/BUILD_RECEIPT.json',{'status':'SOURCE_LIGHTING_REVISION_SAVED_PENDING_REOPEN','source':str(source),'sha256':sha(source),'plan_sha256':sha(B/'CORE_PLAN.json'),'old_source_preserved':True,'unchanged_object_count':len(before)-len(modified|markers),'architecture_palette_programme_exact':True,'native_lighting_accepted':False})
 for p,h in pins.items():assert sha(p)==h,p
 print('PAIRED_SOURCE_SAVED',sha(source),flush=True)
if __name__=='__main__':main()
