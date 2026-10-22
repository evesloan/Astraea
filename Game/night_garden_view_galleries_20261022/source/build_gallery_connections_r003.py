"""Named 16-outer-suite window successor; preserves 14 existing oval atrium views.
Never writes original native, room, floor-owner or hull files.
"""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
N=R/'BlenderCatalogue/assets/night_garden_view_galleries_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in json.loads((P/'evidence/INPUT_PINS.json').read_text()).items():assert sha(R/p)==h,p
package=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())
index=json.loads((G/'data/architecture/night_garden_partition_20261021/index.json').read_text())['rooms']
receipt=json.loads((P/'evidence/BUILD_r002.json').read_text());receipt['galleries']=[]
def xyz(v):return Vector((v[0],-v[2],v[1]))
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.45;bs.inputs['Alpha'].default_value=color[3]
 if color[3]<1:m.surface_render_method='DITHERED'
 return m
def box(name,lo,hi,mat=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz([(a+b)/2 for a,b in zip(lo,hi)]));o=bpy.context.object;o.name=name
 o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 o['runtime_collision']=True;o['construction_role']='view_gallery_architecture';return o
def fingerprint(o):
 return hashlib.sha256(repr(([list(r)for r in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],[[list(u.uv)for u in l.data]for l in o.data.uv_layers])).encode()).hexdigest()
def export(path,objects):
 assert not path.exists();bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
