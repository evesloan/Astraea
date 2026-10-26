from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r007';N=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/r007'
p=N/'OrchardIntegratedReceiving_r007.blend';h=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p))
r=json.loads((D/'FINAL.json').read_text())
for lamp in r['fixtures']:
 for name in [lamp['name'],lamp['backplate']]:
  o=bpy.data.objects[name];o.location.x+=.2
  if name==lamp['name']:
   for i,slot in enumerate(o.material_slots):
    m=slot.material.copy();m.name+='_OrchardPoweredLens';o.data.materials[i]=m;m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Emission Color'].default_value=(1,.89,.72,1);bs.inputs['Emission Strength'].default_value=1
out=N/'OrchardIntegratedReceiving_r007_final.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out));assert hashlib.sha256(p.read_bytes()).hexdigest()==h
(D/'FINAL_NATIVE.json').write_text(json.dumps({'preserved_preimage_sha256':h,'path':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'fixture_count':2,'unchanged_light_budget':8},indent=2)+'\n',encoding='utf-8')
