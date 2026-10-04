"""Original three-station crescent reception desk, authored for Astraea arrivals.
Source XY is plan; Z is up. Front faces -Y. Open staff side faces +Y.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,importlib.util
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-ARR-003'
for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']==AID:assert a['source']=='assets/arrivals_reception/source/'+AID+'.blend'
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
# Three individually shaped counter heights share a shallow crescent. Centre is
# deliberately lower with knee clearance; tall and standard wings flank it.
for name,a,b,height in [('standard',-.82,-.24,1.05),('lower',-.24,.24,.76),('tall',.24,.82,1.24)]:
 if name!='lower':
  ring(name+'_recessed_shoe',a,b,4.65,5.22,0,.07,'dark_rubber')
  ring(name+'_textured_front',a,b,5.10,5.20,.07,height-.075,'warm_walnut')
 ring(name+'_stone_worktop',a-.008,b+.008,4.30,5.30,height-.075,height,'warm_stone')
 if name!='lower':ring(name+'_metal_reveal',a,b,5.195,5.225,height-.14,height-.10,'champagne_metal')
 # Radial support cheeks and open staff-side compartments, never solid-box filler.
 for t in [a+.025,b-.025]:
  inner,outer=4.39,5.12;delta=.012
  pts=[(r*math.sin(ang),5-r*math.cos(ang))for r,ang in [(inner,t-delta),(outer,t-delta),(outer,t+delta),(inner,t+delta)]]
  prism(name+'_support_'+str(t),pts,0,height-.075,'ivory_enamel')
 if name!='lower':ring(name+'_staff_storage_shelf',a+.035,b-.035,4.45,5.10,.28,.32,'warm_walnut')
 t=(a+b)/2;marker(name+'_guest_approach',(6.1*math.sin(t),5-6.1*math.cos(t),0));marker(name+'_staff_position',(3.7*math.sin(t),5-3.7*math.cos(t),0));marker(name+'_work_surface',(4.75*math.sin(t),5-4.75*math.cos(t),height))
# Actual supported information surfaces, separate from future interaction logic.
for i,t in enumerate([-.52,.52]):
 x,y=4.65*math.sin(t),5-4.65*math.cos(t);h=1.05 if i==0 else 1.24
 box('terminal_foot_'+str(i),x-.15,x+.15,y-.10,y+.10,h,h+.035,'champagne_metal')
 box('terminal_stem_'+str(i),x-.025,x+.025,y-.025,y+.025,h+.035,h+.24,'champagne_metal')
 box('terminal_back_'+str(i),x-.26,x+.26,y-.045,y+.045,h+.20,h+.52,'ivory_enamel')
 box('inactive_display_'+str(i),x-.23,x+.23,y+.045,y+.052,h+.23,h+.49,'dark_rubber')
 marker('terminal_'+str(i),(x,y+.06,h+.35))
# Distinct faceted end caps terminate the curved front with substantial trim.
for t in [-.82,.82]:
 x,y=4.83*math.sin(t),5-4.83*math.cos(t);pts=[(x+.18*math.cos(2*math.pi*i/12),y+.18*math.sin(2*math.pi*i/12))for i in range(12)];prism('profiled_end_'+str(t),pts,0,1.05 if t<0 else 1.24,'ivory_enamel')
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
verts=[o.matrix_world@Vector(p)for o in parts for p in o.bound_box];lo=[min(v[i]for v in verts)for i in range(3)];hi=[max(v[i]for v in verts)for i in range(3)];tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
record={'catalogue_id':AID,'name':'Three-height crescent arrivals reception desk','source':'source/'+src.name,'export':'exports/'+out.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounds_min':lo,'bounds_max':hi,'triangles':tri,'status':'Editable draft; placement, accessibility, contact and visual review pending; terminals inactive'}
(R/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
