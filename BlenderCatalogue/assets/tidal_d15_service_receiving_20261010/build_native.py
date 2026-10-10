from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'D15_RECEIVING_PLAN.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/AST-STF-G3-003.blend'))
keep={q['name'] for q in P['retained_source_parts']}|{q['name'] for q in P['fixtures']}
for o in list(bpy.data.objects):
 if o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
assert sum(o.type=='MESH' for o in bpy.context.scene.objects)==64
for role in ['staff_bluegrey_paint','staff_white_paint']:
 names=['TidalStaffWall'+('Low' if role=='staff_bluegrey_paint' else 'High')+'_D15_-6_-63_'+str(i) for i in [0,1]]
 bpy.ops.object.select_all(action='DESELECT')
 for name in names:bpy.data.objects[name].select_set(True)
 bpy.context.view_layer.objects.active=bpy.data.objects[names[0]];bpy.ops.object.join();bpy.context.object.name='screen_wall_'+role+'_D15_-6_-63'
mats={o.data.materials[0].name:o.data.materials[0] for o in bpy.context.scene.objects if o.type=='MESH'}
faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
for p in P['new_parts']:
 b=p['aabb'];vs=[B((x,y,z)) for y in b[2:4] for z in b[4:6] for x in b[0:2]]
 me=bpy.data.meshes.new(p['name']);me.from_pydata(vs,[],faces);me.update();me.materials.append(mats[p['role']]);o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o)
 o['role']=p['role'];o['category']=p['category'];o['runtime_collision']=True;o['source_recipe']=P['catalogue_id']
 uv=me.uv_layers.new(name='MetricUV')
 for q in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda a:abs(q.normal[a]))]
  for li in q.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.3,v[axes[1]]*.3)
for i,z in enumerate([-493,-486]):
 for tail in ['Housing','Diffuser']:
  old=bpy.data.objects['TidalStaffLight'+tail+'_D15_3'];o=old.copy();o.data=old.data.copy();bpy.context.collection.objects.link(o);o.name='D15_LinkLight'+tail+'_'+str(i);o.location+=Vector(B((1,0,z+500)))
 marker=bpy.data.objects.new('D15_LinkLight_'+str(i),None);bpy.context.collection.objects.link(marker);marker.location=B((-44,95.995,z))
def save_export(native,export):
 bpy.data.orphans_purge(do_recursive=True)
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(W/native),compress=True)
 bpy.ops.export_scene.gltf(filepath=str(W/export),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 h=sha(W/export);nh=sha(W/native);bpy.ops.wm.open_mainfile(filepath=str(W/native));tmp=W/'_repeat.glb'
 bpy.ops.export_scene.gltf(filepath=str(tmp),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 assert sha(tmp)==h;tmp.unlink();assert sha(W/native)==nh
 return {'native':native,'native_sha256':nh,'export':export,'export_sha256':h,'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'fresh_native_repeat_identical':True}
corridor=save_export('TidalD15ServiceReceiver.blend','AST-RES-TIDAL_D15_service_receiving_r001.glb')
# Named successors preserve UVs/materials and every untouched triangle. Original GLBs remain unchanged.
bpy.ops.wm.read_factory_settings(use_empty=True)
for family,file in [('group3',R/'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-STF-G3-003.glb'),('house',R/'Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb')]:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(file));bpy.context.view_layer.update();wanted={p['mesh'] for p in P['cuts'] if p['source']==family}
 new=[o for o in bpy.data.objects if o not in before];worlds={o:o.matrix_world.copy() for o in new if o.name in wanted}
 for o in new:
  if o not in worlds:bpy.data.objects.remove(o,do_unlink=True)
 for o,m in worlds.items():o.parent=None;o.matrix_world=m
def clip(poly,ax,value,less):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[ax]<=value if less else a[ax]>=value;ib=b[ax]<=value if less else b[ax]>=value
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[ax])/(b[ax]-a[ax]);out.append(tuple(a[j]+(b[j]-a[j])*t for j in range(5)))
 return out
def minus(poly,cut):
 lo=cut['min'];hi=cut['max']
 if any(max(v[a] for v in poly)<lo[a]-1e-7 or min(v[a] for v in poly)>hi[a]+1e-7 for a in range(3)):return [poly],False
 rem=poly;pieces=[]
 for ax in range(3):
  outside=clip(rem,ax,lo[ax],True) if rem else []
  if len(outside)>=3:pieces.append(outside)
  rem=clip(rem,ax,lo[ax],False) if rem else []
  outside=clip(rem,ax,hi[ax],False) if rem else []
  if len(outside)>=3:pieces.append(outside)
  rem=clip(rem,ax,hi[ax],True) if rem else []
 area=sum((Vector(rem[i][:3])-Vector(rem[0][:3])).cross(Vector(rem[i+1][:3])-Vector(rem[0][:3])).length/2 for i in range(1,len(rem)-1)) if len(rem)>=3 else 0
 return (pieces,True) if area>1e-9 else ([poly],False)
changes=[]
for spec in P['cuts']:
 o=bpy.data.objects[spec['mesh']];old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;vs=[];fs=[];uvs=[];mis=[];affected=0;uncut=0
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):
   v=o.matrix_world@old.vertices[vi].co;tc=uv.data[li].uv if uv else (0,0);poly.append((v.x,v.z,-v.y,tc[0],tc[1]))
  pieces,hit=minus(poly,spec['cut']);affected+=int(hit);uncut+=int(not hit)
  for pp in pieces:
   for i in range(1,len(pp)-1):
    q=[pp[0],pp[i],pp[i+1]]
    if (Vector(q[1][:3])-Vector(q[0][:3])).cross(Vector(q[2][:3])-Vector(q[0][:3])).length<1e-9:continue
    k=len(vs);vs.extend(B(v) for v in q);uvs.extend(v[3:] for v in q);fs.append((k,k+1,k+2));mis.append(tri.material_index)
 me=bpy.data.meshes.new(spec['mesh']+'_D15Opening');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 lay=me.uv_layers.new(name='RetainedInterpolatedUV')
 for p,mi in zip(me.polygons,mis):
  p.material_index=mi
  for li in p.loop_indices:lay.data[li].uv=uvs[me.loops[li].vertex_index]
 o.data=me;o.matrix_world.identity();o['replacement_of']=spec['mesh'];o['source_recipe']=P['catalogue_id'];assert affected>0,spec['mesh']
 changes.append({'mesh':spec['mesh'],'triangles_before':len(old.loop_triangles),'triangles_after':len(fs),'affected':affected,'untouched_original_triangles':uncut})
patch=save_export('TidalD15NamedGuardPatch.blend','TidalD15NamedGuardPatch.glb')
assert all(sha(R/p)==h for p,h in P['source_pins'].items())
result={'status':'PASS','blender_version':bpy.app.version_string,'corridor':corridor,'patch':patch,'named_derivatives':changes,'source_pins_unchanged':True,'no_upper_shaft_installed':True}
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print('D15_NATIVE_PASS',json.dumps(result),flush=True)
