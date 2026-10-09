"""Ordinary eye-level source evidence using exact receiving shell and compiler floor."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();C=json.loads((P/'contract.json').read_text());F=106.5
def xyz(p):return Vector((p[0],-p[2],F+p[1]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'source/native.blend'));sc=bpy.context.scene
# Native is already saved; all context/cameras below are preview-only and never re-saved/exported.
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(P/'dependencies/AST-CMD-001.glb'))
for ob in set(bpy.data.objects)-before:ob['qa_context_only']=True
m=bpy.data.materials.get('A_floor')
d=json.loads((P/'dependencies/receiving_floors.json').read_text())
for r in d['regions']:
 if r['id'] not in ['D18_atrium_structural_cap','D18_fore_apron']:continue
 verts=[];faces=[]
 for t in r['triangles']:
  idx=len(verts);verts.extend([(x,-z,r['floor_y']) for x,z in t]);faces.append((idx,idx+1,idx+2))
 me=bpy.data.meshes.new(r['id']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('QA_'+r['id'],me);sc.collection.objects.link(ob);me.materials.append(m);uv=me.uv_layers.new()
 for f in me.polygons:
  for li in f.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
def area(n,p,w,l,watts,color=(.78,.88,1)):
 data=bpy.data.lights.new('QA_'+n,'AREA');data.energy=watts;data.shape='RECTANGLE';data.size=w;data.size_y=l;data.color=color;ob=bpy.data.objects.new(data.name,data);sc.collection.objects.link(ob);ob.location=xyz(p)
# Retained physical Crown room fixture exits, not invisible ambient sources.
rc=json.loads((P/'dependencies/receiving_crown_contract.json').read_text())
for q in rc['light_markers']:
 if q.get('programme_key')==C['programme_key']:
  pp=q['position'];area(q['name'],[pp[0],pp[1]-F,pp[2]],1.3,.29,1300,tuple(q['suggested_color']))
for n,pp,w,l,watts in C['authored_fixture_preview']:area(n,pp,w,l,watts)
sc.world=bpy.data.worlds.new('QA neutral exterior; no invented celestial acceptance');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.06,.075,.09,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.08
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.cycles.device='CPU';sc.render.threads_mode='FIXED';sc.render.threads=4
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0
camd=bpy.data.cameras.new('QA ordinary 1.65m eye');cam=bpy.data.objects.new('QA camera',camd);sc.collection.objects.link(cam);sc.camera=cam;camd.lens=24;camd.clip_start=.08;camd.clip_end=180
only=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
receipts=[]
if only:
 old=json.loads((P/'qa/view_receipt.json').read_text())
 assert old['native_sha256']==sha(P/'source/native.blend') and old['glb_sha256']==sha(P/'exports'/(C['programme_key']+'.glb'))
 receipts=[v for v in old['views'] if v['name']!=only]
selected=[v for v in C['views'] if not only or v[0]==only]
for n,p,target in selected:
 assert abs(p[1]-1.65)<1e-6
 cam.location=xyz(p);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/'qa/views'/(n+'.png'));bpy.ops.render.render(write_still=True)
 f=Path(sc.render.filepath);receipts.append({'name':n,'path':'qa/views/'+f.name,'camera_godot':[p[0],F+p[1],p[2]],'target_godot':[target[0],F+target[1],target[2]],'lens_mm':24,'bytes':f.stat().st_size,'sha256':sha(f)});(P/'qa/view_receipt.json').write_text(json.dumps({'status':'SOURCE ONLY','native_sha256':sha(P/'source/native.blend'),'glb_sha256':sha(P/'exports'/(C['programme_key']+'.glb')),'lighting':'Actual retained Crown + authored fixture positions; candidate source render wattage; no Godot installed acceptance','context_sha256':sha(P/'dependencies/AST-CMD-001.glb'),'views':receipts},indent=2))
 print('VIEW_DONE',n,flush=True)

