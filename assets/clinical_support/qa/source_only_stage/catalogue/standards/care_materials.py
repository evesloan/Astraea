"""Additive care-oriented ordinary Principled roles; prior materials unchanged."""
from pathlib import Path
import json,bpy
ROOT=Path(__file__).resolve().parents[1]
def materials():
 manifest=json.loads((ROOT/'materials/care/manifest.json').read_text());out={}
 for role,row in manifest['materials'].items():
  name='ASTRAEA_'+role;mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True
  mat['astraea_material_role']=role;mat['material_revision']=manifest['revision'];mat['meters_per_tile_uv']=row['meters_per_tile_uv'];mat['intended_context']='fictional_care_components_unverified_species_fit'
  mat.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,)
  nodes=mat.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic']
  tex=nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(str(ROOT/'materials/care'/row['file']),check_existing=True);img.reload();img.pack();tex.image=img;tex.extension='REPEAT';tex.interpolation='Linear'
  output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);out[role]=mat
 return out
