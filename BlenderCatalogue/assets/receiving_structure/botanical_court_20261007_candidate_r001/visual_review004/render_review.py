"""Read-only source/export review. Adds disposable context/light/cameras; never saves blend."""
from pathlib import Path
import bpy,json,hashlib,math,time
from mathutils import Vector
R=Path(__file__).resolve().parent;P=R.parent;S=P/'closed_interface002';Q=P/'proof_integration003';CAT=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/BlenderCatalogue');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert bpy.app.version[:3]==(4,3,2)
pins={str(p):sha(p) for p in [S/'AST-ATR-001_botanical_receiving_closed002.blend',S/'AST-ATR-001_botanical_receiving_closed002.glb',S/'PACKAGE_SHA256.json',Q/'PACKAGE_SHA256.json',Q/'candidate/Game/data/generated/structural_meshes.json',Q/'candidate/Game/data/spatial_layout.json',CAT/'materials/warm_stone.png']}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(S/'AST-ATR-001_botanical_receiving_closed002.glb'))
guards=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(guards)==136
for o in guards:o['review_role']='actual frozen guard export'
# Context uses the exact selected compiler triangles, sides and thickness; not a room floor.
compiled=json.loads((Q/'candidate/Game/data/generated/structural_meshes.json').read_text());ids=['D06_fore_route','D06_botanical_court_port_receiving_floor','D06_botanical_court_starboard_receiving_floor'];rows=[r for r in compiled['regions'] if r['id'] in ids];assert len(rows)==3
m=bpy.data.materials.new('REVIEW_CONTEXT_ApprovedWarmStone');m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.82;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/warm_stone.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],bsdf.inputs['Base Color'])
for row in rows:
 verts=[];faces=[];y=row['floor_y'];bottom=y-row['thickness']
 def face(points):
  start=len(verts);verts.extend([(x,-z,h) for x,h,z in points]);faces.append(tuple(range(start,len(verts))))
 for tri in row['triangles']:
  face([(p[0],y,p[1]) for p in tri]);face([(p[0],bottom,p[1]) for p in reversed(tri)])
 for ring in row['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):face([(a[0],y,a[1]),(b[0],y,b[1]),(b[0],bottom,b[1]),(a[0],bottom,a[1])])
 mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('CONTEXT_ONLY_'+row['id'],mesh);bpy.context.collection.objects.link(o);o['review_role']='context-only exact compiler floor';mesh.materials.append(m);uv=mesh.uv_layers.new(name='ReviewPlanar')
 for poly in mesh.polygons:
  for index in poly.loop_indices:
   p=mesh.vertices[mesh.loops[index].vertex_index].co;uv.data[index].uv=(p.x*.3,-p.y*.3)
# Diagnostic source-review light rig, not promised installed fixtures.
def source(xyz):return Vector((xyz[0],-xyz[2],xyz[1]))
for i,(at,target,power,size) in enumerate([([0,33.5,-222],[0,27,-222],1800,14),([-3,31,-240],[-6,27.7,-235],750,8),([3,31,-211],[7,27.7,-216],750,8)]):
 light=bpy.data.lights.new('REVIEW_ONLY_Area_'+str(i),'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(light.name,light);bpy.context.collection.objects.link(o);o.location=source(at);o.rotation_euler=(source(target)-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.cycles.max_bounces=5;scene.cycles.transparent_max_bounces=8;scene.render.threads_mode='FIXED';scene.render.threads=2
world=bpy.data.worlds.new('REVIEW_ONLY_NeutralStudio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.14,.16,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.2
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
views=[('01_axial_approach',[0,28.65,-250],[0,28.20,-220],24),('02_moss_future_portal_closed',[-4.5,28.65,-216],[-7.72,27.77,-216],35),('03_port_fore_corner_plinth',[-5.8,28.65,-235.4],[-7.72,27.56,-237.72],38)]
records=[]
for name,at,target,lens in views:
 assert abs(at[1]-27-1.65)<1e-6
 camera=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,camera);bpy.context.collection.objects.link(o);o.location=source(at);o.rotation_euler=(source(target)-o.location).to_track_quat('-Z','Y').to_euler();camera.lens=lens;camera.clip_start=.05;camera.clip_end=700;scene.camera=o;scene.render.filepath=str(R/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True);records.append({'image':name+'.png','camera_world_xyz':at,'target_world_xyz':target,'eye_height_m':1.65,'lens_mm':lens,'render_seconds':round(time.time()-start,2),'sha256':sha(R/(name+'.png'))})
assert all(sha(Path(p))==h for p,h in pins.items())
receipt={'status':'Three normal-eye frozen-export source review images; not Game/normal-play acceptance','blender':'4.3.2','threads':2,'render_engine':'Cycles CPU','samples':48,'actual_guard_mesh_count':len(guards),'context_only_floor_owners':ids,'floor_context_geometry':'Exact selected compiler triangle/ring records and thickness; no room-side floor added','lighting':'Temporary neutral review light rig, not source fixtures or Game lighting','geometry_revision':False,'native_source_saved':False,'input_hashes_unchanged':pins,'views':records,'limitations':['No Godot execution, runtime collision or Game material/shader acceptance.','Empty surroundings reflect absent room interiors/enclosures; not a promised exterior or finished botanical court.','Review camera/light/context objects were disposable and never saved to selected native.']};(R/'RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BOTANICAL_THREE_VIEWS_DONE')
