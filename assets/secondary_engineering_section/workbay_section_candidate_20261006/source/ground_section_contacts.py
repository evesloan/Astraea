"""Bounded final source contact correction; original refined source stays retained."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys,resource
from mathutils import Vector
R=Path(__file__).resolve().parents[1];original=R/'source/AST-ENG-008_workbay_section.blend';source=R/'source/AST-ENG-008_workbay_section_final.blend';before=hashlib.sha256(original.read_bytes()).hexdigest();assert not source.exists();bpy.ops.wm.open_mainfile(filepath=str(original));sc=bpy.context.scene
cv=lambda p:Vector((p[0],-p[2],p[1]));pivot=cv((21.8675,6,-404.5));material=bpy.data.materials['ASTRAEA_staff_zinc']
# Two upper guard posts are outside the tread width: carry them down to the real lower slab.
fixed=[]
for ob in sc.objects:
 if ob.name.startswith('CellStairGuardPost'):
  ymin=min(v.co.z for v in ob.data.vertices)
  if ymin>5.56:
   for v in ob.data.vertices:
    if abs(v.co.z-ymin)<1e-4:v.co.z=5.55
   ob.data.update();fixed.append(ob.name)
# Replace the solid guide box in this new source copy with a real three-piece channel.
old=bpy.data.objects['CellDoorTrack'];bpy.data.objects.remove(old,do_unlink=True)
def mesh(name,vs,fs,door=False):
 me=bpy.data.meshes.new(name);me.from_pydata([cv(p)-(pivot if door else Vector((0,0,0))) for p in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);me.materials.append(material);ob['section_proposal_only']=True;ob['bay']='WORKBAY';ob['kind']='door_carriage' if door else 'door_guide';ob['collision_contract']='moving_door_visual' if door else 'static_surface'
 if door:ob.location=pivot;ob['door_leaf_id']='D02_secondary_engineering_workbay_cell_gate'
 uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/.75,q.dot(v)/.75)
 return ob
def box(n,b,door=False):
 x,y,z,X,Y,Z=b;return mesh(n,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],door)
box('CellDoorGuideCap',[21.815,8.44,-406.36,22.01,8.46,-403.86]);box('CellDoorGuideWestLip',[21.815,8.36,-406.36,21.84,8.44,-403.86]);box('CellDoorGuideEastLip',[21.985,8.36,-406.36,22.01,8.44,-403.86])
for i,z in enumerate([-404.9,-404.1]):
 box('CellDoorHanger'+str(i),[21.852,8.34,z-.018,21.883,8.41,z+.018],True)
 N=12;vs=[(x,8.41+.03*math.cos(j*2*math.pi/N),z+.03*math.sin(j*2*math.pi/N)) for x in [21.852,21.883] for j in range(N)];fs=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];mesh('CellDoorRoller'+str(i),vs,fs,True)
marker=bpy.data.objects['DATUM_WORKBAY_CELL_GATE'];marker['closed_leaf_bounds_xyz']=[21.84,6.03,-405.12,21.895,8.44,-403.88]
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);assert hashlib.sha256(original.read_bytes()).hexdigest()==before
sys.path.insert(0,str(R/'source'));from export_section_package import export_package
S=json.loads((R/'source/section_plan.json').read_text());report=export_package(R,source,S['removed_upper_source_assemblies'])
(R/'qa/final_contact_correction.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':report['export_sha256'],'previous_refined_source_unchanged':True,'grounded_guard_posts':fixed,'door_rollers':2,'closed_leaf_top_y':8.44,'guide_cap_underside_y':8.44,'source_reopen_export_only':True,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)+'\n');print('FINAL_SECTION_CONTACTS_EXPORT_OK',report['export_sha256'],fixed)
