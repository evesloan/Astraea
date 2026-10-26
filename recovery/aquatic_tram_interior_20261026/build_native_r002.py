"""Editable aquatic receiving and retained planted guest refuge. Unselected."""
import bpy,bmesh,json,hashlib,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r002'
N=R/'BlenderCatalogue/assets/aquatic_tram_interior_20261026/r002'
assert not N.exists() and not (D/'AquaticReceiving.glb').exists()
pins=json.loads((D/'SOURCE_PINS.json').read_text(encoding='utf-8'))
original=R/'Game/source_derivatives/group4_aftmid_upper_20261012/AST-TRM-G4-030_aftmid_upper_receiving_r002.glb'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='a2e27cf17fe80acae8608697579c5919aaafe79f289645e22106253ec7aa93a1'
pins[original.relative_to(R).as_posix()]=hashlib.sha256(original.read_bytes()).hexdigest()
for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def xyz(v):return Vector((v[0],-v[2],v[1]))
def imported(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
 return set(bpy.data.objects)-before
def erase(objects):
 for o in objects:bpy.data.objects.remove(o,do_unlink=True)
palette=[]
for name in ['AST-AQU-012.glb','AST-AQU-013.glb','AST-AQU-014.glb','AST-RTL-006.glb','AST-FUR-001.glb']:
 objects=imported(R/'Game/assets/models'/name)
 for o in objects:
  if o.type=='MESH':palette.extend(list(o.data.materials))
 erase(objects)
roles=['warm_stone','warm_walnut','ivory_enamel','champagne_metal','dark_rubber','AquaticTerracottaEnamel','AquaticGuardGlass','botanical_soil']
materials={}
for role in roles:
 candidates=[m for m in palette if m and (m.name==role or m.name=='ASTRAEA_'+role or m.name.startswith(role+'.'))]
 assert candidates, 'No retained material: '+role
 materials[role]=candidates[0]
parts=json.loads((D/'PARTS.json').read_text(encoding='utf-8'));made=[]
for p in parts:
 mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata([xyz(v) for v in p['vertices']],[],p['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 mesh.materials.append(materials[p['material']]);uv=mesh.uv_layers.new(name='MaterialMetres')
 tile={'warm_stone':2,'warm_walnut':1,'champagne_metal':.5,'AquaticTerracottaEnamel':1,'dark_rubber':.5,'botanical_soil':1}.get(p['material'],2)
 for face in mesh.polygons:
  axis=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=axis]
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/tile,v[axes[1]]/tile)
 o=bpy.data.objects.new(p['name'],mesh);bpy.context.collection.objects.link(o);o['retained_material_role']=p['material'];o['contact_policy']='static';made.append(o)
# Preserve the original complete shaft shell/pan and boarding portal geometry.
source_objects=imported(original);retained=[]
old_root=xyz([5.6,0,228.6]);new_root=xyz([23.3,0,187.7])
lift_transform=Matrix.Translation(new_root)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-old_root)
portal_transform=Matrix.Translation(xyz([24.1,0,-24]))
for o in list(source_objects):
 if o.type!='MESH':continue
 name=o.name
 if 'BoardingLift_' in name and 'UpperLanding' not in name:
  o.parent=None;o.matrix_world=lift_transform@o.matrix_world;retained.append(o)
 elif 'Boarding_Portal_Post_' in name or 'Portal_Coral_Reveal_' in name or 'Boarding_Portal_Header' in name:
  o.parent=None;o.matrix_world=portal_transform@o.matrix_world;retained.append(o)
for o in retained:o['original_source']=original.relative_to(R).as_posix();o['contact_policy']='static'
erase(source_objects-set(retained));made+=retained
# The original portal members replace the provisional generic receiver pieces.
for o in list(made):
 if o.name.startswith('OriginalPortalReceiver_') or o.name=='PortalHeader':made.remove(o);bpy.data.objects.remove(o,do_unlink=True)
# Two original opal fixtures, unchanged source geometry. Position posts outside
# the boarding lane, grounded on the authored hanger/underbeam intersections.
source_objects=imported(original);lamps=[];light_rows=[]
for suffix,z,x in [('-218',195.6,25.7),('-211',188.25,25.7)]:
 old_z=218 if suffix=='-218' else 211;delta=xyz([x-1.62,0,z-old_z])
 for role in ['Backplate','Opal']:
  o=next(o for o in source_objects if o.name=='Aftmid_V2__Source_Lamp_'+role+'_'+suffix)
  world=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Translation(delta)@world;o['original_source']=original.relative_to(R).as_posix();o['contact_policy']='detail';lamps.append(o)
 light_rows.append({'source_fixture':'Aftmid_V2__Source_Lamp_Opal_'+suffix,'xyz':[x,58.3,z],'range':8,'energy':.55,'color':[1,.89,.72]})
erase(source_objects-set(lamps));made+=lamps
# Repeated plants share mesh/material data; original catalogue bytes unchanged.
placements=json.loads((D/'PLANTING_AND_SEATING.json').read_text(encoding='utf-8'));instances=[]
for file in sorted({p['file'] for group in placements.values() for p in group}):
 objects=imported(R/'Game/assets/models'/file);meshes=[o for o in objects if o.type=='MESH']
 for group,rows in placements.items():
  for p in [p for p in rows if p['file']==file]:
   transform=Matrix.Translation(xyz(p['xyz']))@Matrix.Rotation(p['yaw'],4,'Z')
   for i,source in enumerate(meshes):
    o=bpy.data.objects.new(p['name']+'_'+str(i),source.data);bpy.context.collection.objects.link(o)
    o.matrix_world=transform@source.matrix_world;o['catalogue_source']=file;o['contact_policy']='foliage_detail' if group=='plants' else 'static';made.append(o)
   instances.append(dict(p,category=group,source_meshes=len(meshes)))
 erase(objects)
bpy.context.view_layer.update()
assert all(o.data.uv_layers for o in made if o.name in {p['name'] for p in parts})
assert len(retained)==10, 'Expected five shaft and five original portal members'
N.mkdir(parents=True)
bpy.ops.object.select_all(action='DESELECT')
for o in made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'AquaticReceiving.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
text=bpy.data.texts.new('AQUATIC_STATUS');text.write('Unselected supported aquatic arrival construction. Original controllers and IDs retained. Guest greenery/seating included. Full guideway supports, installed component clearance, operating/visual/performance acceptance remain held. See repository receipt.')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(N/'AquaticReceiving_r002.blend'))
for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
receipt={'selected':False,'new_architectural_parts':len(parts)-3,'retained_shaft_portal_members':len(retained),'retained_fixture_members':len(lamps),'mesh_objects':len(made),'unique_meshes':len({o.data.as_pointer() for o in made}),'instances':instances,'lights':light_rows,'source_pins':pins,'material_roles':{k:v.name for k,v in materials.items()},'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [D/'AquaticReceiving.glb',N/'AquaticReceiving_r002.blend']}}
(D/'BUILD.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print('AQUATIC_NATIVE '+json.dumps({k:receipt[k] for k in ['selected','new_architectural_parts','retained_shaft_portal_members','mesh_objects','unique_meshes']}))
