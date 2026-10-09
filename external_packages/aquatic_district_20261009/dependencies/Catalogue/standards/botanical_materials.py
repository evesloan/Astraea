"""New botanical-only Principled roles. Existing guest/staff libraries untouched."""
from pathlib import Path
import json,bpy
ROOT=Path(__file__).resolve().parents[1]
def materials():
 spec=json.loads((ROOT/'materials/botanical/manifest.json').read_text());out={}
 for role,row in spec['materials'].items():
  name='ASTRAEA_'+role;mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True
  mat['astraea_material_role']=role;mat['material_revision']=spec['revision'];mat['uv_contract']=row['uv_contract'];mat['alpha_contract']='OPAQUE';mat.use_backface_culling=not row['double_sided']
  if row['meters_per_tile_uv'] is not None:mat['meters_per_tile_uv']=row['meters_per_tile_uv']
  mat.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,)
  nodes=mat.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=0;bs.inputs['Alpha'].default_value=1
  tex=nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(str(ROOT/'materials/botanical'/row['file']),check_existing=True);img.reload();img.pack();tex.image=img;tex.extension='REPEAT';tex.interpolation='Linear'
  output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);tex.location=(-320,80);bs.location=(0,80);output.location=(320,80);out[role]=mat
 return out
