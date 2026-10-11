"""Original lower-rim-borne middle exterior frame; pressure skins are separate seams."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];OLD=P/'dependencies/canonical_77a745';LATEST=P/'dependencies/canonical_9d6f85'
outline=json.loads((OLD/'Game/data/hull_envelope.json').read_text())['plan_xz_m'];points=[Vector(q) for q in outline]
centroid=sum(points,Vector((0,0)))/len(points);normals=[]
for i,a in enumerate(points):
 t=(points[(i+1)%len(points)]-a).normalized();n=Vector((t.y,-t.x));n=n if n.dot(centroid-a)>0 else -n;normals.append(n)
def inset(distance):
 result=[]
 for i,a in enumerate(points):
  n0=normals[i-1];n1=normals[i];d0=n0.dot(a)+distance;d1=n1.dot(a)+distance;det=n0.x*n1.y-n0.y*n1.x;assert abs(det)>1e-8
  result.append(Vector(((d0*n1.y-n0.y*d1)/det,(n0.x*d1-d0*n1.x)/det)))
 return result
materials={};parts=[];contacts=[];geometry=[];exports=[]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for role,tex in [('frame','staff/staff_zinc.png'),('shoe','staff/staff_bluegrey_paint.png')]:
 m=bpy.data.materials.new('G7_middle_'+role);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(LATEST/'BlenderCatalogue/materials'/tex));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);materials[role]=m
def prism(name,poly,y0,y1,role,edge,foot=False):
 n=len(poly);world=[(q.x,y,q.y) for y in [y0,y1] for q in poly];v=[(x,-z,y) for x,y,z in world];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume()>0,name;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(materials[role]);o['edge']=edge;o['contact_category']='solid_frame';o['source_role']=role;parts.append(o)
 uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  nrm=f.normal;u=Vector((0,1,0)) if abs(nrm.x)>.7 else Vector((1,0,0));w=nrm.cross(u)
  for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
 me.calc_loop_triangles();geometry.append({'object':name,'edge':edge,'role':role,'vertices_world_xyz':world,'plan_footprint_xz':[(q.x,q.y) for q in poly],'y_interval':[y0,y1],'triangles':len(me.loop_triangles)})
 if foot:contacts.append({'object':name,'receiver':'AST-HUL-001 actual decoded D04 rim top','contact_y':16.5,'boundary_xz':[(q.x,q.y) for q in poly]})
def local_poly(i,s0,s1,n0,n1):
 a=points[i];b=points[(i+1)%len(points)];t=(b-a).normalized();n=normals[i]
 return [a+t*s+n*d for s,d in [(s0,n0),(s1,n0),(s1,n1),(s0,n1)]]
inner18=inset(.18);inner40=inset(.40)
datums=[16.5,21,27,35.5,44,52.5,61]
for i,a in enumerate(points):
 b=points[(i+1)%len(points)];length=(b-a).length;count=max(1,math.ceil(length/12));spacing=length/count
 # Exact-miter continuous receiving hoops are structural source, not floors.
 for j,y in enumerate(datums):
  lo=16.58 if j==0 else y-.22;hi=16.80 if j==0 else y
  poly=[inner18[i],inner18[(i+1)%len(points)],inner40[(i+1)%len(points)],inner40[i]]
  prism('Middle_Hoop_E%02d_D%02d'%(i,j+4),poly,lo,hi,'frame',i)
 for k in range(count):
  s=(k+.5)*spacing
  prism('Middle_RimShoe_E%02d_%02d'%(i,k),local_poly(i,s-.16,s+.16,.18,.26),16.5,16.58,'shoe',i,True)
  prism('Middle_ShoeTransfer_E%02d_%02d'%(i,k),local_poly(i,s-.16,s+.16,.18,.40),16.58,16.74,'shoe',i)
  prism('Middle_Stanchion_E%02d_%02d'%(i,k),local_poly(i,s-.09,s+.09,.18,.36),16.74,61,'frame',i)
 # Each bay reserves an independent opening/skin decision. No blanket panel
 # is added in front of an unverified installed/private window view.
 for j in range(1,len(datums)):
  y0,y1=datums[j-1],datums[j]
  for k in range(count-1):
   s0=(k+.5)*spacing+.09;s1=(k+1.5)*spacing-.09
   # Thin longitudinal diagonal web, staying within the normal material band.
   a0=points[i]+(b-a).normalized()*s0+normals[i]*.26;a1=points[i]+(b-a).normalized()*s1+normals[i]*.26
   v=[]
   for q,y in [(a0,y0+.30),(a1,y1-.30)]:
    for dn,dy in [(-.035,-.045),(.035,-.045),(.035,.045),(-.035,.045)]:v.append((q.x+normals[i].x*dn,-(q.y+normals[i].y*dn),y+dy))
   name='Middle_Diagonal_E%02d_H%02d_B%02d'%(i,j,k);me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(3,2,1,0),(4,5,6,7)]+[(k,(k+1)%4,(k+1)%4+4,k+4) for k in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(materials['frame']);o['edge']=i;o['contact_category']='solid_frame';o['source_role']='frame';parts.append(o);uv=me.uv_layers.new(name='MetreScaled')
   for f in me.polygons:
    for idx in f.loop_indices:q=me.vertices[me.loops[idx].vertex_index].co;uv.data[idx].uv=(q.x+q.y,q.z)
   me.calc_loop_triangles();world=[(x,y,-z) for x,z,y in v];geometry.append({'object':name,'edge':i,'role':'frame','vertices_world_xyz':world,'plan_footprint_xz':[],'y_interval':[min(q[1] for q in world),max(q[1] for q in world)],'triangles':len(me.loop_triangles)})
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
for name,pos in [('lower_retained_rim',(0,16.5,0)),('upper_body_seam',(0,61,0))]:o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=(pos[0],-pos[2],pos[1])
(P/'source/natives').mkdir(exist_ok=True);(P/'exports/exterior').mkdir(parents=True,exist_ok=True);native=P/'source/natives/G7_MiddleExteriorFrame_r001.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
for edge in range(len(points)):
 for role in materials:
  selected=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('edge')==edge and o.get('source_role')==role]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0]
  if len(selected)>1:bpy.ops.object.join()
  bpy.context.object.name='G7_MiddleExterior_E%02d_%s'%(edge,role);bpy.context.object['contact_category']='solid_frame'
for edge in range(len(points)):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.get('edge')==edge:o.select_set(True)
 f=P/'exports/exterior'/('G7_MiddleExterior_E%02d_r001.glb'%edge);bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,export_lights=False,export_cameras=False)
 exports.append({'edge':edge,'path':f.relative_to(P).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'origin_world_xyz':[0,0,0],'rotation_y':0,'scale':[1,1,1],'end_points_xz':outline[edge:edge+1]+[outline[(edge+1)%len(points)]],'pressure_skin':'Unclosed source increment; future component is a separately owned seam proposal, not a wall/window installation'})
(P/'qa/middle_exterior_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
receipt={'id':'G7_MiddleExteriorFrame_r001','source':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'semantic_parts':len(geometry),'triangles':sum(r['triangles'] for r in geometry),'exports':exports,'normal_material_band_m':[.18,.40],'total_future_component_reservation_normal_m':.8,'rim_foot_contacts':contacts,'datums_y':datums,'new_floor_area_m2':0,'remaining_seams':{'bottom':'Actual HUL001 rim retained; new feet sit atY16.5','top':'AtY61, reversible upper-body/shoulder receiver; HUL002 itself untouched','skin_and_windows':'No opaque blanket facade or invented window. Opening/view schedule, pressure panels and inspection doors remain to be authored against source owners','inspection':'Normal0.40..0.80 is future component withdrawal reservation, not a walkable second service corridor','supports':'Architectural/game frame geometry only; no structural load or pressure engineering certification, no house supports or room-side collars replaced'},'status':'Constructed independent exterior frame increment; uninstalled and incomplete general exterior'}
(P/'docs/MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MIDDLE_EXTERIOR_FRAME',len(geometry),'parts',len(exports),'GLBs',len(contacts),'rim contacts')
