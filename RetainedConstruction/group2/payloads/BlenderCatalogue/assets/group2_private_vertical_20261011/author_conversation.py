"""Five bounded conversation overlooks and rear ramps around unchanged furnishings."""
import bpy,bmesh,json,pathlib,sys,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P/'retained_authoring'));from premium_frame import PremiumFrame
data=json.loads((ROOT/'Game/data/group2_private_vertical/CONVERSATION_INTERFACE.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
mats={}
for name,color in [('stone',(.53,.49,.43,1)),('walnut',(.39,.25,.15,1)),('metal',(.55,.48,.33,1)),('guard',(.62,.76,.71,.25))]:
 m=bpy.data.materials.new('G2R_'+name);m.diffuse_color=color;m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=.65 if name!='guard'else .3
 if name=='guard':b.inputs['Alpha'].default_value=.25;m.surface_render_method='DITHERED'
 mats[name]=m
parts={};metrics=[]
def mesh(name,verts,faces,role,key):
 unique=[];lookup={};mapping=[]
 for p in verts:
  q=tuple(round(float(x),6)for x in p)
  if q not in lookup:lookup[q]=len(unique);unique.append(q)
  mapping.append(lookup[q])
 clean=[]
 for face in faces:
  f=list(dict.fromkeys(mapping[i]for i in face))
  if len(f)>=3:clean.append(f)
 d=bpy.data.meshes.new(name);d.from_pydata(unique,[],clean);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 assert all(e.is_manifold for e in bm.edges),name
 volume=bm.calc_volume(signed=True);assert volume>1e-8,name
 bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.setdefault(key,[]).append(o)
 uv=d.uv_layers.new(name='Metric_metres')
 for poly in d.polygons:
  for li in poly.loop_indices:
   p=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(p.x,p.y)
 o['source_index']=int(key);o['same_private_unit']=True;o['source_only_unadopted']=True
 metrics.append({'name':name,'positive_volume_m3':volume,'closed_manifold':True})
 return o

def box(frame,name,u0,u1,v0,v1,h0,h1,role,key):
 verts=[frame.blender(u,v,h)for h in [h0,h1]for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 return mesh(name,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,key)

for row in data['suites']:
 key=str(row['source_index']);assert key!='790';frame=PremiumFrame(row['boundary'])
 u0,u1=row['ramp_u'];start,end=row['ramp_v'];steps=[start+i*(end-start)/12 for i in range(13)]
 verts=[]
 for v in steps:
  rise=.45*(end-v)/(end-start)
  verts.extend([frame.blender(u0,v,0),frame.blender(u1,v,0),frame.blender(u0,v,rise),frame.blender(u1,v,rise)])
 faces=[]
 for i in range(12):
  a=i*4;b=(i+1)*4;faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
 faces.extend([(0,2,3,1),(48,49,51,50)])
 mesh('G2R_'+key+'_ContinuousRearRamp',verts,faces,'stone',key)
 a,b=row['overlook_u'];c,d=row['overlook_v'];box(frame,'G2R_'+key+'_ConversationOverlook',a,b,c,d,0,.45,'stone',key)
 # Continuous transparent infill and rail; ramp throat remains open.
 for label,lo,hi,v0,v1 in [('Fore',a,b,c-.035,c+.035),('Outer',b-.035,b+.035,c,d),('Inner',a-.035,a+.035,c,d),('RearClosed',u1,b,d-.035,d+.035)]:
  if hi-lo<.001:continue
  box(frame,'G2R_'+key+'_'+label+'_Infill',lo,hi,v0,v1,.50,1.47,'guard',key)
  box(frame,'G2R_'+key+'_'+label+'_Foot',lo,hi,v0,v1,.45,.51,'metal',key)
  box(frame,'G2R_'+key+'_'+label+'_Handrail',lo,hi,v0,v1,1.47,1.55,'walnut',key)
 # Sloping handrails and infill follow the entire ramp, including its level seam.
 for side,u in [('L',u0),('R',u1)]:
  for i in range(12):
   v0,v1=steps[i:i+2];h0=.45*(end-v0)/(end-start);h1=.45*(end-v1)/(end-start)
   for role,low,high in [('guard',.05,1.02),('walnut',1.02,1.10)]:
    verts=[frame.blender(x,v,h+offset)for v,h in [(v0,h0),(v1,h1)]for x,offset in [(u-.03,low),(u+.03,low),(u+.03,high),(u-.03,high)]]
    mesh('G2R_'+key+'_Ramp_'+side+'_'+role+'_'+str(i),verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,key)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
native=P/'source/CONVERSATION_RECEIVERS_r001.blend';assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
exports=[]
for key,objects in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 path=ROOT/'Game/assets/group2_private_vertical'/('CONVERSATION_'+key+'_r001.glb');assert not path.exists()
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 exports.append({'source_index':int(key),'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'meshes':len(objects)})
(P/'evidence/CONVERSATION_NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'source_interface_sha256':hashlib.sha256((ROOT/'Game/data/group2_private_vertical/CONVERSATION_INTERFACE.json').read_bytes()).hexdigest(),'exports':exports,'metrics':metrics,'protected_originals_moved':False,'full_pit_perimeter_accepted':False,'production_adoption':False},indent=2)+'\n')
print('PASS five closed ramp/overlook/guard source assemblies; original furniture unchanged')
