from pathlib import Path
import bpy,json,hashlib,struct,math
from mathutils import Vector
D=Path(__file__).resolve().parent;S=D/'retained_source';P=S/'BlenderCatalogue/assets/group5_completion_20261011';old=P/'source/thread_stock/thread_stock_repair_r004.blend';oldglb=P/'exports/thread_stock/thread_stock_repair_r004.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={str(p.relative_to(D)):sha(p)for p in[old,oldglb]};native=D/'native/thread_stock_repair_r005.blend';export=D/'import/Game/assets/models/group5/thread_stock/thread_stock_repair_r005.glb';assert not native.exists()and not export.exists();native.parent.mkdir(parents=True,exist_ok=True);export.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(old));bpy.context.preferences.filepaths.save_version=0

def meshhash(m):
 h=hashlib.sha256()
 for v in m.vertices:h.update(struct.pack('<3f',*v.co))
 for f in m.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
 for layer in m.uv_layers:
  for v in layer.data:h.update(struct.pack('<2f',*v.uv))
 return h.hexdigest()
before={o.name:{'mesh':meshhash(o.data),'matrix':[list(r)for r in o.matrix_world]}for o in bpy.context.scene.objects if o.type=='MESH'};changed=[]
for o in bpy.context.scene.objects:
 if o.name.startswith(('East_CeilingCove_','East_CoveReveal_','East_Skirting_')):o.location.x-=.08;changed.append(o.name)
assert len(changed)==6
# Cut only the candidate's 2mm applied ceiling, retaining both original fixture housings and source ceiling.
o=bpy.data.objects['Group5VisualFinish_ThreadCeiling'];m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active;triangles=[];holes=[(39.63,40.37,-227.29,-226.71),(39.63,40.37,-209.29,-208.71)];origin=Vector((8,52.5,-216));gd=lambda v:Vector((v.x,v.z,-v.y))+origin;bl=lambda v:Vector((v.x-origin.x,-(v.z-origin.z),v.y-origin.y));normal_matrix=o.matrix_world.to_3x3().inverted().transposed()
def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k].lerp(e[k],t)for k in['p','n','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out
def subtract(poly,box):
 pieces=[];inside=poly
 for axis,plane,less in[(0,box[0],False),(0,box[1],True),(2,box[2],False),(2,box[3],True)]:
  outside=clip(inside,axis,plane,not less)
  if len(outside)>=3:pieces.append(outside)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
for t in m.loop_triangles:
 polys=[[{'p':gd(o.matrix_world@m.vertices[vi].co),'n':normal_matrix@m.corner_normals[li].vector,'uv':uv.data[li].uv.copy()}for li,vi in zip(t.loops,t.vertices)]]
 for hole in holes:polys=[q for poly in polys for q in subtract(poly,hole)]
 for poly in polys:
  for i in range(1,len(poly)-1):triangles.append([poly[0],poly[i],poly[i+1]])
# Editable painted cut edges on the thin applied plate.
for x0,x1,z0,z1 in holes:
 for a,b in[((x0,z0),(x1,z0)),((x1,z0),(x1,z1)),((x1,z1),(x0,z1)),((x0,z1),(x0,z0))]:
  ps=[Vector((a[0],56.196,a[1])),Vector((b[0],56.196,b[1])),Vector((b[0],56.198,b[1])),Vector((a[0],56.198,a[1]))];normal=bl(ps[1])-bl(ps[0]);normal=normal.cross(bl(ps[2])-bl(ps[0])).normalized()
  for ids in[(0,1,2),(0,2,3)]:triangles.append([{'p':ps[i],'n':normal,'uv':Vector((ps[i].x,ps[i].z))}for i in ids])
flat=[v for tri in triangles for v in tri];new=bpy.data.meshes.new(o.name+'_exact_housing_clearances_r005');inv=o.matrix_world.inverted();new.from_pydata([inv@bl(v['p'])for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);new.update()
for material in m.materials:new.materials.append(material)
u=new.uv_layers.new(name=uv.name)
for i,v in enumerate(flat):u.data[i].uv=v['uv']
for p in new.polygons:p.use_smooth=True
new.normals_split_custom_set([v['n'].normalized()for v in flat]);o.data=new;changed.append(o.name);bpy.context.view_layer.update();unchanged=0
for name,row in before.items():
 obj=bpy.data.objects[name]
 if name not in changed:assert meshhash(obj.data)==row['mesh']and[list(r)for r in obj.matrix_world]==row['matrix'];unchanged+=1
 elif name!='Group5VisualFinish_ThreadCeiling':assert meshhash(obj.data)==row['mesh']
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True);nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=D/'FRESH_REEXPORT_r005.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True);assert sha(repeat)==esha and sha(native)==nsha;assert all(sha(D/p)==v for p,v in pins.items());receipt={'status':'PASS_NATIVE_MINIMAL_SUCCESSOR_CANDIDATE_NOT_ADOPTED','native_sha256':nsha,'model_sha256':esha,'parent_pins':pins,'changed_meshes':changed,'six_east_trim_meshes_rigid_delta_xyz':[-.08,0,0],'candidate_ceiling_housing_cutouts_world_x0_x1_z0_z1':holes,'all_other_native_mesh_geometry_uv_and_transforms_unchanged':unchanged,'fresh_reexport_byte_identical':True,'r002_still_selected':True,'runtime_contact_route_and_visual_acceptance_pending':True};(D/'NATIVE_SUCCESSOR_r005.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_THREAD_R005_NATIVE',unchanged,len(changed),esha)