for row in []:
 i=row['allocation']['source_envelope_index'];a=row['allocation'];record=index[row['model_file']]
 if a['allocation_x'][0]<84:continue
 batch=next(b for b in record['always_resident_meshes'] if any('OpaqueRearBoundary'in n for n in b['source_names']))
 source=R/'BlenderCatalogue'/row['native_source'];assert sha(source)==row['native_source_sha256']
 native=N/f'NightGardenViewShell_{i}_r002.blend';out=P/'runtime'/f'NightGardenViewShell_{i}_r002.glb';assert not native.exists() and not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 members=[bpy.data.objects[n]for n in batch['source_names']];rear=next(o for o in members if 'OpaqueRearBoundary'in o.name)
 unchanged={o.name:fingerprint(o)for o in members if o!=rear}
 x0,x1=a['allocation_x'];z0,z1=a['allocation_z'];cz=(z0+z1)/2;outboard=x0>84;rear_x=x1 if outboard else x0;inside=-1 if outboard else 1
 cutter=box('WindowCut',[rear_x-.4,94.05,cz-2.3],[rear_x+.4,96.25,cz+2.3])
 bpy.context.view_layer.objects.active=rear;mod=rear.modifiers.new('ResidentViewOpening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 wood=material('NVG_WarmWalnut',(.16,.085,.035,1));glass=material('NVG_PrivateViewGlazing',(.19,.34,.31,.13));extra=[]
 for suffix,lo,hi in [('Sill',[rear_x-.09,93.91,cz-2.45],[rear_x+.09,94.06,cz+2.45]),('Head',[rear_x-.09,96.24,cz-2.45],[rear_x+.09,96.39,cz+2.45]),('Left',[rear_x-.09,94.06,cz-2.45],[rear_x+.09,96.24,cz-2.30]),('Right',[rear_x-.09,94.06,cz+2.30],[rear_x+.09,96.24,cz+2.45])]:extra.append(box(f'NVG_{i}_ViewFrame_{suffix}',lo,hi,wood))
 pane=box(f'NVG_{i}_PrivateViewPane',[rear_x-.012,94.05,cz-2.3],[rear_x+.012,96.25,cz+2.3],glass);pane['private_view_sign']=inside;pane['private_view_plane_x']=rear_x;pane['material_role']='private_view_glazing';extra.append(pane)
 assert all(fingerprint(bpy.data.objects[n])==h for n,h in unchanged.items())
 keep=members+extra
 for o in list(bpy.context.scene.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in members:o.select_set(True)
 bpy.context.view_layer.objects.active=members[0];bpy.ops.object.join();combined=bpy.context.object;combined.name=batch['node']
 export(out,[combined]+extra)
 receipt['rooms'].append({'model_file':row['model_file'],'index':i,'runtime_id':a['proposed_runtime_id'],'batch':batch['node'],'unchanged_wall_members':unchanged,'rear_x':rear_x,'interior_sign':inside,'window_center_z':cz,'window_clear_width':4.6,'window_clear_height':2.2,'native':str(native.relative_to(R)),'native_sha256':sha(native),'export':str(out.relative_to(G)),'export_sha256':sha(out)})
 print('VIEW_SHELL',i,flush=True)
# Four actual shared interiors and two public terminal connections, inside retained hull.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
floor=material('NVG_WarmStone',(.43,.39,.31,1));wood=material('NVG_WalnutStructure',(.13,.075,.035,1));ivory=material('NVG_Ivory',(.68,.66,.55,1));glass=material('NVG_PublicGardenGlass',(.26,.39,.34,.16));soil=material('NVG_PlanterSoil',(.065,.045,.025,1))
objects=[];lights=[]
def add(name,lo,hi,mat):
 o=box(name,lo,hi,mat);objects.append(o);return o
def beam(name,a,b,width,mat):
 va,vb=xyz(a),xyz(b);mid=(va+vb)/2;bpy.ops.mesh.primitive_cube_add(size=1,location=mid);o=bpy.context.object;o.name=name;o.dimensions=(width,width,(vb-va).length);o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o['runtime_collision']=True;objects.append(o);return o
for sign in [-1,1]:
 za,zb=sorted([sign*38.4,sign*97.4])
 for side,(xa,xb) in [(1,(98.95,105.8))]:
  label=f'NVG_Gallery_{sign}_{side}';receipt['galleries'].append({'name':label,'bounds':[[xa,92.44,za],[xb,97.26,zb]],'floor_y':93,'purpose':'shared internal planted residential view gallery','private_room_overlap':False})
  add(label+'_Floor',[xa,92.76,za],[xb,93,zb],floor)
  for x in [xa+.1,xb-.1]:add(label+'_LongBearing_'+str(x),[x-.1,92.44,za],[x+.1,92.76,zb],wood)
  outer=xa if side==0 else xb
  add(label+'_OuterSill',[outer-.06,93,za],[outer+.06,93.65,zb],wood);add(label+'_OuterGlass',[outer-.04,93.65,za],[outer+.04,96.65,zb],glass)
  add(label+'_ForeCap',[xa,93,min(sign*38.4-.06,sign*38.4+.06)],[xb,96.65,max(sign*38.4-.06,sign*38.4+.06)],glass)
  for j in range(9):
   z=za+(zb-za)*j/8
   add(label+f'_CrossBearing_{j}',[xa-.08,92.44,z-.08],[xb+.08,92.76,z+.08],wood)
   for x in [xa,xb]:add(label+f'_Column_{j}_{x}',[x-.06,93,z-.06],[x+.06,96.65,z+.06],wood)
   points=[(xa+(xb-xa)*k/4,96.65+.55*math.sin(math.pi*k/4),z)for k in range(5)]
   for k in range(4):beam(label+f'_RoofRib_{j}_{k}',points[k],points[k+1],.12,wood)
  for k in range(4):
   xlo=xa+(xb-xa)*k/4;xhi=xa+(xb-xa)*(k+1)/4;y=96.65+.55*math.sin(math.pi*(k+.5)/4)
   add(label+f'_RoofPanel_{k}',[xlo,y,za],[xhi,y+.06,zb],ivory)
  for j in range(8):
   z=za+3.7+j*7.2;cx=60.5 if side==0 else 104
   add(label+f'_GardenBed_{j}',[cx-1.15,93,z-1.6],[cx+1.15,93.38,z+1.6],wood);add(label+f'_Soil_{j}',[cx-1.08,93.38,z-1.53],[cx+1.08,93.40,z+1.53],soil)
   lx=(xa+xb)/2;lights.append([lx,96.45,z]);add(label+f'_Fixture_{j}',[lx-.22,96.45,z-.22],[lx+.22,96.6,z+.22],ivory)
 for j,(xa,xb) in enumerate([(81.95,86.05),(86.05,105.8)]):
  zlo,zhi=sorted([sign*97.4,sign*101.5]);add(f'NVG_EndLink_{sign}_{j}',[xa,92.76,zlo],[xb,93,zhi],floor);add(f'NVG_EndRoof_{sign}_{j}',[xa,96.9,zlo],[xb,97.1,zhi],ivory)
  for z in [zlo+.1,zhi-.1]:add(f'NVG_EndBearing_{sign}_{j}_{z}',[xa,92.44,z-.1],[xb,92.76,z+.1],wood)
 zz=sign*101.5;add(f'NVG_EndBoundary_{sign}',[81.95,93,zz-.06],[105.86,96.9,zz+.06],glass)
 for x in [81.95,105.8]:
  zlo,zhi=sorted([sign*97.4,sign*101.5]);add(f'NVG_EndSide_{sign}_{x}',[x-.06,93,zlo],[x+.06,96.9,zhi],glass)
# Retained authored planting and benches at unchanged scale, in the new public interior.
for asset in ['AST-BOT-001.glb','AST-FUR-001.glb']:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(G/'assets/models'/asset));templates=list(set(bpy.context.scene.objects)-before)
 for sign in [-1,1]:
  for side,cx in [(1,104.)]:
   for j in range(8):
    z=sign*(42.1+j*7.2);offset=xyz((cx,93.4,z) if asset.startswith('AST-BOT') else (cx,93,z+2.25))
    for template in templates:
     ob=template.copy();ob.data=template.data;bpy.context.collection.objects.link(ob);ob.parent=None;ob.matrix_world=template.matrix_world.copy();ob.location+=offset;ob.name=f'NVG_{sign}_{side}_{j}_'+template.name;ob['runtime_collision']=True;objects.append(ob)
 for ob in templates:bpy.data.objects.remove(ob,do_unlink=True)
native=N/'NightGardenSharedViewGalleries_r003.blend';assert not native.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
out=P/'runtime/SharedViewGalleries_r003.glb';export(out,objects)
receipt['gallery_native']=str(native.relative_to(R));receipt['gallery_native_sha256']=sha(native);receipt['gallery_export']=str(out.relative_to(G));receipt['gallery_export_sha256']=sha(out);receipt['lights']=lights
(P/'evidence/BUILD_r003.json').write_text(json.dumps(receipt,indent=2)+'\n');print('VIEW_PACKAGE_COMPLETE 16 windows,2 shared interiors,2 terminal links;14 oval atrium views unchanged',flush=True)
