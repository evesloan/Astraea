"""Parent-run read-only Blender internal inspection; no source save/export/render."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];plan=json.loads((R/'review/RENDER_PLAN.json').read_text());parts=json.loads((R/'source/geometry_parts.json').read_text());contract=json.loads((R/'source/section_contract.json').read_text());staff=json.loads((C/'materials/staff/manifest.json').read_text())['materials']
for path,sha in plan['frozen_inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-STF-010.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
actual={o.name:o for o in scene.objects if o.type=='MESH'};assert set(actual)=={p['name'] for p in parts};max_bound=0;max_uv=0;uv_loops=0;faces=0;role_images={};hidden=[];object_witness=[]
for p in parts:
 ob=actual[p['name']];me=ob.data
 if ob.hide_render or ob.hide_viewport or ob.hide_get():hidden.append(ob.name)
 assert ob['catalogue_id']=='AST-STF-010' and ob['source_kind']==p['kind'];assert len(me.vertices)==8 and len(me.polygons)==6
 xyz=[ob.matrix_world@v.co for v in me.vertices];godot=[(v.x,v.z,-v.y) for v in xyz];bounds=[min(v[k] for v in godot) if j%2==0 else max(v[k] for v in godot) for k in range(3) for j in range(2)];want=p['world_aabb'];error=max(abs(a-b) for a,b in zip(bounds,want));assert error<5e-5,(ob.name,error);max_bound=max(max_bound,error)
 # Every source mesh is a closed outward cuboid; each undirected boundary edge has two face uses.
 uses={}
 for f in me.polygons:
  assert f.area>1e-9 and f.normal.length>.999
  centre=sum((me.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);meshcentre=sum((v.co for v in me.vertices),Vector())/8;assert f.normal.dot(centre-meshcentre)>0,ob.name
  for i,j in zip(f.vertices,list(f.vertices[1:])+[f.vertices[0]]):
   key=tuple(sorted([i,j]));uses[key]=uses.get(key,0)+1
 assert len(uses)==12 and all(v==2 for v in uses.values())
 assert me.uv_layers.active and me.uv_layers.active.name=='MetreScaled';uv=me.uv_layers.active.data;assert len(uv)==len(me.loops)==24
 assert len(me.materials)==1;mat=me.materials[0];role=mat['astraea_material_role'];assert role==p['role'];scale=staff[role]['meters_per_tile_uv'];texnodes=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(texnodes)==1;image=texnodes[0].image;assert image is not None and image.packed_file is not None
 sha=hashlib.sha256(bytes(image.packed_file.data)).hexdigest();assert sha==staff[role]['sha256'];role_images[role]=dict(image=image.name,sha256=sha,packed=True)
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;pred=(q.dot(u)/scale[0],q.dot(v)/scale[1]);ue=max(abs(pred[k]-uv[li].uv[k]) for k in [0,1]);assert ue<1e-4,(ob.name,ue);max_uv=max(max_uv,ue)
 uv_loops+=len(uv);faces+=len(me.polygons);object_witness.append(dict(name=ob.name,source_bound_error_m=error,closed_outward=True,metre_scaled_uv=True,visible=ob.name not in hidden))
assert not hidden
light_witness=[]
for i,light in enumerate(contract['light_markers']):
 name='CRW_TASK_LIGHT_DATUM_%03d'%i;ob=bpy.data.objects[name];assert ob.type=='EMPTY' and ob['datum_kind']=='supported_staff_task_light';assert list(ob['world_direction_godot_xyz'])==[0,-1,0]
 pos=ob.matrix_world.translation;actual_xyz=[pos.x,pos.z,-pos.y];error=max(abs(a-b) for a,b in zip(actual_xyz,light['xyz']));assert error<5e-5
 assert ob['source_housing'] in actual;supports=json.loads(ob['source_supports_json']);assert len(supports)==2 and all(s in actual for s in supports)
 light_witness.append(dict(name=name,world_xyz=actual_xyz,error_m=error,housing=ob['source_housing'],supports=supports,downward=True))
assert len([o for o in scene.objects if o.name.startswith('CRW_TASK_LIGHT_DATUM_')])==166
for i,g in enumerate(contract['gate_reservations']):
 ob=bpy.data.objects['CRW_RESERVED_GATE_%02d'%i];assert ob.type=='EMPTY' and ob['clear_width_m']==3.6 and ob['clear_height_m']==2.65
assert not any(o.name.startswith('PREVIEW_') for o in scene.objects)
for path,sha in plan['frozen_inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path
out=dict(status='read-only Blender internal source QA passed',blender_version=bpy.app.version_string,source_meshes=len(actual),source_faces=faces,source_uv_loops=uv_loops,max_bound_error_m=max_bound,max_metre_scaled_uv_error=max_uv,packed_staff_images=role_images,source_fixture_datums=len(light_witness),gate_empty_datums=len(contract['gate_reservations']),hidden_source_meshes=hidden,compiler_preview_saved=False,render_run=False,source_save=False,source_export=False,frozen_inputs_preserved=True,objects=object_witness,fixture_datums=light_witness)
(R/'review/BLENDER_INTERNAL_QA.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['objects','fixture_datums']},indent=2))
