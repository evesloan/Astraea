"""DEFERRED: run only in the authorized single Blender lane; never executed by preparation.
Creates a separate editable receiving asset. Does not open or modify either source room.
Usage: blender --background --threads 2 --python build_guards.py -- --out NEW_EMPTY_DIR
"""
from pathlib import Path
import sys,json,hashlib,importlib.util
import bpy,bmesh
O=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x');CAT=R/'BlenderCatalogue'
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[args.index('--out')+1]);assert not out.exists(),'Use a new output directory; preserve prior candidates'
pins=json.loads((O/'INPUT_PINS.json').read_text())
for p,row in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==row['sha256'],('Input drift',p)
data=json.loads((O/'GUARD_SOLIDS.json').read_text());ident=data['asset_id'];catalogue=json.loads((CAT/'catalogue_manifest.json').read_text());matches=[r for r in catalogue['assets'] if r['catalogue_id']==ident];assert not matches,'ID must remain unused; never overwrite another family'
out.mkdir(parents=True);bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2
spec=importlib.util.spec_from_file_location('astraea_materials',CAT/'standards/auditorium_materials.py');materials=importlib.util.module_from_spec(spec);spec.loader.exec_module(materials);M=materials.materials()
root=bpy.data.objects.new(ident,None);scene.collection.objects.link(root);root['asset_id']=ident;root['status']='Construction candidate, no operational acceptance';objects=[]
for row in data['solids']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([(x,-z,y)for x,y,z in row['vertices']],[],row['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(row['name'],mesh);scene.collection.objects.link(ob);ob.parent=root
 role='ivory_enamel' if ('Panel' in row['name'] or 'Terminal' in row['name']) else 'champagne_metal';ob.data.materials.append(M[role]);ob['asset_id']=ident;ob['support']=row['support'];ob['astraea_material_role']=role;ob['collision']='visible_mesh_static';ob['world_metres']='Blender=(X,-Z,Y)'
 uv=mesh.uv_layers.new(name='UVMap');tile=M[role].get('meters_per_tile_uv',(1.,1.));tile=(tile,tile) if isinstance(tile,(int,float)) else tuple(tile)
 for poly in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=([1,2],[0,2],[0,1])[axis]
  for li in poly.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/tile[0],v[axes[1]]/tile[1])
 objects.append(ob)
# No bevel modifier: exact mating planes and the source-fitted jamb profile must survive.
bpy.ops.wm.save_as_mainfile(filepath=str(out/(ident+'.blend')))
bpy.ops.object.select_all(action='DESELECT')
for ob in objects+[root]:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/(ident+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
# This is a generation receipt, not saved-native/export or Godot acceptance.
(out/'GENERATION_RECEIPT.json').write_text(json.dumps({'asset_id':ident,'objects':len(objects),'geometry_input_sha256':hashlib.sha256((O/'GUARD_SOLIDS.json').read_bytes()).hexdigest(),'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/(ident+'.blend'),out/(ident+'.glb')]},'validation_pending':['saved native reopen','raw export parity','contacts/source triangle clearance','Godot import and loaded route/guard validation']},indent=2))
