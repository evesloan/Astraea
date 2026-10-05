"""Editable structural public core, with real shaft enclosure and guarded stair edges."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CIR-005'
assert all(a['catalogue_id']!=AID or a['family']=='primary_atrium_core'for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
D=json.loads((R/'source/section_contract.json').read_text());ys=D['floor_y'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal']:
 m=bpy.data.materials.new(role);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=.78
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials'/(role+'.png')));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],n.inputs['Base Color']);materials[role]=m
m=bpy.data.materials.new('core_opal_lens');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(1,.96,.88,1);n.inputs['Emission Color'].default_value=(1,.93,.82,1);n.inputs['Emission Strength'].default_value=.65;materials['lens']=m
parts=[]
def box(name,x0,x1,z0,z1,y0,y1,role):
 verts=[(x,-(z+100),y)for y in [y0,y1]for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
 faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(materials[role]);uv=mesh.uv_layers.new(name='MetreScaled')
 for p in mesh.polygons:
  normal=p.normal.normalized();u=(Vector((1,0,0))-normal*normal.x).normalized()if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
  for k in p.loop_indices:
   q=mesh.vertices[mesh.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(v))
 parts.append(o)
def datum(name,x,y,z):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=(x,-(z+100),y)
# Shaft skins are outside the actual moving cabin and keep every absent stop safe.
box('CORE_ShaftRear',1.88,2,-108.2,-103.8,-.24,109.85,'ivory_enamel')
box('CORE_ShaftNorth',-2,2,-108.2,-108.08,-.24,109.85,'ivory_enamel')
box('CORE_ShaftSouth',-2,2,-103.92,-103.8,-.24,109.85,'ivory_enamel')
box('CORE_PitPan',-1.99,1.99,-108.19,-103.81,-.24,-.20,'champagne_metal')
for i,y in enumerate(ys):
 ceil=ys[i+1]-.24 if i<17 else 109.73
 box('CORE_GateSpandrel_%02d'%i,-2,-1.88,-108.2,-103.8,y+2.82,ceil,'ivory_enamel')
 for side in [-1,1]:
  x=side*7.8
  box('CORE_OuterWall_%02d_%s'%(i,side),x-.08,x+.08,-113,-80,y,ceil,'ivory_enamel')
  box('CORE_WallDado_%02d_%s'%(i,side),x-side*.14-.025,x-side*.14+.025,-113,-80,y+.12,y+.78,'warm_walnut')
  # Incoming8m spine is narrower than the lobby. Guard the unsupported wings.
  a,b=(-7.8,-4.0)if side<0 else(4.0,7.8)
  for h in [.14,1.06]:box('CORE_ForeWingRail_%02d_%s_%s'%(i,side,h),a,b,-113.04,-112.96,y+h,y+h+.08,'champagne_metal')
  for xpost in [a+.12,b-.12]:box('CORE_ForeWingPost_%02d_%s_%s'%(i,side,xpost),xpost-.04,xpost+.04,-113.04,-112.96,y,y+1.14,'champagne_metal')
  # Main framing stays outside the nominal4.3m bypass lanes.
  for z in [-103.5,-96.5]:box('CORE_Pier_%02d_%s_%s'%(i,side,z),side*3.35-.10,side*3.35+.10,z-.12,z+.12,y,ceil,'champagne_metal')
  xlight=side*5.6
  box('CORE_LightCase_%02d_%s'%(i,side),xlight-.32,xlight+.32,-100.28,-99.72,ceil-.18,ceil,'warm_walnut')
  box('CORE_LightLens_%02d_%s'%(i,side),xlight-.27,xlight+.27,-100.23,-99.77,ceil-.20,ceil-.18,'lens')
  datum('light_%02d_%s'%(i,side),xlight,ceil-.23,-100)
 for z in [-103.5,-96.5]:box('CORE_Crossbeam_%02d_%s'%(i,z),-7.72,7.72,z-.12,z+.12,ceil-.26,ceil,'warm_walnut')
 if i>0:
  # Per-level slab guards, separate from the descending flight's own rails.
  for x in [-3.18,3.18]:
   for h in [.14,1.06]:box('CORE_StairSideRail_%02d_%s_%s'%(i,x,h),x-.04,x+.04,-96,-85.2,y+h,y+h+.08,'champagne_metal')
   for z in [-95.9,-90.6,-85.3]:box('CORE_StairSidePost_%02d_%s_%s'%(i,x,z),x-.04,x+.04,z-.04,z+.04,y,y+1.14,'champagne_metal')
  for h in [.14,1.06]:
   box('CORE_StairRearRail_%02d_%s'%(i,h),-3.18,3.18,-85.24,-85.16,y+h,y+h+.08,'champagne_metal')
   box('CORE_StairFrontDivider_%02d_%s'%(i,h),-.48,.48,-96.17,-96.09,y+h,y+h+.08,'champagne_metal')
  for x in [-.44,.44]:box('CORE_FrontDividerPost_%02d_%s'%(i,x),x-.04,x+.04,-96.17,-96.09,y,y+1.14,'champagne_metal')
  for x in [-3.18,0,3.18]:box('CORE_StairRearPost_%02d_%s'%(i,x),x-.04,x+.04,-85.24,-85.16,y,y+1.14,'champagne_metal')
  if i==17:
   box('CORE_TopFrontGuardPost',3.08,3.16,-96.17,-96.09,y,y+1.14,'champagne_metal')
   for h in [.14,1.06]:box('CORE_TopNoFurtherStair_%s'%h,.48,3.18,-96.17,-96.09,y+h,y+h+.08,'champagne_metal')
 datum('landing_%02d'%(i+1),-5.4,y,-100)
# The top public landing has a proper opaque cover; it is not a new deck.
box('CORE_TopCover',-7.88,7.88,-113,-80,109.73,109.85,'ivory_enamel')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();src=R/'source'/(AID+'.blend');out=R/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(src));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
tri=sum(len(p.vertices)-2 for o in parts for p in o.data.polygons)
(R/(AID+'.manifest.json')).write_text(json.dumps({'catalogue_id':AID,'name':'Central18-deck public core enclosure, framing and guarded landings','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','triangles':tri,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'Original structural platform architecture; runtime and visual checks pending'},indent=2)+'\n')
print(AID,tri)
