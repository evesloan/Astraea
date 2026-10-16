from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;R=D.parents[2];p=json.loads((D/'PLAN.json').read_text());assert bpy.app.version[:3]==(4,3,2)
for f,h in p['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
donor=json.loads((R/'BlenderCatalogue/assets/cinema1_receiving_20261016/NATIVE_PLAN.json').read_text());native=R/donor['source_native'];assert hashlib.sha256(native.read_bytes()).hexdigest()==donor['source_native_sha256']
with bpy.data.libraries.load(str(native),link=False)as(a,b):b.materials=[n for n in a.materials if n in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint']]
mats={k:bpy.data.materials[k]for k in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint']};parts=[]
def mesh(name,vs,fs,mat):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();m.materials.append(mats[mat]);uv=m.uv_layers.new(name='MetreUV')
 for f in m.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda j:abs(f.normal[j]))]
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
 o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o['candidate_only']=True;parts.append(o);return o
def prism(name,ring,lo,hi,mat):
 v=[Vector((x,-z,lo))for x,z in ring]
 if sum(v[i].x*v[(i+1)%len(v)].y-v[(i+1)%len(v)].x*v[i].y for i in range(len(v)))<0:v.reverse()
 n=len(v);lookup={tuple(q):i for i,q in enumerate(v)};fs=[]
 for t in tessellate_polygon([v]):
  ids=[a if isinstance(a,int)else lookup[tuple(a)]for a in t]
  if (v[ids[1]]-v[ids[0]]).cross(v[ids[2]]-v[ids[0]]).z<0:ids.reverse()
  fs.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
 fs.extend((i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n))
 return mesh(name,[tuple(q)for q in v]+[(q.x,q.y,hi)for q in v],fs,mat)
def box(n,a,b,mat):return prism(n,[(a[0],a[2]),(b[0],a[2]),(b[0],b[2]),(a[0],b[2])],a[1],b[1],mat)
def line(n,a,b,w,lo,hi,mat):
 a,b=Vector(a),Vector(b);v=Vector((-(b-a).y,(b-a).x)).normalized()*w/2
 return prism(n,[a-v,b-v,b+v,a+v],lo,hi,mat)
blue='ASTRAEA_staff_bluegrey_paint';white='ASTRAEA_staff_white_paint';metal='ASTRAEA_staff_zinc'
prism('Q15_MissingFloor',p['floor_outline_xz'],92.76,93,blue)
# Inactive outer shell leaves both receiving interfaces unmodified and unsealed in this candidate.
prism('Q15_Canopy',[[19.3,-485.6],[45.7,-485.6],[45.7,-482.2001],[19.3,-482.2001]],95.82,95.98,white)
edges=[((23.26,-485.52),(45.62,-485.52)),((19.38,-482.28),(42.2,-482.28)),((45.62,-485.52),(45.62,-482.28)),((19.38,-483.92),(19.38,-482.28))]
for i,(a,b)in enumerate(edges):
 for s,w,y0,y1,m in [('Toe',.14,93,93.14,metal),('Dado',.12,93.14,94.05,blue),('Reveal',.16,94.05,94.12,metal),('Enamel',.12,94.12,95.82,white)]:line(f'Q15_Edge{i}_{s}',a,b,w,y0,y1,m)
# Full-height side-frame source study; its connections/load sizing remain explicit hold points.
for z in [-485.47,-482.33]:
 for y0,y1 in [(93.14,93.34),(95.55,95.75)]:line(f'Q15_Chord_{z}_{y0}',(23.26,z),(42.15,z),.20,y0,y1,metal)
 for i,x in enumerate([23.36,27.1,30.84,34.58,38.32,42.05]):box(f'Q15_Post_{z}_{i}',(x-.075,93.14,z-.1),(x+.075,95.75,z+.1),metal)
 for i,(a,b)in enumerate(zip([23.36,27.1,30.84,34.58,38.32],[27.1,30.84,34.58,38.32,42.05])):
  # Side-frame diagonal rectangular prism, preserving an editable object per member.
  v0=Vector((a,-z,93.34 if i%2==0 else 95.55));v1=Vector((b,-z,95.55 if i%2==0 else 93.34));mid=(v0+v1)/2
  bpy.ops.mesh.primitive_cube_add(size=1,location=mid);o=bpy.context.object;o.name=f'Q15_Diagonal_{z}_{i}';o.rotation_euler=(v1-v0).to_track_quat('Z','Y').to_euler();o.scale=(.12,.12,(v1-v0).length);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[metal]);o['candidate_only']=True;parts.append(o)
# No fixture or operating light is invented in this first source structure candidate.
for o in parts:o.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'QuietD15StaffReceiving_r001.blend'))
bpy.ops.export_scene.gltf(filepath=str(D/'QUIET_D15_STAFF_RECEIVING_r001.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
receipt={'status':'INACTIVE_SOURCE_CANDIDATE_ONLY','mesh_count':len(parts),'native_sha256':hashlib.sha256((D/'QuietD15StaffReceiving_r001.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((D/'QUIET_D15_STAFF_RECEIVING_r001.glb').read_bytes()).hexdigest(),'source_material_native':donor['source_native'],'source_material_native_sha256':donor['source_native_sha256'],'runtime_installed':False,'original_sources_changed':False,'remaining':p['limits']}
(D/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CANDIDATE_EXPORTED',len(parts))
