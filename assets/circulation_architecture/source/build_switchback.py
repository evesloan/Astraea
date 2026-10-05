"""Original editable Astraea switchback stair; 8.5m public deck pitch, Blender Z up."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,argparse,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--rise',type=float,choices=[4.5,6.0,8.5],default=8.5)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
rise=args.rise;half=rise/2;steps={4.5:14,6.0:18,8.5:25}[rise];riser=half/steps;going=7.5/steps
variant='AST-CIR-001'if rise==8.5 else 'AST-CIR-001_H%03d'%round(rise*100)
assert next(a for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets']if a['catalogue_id']=='AST-CIR-001')['family']=='circulation_architecture'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal','dark_rubber']:
 mat=bpy.data.materials.new(role);mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.7
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);materials[role]=mat
glass=bpy.data.materials.new('circulation_glass');glass.use_nodes=True
bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.49,.51,1);bs.inputs['Alpha'].default_value=.23;bs.inputs['Roughness'].default_value=.22
glass.diffuse_color=(.23,.49,.51,.23);glass.surface_render_method='DITHERED';materials['circulation_glass']=glass
parts=[]
def mesh(name,verts,faces,role):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);data.materials.append(materials[role]);parts.append(ob)
 uv=data.uv_layers.new(name='MetreScaled')
 for face in data.polygons:
  for i in face.loop_indices:
   v=data.vertices[data.loops[i].vertex_index].co;uv.data[i].uv=(v.x*.5+v.z*.5,v.y*.5)
 return ob

def extrude(name,profile,x0,x1,role):
 n=len(profile);v=[(x,y,z) for x in [x0,x1] for y,z in profile];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for j in range(n):k=(j+1)%n;f.append((j,k,n+k,n+j))
 return mesh(name,v,f,role)
def rail(name,a,b,r,role):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1))).normalized()
 if u.length<.5:u=Vector((1,0,0))
 v=axis.cross(u);verts=[]
 for p in [a,b]:
  for i in range(8):verts.append(p+r*(math.cos(i*math.pi/4)*u+math.sin(i*math.pi/4)*v))
 mesh(name,verts,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8)],role)
for flight in range(2):
 x0,x1=(0,2.5) if flight==0 else (3.5,6)
 def p(y,z):return (y,z) if flight==0 else (7.5-y,half+z)
 profile=[p(0,-.25),p(7.5,half-.25),p(7.5,half)]
 for i in reversed(range(steps)):
  profile.extend([p(i*going,(i+1)*riser),p(i*going,i*riser)])
 extrude(f'CIR_Flight_{flight}',profile,x0,x1,'warm_stone')
 for i in range(steps):
  y,z=p(i*going,(i+1)*riser)
  extrude(f'CIR_Nosing_{flight}_{i:02}',[(y,z+.002),(y+(.045 if flight==0 else -.045),z+.002),(y+(.045 if flight==0 else -.045),z-.018),(y,z-.018)],x0+.09,x1-.09,'dark_rubber')
 for side,x in enumerate([x0+.08,x1-.08]):
  extrude(f'CIR_Guard_{flight}_{side}',[p(.04,.23),p(7.46,half+.185),p(7.46,half+.99),p(.04,1.035)],x-.012,x+.012,'circulation_glass')
  a=p(0,1.04);b=p(7.5,half+1.04)
  rail(f'CIR_Handrail_{flight}_{side}',(x,*a),(x,*b),.055,'warm_walnut')
  for i in range(6):
   y,z=p(i*1.5,i*half/5)
   rail(f'CIR_Post_{flight}_{side}_{i}',(x,y,z+.05),(x,y,z+1.04),.032,'champagne_metal')
  extrude(f'CIR_ProfiledStringer_{flight}_{side}',[p(0,-.32),p(7.5,half-.32),p(7.5,half-.03),p(0,-.03)],x-.09,x+.09,'ivory_enamel')
extrude('CIR_MidLanding',[(7.5,half),(10.5,half),(10.5,half-.32),(7.5,half-.32)],0,6,'warm_stone')
extrude('CIR_LandingFascia',[(10.42,half),(10.55,half),(10.55,half-.30),(10.48,half-.38),(10.42,half-.30)],0,6,'ivory_enamel')
extrude('CIR_GuardLandingRear',[(10.38,half+.22),(10.42,half+.22),(10.42,half+.98),(10.38,half+.98)],.08,5.92,'circulation_glass')
rail('CIR_LandingRearRail',(.08,10.4,half+1.04),(5.92,10.4,half+1.04),.055,'warm_walnut')
for x in [.08,5.92]:
 extrude('CIR_GuardLandingSide_'+str(x),[(7.52,half+.22),(10.38,half+.22),(10.38,half+.98),(7.52,half+.98)],x-.012,x+.012,'circulation_glass')
 rail('CIR_LandingSideRail_'+str(x),(x,7.5,half+1.04),(x,10.4,half+1.04),.055,'warm_walnut')
 rail('CIR_LandingSidePost_'+str(x),(x,8.95,half),(x,8.95,half+1.04),.032,'champagne_metal')
for x in [.08,2,4,5.92]:rail('CIR_LandingPost_'+str(x),(x,10.4,half),(x,10.4,half+1.04),.032,'champagne_metal')
for name,loc in [('LOWER',(1.25,0,0)),('UPPER',(4.75,0,rise)),('MID',(3,9,half))]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=loc
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source'/(variant+'.blend');glb=ROOT/'exports'/(variant+'.glb')
bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for ob in parts:ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
assert tri<10000
(ROOT/(variant+'.manifest.json')).write_text(json.dumps({'catalogue_id':'AST-CIR-001','name':'Public switchback stair for%gm pitch'%rise,'representation':variant,'status':'Draft awaiting topology, headroom, traversal and visual review','rise_m':rise,'flight_width_m':2.5,'nominal_clear_between_guards_m':2.316,'risers':steps*2,'riser_m':riser,'going_m':going,'footprint_m':[6,10.55],'triangles':tri,'source':'source/'+variant+'.blend','export':'exports/'+variant+'.glb','collision_policy':'Separate simplified ramp surfaces and rail contacts; never convex-hull the stairwell void','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('STAIR_CREATED',tri)
