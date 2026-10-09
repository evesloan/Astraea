"""Recessed public-retail enamel plus the unchanged common catalogue palette."""
from pathlib import Path
import importlib.util
import json
import bpy

ROOT = Path(__file__).resolve().parents[1]


def materials():
    spec = importlib.util.spec_from_file_location('astraea_common_materials', ROOT / 'standards/materials.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    output = common.materials()
    manifest = json.loads((ROOT / 'materials/retail/manifest.json').read_text())
    for role, row in manifest['materials'].items():
        material = bpy.data.materials.new('ASTRAEA_' + role)
        material.use_nodes = True
        material['astraea_material_role'] = role
        material['material_revision'] = manifest['revision']
        material['meters_per_tile_uv'] = row['meters_per_tile_uv']
        material.diffuse_color = tuple(channel / 255 for channel in row['colour_srgb_8bit']) + (1,)
        nodes = material.node_tree.nodes
        nodes.clear()
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Roughness'].default_value = row['roughness']
        shader.inputs['Metallic'].default_value = row['metallic']
        texture = nodes.new('ShaderNodeTexImage')
        image = bpy.data.images.load(str(ROOT / 'materials/retail' / row['file']), check_existing=True)
        image.reload()
        image.pack()
        texture.image = image
        texture.extension = 'REPEAT'
        texture.interpolation = 'Linear'
        surface = nodes.new('ShaderNodeOutputMaterial')
        material.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
        material.node_tree.links.new(shader.outputs['BSDF'], surface.inputs['Surface'])
        output[role] = material
    return output
