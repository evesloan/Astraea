"""Read-only source views with explicit retained context, no production writes."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745'
def world(q):return Vector((q[0],-q[2],q[1]))
def setup(camera,target,out):
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
 s.render.resolution_x=1000;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(P/'qa'/out)
 s.world=bpy.data.worlds.new('QA neutral background');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.17,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 cam=bpy.data.objects.new('QA source camera',bpy.data.cameras.new('QA source camera'));s.collection.objects.link(cam);cam.location=world(camera);cam.rotation_euler=(world(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22;s.camera=cam
 for i,(q,power,size) in enumerate([(camera,1400,6),((camera[0],camera[1]+6,camera[2]+8),2200,10)]):
  l=bpy.data.lights.new('QA area '+str(i),'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.location=world(q);o.rotation_euler=(world(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.render.render(write_still=True)
def retained_floors(decks):
 data=json.loads((D/'Game/data/generated/structural_meshes.json').read_text());m=bpy.data.materials.new('QA retained slab neutral');m.diffuse_color=(.52,.48,.40,1)
 for r in data['regions']:
  if r['id'] not in [f'{deck}_{kind}' for deck in decks for kind in ['atrium_circulation','authored_atrium_terrace']]:continue
  v=[];f=[]
  for tri in r['triangles']:
   k=len(v);v.extend([(q[0],-q[1],r['floor_y']) for q in tri]);f.append((k,k+1,k+2))
  me=bpy.data.meshes.new('QA context '+r['id']);me.from_pydata(v,[],f);me.materials.append(m);o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
rows=[]
cases=[('upper_hull_theater_shoulders002','AST-HUL-002',(-114.5,79.6,-209),(-118.1,82,-205),'retained_theater_inner_normal_eye.png'),('atrium_guard_network','AST-ATR-001',(41,54.1,12),(0,60,0),'retained_atrium_guard_normal_eye.png'),('canopy_terrace','AST-GAR-004',(-4,1.6,0),(-17,2.4,0),'retained_canopy_arrival_normal_eye.png')]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if selected:
 rows=json.loads((P/'qa/retained_source_view_receipt.json').read_text())['views']
 rows=[r for r in rows if not any(a in r['retained_source'] for a in selected)]
 cases=[c for c in cases if c[1] in selected]
for fam,asset,cam,target,out in cases:
 f=D/f'BlenderCatalogue/assets/{fam}/source/{asset}.blend';h=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
 if asset=='AST-ATR-001':retained_floors(['D06','D07','D08','D09','D10','D11','D12','D13','D14','D15','D16','D17'])
 setup(cam,target,out);assert hashlib.sha256(f.read_bytes()).hexdigest()==h
 rows.append({'image':'qa/'+out,'retained_source':f.relative_to(D).as_posix(),'source_sha256':h,'camera_source_y_up_xyz':cam,'target_source_y_up_xyz':target,'eye_scope':'1.6m above retained D12 theater / D09 gallery / local canopy datum','context':'Only retained native, plus pinned atrium compiled top planes for guard-layer view. No complete game, neighbors, gameplay, source fixtures or new architecture. Temporary diagnostic area lighting.'})
(P/'qa/retained_source_view_receipt.json').write_text(json.dumps({'source_only':True,'production_scene_saved':False,'views':rows},indent=2)+'\n')
