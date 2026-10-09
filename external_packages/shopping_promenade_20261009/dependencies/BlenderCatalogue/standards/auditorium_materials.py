"""Audience-facing roles plus the unchanged common catalogue palette."""
from pathlib import Path
import json,importlib.util,bpy
ROOT=Path(__file__).resolve().parents[1]
def materials():
 spec=importlib.util.spec_from_file_location('astraea_common_materials',ROOT/'standards/materials.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);out=base.materials()
 data=json.loads((ROOT/'materials/auditorium/manifest.json').read_text())
 for role,row in data['materials'].items():
  mat=bpy.data.materials.new('ASTRAEA_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['material_revision']=data['revision'];mat['meters_per_tile_uv']=row['meters_per_tile_uv'];mat.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,)
  nodes=mat.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];tex=nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(str(ROOT/'materials/auditorium'/row['file']),check_existing=True);img.reload();img.pack();tex.image=img;tex.extension='REPEAT';tex.interpolation='Linear';output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);out[role]=mat
 return out
