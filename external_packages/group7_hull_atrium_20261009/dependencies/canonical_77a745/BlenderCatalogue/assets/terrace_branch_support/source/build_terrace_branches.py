"""Fitted branching terrace support, connecting a front column to the upper gallery.
Three height fits share one construction design; editable Blender parts remain separate.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
for suffix,H in [('H826',8.26),('H576',5.76),('H426',4.26)]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);mats={};parts=[]
 for role in ['ivory_enamel','champagne_metal','warm_walnut']:
  m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.66;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
 def mesh(name,v,f,role):
  d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
  for p in d.polygons:
   for li in p.loop_indices:q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.5,(q.y+q.z)*.5)
  return o
 for branch in [-1,0,1]:
  points=[Vector((.05,branch*.20,H-.85)),Vector((1.1,branch*.34,H-.79)),Vector((2.2,branch*.63,H-.47)),Vector((3.5,branch*.93,H-.20)),Vector((5.2,branch*1.25,H-.12))]
  v=[];profile=[(-.16,-.12),(.16,-.12),(.20,-.06),(.20,.06),(.12,.12),(-.12,.12),(-.20,.06),(-.20,-.06)];n=len(profile)
  for i,p in enumerate(points):
   tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();side=Vector((0,1,0));up=tangent.cross(side).normalized()
   for width,depth in profile:v.append(tuple(p+side*width+up*depth))
  faces=[tuple(reversed(range(n))),tuple(range((len(points)-1)*n,len(points)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(points)-1) for j in range(n)]
  mesh('BRANCH_Profile_'+str(branch),v,faces,'ivory_enamel')
  # Broad, flush bearing shoe at the upper gallery underside.
  x=5.2;y=branch*1.25
  v=[(x+dx,y+dy,z) for z in [H-.15,H] for dx,dy in [(-.42,-.26),(.42,-.26),(.42,.26),(-.42,.26)]]
  mesh('BRANCH_BearingShoe_'+str(branch),v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'champagne_metal')
  o=bpy.data.objects.new('DATUM_upper_bearing_'+str(branch),None);bpy.context.collection.objects.link(o);o.location=(x,y,H)
 # A profiled soffit ties the three forks into one readable architectural fan.
 v=[(.45,-.63,H-.97),(2.2,-.91,H-.62),(4.9,-1.39,H-.28),(4.9,1.39,H-.28),(2.2,.91,H-.62),(.45,.63,H-.97)]
 v=v+[(x,y,z+.06) for x,y,z in v];mesh('BRANCH_RecessedSoffit',v,[(5,4,3,2,1,0),(6,7,8,9,10,11)]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)],'warm_walnut')
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();aid='AST-STR-002-'+suffix;blend=ROOT/'source'/(aid+'.blend');glb=ROOT/'exports'/(aid+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
 tri=0
 for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 (ROOT/(aid+'.manifest.json')).write_text(json.dumps({'catalogue_id':'AST-STR-002','variant_id':aid,'name':'Branching terrace-to-gallery bearing fan','source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','triangles':tri,'bearing_height_m':H,'outward_reach_m':5.62,'fit_policy':'Local positive X points out from the atrium to the upper gallery; shoe tops meet its existing underside','status':'Draft; source and upper-floor contact checks pending','new_design_count':1 if suffix=='H826' else 0,'source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('TERRACE_BRANCH_CREATED',aid,tri)
