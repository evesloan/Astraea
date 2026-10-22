from pathlib import Path
import bpy,json,hashlib,math,sys,struct,shutil
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=R/'Game/quiet_court_finish_20261022';d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert shutil.disk_usage(R).free>700*1024**2
src=R/d['native_source'];assert sha(src)==d['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src))
def geometry():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  h.update(o.name.encode());h.update(bytes(str(tuple(tuple(r)for r in o.matrix_world)),'utf8'))
  for v in o.data.vertices:h.update(struct.pack('<fff',*v.co))
  for f in o.data.polygons:h.update(bytes(str(tuple(f.vertices)),'utf8'))
 return h.hexdigest()
before=geometry();changed=[]
surfaces=json.loads((R/'Game/quiet_court_illumination_20261022/SURFACES.json').read_text());d['materials']={k:v['color'] for k,v in surfaces.items()}
for role,color in d['materials'].items():
 mat=bpy.data.materials['COURT_'+role];mat.use_nodes=True;mat.diffuse_color=color;bs=mat.node_tree.nodes.get('Principled BSDF')
 for link in list(mat.node_tree.links):
  if link.to_node==bs and link.to_socket.name=='Base Color':mat.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=surfaces[role]['roughness']
 bs.inputs['Metallic'].default_value=.55 if role=='champagne_metal'else 0
 if role in ['warm_stone','warm_walnut','oatmeal_weave']:
  noise=mat.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.65;noise.inputs['Detail'].default_value=2
  coord=mat.node_tree.nodes.new('ShaderNodeTexCoord');mat.node_tree.links.new(coord.outputs['Object'],noise.inputs['Vector'])
  ramp=mat.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(c*.80 for c in color[:3])+(1,);ramp.color_ramp.elements[1].color=color
  mat.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);mat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 changed.append(mat.name)
assert geometry()==before;bpy.context.preferences.filepaths.save_version=0;native=W/'QuietGroveCourtSurface_r003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)

(R/'Game/quiet_court_balance_20261022/evidence/NATIVE.json').write_text(json.dumps(dict(status='PASS',native=native.name,sha256=sha(native),source_geometry_sha256=before,successor_geometry_sha256=geometry(),materials=changed,objects=len(bpy.data.objects)),indent=2)+'\n')
print('SURFACE_R002_PASS',before,flush=True)
