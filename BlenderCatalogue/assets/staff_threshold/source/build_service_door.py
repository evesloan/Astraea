"""Original two-leaf staff service door. Real hinges and open sweep datums."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['staff/staff_bluegrey_paint','staff/staff_white_paint','staff/staff_zinc','staff/staff_rubber','staff/staff_label']:
 m=bpy.data.materials.new(role.split('/')[-1]);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.72
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
parts=[]
def prism(name,profile,y0,y1,role,parent=None):
 n=len(profile);v=[(x,y,z) for y in [y0,y1] for x,z in profile];f=[tuple(reversed(range(n))),tuple(range(n,n*2))]
 for j in range(n):k=(j+1)%n;f.append((j,k,n+k,n+j))
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.parent=parent;d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for face in d.polygons:
  for li in face.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.5,q.z*.5)
 return o
# Profiled formed jambs; no hidden leaf pockets or wall clipping.
prism('STF_JambLeft',[(-1.38,0),(-1.20,0),(-1.20,2.54),(-1.15,2.64),(-1.30,2.74),(-1.38,2.58)],-.18,.18,'staff/staff_bluegrey_paint')
prism('STF_JambRight',[(1.20,0),(1.38,0),(1.38,2.58),(1.30,2.74),(1.15,2.64),(1.20,2.54)],-.18,.18,'staff/staff_bluegrey_paint')
prism('STF_Header',[(-1.38,2.58),(-1.20,2.54),(-1.15,2.64),(1.15,2.64),(1.20,2.54),(1.38,2.58),(1.38,2.82),(-1.38,2.82)],-.18,.18,'staff/staff_bluegrey_paint')
for side,sign in [('LEFT',1),('RIGHT',-1)]:
 pivot=bpy.data.objects.new('HINGE_'+side,None);bpy.context.collection.objects.link(pivot);pivot.location=(-1.15 if sign==1 else 1.15,0,0)
 x0,x1=(.01,1.14) if sign==1 else (-1.14,-.01)
 prism('LEAF_'+side,[(x0,.025),(x1,.025),(x1,2.56),(x0,2.56)],-.035,.035,'staff/staff_white_paint',pivot)
 if side=='LEFT':prism('MEETING_SEAL_LEFT',[(1.13,.03),(1.17,.03),(1.17,2.56),(1.13,2.56)],-.065,-.035,'staff/staff_rubber',pivot)
 prism('KICK_'+side,[(x0+.05,.12),(x1-.05,.12),(x1-.05,.48),(x0+.05,.48)],-.041,-.035,'staff/staff_zinc',pivot)
 h=(x1-.16) if sign==1 else (x0+.16)
 prism('PUSH_'+side,[(h-.065,.98),(h+.065,.98),(h+.065,1.40),(h-.065,1.40)],-.066,-.042,'staff/staff_rubber',pivot)
 prism('IDENTIFIER_'+side,[(x0+.16,1.70),(x1-.16,1.70),(x1-.16,1.82),(x0+.16,1.82)],-.039,-.035,'staff/staff_label',pivot)
for name,loc in [('INTERACTION',(0,-.12,1.25)),('LOWER',(0,0,0)),('CLEAR_FRONT',(0,-1.6,0)),('CLEAR_REAR',(0,1.6,0))]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=loc
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source/AST-STF-008.blend';glb=ROOT/'exports/AST-STF-008.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-STF-008.manifest.json').write_text(json.dumps({'catalogue_id':'AST-STF-008','name':'Profiled two-leaf staff service threshold','status':'Draft; hinge sweep, collision and in-engine visual review pending','frame_aperture_m':[2.4,2.54],'open_clear_between_handles_m':2.168,'hinge_centres_x_m':[-1.15,1.15],'outer_m':[2.76,.36,2.82],'triangles':tri,'source':'source/AST-STF-008.blend','export':'exports/AST-STF-008.glb','motion':'Blender left hinge rotates+90degrees localZ and right-90degrees into rear+Y; GLB maps to localY with same rotation sign','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('STAFF_DOOR_CREATED',tri)
