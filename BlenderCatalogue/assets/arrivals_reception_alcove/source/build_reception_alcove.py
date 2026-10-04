"""Original fitted reception enclosure, coordinated with AST-ARR-003."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,importlib.util
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-ARR-004'
for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']==AID:assert a['source']=='assets/arrivals_reception_alcove/source/'+AID+'.blend'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
spec=importlib.util.spec_from_file_location('palette',C/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials();parts=[]
def mesh(name,verts,faces,role):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(M[role]);parts.append(o);layer=me.uv_layers.new(name='MetricUV');scale=M[role].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda j:abs(f.normal[j]))]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(p[axes[0]]/scale[0],p[axes[1]]/scale[1])
 return o

def prism(name,outline,lo,hi,role):
 n=len(outline);return mesh(name,[(x,y,z)for z in [lo,hi]for x,y in outline],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)
def ring(name,lo_angle,hi_angle,inner,outer,lo,hi,role,steps=12):
 # Small convex arc bays avoid a concave n-gon cap across the staff recess.
 for i in range(steps):
  a=lo_angle+(hi_angle-lo_angle)*i/steps;b=lo_angle+(hi_angle-lo_angle)*(i+1)/steps
  pts=[(r*math.sin(t),5-r*math.cos(t))for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]]
  prism(name+'_%02d'%i,pts,lo,hi,role)
def box(name,x0,x1,y0,y1,z0,z1,role):return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,role)
def marker(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p
# The enclosure itself forms a shallow fan around the staffed counter.
outline=[(-6.6,.2),(-6.6,2.7),(-6.2,4.1),(-5.2,5.4),(-3.5,6.2),(0,6.7),(3.5,6.2),(5.2,5.4),(6.2,4.1),(6.6,2.7),(6.6,.2)]
def wall(name,a,b,width,z0,z1,role):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return prism(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0,z1,role)
for i,(a,b)in enumerate(zip(outline,outline[1:])):
 wall('Reception_WarmPlinth_'+str(i),a,b,.24,0,.16,'warm_walnut')
 wall('Reception_LowerProfile_'+str(i),a,b,.18,.16,1.18,'warm_walnut')
 wall('Reception_StoneWall_'+str(i),a,b,.16,1.18,3.38,'warm_stone')
 wall('Reception_Crown_'+str(i),a,b,.30,3.38,3.68,'ivory_enamel')
 wall('Reception_InlaidReveal_'+str(i),a,b,.195,1.16,1.20,'champagne_metal')
# Convex ceiling field follows the entire curved enclosure. The existing larger
# hospitality canopy stays above this fitted inner ceiling, not through it.
prism('Reception_FanCeiling',outline,3.70,3.77,'ivory_enamel')
for i,p in enumerate(outline[1:-1]):
 wall('Reception_CeilingFanRib_'+str(i),(0,.25),p,.12,3.52,3.70,'warm_walnut')
# A segmented front valance frames arrival without narrowing the open threshold.
front=[(-6.6,.2),(-4.4,-.20),(-2.2,-.43),(0,-.50),(2.2,-.43),(4.4,-.20),(6.6,.2)]
for i,(a,b)in enumerate(zip(front,front[1:])):
 wall('Reception_ProfiledValance_'+str(i),a,b,.22,3.30,3.76,'ivory_enamel')
 wall('Reception_ValanceMetalInlay_'+str(i),a,b,.24,3.34,3.38,'champagne_metal')
# Two low integrated side ledges support guest documents and belongings.
for side in [-1,1]:
 x=side*6.30
 box('Reception_SideLedge_'+str(side),x-.25,x+.25,.65,2.2,.84,.90,'warm_walnut')
 box('Reception_LedgeSupport_'+str(side),x-.08,x+.08,.8,2.05,0,.84,'ivory_enamel')
# Visible opal sources over the three work stations, with actual ceiling mounts.
m=bpy.data.materials.new('ReceptionOpalLens');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,.95,.85,1);p.inputs['Emission Color'].default_value=(1,.93,.8,1);p.inputs['Emission Strength'].default_value=.5;m['meters_per_tile_uv']=[1,1];M['reception_lens']=m
for i,(x,y)in enumerate([(-3.4,1.6),(0,1.4),(3.4,1.6)]):
 q=[(x+.30*math.cos(j*math.pi/8),y+.30*math.sin(j*math.pi/8))for j in range(16)]
 prism('Reception_LensHousing_'+str(i),q,3.20,3.29,'champagne_metal')
 prism('Reception_OpalLens_'+str(i),[(x+(a-x)*.88,y+(b-y)*.88)for a,b in q],3.18,3.20,'reception_lens')
 box('Reception_LightStem_'+str(i),x-.035,x+.035,y-.035,y+.035,3.29,3.70,'champagne_metal')
 marker('light_'+str(i),(x,y,3.16))
# All guest and staff approaches remain open; future signs belong on the rear wall.
marker('information_wall',(0,6.53,2.30))
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
verts=[o.matrix_world@Vector(p)for o in parts for p in o.bound_box];lo=[min(v[i]for v in verts)for i in range(3)];hi=[max(v[i]for v in verts)for i in range(3)];tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
record={'catalogue_id':AID,'name':'Fitted fan-shaped arrivals reception alcove','source':'source/'+src.name,'export':'exports/'+out.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounds_min':lo,'bounds_max':hi,'triangles':tri,'status':'Editable district-fitted enclosure; placement, light, contact and visual review pending'}
(R/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
