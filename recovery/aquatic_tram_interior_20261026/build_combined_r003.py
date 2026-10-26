"""Join the authored station and source-received guideway in a new native."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r003';S=D.parent/'r002';N=R/'BlenderCatalogue/assets/aquatic_tram_interior_20261026/r003'
assert not D.exists() and not N.exists()
source=R/'BlenderCatalogue/assets/aquatic_tram_interior_20261026/r002/AquaticReceiving_r002.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
routes=json.loads((S/'ROUTE_SUPPORTS_r002.json').read_text());assert not routes['unresolved']
bpy.ops.wm.open_mainfile(filepath=str(source))
metal=next(m for m in bpy.data.materials if m.name=='champagne_metal')
created=[]
for p in routes['parts']:
 mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata([(v[0],-v[2],v[1]) for v in p['vertices']],[],p['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.materials.append(metal)
 uv=mesh.uv_layers.new(name='MaterialMetres')
 for face in mesh.polygons:
  axis=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=axis]
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/.5,v[axes[1]]/.5)
 o=bpy.data.objects.new(p['name'],mesh);bpy.context.collection.objects.link(o);o['contact_policy']='rolling_guideway' if p['name'].startswith(('Aquatic_Rail','Aquatic_ContinuousWeb')) else 'static';created.append(o.name)
D.mkdir();N.mkdir(parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(D/'AquaticIntegratedReceiving.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(N/'AquaticIntegratedReceiving_r003.blend'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
receipt={'selected':False,'station_source_sha256':before,'new_route_members':created,'route_receivers':routes['receivers'],'unresolved_route_receivers':routes['unresolved'],'preserved_station_meshes':280,'total_meshes':len([o for o in bpy.data.objects if o.type=='MESH']),'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [D/'AquaticIntegratedReceiving.glb',N/'AquaticIntegratedReceiving_r003.blend']}}
(D/'BUILD.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print('AQUATIC_COMBINED '+json.dumps({'meshes':receipt['total_meshes'],'new_route_members':len(created),'receivers':len(routes['receivers']),'selected':False}))
