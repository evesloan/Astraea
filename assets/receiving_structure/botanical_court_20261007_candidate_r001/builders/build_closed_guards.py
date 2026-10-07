"""Reversible U-shaped receiving guards, never an operating room entrance."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;P=R.parent;C=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/BlenderCatalogue');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=next(x for x in json.loads((C/'catalogue_manifest.json').read_text())['assets'] if x['catalogue_id']=='AST-ATR-001');assert row['family']=='atrium_guard_network';native=C/row['source'];assert sha(native)==row['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));assert bpy.app.version[:3]==(4,3,2)
mats={r:bpy.data.materials[r] for r in ['ivory_enamel','warm_walnut','champagne_metal','gallery_glass']}
for m in mats.values():m.use_fake_user=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[]
def mesh(name,verts,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata([(x,-z,y) for x,y,z in verts],[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);o['source_family']='AST-ATR-001';o['material_role']=role;o['receiving_only']=True;parts.append(o)
 uv=d.uv_layers.new(name='MetreScaled')
 for f in d.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
  for li in f.loop_indices:
   p=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)*.5,p.dot(v)*.5)
 return o
profiles={'GuardPlinth':([(.01,0),(.43,0),(.43,.14),(.32,.21),(.1,.21),(.01,.13)],'ivory_enamel'),'Handrail':([(.115,1.10),(.14,1.08),(.29,1.08),(.315,1.10),(.315,1.13),(.29,1.15),(.14,1.15),(.115,1.13)],'warm_walnut'),'RailSeat':([(.17,1.055),(.26,1.055),(.26,1.08),(.17,1.08)],'champagne_metal')}
paths={'port':[(-4,-238),(-8,-238),(-8,-218.1),(-8,-213.9),(-8,-208),(-4,-208)],'starboard':[(4,-208),(8,-208),(8,-213),(8,-219),(8,-238),(4,-238)]}
segments=[]
for side,path in paths.items():
 points=[Vector(p) for p in path];normals=[]
 for i,p in enumerate(points):
  t0=(points[i]-points[i-1]).normalized() if i else (points[1]-p).normalized();t1=(points[i+1]-p).normalized() if i<len(points)-1 else t0
  n0=Vector((t0.y,-t0.x));n1=Vector((t1.y,-t1.x));n=(n0+n1).normalized();n/=n.dot(n1);normals.append(n)
 for i,(a,b) in enumerate(zip(points,points[1:])):
  closure=i==2;label=f'BOTCOURT_{side}_'+('PORTAL_CLOSURE' if closure else f'EDGE_{i}');length=(b-a).length;segments.append({'id':label,'side':side,'a':list(a),'b':list(b),'start_normal':list(normals[i]),'end_normal':list(normals[i+1]),'future_portal_closure':closure,'length_m':length})
  def sweep(suffix,profile,role,t0=0,t1=1):
   verts=[]
   for t in [t0,t1]:
    p=a.lerp(b,t);n=normals[i].lerp(normals[i+1],t)
    for dep,h in profile:q=p+n*dep;verts.append((q.x,27+h,q.y))
   n=len(profile);return mesh(label+'_'+suffix,verts,[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],role)
  for suffix,(profile,role) in profiles.items():sweep(suffix,profile,role)
  panels=math.ceil(length/1.95)
  for j in range(panels):
   # A distinct physical panel with only 20mm setback at each post.
   t0=j/panels+.02/length;t1=(j+1)/panels-.02/length
   sweep('Glass_'+str(j),[(.218,.21),(.236,.21),(.236,1.055),(.218,1.055)],'gallery_glass',t0,t1)
  for j in range(panels+1):
   if i and j==0:continue
   t=j/panels;p=a.lerp(b,t);normal=normals[i].lerp(normals[i+1],t);center=p+normal*.225;verts=[]
   for h,r in [(.16,.05),(.24,.035),(1.10,.035)]:
    for k in range(6):angle=math.pi*k/3;verts.append((center.x+r*math.cos(angle),27+h,center.y+r*math.sin(angle)))
   # End posts sit fully in floor, including at the two axial ends.
   if i==0 and j==0 or i==len(points)-2 and j==panels:
    shift=(b-a).normalized()*(.051 if j==0 else -.051);verts=[(x+shift.x,y,z+shift.y) for x,y,z in verts]
   mesh(label+'_Post_'+str(j),verts,[tuple(reversed(range(6))),tuple(range(12,18))]+[(h*6+k,h*6+(k+1)%6,(h+1)*6+(k+1)%6,(h+1)*6+k) for h in range(2) for k in range(6)],'champagne_metal')
 # A mounted plaque clearly communicates closure, rather than a fake usable doorway.
 x=-7.67 if side=='port' else 7.67;sign=1 if side=='port' else -1;z=-216
 verts=[(xx,yy,zz) for xx in [x,x+sign*.03] for yy,zz in [(27.4,z-1.5),(27.4,z+1.5),(27.98,z+1.5),(27.98,z-1.5)]]
 mesh(f'BOTCOURT_{side}_PORTAL_CLOSURE_Plaque',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 # Connecting brackets seat into the rail posts/plinth rather than floating signage.
 for zz in [z-1.2,z+1.2]:
  xx=-7.775 if side=='port' else 7.775
  vs=[(vx,vy,vz) for vy in [27.42,27.5] for vx,vz in [(min(xx,x),zz-.045),(max(xx,x),zz-.045),(max(xx,x),zz+.045),(min(xx,x),zz+.045)]]
  mesh(f'BOTCOURT_{side}_PORTAL_CLOSURE_Bracket_{zz}',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'champagne_metal')
 title='MOSS SANCTUARY' if side=='port' else 'BOTANICAL NURSERY'
 for txt,yy,size in [(title,27.79,.155),('RECEIVING EDGE - ENTRY NOT OPEN',27.57,.085)]:
  curve=bpy.data.curves.new('ReceivingLabel','FONT');curve.body=txt;curve.align_x='CENTER';curve.size=size;curve.extrude=.001
  o=bpy.data.objects.new(f'BOTCOURT_{side}_PORTAL_CLOSURE_Label',curve);bpy.context.collection.objects.link(o);curve.materials.append(mats['ivory_enamel'])
  # Blender text local X follows ship Z, local Y is ship up; front faces the axial route.
  right=Vector((0,sign,0));up=Vector((0,0,1));normal=right.cross(up);o.matrix_world=Matrix((right,up,normal)).transposed().to_4x4();o.location=(x+sign*.034,-z,yy)
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o['source_family']='AST-ATR-001';o['material_role']='ivory_enamel';o['role']='closure_label';parts.append(o);o.select_set(False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all()
name='AST-ATR-001_botanical_receiving_closed002';bpy.ops.wm.save_as_mainfile(filepath=str(R/(name+'.blend')))
geometry=[]
for o in parts:
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];geometry.append({'name':o.name,'material_role':o['material_role'],'vertices_world':[[v.x,v.z,-v.y] for v in vs],'triangles':[list(t.vertices) for t in o.data.loop_triangles]})
(R/'NATIVE_GEOMETRY.json').write_text(json.dumps({'objects':geometry,'segments':segments},indent=2)+'\n');bpy.ops.export_scene.gltf(filepath=str(R/(name+'.glb')),export_format='GLB',export_yup=True,export_extras=True)
manifest={'representation':name,'parent_design_ids':['AST-ATR-001'],'new_catalogue_id':None,'source_sha256':sha(R/(name+'.blend')),'export_sha256':sha(R/(name+'.glb')),'builder_sha256':sha(Path(__file__)),'parent_native_sha256':sha(native),'objects':len(parts),'triangles':sum(len(o['triangles']) for o in geometry),'segments':segments,'interim':True,'portal_release':'Remove named PORTAL_CLOSURE parts only after actual room floor and enclosure adoption and validated supported access; preserve exact original portal coordinates. No controls, opening animation or false usable door.','predecessor_retained':str(P/'guards'),'no_room_interior_adoption':True}
(R/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print('CLOSED_RECEIVING_BUILT',len(parts))
