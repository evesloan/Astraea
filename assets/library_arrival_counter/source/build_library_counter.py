"""Original library arrival counter, metres, source Z up, front -Y."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,importlib.util
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-LIB-012'
for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']==AID:assert a['source']=='assets/library_arrival_counter/source/'+AID+'.blend'
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
  pts=[(r*math.sin(t),2.5-r*math.cos(t))for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]]
  prism(name+'_%02d'%i,pts,lo,hi,role)
def box(name,x0,x1,y0,y1,z0,z1,role):return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,role)
def marker(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p
# A shallow reference counter gives the library entrance a real destination.
# Standard-height book wings flank an open lower writing/reach position.
for name,a,b,height in [('west',-.78,-.25,.95),('lower',-.25,.25,.74),('east',.25,.78,.95)]:
 if name!='lower':
  ring(name+'_recessed_shoe',a,b,2.22,2.72,0,.06,'dark_rubber')
  ring(name+'_profiled_book_front',a,b,2.62,2.70,.06,height-.065,'warm_walnut')
  ring(name+'_inset_trim',a,b,2.697,2.715,height-.15,height-.115,'champagne_metal')
 ring(name+'_reference_surface',a-.008,b+.008,1.90,2.82,height-.065,height,'warm_stone')
 for angle in [a+.023,b-.023]:
  pts=[(radius*math.sin(t),2.5-radius*math.cos(t)) for radius,t in [(1.97,angle-.016),(2.63,angle-.016),(2.63,angle+.016),(1.97,angle+.016)]]
  prism(name+'_support_cheek_'+str(angle),pts,0,height-.065,'ivory_enamel')
 if name!='lower':ring(name+'_open_storage',a+.032,b-.032,2.02,2.62,.26,.30,'warm_walnut')
 angle=(a+b)/2
 marker(name+'_work_surface',(2.32*math.sin(angle),2.5-2.32*math.cos(angle),height))
 if name!='lower':marker(name+'_fixture_receiver',(2.03*math.sin(angle),2.5-2.03*math.cos(angle),height))
 marker(name+'_guest_approach',(3.55*math.sin(angle),2.5-3.55*math.cos(angle),0))
 marker(name+'_rear_approach',(1.20*math.sin(angle),2.5-1.20*math.cos(angle),0))
for angle in [-.78,.78]:
 x,y=2.36*math.sin(angle),2.5-2.36*math.cos(angle)
 outline=[(x+.12*math.cos(i*math.pi/6),y+.12*math.sin(i*math.pi/6)) for i in range(12)]
 prism('finished_end_'+str(angle),outline,0,.95,'ivory_enamel')
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb')
bpy.ops.wm.save_as_mainfile(filepath=str(src))
verts=[o.matrix_world@Vector(p) for o in parts for p in o.bound_box];lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)];tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,material in M.items():
 selected=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='LBC_static_'+role
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Crescent library reference and orientation counter','source':'source/'+src.name,'export':'exports/'+out.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounds_min':lo,'bounds_max':hi,'triangles':tri,'status':'Editable fitted component; contact, approaches and visual review pending. No staff or catalogue-service implementation implied.'}
(R/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
