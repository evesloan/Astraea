"""Read-only diagnostic view of reversible coordinate proposals, not architecture."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];f=P/'source/natives/G7_UpperSeamProposals_r001.blend';h=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
for o in bpy.context.scene.objects:
 if o.type=='CURVE':o.data.bevel_depth=.4
for m in bpy.data.materials:
 m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,.35,.04,1);p.inputs['Emission Color'].default_value=(1,.35,.04,1);p.inputs['Emission Strength'].default_value=1
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('QA proposal daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.22,.29,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=1
sun=bpy.data.objects.new('QA sun',bpy.data.lights.new('QA sun','SUN'));s.collection.objects.link(sun);sun.data.energy=3;sun.rotation_euler=(.4,.4,.5)
c=bpy.data.objects.new('QA proposal camera',bpy.data.cameras.new('QA proposal camera'));s.collection.objects.link(c);c.location=(850,-600,470);target=Vector((0,0,85));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=1300;s.camera=c;s.render.filepath=str(P/'qa/upper_seam_PROPOSAL_ONLY.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(f.read_bytes()).hexdigest()==h
(P/'qa/upper_seam_source_view_receipt.json').write_text(json.dumps({'image':s.render.filepath,'native_sha256':h,'native_resaved':False,'view':'External diagnostic coordinate guides only; not a source architectural assembly, supported route, whole-hull silhouette or final art acceptance. QA-only0.4m line weight replaces native0.018m guide bevel for legibility; not construction thickness.','lighting':'Temporary diagnostic sun/ambient and amber guide emission; no production light installed'},indent=2)+'\n');print('UPPER_PROPOSAL_SOURCE_VIEW')
