"""Local editable profile helpers, adapted from the unchanged original botanical planter generator.
No pre-existing source outputs are needed for rebuild. Materials supplied by the author.
"""
import bpy,bmesh,math,json
MATS={}
def sweep(name,stations,profile,role,bevel=.0007,grain='length'):
 verts=[(x+ty*d,y-tx*d,z) for x,y,tx,ty,s in stations for d,z in profile];n=len(profile)
 faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(stations)-1) for j in range(n)]
 faces += [tuple(reversed(range(n))),tuple((len(stations)-1)*n+j for j in range(n))]
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role])
 ob['material_role']=role;ob['profile_depth_height_m']=json.dumps(profile);ob['uv_grain']='V follows '+grain
 ob['design_method']='Original intentional metric profile sweep, script-assisted editable mesh'
 uv=me.uv_layers.new(name='metric_material_uv');scale=tuple(MATS[role].get('meters_per_tile_uv',[1,1]))
 perimeter=[0]
 for p,q in zip(profile,profile[1:]):perimeter.append(perimeter[-1]+math.dist(p,q))
 total=perimeter[-1]+math.dist(profile[-1],profile[0])
 for p in me.polygons:
  edge=p.index%n
  for li in p.loop_indices:
   k,j=divmod(me.loops[li].vertex_index,n);d,z=profile[j];s=stations[k][4]
   if p.index>=len(faces)-2:pair=(d/scale[0],z/scale[1])
   elif grain=='vertical':pair=(s/scale[0],(z if abs(profile[(edge+1)%n][1]-profile[edge][1])>.01 else d)/scale[1])
   else:pair=((total if edge==n-1 and j==0 else perimeter[j])/scale[0],s/scale[1])
   uv.data[li].uv=pair
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if bevel:
  m=ob.modifiers.new('Editable eased arris','BEVEL');m.width=bevel;m.segments=1;m.limit_method='ANGLE';m.angle_limit=math.radians(42)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=30
 return ob


def measured(obs):
 dg=bpy.context.evaluated_depsgraph_get();verts=[];tri=0
 for ob in obs:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);verts += [ob.matrix_world@v.co for v in me.vertices];eo.to_mesh_clear()
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 return lo,hi,[b-a for a,b in zip(lo,hi)],tri

def export(obs,p,markers=()):
 dg=bpy.context.evaluated_depsgraph_get();groups={};repairs=0
 for src in obs:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for other in list(me.uv_layers):
   if other!=active:me.uv_layers.remove(other)
  active.name='metric_material_uv';active.active_render=True
  me.calc_loop_triangles();repair=set();sc=tuple(MATS[src['material_role']].get('meters_per_tile_uv',[1,1]))
  for tr in me.loop_triangles:
   a,b,c=[active.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:repair.add(tr.polygon_index)
  for idx in repair:
   face=me.polygons[idx];axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in face.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(v[axes[0]]/sc[0],v[axes[1]]/sc[1])
  repairs+=len(repair)
  ob=bpy.data.objects.new('runtime_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
 runtime=[]
 for role,parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in parts:ob.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name='ASTRAEA_planted_seat_'+role;ob['material_role']=role;ob['semantic_parts']=json.dumps([o.name for o in obs if o['material_role']==role]);runtime.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in runtime+list(markers):ob.select_set(True)
 bpy.context.view_layer.objects.active=runtime[0]
 bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)
 return repairs

