import bpy,json
from pathlib import Path
from mathutils import Vector
here=Path(__file__).resolve().parent;d=json.loads((here/'STREET_PLAN.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def convert(v):return (v[0],-v[2],v[1])
for reg in d['regions']:
 verts=[];faces=[];y=reg['floor_y'];th=reg['thickness']
 for tri in reg['triangles']:
  for yy,up in [(y,True),(y-th,False)]:
   off=len(verts);pts=[convert((p[0],yy,p[1])) for p in tri];cross=(Vector(pts[1])-Vector(pts[0])).cross(Vector(pts[2])-Vector(pts[0])).z
   verts.extend(pts);faces.append((off,off+1,off+2) if ((cross>0)==up) else (off+2,off+1,off))
 for ring in reg['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   off=len(verts);verts.extend([convert((a[0],y,a[1])),convert((b[0],y,b[1])),convert((b[0],y-th,b[1])),convert((a[0],y-th,a[1]))]);faces.append((off,off+1,off+2,off+3))
 me=bpy.data.meshes.new(reg['id']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(reg['id'],me);bpy.context.collection.objects.link(ob);ob['owner']=reg['id'];ob['source_scope']='missing-only residential street construction; existing floors preserved'
for e in d['exposed_edge_guards']:
 a,b=Vector(convert(e['a'])),Vector(convert(e['b']));up=Vector((0,0,e['height']));direction=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.04,depth=direction.length,location=(a+b)*.5+up)
 ob=bpy.context.object;ob.name=e['id'];ob.rotation_euler=direction.to_track_quat('Z','Y').to_euler();ob['scope']='guard on exposed new floor boundary'
bpy.context.scene['scope']='Six paired-bank street systems;15missing-only floor regions; existing commons/atrium/pilots preserved; frame and garden completion outstanding'
bpy.ops.wm.save_as_mainfile(filepath=str(here/'central_residential_streets.blend'))
