"""One actual-source wide view; no source edits and no game acceptance claim."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
G = Path(__file__).resolve().parents[2]
out = G / 'docs/validation/night_garden_residency_20261022'
image = out / 'SOURCE_CANDIDATE_WIDE.png'
assert not image.exists()
package = json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
pins = {}
for record in [package['receiving']] + package['rooms']:
    path = G/'assets/models'/record['model_file']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == record['model_sha256']
    pins[record['model_file']] = digest
    bpy.ops.import_scene.gltf(filepath=str(path))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 12
scene.cycles.use_denoising = False  # This installed Blender lacks OpenImageDenoise.
scene.render.resolution_x = 1400
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
world = bpy.data.worlds.new('SourceReviewWorld'); scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.35,.4,.5,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .65
sun = bpy.data.lights.new('ReviewSun','SUN'); sun.energy = 2.5; sun.angle = .2
lamp = bpy.data.objects.new('ReviewSun',sun); scene.collection.objects.link(lamp)
lamp.rotation_euler = (.4,-.6,-.4)
camera = bpy.data.cameras.new('ReviewCamera'); obj = bpy.data.objects.new('ReviewCamera',camera)
scene.collection.objects.link(obj); scene.camera = obj
obj.location = (205, -105, 265)
target = Vector((84,0,94))
obj.rotation_euler = (target-obj.location).to_track_quat('-Z','Y').to_euler()
camera.type = 'ORTHO'; camera.ortho_scale = 235
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(image)
bpy.ops.render.render(write_still=True)
from datetime import datetime, timezone
(out/'SOURCE_CANDIDATE_WIDE.json').write_text(json.dumps({
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Actual retained 30-room and r003 receiving GLBs; isolated source candidate, not integrated ship or engine screenshot',
 'unfinished':True,'visual_acceptance':False,'source_geometry_modified':False,
 'note':'Review illumination only; no commons context or runtime doors/lights; does not depict residency behavior',
 'sources':pins,'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest()
},indent=2)+'\n')
