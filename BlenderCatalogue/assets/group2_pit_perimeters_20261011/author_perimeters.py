"""Editable raised perimeter receiver and exact floor/edge source exports."""
import bpy,bmesh,pathlib,json,hashlib,sys,argparse
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--revision',default='r003');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else [])
data_path=ROOT/'Game/data/group2_pit_perimeters'/('PLAN_'+args.revision+'.json')
data=json.loads(data_path.read_text())
sys.path.insert(0,str(ROOT/'BlenderCatalogue/assets/group2_private_vertical_20261011/retained_authoring'));from premium_frame import PremiumFrame
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
for role,color in [('stone',(.53,.49,.43,1)),('walnut',(.39,.25,.15,1)),('metal',(.55,.48,.33,1)),('glass',(.62,.76,.71,.25))]:
 m=bpy.data.materials.new('G2P_'+role);m.diffuse_color=color;m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=.65
 if role=='glass':b.inputs['Alpha'].default_value=.25;m.surface_render_method='DITHERED'
 materials[role]=m
parts={};metrics=[]
def mesh(name,vertices,faces,role,key):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 assert all(e.is_manifold for e in bm.edges),name
 volume=bm.calc_volume(signed=True);assert volume>1e-7,name;bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(materials[role]);parts.setdefault(key,[]).append(o)
 uv=d.uv_layers.new(name='Metric_metres')
 for p in d.polygons:
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x,q.y)
 o['source_index']=int(key);o['same_private_unit']=True;o['source_only_unadopted']=True
 metrics.append({'name':name,'positive_volume_m3':volume,'closed_manifold':True})
 return o
def prism_region(row,key):
 vertices=[];faces=[];lookup={}
 def vert(p,h):
  q=(float(p[0]),-float(p[1]),float(h))
  if q not in lookup:lookup[q]=len(vertices);vertices.append(q)
  return lookup[q]
 for triangle in row['triangles']:
  faces.append(tuple(vert(p,102.45)for p in triangle));faces.append(tuple(vert(p,102)for p in reversed(triangle)))
 for ring in [row['boundary']]+row['holes']:
  for i,a in enumerate(ring):
   b=ring[(i+1)%len(ring)];faces.append((vert(a,102),vert(b,102),vert(b,102.45),vert(a,102.45)))
 return mesh(row['id'],vertices,faces,'stone',key)
def beam(frame,name,a,b,width,h0,h1,role,key):
 # New shapes follow the fitted section profile; retained assets never shear.
 import math
 du=b[0]-a[0];dv=b[1]-a[1];length=math.hypot(du,dv);assert length>.001
 x=-dv/length*width/2;y=du/length*width/2
 outline=[(a[0]+x,a[1]+y),(b[0]+x,b[1]+y),(b[0]-x,b[1]-y),(a[0]-x,a[1]-y)]
 v=[frame.blender(u,w,h)for h in [h0,h1]for u,w in outline]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,key)
for row in data['suites']:
 key=str(row['source_index']);assert key!='790'
 assert not row['unsupported_selected_feet']
 contract=json.loads((ROOT/'Game/data/group2_completion/contracts'/f'{key}.json').read_text());frame=PremiumFrame(contract['floor_proposal']['boundary'])
 for region in row['raised_regions']:prism_region(region,key)
 # A continuous low seating-court perimeter; a level gallery portal preserves
 # the original route into the pit. Rear standing terraces receive full infill.
 boundary=row['pit_boundary_uv']
 for i,a in enumerate(boundary):
  b=boundary[(i+1)%len(boundary)];segments=[(a,b)]
  if a[0]==b[0]==10.8:
   lo,hi=sorted([a[1],b[1]]);segments=[((10.8,lo),(10.8,9.55)),((10.8,10.85),(10.8,hi))]
  for n,(p,q)in enumerate(segments):
   if abs(p[0]-q[0])+abs(p[1]-q[1])<.005:continue
   beam(frame,f'G2P_{key}_PitEdge_{i}_{n}',p,q,.08,0,.45,'walnut',key)
 # Rear edge overlooking the lower conversation court; preserve the wide
 # original seating route and do not put a new barrier across its portal.
 for i,(a,b)in enumerate([((16.95,12.6),(11.3,12.6)),((11.3,12.6),(11.3,10.9))]):
  beam(frame,f'G2P_{key}_RearGuardGlass_{i}',a,b,.055,.50,1.47,'glass',key)
  beam(frame,f'G2P_{key}_RearGuardRail_{i}',a,b,.07,1.47,1.55,'walnut',key)
 # Retain the rear ramp throat while guarding the expanded outside edges.
 for i,(a,b)in enumerate([((9,11),(9,14)),((9,14),(11.5,14)),((12.7,14),(17.7,14))]):
  beam(frame,f'G2P_{key}_OuterGuard_{i}',a,b,.055,.50,1.47,'glass',key)
  beam(frame,f'G2P_{key}_OuterRail_{i}',a,b,.07,1.47,1.55,'walnut',key)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
native=P/'source'/('PIT_PERIMETERS_'+args.revision+'.blend');assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
exports=[]
for key,objects in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 path=ROOT/'Game/assets/group2_pit_perimeters'/f'PERIMETER_{key}_{args.revision}.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 exports.append({'source_index':int(key),'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(P/'evidence'/('NATIVE_'+args.revision+'.json')).write_text(json.dumps({'pass':True,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),'exports':exports,'metrics':metrics,'originals_changed':False,'production_adoption':False},indent=2)+'\n')
print('PASS five editable private pit perimeter and terrace receivers')
