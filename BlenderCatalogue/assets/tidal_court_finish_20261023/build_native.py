"""Editable material/light successor library. Does not reconstruct architecture."""
from pathlib import Path
import bpy, hashlib, json, struct

N = Path(__file__).resolve().parent
R = N.parents[2]
G = R / 'Game/tidal_court_finish_20261023'
plan = json.loads((G / 'PLAN.json').read_text())
target = N / 'TidalCourtSurfaceAndFixtures_r001.blend'
assert not target.exists(), 'Preserve the immutable named native successor'
model = R / 'Game' / plan['model'].removeprefix('res://')
raw = model.read_bytes()
assert hashlib.sha256(raw).hexdigest() == plan['model_sha256']
size = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20+size])
binary = raw[28+size:]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
materials = []
for role, spec in plan['materials'].items():
    source = next(m for m in doc['materials'] if m['name'] == 'COURT_'+role)
    image = doc['images'][doc['textures'][source['pbrMetallicRoughness']['baseColorTexture']['index']]['source']]
    view = doc['bufferViews'][image['bufferView']]
    data = binary[view.get('byteOffset', 0):view.get('byteOffset', 0)+view['byteLength']]
    # Packed images are exact retained PNG bytes, not a new texture generation.
    tmp = Path('/tmp') / ('astraea-tidal-surface-'+role+'.png')
    tmp.write_bytes(data)
    im = bpy.data.images.load(str(tmp), check_existing=False)
    im.name = 'RetainedTidal_'+role
    im.pack()
    material = bpy.data.materials.new('TidalCourtSurface_r001_'+role)
    material.use_nodes = True
    material.use_fake_user = True
    material.diffuse_color = spec['tint']
    nodes = material.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = spec['roughness']
    bsdf.inputs['Metallic'].default_value = spec['metallic']
    tex = nodes.new('ShaderNodeTexImage'); tex.image = im
    mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0
    mix.inputs[2].default_value = spec['tint']
    material.node_tree.links.new(tex.outputs['Color'], mix.inputs[1])
    material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    material['retained_png_sha256'] = hashlib.sha256(data).hexdigest()
    materials.append(material.name)
    tmp.unlink()
for row in plan['lights']:
    light = bpy.data.lights.new(row['name'], 'POINT')
    light.color = row['color']; light.energy = 110 if row['role']=='court' else 85
    light.shadow_soft_size = .18
    o = bpy.data.objects.new(row['name'], light)
    bpy.context.scene.collection.objects.link(o)
    x,y,z = row['position']; o.location = (x,-z,y)
    for key in ('energy','range','attenuation'):o['godot_'+key]=row[key]
    o['retained_fixture_source']=row['source_part_id']
    o['preview_watts_not_godot_energy']=True
bpy.context.scene['source_geometry_owner']=plan['model']
bpy.context.scene['scope']='Material and light library only; immutable architecture remains in retained source.'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
(G/'evidence/NATIVE.json').write_text(json.dumps({'status':'PASS','native':str(target.relative_to(R)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'materials':materials,'retained_fixture_lights':len(plan['lights']),'architecture_geometry_recreated':False,'original_native_path_recovered':False},indent=2)+'\n')
print('TIDAL_COURT_NATIVE_LIBRARY',len(materials),len(plan['lights']))
