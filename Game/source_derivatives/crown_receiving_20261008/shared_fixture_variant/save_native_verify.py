"""Run only after parent releases one bounded CPU2 Blender slot. No runtime re-export."""
from pathlib import Path
import bpy,json,hashlib,collections,sys,traceback
from mathutils import Vector
B=Path(__file__).resolve().parent;A='AST-CMD-001_crown_fixture_relocation_20261008_r002';proof=json.loads((B/'BINARY_EDIT_PROOF.json').read_text());src=Path(proof['source_native']);out=B/(A+'.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(o):
 d={'name':o.name,'type':o.type,'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'props':dict(o.items())}
 if o.type=='MESH':
  m=o.data;d.update(vertices=[list(v.co)for v in m.vertices],polygons=[(list(p.vertices),p.material_index,p.use_smooth)for p in m.polygons],edges=[list(e.vertices)for e in m.edges],uv=[(l.name,[list(v.uv)for v in l.data])for l in m.uv_layers],materials=[x.name if x else None for x in m.materials],modifiers=[(x.name,x.type)for x in o.modifiers])
 return d
def signatures():
 s=collections.Counter()
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();uv=o.data.uv_layers.active
  for t in o.data.loop_triangles:
   pts=[]
   for vi,li in zip(t.vertices,t.loops):
    v=o.matrix_world@o.data.vertices[vi].co;u=uv.data[li].uv;pts.append(tuple(round(x,4)for x in (*v,*u)))
   s[(o.data.materials[t.material_index].name,tuple(sorted(pts)))]+=1
 return s
try:
 assert not out.exists();assert sha(src)==proof['source_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));before={o.name:snapshot(o)for o in bpy.context.scene.objects};proposals=json.loads((B.parent/'fixture_fit_candidates/MOUNTED_FIXTURE_RELOCATION_PROPOSALS.json').read_text());delta={s['name']:s['translation']for s in proof['selected_source_parts']}
 delta.update({q['existing_marker']:q['translation']for q in proposals})
 for name,d in delta.items():
  o=bpy.data.objects[name];assert o.parent is None;assert not o.constraints;assert not o.animation_data;o.location+=Vector((d[0],-d[2],d[1]))
 bpy.context.view_layer.update();after={o.name:snapshot(o)for o in bpy.context.scene.objects};assert before.keys()==after.keys()
 for name,old in before.items():
  new=after[name]
  if name in delta:
   old=old.copy();old['matrix']=new['matrix'];assert old==new,(name,'nontransform drift')
  else:assert old==new,(name,'unchosen source changed')
 native_tri=signatures();native_markers={o.name:list(o.matrix_world.translation)for o in bpy.context.scene.objects if o.type=='EMPTY'}
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out));assert sha(src)==proof['source_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(out));assert {o.name:snapshot(o)for o in bpy.context.scene.objects}==after;assert signatures()==native_tri
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(B/(A+'.glb')));runtime_tri=signatures();assert native_tri==runtime_tri,('triangle UV material mismatch',sum((native_tri-runtime_tri).values()),sum((runtime_tri-native_tri).values()))
 for name,p in native_markers.items():assert (bpy.data.objects[name].matrix_world.translation-Vector(p)).length<1e-5,name
 (B/'NATIVE_RUNTIME_PROOF.json').write_text(json.dumps({'variant_native_sha256':sha(out),'variant_runtime_sha256':sha(B/(A+'.glb')),'original_native_sha256':sha(src),'unchanged_native_objects':len(before)-len(delta),'translated_native_objects':len(delta),'source_objects':len(before),'triangle_uv_material_signature_count':sum(native_tri.values()),'source_runtime_signatures_equal_4_decimal':True,'all_markers_match_within_1e_5_m':True,'save_reload_snapshot_equal':True,'no_runtime_reexport':True},indent=2));print('NATIVE_RUNTIME_PROOF_PASSED',flush=True)
except Exception:
 traceback.print_exc();sys.stdout.flush();sys.stderr.flush();sys.exit(1)
