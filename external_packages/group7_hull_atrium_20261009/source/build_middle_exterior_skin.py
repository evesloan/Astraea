"""Separate middle-body opaque/glazed skin fields, preserving room-side owners."""
import bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';L=P/'dependencies/canonical_9d6f85'
points=[Vector(q) for q in json.loads((D/'Game/data/hull_envelope.json').read_text())['plan_xz_m']]
normals=[]
for i,a in enumerate(points):
 t=(points[(i+1)%len(points)]-a).normalized();n=Vector((t.y,-t.x));normals.append(n if n.dot(-a)>0 else -n)
def inset(d):
 out=[]
 for i,a in enumerate(points):
  n0,n1=normals[i-1],normals[i];c0,c1=n0.dot(a)+d,n1.dot(a)+d;det=n0.x*n1.y-n0.y*n1.x
  out.append(Vector(((c0*n1.y-n0.y*c1)/det,(n0.x*c1-c0*n1.x)/det)))
 return out
outer,inner=inset(.02),inset(.18);parts=[];geo=[];schedule=[];exports=[]
export_only='--export-only' in sys.argv
if export_only:bpy.ops.wm.open_mainfile(filepath=str(P/'source/natives/G7_MiddleExteriorSkin_r001.blend'),load_ui=False)
else:bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role,tex in [('spandrel','staff/staff_bluegrey_paint.png'),('joint','staff/staff_zinc.png')]:
 m=bpy.data.materials.new('G7_skin_'+role);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.75;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(L/'BlenderCatalogue/materials'/tex));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('G7_skin_clear_glazing');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.53,.72,.77,.24);p.inputs['Alpha'].default_value=.24;p.inputs['Roughness'].default_value=.12;p.inputs['Transmission Weight'].default_value=.45;m.surface_render_method='DITHERED';mats['glazing']=m
def prism(name,edge,u0,u1,y0,y1,role):
 assert 0<=u0<u1<=1 and y0<y1
 a,b=outer[edge],outer[(edge+1)%len(points)];c,d=inner[edge],inner[(edge+1)%len(points)]
 poly=[a.lerp(b,u0),a.lerp(b,u1),c.lerp(d,u1),c.lerp(d,u0)]
 world=[(q.x,y,q.y) for y in (y0,y1) for q in poly];vertices=[(x,-z,y) for x,y,z in world]
 if export_only:
  o=bpy.context.scene.objects.get(name);assert o is not None,name;actual=[tuple(o.matrix_world@v.co) for v in o.data.vertices];assert len(actual)==len(vertices);assert max((Vector(a)-Vector(b)).length for a,b in zip(actual,vertices))<1e-4,name
  geo.append({'object':name,'edge':edge,'role':role,'uv_edge_interval':[u0,u1],'y_interval':[y0,y1],'vertices_world_xyz':[(x,z,-y) for x,y,z in actual],'triangles':12});return
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],[(3,2,1,0),(4,5,6,7)]+[(k,(k+1)%4,(k+1)%4+4,k+4) for k in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[role]);o['edge']=edge;o['source_role']=role;o['contact_category']='solid_glazing' if role=='glazing' else 'solid_skin';o['operating_window']=False;parts.append(o)
 uv=me.uv_layers.new(name='MetreScaled');t=(b-a).normalized()
 for f in me.polygons:
  for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(Vector((q.x,-q.y)).dot(t),q.z)
 me.calc_loop_triangles();geo.append({'object':name,'edge':edge,'role':role,'uv_edge_interval':[u0,u1],'y_interval':[y0,y1],'vertices_world_xyz':world,'triangles':len(me.loop_triangles)})
