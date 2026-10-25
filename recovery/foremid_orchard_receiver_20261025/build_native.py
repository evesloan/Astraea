"""Blender-only build of the new candidate, with no retained-source mutations."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2]
src=R/'Game/foremid_orchard_receiver_20261025/RECEIVER_r003.json'
c=json.loads(src.read_text(encoding='utf-8'))
for p,h in c['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
out=R/'BlenderCatalogue/assets/foremid_orchard_receiver_20261025/source'
out.mkdir(parents=True,exist_ok=True)
blend=out/'ForemidOrchardReceiver_r003.blend'
glb=R/'Game/foremid_orchard_receiver_20261025/ForemidOrchardReceiver_r003.glb'
assert not blend.exists() and not glb.exists(),'Never overwrite a previous native/export'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'warm_stone':(.62,.57,.47,1),'warm_walnut':(.20,.115,.06,1),'champagne_metal':(.65,.58,.42,1),'glass':(.25,.43,.46,.24)}
mats={}
for n,col in colors.items():
 m=bpy.data.materials.new(n);m.diffuse_color=col;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=col;bs.inputs['Roughness'].default_value=.65;bs.inputs['Alpha'].default_value=col[3]
 if n=='champagne_metal':bs.inputs['Metallic'].default_value=.65
 if n=='glass':m.surface_render_method='DITHERED'
 mats[n]=m
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def xyz(v):return(v[0],-v[2],v[1])
def cube(lo,hi):
 return [[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]]
for p in c['parts']:
 if p.get('kind')=='beam':
  a=Vector(p['a']);b=Vector(p['b']);t=(b-a).normalized();side=Vector((0,0,1));up=side.cross(t).normalized();v=[]
  for q in [a,b]:
   for w,h in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append(q+side*w*p['width']/2+up*h*p['depth']/2)
 elif p.get('kind')=='poly':v=p['vertices']
 else:v=cube(p['lo'],p['hi'])
 mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata([xyz(q) for q in v],[],faces);mesh.update()
 o=bpy.data.objects.new(p['name'],mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mats[p['role']]);o['physical_contact_required']=True;o['candidate_only']=True
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['selected']=False;scene['source_contract_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
assert len(scene.objects)==len(c['parts'])
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
proof={'candidate_only':True,'parts':len(c['parts']),'source_pins_verified':len(c['source_pins']),'native':{'path':str(blend.relative_to(R)),'sha256':hashlib.sha256(blend.read_bytes()).hexdigest()},'export':{'path':str(glb.relative_to(R)),'sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},'limitations':c['holds']}
(out/'BUILD_r003.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
