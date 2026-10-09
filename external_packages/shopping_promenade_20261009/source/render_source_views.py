"""Representative normal-height views from saved editable sources; never resave them."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
P=Path(__file__).resolve().parents[1];plan=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());lights=json.loads((P/'docs/LIGHT_SOURCES.json').read_text());receipts=[]
def xyz(p):return Vector((p[0],-p[2],p[1]-52.5))
views=[('parcel_entry','D09_shops_S72.blend',(80,54.15,80),(71.5,54.0,81)),('soft_landing','D09_shops_S72.blend',(80,54.15,106),(71.0,54.0,106)),('paper_library','D09_shops_S72.blend',(80,54.15,132),(71.5,54.0,133)),('orbit_gallery','D09_shops_S72.blend',(80,54.15,262),(71.5,54.0,263)),('textile_fitting','D09_shops_S100.blend',(92,54.15,158),(101.0,54.0,158)),('pocket_garden','D09_shops_S100.blend',(92,54.15,184),(101.0,54.0,185)),('public_street','D09_shops_S72.blend',(86,54.15,86),(86,55.5,125))]
for name,native,eye,target in views:
 bpy.ops.wm.open_mainfile(filepath=str(P/'source/natives'/native));sc=bpy.context.scene
 # Append actual court and adjacent bank sources, preserving their source transforms.
 more=['D09_courts_and_services.blend']
 if name=='public_street':more.append('D09_shops_S100.blend')
 for f in more:
  with bpy.data.libraries.load(str(P/'source/natives'/f),link=False) as (a,d):d.objects=a.objects
  col=bpy.data.collections.new('review_'+f);sc.collection.children.link(col)
  for o in d.objects:
   if o:col.objects.link(o)
 # Retain geometry inside the representative court/room catchment only. This is
 # a declared source view isolation, not shipped streaming or a whole-scene cull.
 hidden=[]
 for ob in sc.objects:
  if ob.type!='MESH':continue
  centre=ob.matrix_world@sum((Vector(c) for c in ob.bound_box),Vector())/8
  if abs(centre.x-eye[0])>33 or abs(-centre.y-eye[2])>65:
   ob.hide_render=True;hidden.append(ob.name)
 world=bpy.data.worlds.new('SourceReviewWorld');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.18,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.32
 used=[]
 for row in lights:
  p=row['position_world']
  if abs(p[0]-eye[0])>23 or abs(p[2]-eye[2])>38:continue
  data=bpy.data.lights.new(row['id'],'SPOT');data.energy=210*row['energy'];data.color=row['colour'];data.spot_size=math.radians(row['angle_deg']);data.spot_blend=.50;ob=bpy.data.objects.new(row['id'],data);sc.collection.objects.link(ob);ob.location=xyz(p);ob.rotation_euler=(0,0,0);used.append(row['id'])
 data=bpy.data.cameras.new('ConstructionReviewCamera');camera=bpy.data.objects.new('ConstructionReviewCamera',data);sc.collection.objects.link(camera);camera.location=xyz(eye);camera.rotation_euler=(xyz(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=22;sc.camera=camera
 sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.exposure=1.25;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'qa'/('source_'+name+'.png'));bpy.ops.render.render(write_still=True)
 receipts.append({'view':name,'native':native,'eye_xyz':eye,'target_xyz':target,'source_height_above_floor_m':1.65,'actual_fixture_sources':used,'isolated_distant_source_parts':len(hidden),'geometry_hidden_near_camera':False,'lighting_note':'Blender source view with physical fixture positions and neutral world/exposure; no equivalence to final Godot lighting claimed','scope':'Construction source review; no final art or whole-ship acceptance'})
 print('SOURCE_VIEW',name,flush=True)
(P/'qa/source_view_receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