datums=[16.5,21,27,35.5,44,52.5,61]
for edge,a in enumerate(points):
 b=points[(edge+1)%len(points)];length=(b-a).length;count=math.ceil(length/12);stations=[0]+[(k+.5)/count for k in range(count)]+[1]
 for level,(y0,y1) in enumerate(zip(datums,datums[1:])):
  for bay,(u0,u1) in enumerate(zip(stations,stations[1:])):
   prefix='MiddleSkin_E%02d_D%02d_B%02d'%(edge,level+4,bay)
   prism(prefix+'_Sill',edge,u0,u1,y0,y0+1.05,'spandrel')
   prism(prefix+'_Head',edge,u0,u1,y1-.25,y1,'spandrel')
   width=(u1-u0)*length;cols=max(1,math.ceil(width/3));bottom,top=y0+1.05,y1-.25;rows=max(1,math.ceil((top-bottom)/3.5));du=.06/length
   # Full parametric face tiling: joints and glazing occupy disjoint rectangles.
   for col in range(cols+1):
    u=u0+(u1-u0)*col/cols;lo=u if col==0 else u-du/2;hi=u if col==cols else u+du/2
    if hi>lo:prism(prefix+'_VJoint%02d'%col,edge,lo,hi,bottom,top,'joint')
   for col in range(cols):
    ua=u0+(u1-u0)*col/cols+du/2;ub=u0+(u1-u0)*(col+1)/cols-du/2
    for row in range(rows):
     ya=bottom+(top-bottom)*row/rows;yb=bottom+(top-bottom)*(row+1)/rows
     if row:prism(prefix+'_HJoint%02d_%02d'%(col,row),edge,ua,ub,ya-.0375,ya+.0375,'joint')
     name=prefix+'_ReplaceableGlazedField%02d_%02d'%(col,row);prism(name,edge,ua,ub,ya+(0 if row==0 else .0375),yb-(0 if row==rows-1 else .0375),'glazing')
   schedule.append({'id':prefix,'edge':edge,'deck_interval':[level+4,level+5],'uv_edge_interval':[u0,u1],'y_interval':[y0,y1],'frame_receiver':'G7_MiddleExteriorFrame_r001, inward normal0.18m interface','architecture':'Fixed replaceable pressure-envelope glazing fields; not new room windows or doors','maintenance':'Panels demount inward into normal0.18..0.80m component reservation. Root service owner must prove local receiver/withdrawal access; no working mechanism or service-route acceptance','room_side_ownership':'Retained room walls, private windows, privacy and operating systems unchanged. Clear outer glazing preserves potential views; no new view ray through another room is asserted.'})
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
native=P/'source/natives/G7_MiddleExteriorSkin_r001.blend'
if not export_only:bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
# A separate active export scene avoids repeatedly unlinking thousands of
# semantic native parts. The native remains untouched; only compact meshes
# belong to this temporary scene. Explicit active-scene export excludes it.
scene=bpy.data.scenes.new('G7CompactRuntimeExport');bpy.context.window.scene=scene
for edge in range(len(points)):
 for role in mats:
  selected=[g for g in geo if g['edge']==edge and g['role']==role];v=[];faces=[]
  for g in selected:
   i=len(v);v.extend((x,-z,y) for x,y,z in g['vertices_world_xyz']);faces.extend(tuple(i+k for k in f) for f in [(3,2,1,0),(4,5,6,7)]+[(k,(k+1)%4,(k+1)%4+4,k+4) for k in range(4)])
  me=bpy.data.meshes.new('G7_MiddleSkin_E%02d_%s'%(edge,role));me.from_pydata(v,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[role]);o['edge']=edge;o['source_role']=role;o['contact_category']='solid_glazing' if role=='glazing' else 'solid_skin';uv=me.uv_layers.new(name='MetreScaled');t=(points[(edge+1)%len(points)]-points[edge]).normalized()
  for f in me.polygons:
   for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(Vector((q.x,-q.y)).dot(t),q.z)
 for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' and o.get('edge')==edge)
 f=P/'exports/exterior'/('G7_MiddleExteriorSkin_E%02d_r001.glb'%edge);bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,use_active_scene=True,export_lights=False,export_cameras=False)
 exports.append({'edge':edge,'path':f.relative_to(P).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'origin_world_xyz':[0,0,0],'rotation_y':0,'scale':[1,1,1]})
(P/'qa/middle_skin_geometry.json').write_text(json.dumps(geo,indent=2)+'\n')
out={'id':'G7_MiddleExteriorSkin_r001','source':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'parts':len(geo),'triangles':sum(g['triangles'] for g in geo),'exports':exports,'panel_schedule':schedule,'normal_skin_band_m':[.02,.18],'y_interval':[16.5,61],'frame_dependency':'G7_MiddleExteriorFrame_r001','status':'Uninstalled middle side-envelope architectural source; geometric side fields only, not whole pressure/load certification or operating windows','open_interfaces':['Y16.5 lower-owner pressure sealing','Y61 upper-owner closure, HUL002 retained','Every room-side privacy/window/route receiver retains existing source ownership','Root confirms panel withdrawal and inspection receivers before adoption','Upper taper/terminal/crown roofs remain separately owned; no cap authored'],'collision':'Both solid_skin and solid_glazing must provide collision after root adoption. Transparent visual materials do not imply passable glass.'}
(P/'docs/MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json').write_text(json.dumps(out,indent=2)+'\n');print('MIDDLE_SKIN',len(geo),'parts',len(exports),'exports',len(schedule),'bay/deck fields')
