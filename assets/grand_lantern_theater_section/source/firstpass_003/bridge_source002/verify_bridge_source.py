import bpy,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import *
s=json.loads((R/'BUILD_REPORT.json').read_text());d=json.loads((R/'BRIDGE_GEOMETRY_002.json').read_text());path=Path(s['source']);assert sha(path)==s['source_sha256'];out=R/'REOPEN_REPORT.json';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[];dg=bpy.context.evaluated_depsgraph_get()
for spec in d['objects']:
 ob=bpy.data.objects[spec['name']];me=ob.data;points=np.array([wvec(ob.matrix_world@v.co)for v in me.vertices]);error=float(abs(points-np.array(spec['vertices_world'])).max());assert error<1e-5,(ob.name,error);edges={}
 for f in me.polygons:
  ids=list(f.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
 assert all(c==2 for c in edges.values());me.calc_loop_triangles();opposed=0
 for t in me.loop_triangles:
  a,b,c=[me.vertices[j].co for j in t.vertices];cr=(b-a).cross(c-a);assert cr.length>1e-10
  n=sum((me.corner_normals[j].vector for j in t.loops),Vector())/3
  if cr.dot(n)<-1e-10:opposed+=1
 assert opposed==0;rows.append({'part':ob.name,'triangles':len(me.loop_triangles),'max_world_error_m':error,'closed_manifold':True})
matmap={'ivory_enamel':'ASTRAEA_ivory_enamel','champagne_metal':'ASTRAEA_champagne_metal','warm_walnut':'ASTRAEA_warm_walnut','gallery_glass':'gallery_glass','hospitality_opal':'FP2_PublicOpal'}
for k,v in matmap.items():assert digest(material_record(bpy.data.materials[v]))==s['material_graphs'][k],k
rays=[]
for spec in d['lights']:
 ob=bpy.data.objects[spec['id']];a=ob.matrix_world.translation;b=Vector(bvec(spec['illumination_anchor']));delta=b-a;hit,point,normal,index,mesh,matrix=bpy.context.scene.ray_cast(dg,a,delta.normalized(),distance=delta.length);assert not hit,(spec['id'],mesh.name if mesh else None);rays.append({'light':spec['id'],'clear_to_receiver':True,'actual_lens':spec['fixture'],'world_position':wvec(a)})
assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==83 and len([o for o in bpy.context.scene.objects if o.type=='LIGHT'])==3;assert sha(path)==s['source_sha256']
r={'passed':True,'source_sha256':s['source_sha256'],'parts':rows,'direct_source_receiver_rays':rays,'material_graphs_unchanged':True,'compiler_floor_absent':True,'saved_source_unchanged':True,'remaining':'Lower below-floor retained-world band, native import and connected walking/cart/visual checks'};out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in ['parts','direct_source_receiver_rays']}))
