from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/BlenderCatalogue');A='AST-HUL-002'
assert not any(a['catalogue_id']==A for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
D=json.load(open(R/'SOURCE_AUTHORITY.json'))
for p,h in D['pins'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for role,f in [('skin','ivory_enamel.png'),('frame','staff/staff_zinc.png')]:
 m=bpy.data.materials.new('upper_hull_'+role);m.use_nodes=True;nodes=m.node_tree.nodes;t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials'/f));t.interpolation='Closest';b=nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.82;m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);materials[role]=m
objects=[]
def box(name,lo,hi,role):
 # world XYZ maps to Blender X,-Z,Y; no scaling at export.
 x0,y0,z0=lo;x1,y1,z1=hi
 w=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 v=[(x,-z,y)for x,y,z in w];f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
 for face in me.polygons:
  n=face.normal;u=Vector((0,1,0))if abs(n.x)>.9 else Vector((1,0,0));vv=n.cross(u)
  for k in face.loop_indices:
   q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(vv))
 o['world_bounds']=[*lo,*hi];o['source_role']=role;objects.append(o)
box('HUL2_ContinuousOpaqueSkin',[-118.5,74.5,-250],[-118.32,87.5,-160],'skin')
for i in range(19):
 z=-250+i*5;a=max(-250,z-.09);b=min(-160,z+.09)
 box('HUL2_InteriorRib_%02d'%i,[-118.32,74.5,a],[-118.10,87.5,b],'frame')
for i,y in enumerate([74.5,81.0,87.5]):
 lo=max(74.5,y-.08);hi=min(87.5,y+.08)
 # Horizontal members segmented between ribs, touching but never overlapping.
 for j in range(18):box('HUL2_CrossRail_%d_%02d'%(i,j),[-118.32,lo,-250+j*5+.09],[-118.10,hi,-245+j*5-.09],'frame')
for name,pos in [('fore_seam',(-118.5,250,81)),('aft_seam',(-118.5,160,81)),('inspection_inner_limit',(-117.7,205,81))]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=pos
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.ops.file.pack_all()
source=R/'source'/(A+'.blend');out=R/'exports'/(A+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
r={'catalogue_id':A,'meshes':len(objects),'triangles':sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),'native_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'world_bounds':[-118.5,74.5,-250,-118.1,87.5,-160],'inspection_band_unoccupied_x':[-118.1,-117.7],'scope':'90m vertical theater-west upper hull skin and supported internal framing; four boundary seams remain for adjoining shell. No whole-hull/pressure/load certification.','installed':False};(R/'SOURCE_BUILD.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
