"""Reload native and actual GLB, then bounded diagnostic reviews. No engine proof."""
from pathlib import Path
import bpy,json,sys,hashlib,math
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];SRC=Path('/workspace/scratch/375c2e438292/library_cinema_support_20261007')
def xyz(p):return Vector((p[0],-p[2],p[1]))
def world(v):return [v.x,v.z,-v.y]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'source/cinema_library_receiving_r001.blend'))
record=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('asset_id')!='AST-RCV-CL-001':continue
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
 record.append(dict(name=o.name,manifold=bad==0,has_uv=bool(o.data.uv_layers),material_roles=[m.get('astraea_material_role') for m in o.data.materials]))
imgs=[dict(name=i.name,packed=bool(i.packed_file)) for i in bpy.data.images if i.source=='FILE']
(OUT/'qa/native_reload.json').write_text(json.dumps(dict(mesh_count=len(record),all_closed=all(r['manifold'] for r in record),all_have_uv=all(r['has_uv'] for r in record),images=imgs,objects=record),indent=2))
assert all(r['manifold'] and r['has_uv'] for r in record)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'exports/cinema_library_receiving_r001.glb'));candidate=list(bpy.data.objects)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('QA_neutral_world');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.10,.13,.18,1);bg.inputs[1].default_value=.45
qa=bpy.data.collections.new('QA_ONLY_LIGHTS_AND_CAMERAS');scene.collection.children.link(qa)
def camera(name,pos,target,lens=38):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);qa.objects.link(o);o.location=xyz(pos);o.rotation_euler=(xyz(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.10;d.clip_end=500;scene.camera=o;return o
def area(name,pos,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);qa.objects.link(o);o.location=xyz(pos);o.rotation_euler=(xyz(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
lights=[area('QA_key',[20,102,-449],[30,71,-431],12000,45,(1,.83,.64)),area('QA_fill',[80,86,-405],[30,73,-431],10000,32,(.64,.76,1)),area('QA_rear',[-15,86,-470],[30,74,-441],12000,30,(1,.86,.7))]
VIEW=[]
ONLY_SEATED='--only-seated' in sys.argv
def render(name,pos,target,lens,notes,hide=()):
 if ONLY_SEATED and not name.startswith('03_'):return
 before={o:o.hide_render for o in hide}
 for o in hide:o.hide_render=True
 camera(name,pos,target,lens);scene.render.filepath=str(OUT/'views'/(name+'.png'));bpy.ops.render.render(write_still=True)
 VIEW.append(dict(file='views/'+name+'.png',world_eye_xyz=pos,world_target_xyz=target,lens_mm=lens,notes=notes,rendered_source='actual reimported selected GLB',diagnostic_hidden_objects=[o.name for o in hide],candidate_glb_sha256=hashlib.sha256((OUT/'exports/cinema_library_receiving_r001.glb').read_bytes()).hexdigest()))
 for o,v in before.items():o.hide_render=v
# A source overview, underside exposed by omitting only the slab collection in this diagnostic capture.
slabs=[o for o in candidate if o.get('semantic_group') in ['Library_slab','Library_feet']]
render('01_transfer_frame_cutaway_SOURCE_CANDIDATE',[114,118,-351],[31,73.8,-432],38,'High diagnostic cutaway; Library slab intentionally hidden so the five trusses and gridded connections are reviewable. Not normal-play or installed-room evidence.',slabs)
detail_light=area('QA_detail_underside',[18,73,-444],[13,75.4,-450.8],1800,5,(1,.84,.64))
render('02_pier_grid_joint_DETAIL',[18,71.15,-445.0],[13,75.4,-450.8],36,'Structural detail at normal standing eye over the level floor: shaped pier, exact seat and perpendicular grid connection. QA studio lights only.')
detail_light.hide_render=True
# Read-only retained Cinema composition. Import original bytes, add their documented world placement.
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(SRC/'WP13_FULL/WP13_D11_directory_02/exports/WP13_cinema1.glb'));cinema=[o for o in bpy.data.objects if o not in old];cinset=set(cinema)
for o in cinema:
 if o.parent not in cinset:o.location += xyz([11,69.5,-468])
# Exclude known incompatible ceiling only for this diagnostic; originals are never saved or replaced.
hidden=[]
for o in cinema:
 if o.name.startswith(('CINEMA_ROOF','VAULT_')):o.hide_render=True;hidden.append(o.name)
# Original punctual fixture lights stay visible; QA wash is reduced in eye views and explicitly disclosed.
for l in lights:l.data.energy*=.12
bg.inputs[1].default_value=.10
# Local review fill corresponds to guest eye view but is not a proposed new production fixture.
fill=area('QA_context_fill',[36,74.0,-432],[36,72,-449],1500,18,(1,.86,.70));lights.append(fill)
render('03_cinema_seated_optics_CONTEXT',[38.739999771118164,71.95999999046326,-431.20000076293945],[36,73.8,-459.47],28,'Seated eye proxy bound to actual retained seat WP13_C1_R08_P11, 1.20m above its source floor anchor [38.73999977,70.75999999,-431.20000076]; no species pose certification. All198 chairs plus2 transfer bays remain. Existing Cinema roof/vault hidden only for diagnostic composition. Final acoustic closure and fixture revision belong to WP13. Supplemental QA fill is not a production fixture.')
render('04_cinema_side_route_NORMAL_EYE',[16.0,71.15,-445.5],[36,74.5,-450.8],28,'Standing eye proxy1.65m above level D11 floor, viewing truss underside and retained audience. Not a runtime arrival/body/cart test. Same diagnostic old-roof/vault overrides.')
# Record contexts and transforms; do not save copied room source as an authored room deliverable.
if ONLY_SEATED:
 prior=json.loads((OUT/'qa/view_manifest.json').read_text())['views']; VIEW=[next((v for v in VIEW if v['file']==p['file']),p) for p in prior]
(OUT/'qa/view_manifest.json').write_text(json.dumps(dict(candidate_source_sha256=hashlib.sha256((OUT/'source/cinema_library_receiving_r001.blend').read_bytes()).hexdigest(),views=VIEW,cinema_context_glb_sha256=hashlib.sha256((SRC/'WP13_FULL/WP13_D11_directory_02/exports/WP13_cinema1.glb').read_bytes()).hexdigest(),cinema_context_world_offset=[11,69.5,-468],hidden_old_cinema_objects=hidden,context_policy='Read-only imported copies for review only. No original writes, no installed acceptance.',source_only=True),indent=2))
print('RECEIVING_REVIEW_RENDER_COMPLETE',len(VIEW))
