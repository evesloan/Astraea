"""Wide real-source view: delivered Supreme plus exact private floor proposal.

Workbench light is source review only. It does not claim Godot lighting,
normal-play views, exterior vista or structural/occupancy acceptance.
"""
import bpy, hashlib, json, pathlib
from mathutils import Vector
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
native = pathlib.Path('/workspace/group2-native-originals/sections/787_supreme/787_supreme.blend')
contract = json.loads((ROOT / 'Game/data/group2_completion/contracts/787.json').read_text())
assert hashlib.sha256(native.read_bytes()).hexdigest() == contract['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
scene = bpy.context.scene
# Keep every source mesh. Reframe at ordinary source eye height across the
# double-height conversation volume towards the staircase/upper rest gallery.
floor_source = P / 'source/FLOOR_INTERFACE_r001.blend'
with bpy.data.libraries.load(str(floor_source), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n.startswith('GROUP2_787_')]
for obj in dst.objects:
    scene.collection.objects.link(obj)
# Original source preview cameras/lights are retained in the immutable native;
# the review session adds its own camera and does not save over that native.
camera_data = bpy.data.cameras.new('Group2_Wide_Source_Camera')
camera = bpy.data.objects.new('Group2_Wide_Source_Camera', camera_data)
scene.collection.objects.link(camera)
def source(a):
    return Vector((a[0], -a[2], a[1]))
camera.location = source([-111.3, 103.65, 28.0])
target = source([-98.6, 106.0, 38.0])
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.lens = 20
scene.camera = camera
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.display.shading.light = 'STUDIO'
scene.display.shading.studiolight_rotate_z = .3
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.shadow_intensity = .15
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.background_type = 'WORLD'
scene.world.color = (.35, .35, .35)
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 1.0
out = P / 'evidence/SOURCE_SUPREME_WIDE_CONTEXT002.png'
assert not out.exists(), 'Preserve review revisions'
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
(P / 'evidence/SOURCE_CONTEXT_RECEIPT002.json').write_text(json.dumps({
    'image': str(out.relative_to(ROOT)), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
    'native_sha256': contract['native_sha256'], 'floor_source_sha256': hashlib.sha256(floor_source.read_bytes()).hexdigest(),
    'real_source_geometry': True, 'source_meshes_removed': 0,
    'camera_world_xyz': [-111.3, 103.65, 28.0], 'height_above_proposed_floor': 1.65,
    'review': 'Wide source composition with held missing-only floor proposals; neutral Workbench material colors',
    'accepted_game_visuals': False, 'original_native_modified': False}, indent=2) + '\n')
