"""Shared ordinary Principled materials for new editable catalogue assets.

Import via importlib. Each role has a separate texture/material slot. Packed
image data preserves editability in .blend; GLB embeds referenced colour maps.
Author geometry UVs using meters_per_tile_uv, wood grain along V.
"""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def materials():
 manifest=json.loads((ROOT/'materials/material_manifest.json').read_text())
 records=manifest['materials']
 out={}
 for role,record in records.items():
  name='ASTRAEA_'+role
  mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
  mat.use_nodes=True
  mat['astraea_material_role']=role
  mat['meters_per_tile_uv']=record['meters_per_tile_uv']
  mat['texture_revision']=manifest['revision']
  mat.diffuse_color=tuple(c/255 for c in record['colour_srgb_8bit'])+(1.0,)
  nodes=mat.node_tree.nodes;nodes.clear()
  bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=record['roughness'];bs.inputs['Metallic'].default_value=record['metallic']
  tex=nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(str(ROOT/'materials'/record['base_color_file']),check_existing=True);img.reload();img.pack();tex.image=img;tex.interpolation='Linear';tex.extension='REPEAT'
  output=nodes.new('ShaderNodeOutputMaterial')
  mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
  tex.location=(-320,80);bs.location=(0,80);output.location=(320,80)
  out[role]=mat
 return out
