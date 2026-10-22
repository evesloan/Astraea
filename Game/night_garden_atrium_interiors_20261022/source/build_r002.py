"""Native architectural finish successor. Original geometry/allocations remain pinned."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]; G=P.parent; R=G.parent
OLD=G/'night_garden_panoramic_suites_20261022'
N=R/'BlenderCatalogue/assets/night_garden_atrium_interiors_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(p):return Vector((p[0],-p[2],p[1]))
def bounds(o):
 bpy.context.view_layer.update();v=[o.matrix_world@Vector(c)for c in o.bound_box];v=[(p.x,p.z,-p.y)for p in v]
 return [[min(p[k]for p in v)for k in range(3)],[max(p[k]for p in v)for k in range(3)]]
def geometry(o):return hashlib.sha256(repr(([list(r)for r in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])).encode()).hexdigest()
def mat(name,color,rough=.6,metal=0,emission=0,pattern=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
 if pattern:
  image=bpy.data.images.new(name+'_original_pattern',width=128,height=128);pixels=[]
  for y in range(128):
   for x in range(128):
    if pattern=='timber':v=1+.09*math.sin(x*.3+math.sin(y*.05))+.035*math.sin(x*1.7+y*.03)
    elif pattern=='weave':v=1+.025*((x%4<2)-(y%4<2))
    else:v=1+.018*math.sin(x*1.7+y*2.3)
    pixels.extend([min(1,c*v)for c in color]+[1])
  image.pixels=pixels;image.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 return m
def uv(o):
 layer=o.data.uv_layers.active or o.data.uv_layers.new(name='FinishUV')
 for poly in o.data.polygons:
  n=poly.normal;skip=max(range(3),key=lambda k:abs(n[k]));axes=[k for k in range(3)if k!=skip]
  for li in poly.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=(co[axes[0]]*.4,co[axes[1]]*.4)
def box(name,lo,hi,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz([(a+b)/2 for a,b in zip(lo,hi)]));o=bpy.context.object;o.name=name
 o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material);uv(o)
 if bevel:
  modifier=o.modifiers.new('CraftedEdge','BEVEL');modifier.width=bevel;modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
 return o
partition=json.loads((G/'data/architecture/night_garden_partition_20261021/index.json').read_text())['rooms']
package=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())
for f,h in json.loads((G/'night_garden_panoramic_suites_20261022/evidence/INPUT_PINS.json').read_text()).items():assert sha(R/f)==h
receipt=json.loads((P/'evidence/BUILD.json').read_text());receipt['rooms']=[r for r in receipt['rooms'] if r['index'] not in [416,440]]
def group_bounds(items):
 bs=[bounds(o)for o in items];return [[min(b[0][k]for b in bs)for k in range(3)],[max(b[1][k]for b in bs)for k in range(3)]]
for room in package['rooms']:
 a=room['allocation'];i=a['source_envelope_index']
 if i not in [416,440]:continue
 source=R/'BlenderCatalogue'/room['native_source'];assert sha(source)==room['native_source_sha256']
 native=N/f'NG{i}_AtriumInterior_r002.blend';out=P/'runtime'/f'NG{i}_AtriumInterior_r002.glb';assert not native.exists() and not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];before={o.name:geometry(o)for o in meshes}
 zl,zh=a['allocation_z'];cz=(zl+zh)/2;quiet=room['source_profile'].startswith(('quiet','paired_cocoons','parallel_cocoons','staggered_cocoons'))
 cream=mat('NGA_LinenPlaster',(.77,.69,.56),.86,pattern='plaster');ceiling=mat('NGA_WarmPorcelain',(.86,.8,.68),.72)
 wood=mat('NGA_HoneyWalnut',(.38,.205,.09),.48,pattern='timber');brass=mat('NGA_BrushedChampagne',(.55,.39,.19),.33,.65)
 cloth=mat('NGA_QuietSage' if quiet else 'NGA_AquaticMineral',(.34,.40,.31)if quiet else(.28,.40,.39),.9,pattern='weave')
 stone=mat('NGA_WarmLimestone',(.53,.47,.37),.8,pattern='plaster');glow=mat('NGA_OpalCove',(1,.72,.38),.5,emission=2.2)
 for o in meshes:
  if 'Glass' in o.name:continue
  changed=False
  for slot in o.material_slots:
   if not slot.material:continue
   name=slot.material.name.lower();replacement=None
   if 'ivory' in name:replacement=ceiling if 'Ceiling' in o.name or 'Roof' in o.name else cream
   elif 'walnut' in name:replacement=wood
   elif 'weave' in name:replacement=cloth
   elif 'warm_stone' in name:replacement=stone
   elif 'champagne' in name:replacement=brass
   elif 'opal_glow' in name:replacement=glow
   if replacement:slot.material=replacement;changed=True
  if changed:uv(o)
 # Relocate complete rest-support/enclosure assemblies, preserving each original slot.
 moved=[];rest_moves=[]
 for j,rest in enumerate(room['rest_adjustments']):
  group=[o for o in meshes if o.name.startswith(f'NG{i}_{rest["component_name"]}__')or o.name.startswith(f'NG{i}_Cocoon{j+1:02d}_')]
  assert group,(i,rest['component_name'])
  b=group_bounds(group);dx=min(2.30,76.35-b[1][0]);assert dx>1.0,(i,b)
  for o in group:o.location+=xyz((dx,0,0))
  moved+=group;rest_moves.append({'component_name':rest['component_name'],'slot_id':rest['slot_id'],'delta':[dx,0,0]})
 rest_bounds=group_bounds(moved);assert rest_bounds[0][0]>72.35 and rest_bounds[1][0]<76.43
 study=[o for o in meshes if any(o.name.startswith(f'NG{i}_{n}__')for n in ['LibraryStudyEdge','SupportedOpenFolio','HousedStudyTaskFixture','DayReadingChair'])];assert study
 b=group_bounds(study);center=[(b[0][k]+b[1][k])/2 for k in range(3)];study_z=cz+(1.15 if cz>0 else -1.15)
 target=[70.65,center[1],study_z];pose=Matrix.Translation(xyz(target))@Matrix.Rotation(-math.pi/2,4,'Z')@Matrix.Translation(-xyz(center))
 for o in study:o.matrix_world=pose@o.matrix_world
 b=group_bounds(study);assert b[0][0]>69.3 and b[1][0]<72.2 and b[0][2]>zl+.12 and b[1][2]<zh-.12,(i,b)
 old_light=room['lights'][1];new_light=[70.85,old_light['position'][1],cz];delta=[new_light[k]-old_light['position'][k]for k in range(3)];fixture=[]
 for suffix in ['LightHousing_1','LightDiffuser_1']:
  o=bpy.data.objects[f'NG{i}_{suffix}'];o.location+=xyz(delta);fixture.append(o)
 extras=[]
 def add(suffix,lo,hi,m,bevel=0):
  o=box(f'NGA_{i}_{suffix}',lo,hi,m,bevel);extras.append(o);return o
 # Preserve the full original oval aperture and thick reveal; add coherent facing joinery.
 for side,z0,z1 in [('South',zl+.125,zl+.20),('North',zh-.20,zh-.125)]:
  add(side+'_LowPanel',[69.42,93.12,z0],[72.3,94.03,z1],wood,.018)
  add(side+'_PanelCap',[69.40,94.03,z0-.01],[72.32,94.08,z1+.01],brass,.008)
  add(side+'_BasePlinth',[69.4,93.01,z0],[76.2,93.12,z1+.02],wood,.014)
  c0,c1=(z0,z1+.19)if side=='South'else(z0-.19,z1)
  add(side+'_CeilingCove',[69.4,96.51,c0],[72.4,96.70,c1],ceiling,.025)
  add(side+'_CoveGlow',[69.45,96.68,c0+.03],[72.35,96.70,c1-.03],glow)
 add('ViewBayCeilingInset',[69.4,96.69,zl+.42],[72.4,96.73,zh-.42],ceiling,.012)
 add('OvalHeadJoin',[69.22,96.44,cz-3.12],[69.5,96.73,cz+3.12],wood,.02)
 add('OvalHeadLight',[69.5,96.49,cz-2.8],[69.53,96.54,cz+2.8],glow,.008)
 add('OutlookFloorInlay',[69.45,93.002,cz-3.0],[72.35,93.006,cz+3.0],cloth)
 seat_z=cz+(-2.05 if study_z>cz else 2.05)
 for suffix,lo,hi,m in [('Base',[70.65,93,seat_z-.55],[71.5,93.32,seat_z+.55],wood),('Cushion',[70.63,93.32,seat_z-.53],[71.45,93.48,seat_z+.53],cloth),('Back',[71.4,93.32,seat_z-.58],[71.55,93.95,seat_z+.58],cream)]:add('ViewSeat_'+suffix,lo,hi,m,.025)
 changed={o.name for o in moved+study+fixture};assert all(geometry(o)==before[o.name]for o in meshes if o.name not in changed)
 for o in moved+study+fixture+extras:
  lo,hi=bounds(o);assert lo[0]>=69.05-.001 and hi[0]<=81.95+.001 and lo[2]>=zl-.001 and hi[2]<=zh+.001,(i,o.name,lo,hi)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 exports=[]
 for batch in partition[room['model_file']]['always_resident_meshes']+partition[room['model_file']]['immutable_private_detail_meshes']:
  members=[bpy.data.objects[n]for n in batch['source_names']];bpy.ops.object.select_all(action='DESELECT')
  for o in members:o.select_set(True)
  bpy.context.view_layer.objects.active=members[0]
  if len(members)>1:bpy.ops.object.join()
  combined=bpy.context.object;combined.name=batch['node'];exports.append(combined)
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports+extras:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
 receipt['rooms'].append({'index':i,'model_file':room['model_file'],'room_id':a['proposed_runtime_id'],'rest_slot_ids':a['proposed_rest_slot_ids'],'rest_moves':rest_moves,'rest_bounds':rest_bounds,'study_bounds':b,'view_stance':[69.85,94.65,seat_z],'seated_eye':[71.05,94.15,seat_z],'finish_meshes':[o.name for o in extras],'source_native':str(source.relative_to(R)),'source_sha256':sha(source),'native':str(native.relative_to(R)),'native_sha256':sha(native),'export':str(out.relative_to(G)),'export_sha256':sha(out),'changed_members':sorted(changed),'unchanged_geometry_count':len(meshes)-len(changed),'view_light_name':old_light['name'],'view_light_position':new_light,'cove_light_position':[69.62,96.48,cz]})
 (P/'evidence/BUILD_R002.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ATRIUM_INTERIOR_SAVED',i,flush=True)
assert len(receipt['rooms'])==14
print('ATRIUM_INTERIORS_COMPLETE 14',flush=True)
