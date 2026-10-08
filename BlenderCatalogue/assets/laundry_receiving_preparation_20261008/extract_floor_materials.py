import bpy,json,hashlib
from pathlib import Path
r=Path('/workspace/scratch/375c2e438292/laundry_receiving_20261008');d=r/'runtime_candidate/assets/material_textures/laundry';d.mkdir(parents=True,exist_ok=True);out=[]
for objname in ['PREVIEW_ONLY_whole_floor','PREVIEW_ONLY_spine_finish','PREVIEW_ONLY_wayfinding_margin']:
 o=bpy.data.objects[objname];m=o.data.materials[0];bsdf=m.node_tree.nodes.get('Principled BSDF');tex=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image];spec={'object':objname,'name':m.name,'tile_uv_m':list(m.get('meters_per_tile_uv',[1,1])),'roughness':float(bsdf.inputs['Roughness'].default_value),'metallic':float(bsdf.inputs['Metallic'].default_value),'base_color_linear':list(bsdf.inputs['Base Color'].default_value),'textures':[]}
 for i,img in enumerate(tex):
  assert img.packed_file;p=d/(m.name+'_'+str(i)+'.png');p.write_bytes(bytes(img.packed_file.data));spec['textures'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 out.append(spec)
(r/'FLOOR_MATERIALS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
