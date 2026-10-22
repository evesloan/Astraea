"""Native architectural finish successor. Original geometry/allocations remain pinned."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; G=P.parent; R=G.parent
OLD=G/'night_garden_panoramic_suites_20261022'
N=R/'BlenderCatalogue/assets/night_garden_warm_interiors_20261022'
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
original=json.loads((OLD/'evidence/BUILD.json').read_text())
partition=json.loads((G/'data/architecture/night_garden_partition_20261021/index.json').read_text())['rooms']
packages=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())
receipt={'rooms':[],'inner_suites_unchanged':14,'allocations_changed':0,'hull_changes':0,'visual_accepted':False}
for row in original['rooms']:
 i=row['index'];source=R/row['native'];assert sha(source)==row['native_sha256']
 native=N/f'NG{i}_WarmInterior_r001.blend';out=P/'runtime'/f'NG{i}_WarmInterior_r001.glb'
 assert not native.exists() and not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];before={o.name:geometry(o)for o in meshes}
 room=next(r for r in packages['rooms']if r['allocation']['source_envelope_index']==i);a=room['allocation'];cz=sum(a['allocation_z'])/2;zl,zh=a['allocation_z'];quiet=any('Cocoon' in o.name for o in meshes)
 cream=mat('NGW_LinenPlaster',(.77,.69,.56),.86,pattern='plaster');ceiling=mat('NGW_WarmPorcelain',(.86,.8,.68),.72)
 wood=mat('NGW_HoneyWalnut',(.38,.205,.09),.48,pattern='timber');brass=mat('NGW_BrushedChampagne',(.55,.39,.19),.33,.65)
 cloth=mat('NGW_CocoonSage' if quiet else 'NGW_AquaticMineral',(.34,.40,.31)if quiet else(.28,.40,.39),.9,pattern='weave')
 stone=mat('NGW_WarmLimestone',(.53,.47,.37),.8,pattern='plaster');glow=mat('NGW_OpalCove', (1,.72,.38),.5,emission=2.2)
 for o in meshes:
  if 'PrivateViewPane' in o.name or 'ScreenedStreetGlass' in o.name:continue
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
 # Move the existing view-bay physical fixture together with its original light ID.
 old_light=room['lights'][1];new_light=[97.15,old_light['position'][1],cz]
 delta=[new_light[k]-old_light['position'][k]for k in range(3)]
 moved=[]
 for suffix in ['LightHousing_1','LightDiffuser_1']:
  o=bpy.data.objects[f'NG{i}_{suffix}'];o.location+=xyz(delta);moved.append(o.name)
 extras=[]
 def add(suffix,lo,hi,m,bevel=0):
  o=box(f'NGW_{i}_{suffix}',lo,hi,m,bevel);extras.append(o);return o
 # Layered wall furniture: full-height timber returns, lower panels and recessed joins.
 for side,z0,z1 in [('South',zl+.125,zl+.20),('North',zh-.20,zh-.125)]:
  add(side+'_LowWallPanel',[95.5,93.12,z0],[98.65,94.03,z1],wood,.018)
  add(side+'_PanelCap',[95.48,94.03,z0-.01],[98.67,94.08,z1+.01],brass,.008)
  add(side+'_BasePlinth',[91.65,93.01,z0],[98.68,93.12,z1+.025],wood,.014)
  add(side+'_WindowReturn',[98.51,94.08,z0],[98.65,96.46,z1+.035],wood,.018)
  c0,c1=(z0,z1+.19) if side=='South' else (z0-.19,z1)
  add(side+'_CeilingCove',[95.55,96.51,c0],[98.65,96.70,c1],ceiling,.025)
  add(side+'_CoveGlow',[95.61,96.68,c0+.03],[98.60,96.70,c1-.03],glow)
 # A broad ceiling plane with a real stepped reveal; all work below the existing ceiling.
 add('ViewBayCeilingInset',[95.55,96.69,zl+.42],[98.55,96.73,zh-.42],ceiling,.012)
 add('WindowHeadJoin',[98.50,96.46,cz-3.17],[98.79,96.73,cz+3.17],wood,.02)
 add('WindowHeadLight',[98.48,96.49,cz-2.9],[98.51,96.54,cz+2.9],glow,.008)
 add('WindowSillApron',[98.53,93.13,cz-3.17],[98.78,93.28,cz+3.17],wood,.018)
 # Broad floor border ties the existing outward seat and study bay into one sitting area.
 add('OutlookFloorInlay',[95.45,93.002,cz-3.0],[98.58,93.006,cz+3.0],cloth)
 assert all(geometry(o)==before[o.name]for o in meshes if o.name not in moved)
 for o in extras:
  lo,hi=bounds(o);assert lo[0]>=a['allocation_x'][0] and hi[0]<=a['allocation_x'][1]+.001
  assert lo[2]>=zl-.001 and hi[2]<=zh+.001 and lo[1]>=93-.001 and hi[1]<=96.74+.001,(o.name,lo,hi)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 exports=[]
 for batch in partition[row['model_file']]['always_resident_meshes']+partition[row['model_file']]['immutable_private_detail_meshes']:
  members=[bpy.data.objects[n]for n in batch['source_names']];bpy.ops.object.select_all(action='DESELECT')
  for o in members:o.select_set(True)
  bpy.context.view_layer.objects.active=members[0]
  if len(members)>1:bpy.ops.object.join()
  combined=bpy.context.object;combined.name=batch['node'];exports.append(combined)
 preserved=[bpy.data.objects[n]for n in row['new_meshes']]
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports+preserved+extras:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
 item=dict(row);item.update(native=str(native.relative_to(R)),native_sha256=sha(native),export=str(out.relative_to(G)),export_sha256=sha(out),predecessor_native=str(source.relative_to(R)),predecessor_native_sha256=sha(source),finish_meshes=[o.name for o in extras],finish_bounds={o.name:bounds(o)for o in extras},unchanged_geometry_count=len(meshes)-len(moved),moved_fixture_names=moved,view_light_name=old_light['name'],view_light_position=new_light,cove_light_position=[98.40,96.48,cz])
 receipt['rooms'].append(item);(P/'evidence/BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('WARM_INTERIOR_SAVED',i,len(extras),flush=True)
assert len(receipt['rooms'])==16
print('WARM_INTERIOR_PACKAGE_COMPLETE',flush=True)
