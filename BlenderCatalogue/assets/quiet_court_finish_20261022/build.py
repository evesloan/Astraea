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
for role,color in d['materials'].items():
 mat=bpy.data.materials['COURT_'+role];mat.use_nodes=True;mat.diffuse_color=color;bs=mat.node_tree.nodes.get('Principled BSDF')
 for link in list(mat.node_tree.links):
  if link.to_node==bs and link.to_socket.name=='Base Color':mat.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.62 if role!='champagne_metal' else .34
 bs.inputs['Metallic'].default_value=.55 if role=='champagne_metal'else 0
 # Authored material layering without changing structural mesh topology.
 noise=mat.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=2;coord=mat.node_tree.nodes.new('ShaderNodeTexCoord');mat.node_tree.links.new(coord.outputs['Object'],noise.inputs['Vector']);bump=mat.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.012;mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal']);changed.append(mat.name)
assert geometry()==before;bpy.context.preferences.filepaths.save_version=0;native=W/'QuietGroveCourtSurface_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Keep current lifted/slab/guard geometry as editable reference; runtime applies only materials.
surface_record=dict(native=native.name,sha256=sha(native),source_geometry_sha256=before,successor_geometry_sha256=geometry(),materials=changed,objects=len(bpy.data.objects))
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import preview_only
records=[]
for row in d['placements']:
 a=next(x for x in d['sources']if x['catalogue_id']==row['catalogue_id']);src=R/'BlenderCatalogue'/a['source'];assert sha(src)==a['source_sha256']
 with bpy.data.libraries.load(str(src),link=False)as(s,t):t.objects=s.objects
 obs=[o for o in t.objects if o and not preview_only(o.name,{k:o.get(k,False)for k in ['preview_only','presentation_only','exclude_from_production']})];root=bpy.data.objects.new(row['name'],None);bpy.context.collection.objects.link(root)
 for o in obs:bpy.context.collection.objects.link(o)
 for o in obs:
  if o.parent not in obs:o.parent=root
  o.name=row['name']+'__'+o.name;o['runtime_collision']=False;o['retained_catalogue_id']=row['catalogue_id']
 root.location=(row['position'][0],-row['position'][2],row['position'][1]);root.rotation_euler.z=row['yaw'];root.scale=(row['scale'],)*3;bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in obs if o.type=='MESH'for v in o.data.vertices];lo=[min(v[k]for v in pts)for k in range(3)];hi=[max(v[k]for v in pts)for k in range(3)];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
 assert glo[0]>=row['bed_min'][0]-.02 and ghi[0]<=row['bed_max'][0]+.02 and glo[2]>=row['bed_min'][2]-.02 and ghi[2]<=row['bed_max'][2]+.02,(row['name'],glo,ghi)
 records.append(dict(name=row['name'],min=glo,max=ghi,bed=row['receiving_bed']))
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;native=W/'QuietGroveCourtPlanting_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);glb=P/'runtime/QuietGroveCourtPlanting_r001.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_extras=True,export_yup=True,export_apply=True)
(P/'evidence/NATIVE.json').write_text(json.dumps(dict(status='PASS',surface=surface_record,planting_native=native.name,planting_native_sha256=sha(native),glb_sha256=sha(glb),placements=records,all33_bed_footprints_preserved=True,source_native_unchanged=sha(R/d['native_source'])==d['native_sha256']),indent=2)+'\n');print('QUIET_COURT_NATIVE_PASS',len(records),flush=True)
