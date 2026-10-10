"""Preserve retained architecture coordinates and repair closed floor orientation.
The full original house and linked interiors remain unchanged in their source package.
"""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[4]
SRC=R/'BlenderCatalogue/assets/residential_hotels/tidal_garden_20261007_r001/residential-neighborhood-courts-20261007/tidal_garden_house/outputs/house_r001'
OUT=Path(__file__).resolve().parents[1];EXP=OUT/'exports';EXP.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins={str(SRC/f):sha(SRC/f)for f in ['PLAN.json','house.blend','architecture.glb']}
plan=json.loads((SRC/'PLAN.json').read_text());names=[p['name']for p in plan['parts']]
assert not(OUT/'source/architecture_floor_winding.blend').exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(SRC/'house.blend'),link=False)as(src,dst):
 assert set(names)<=set(src.objects)
 dst.objects=names
objects={o.name:o for o in dst.objects};sourcecol=bpy.data.collections.new('EditableRetainedArchitecture');bpy.context.scene.collection.children.link(sourcecol)
groupkeys={};before={};fixes=[]
for p in plan['parts']:
 o=objects[p['name']];sourcecol.objects.link(o)
 coords=[o.matrix_world@v.co for v in o.data.vertices]
 groupkeys[o.name]=(p['role'],p['category'],int((sum(v.y for v in coords)/len(coords))//25),int(((sum(v.z for v in coords)/len(coords))-78)//4.5))
 before[o.name]=sorted(set(tuple(round(c,6)for c in v)for v in coords))
 if p['category'] not in ['floor','stair_landing']:continue
 old=o.data
 # Source PLAN already has explicit outward slab winding. Recalculation on
 # disconnected triangles changed it. Preserve that authoritative topology.
 uv_faces={}
 for poly in old.polygons:
  record={tuple(round(c,6)for c in old.vertices[old.loops[li].vertex_index].co):tuple(old.uv_layers.active.data[li].uv)for li in poly.loop_indices}
  uv_faces[frozenset(record)]=record
 me=bpy.data.meshes.new(o.name+'_AuthoredWinding')
 me.from_pydata([(v[0],-v[2],v[1])for v in p['verts']],[],p['faces']);me.update()
 for material in old.materials:me.materials.append(material)
 uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  key=frozenset(tuple(round(c,6)for c in me.vertices[me.loops[li].vertex_index].co)for li in poly.loop_indices)
  assert key in uv_faces,(o.name,'face correspondence')
  for li in poly.loop_indices:
   coord=tuple(round(c,6)for c in me.vertices[me.loops[li].vertex_index].co);uv.data[li].uv=uv_faces[key][coord]
 o.data=me
 assert before[o.name]==sorted(set(tuple(round(c,6)for c in o.matrix_world@v.co)for v in me.vertices)),o.name
 y0=min(v[1]for v in p['verts']);y1=max(v[1]for v in p['verts']);horizontal=0
 for face in p['faces']:
  vs=[Vector(p['verts'][j])for j in face]
  if len({round(v.y,6)for v in vs})!=1:continue
  normal=(vs[1]-vs[0]).cross(vs[2]-vs[0]);top=abs(vs[0].y-y1)<1e-6
  assert normal.y>0 if top else normal.y<0
  horizontal+=1
 fixes.append({'name':o.name,'vertices':len(me.vertices),'horizontal_faces_checked':horizontal,'coordinate_set_unchanged':True,'face_topology_unchanged':True,'uv_correspondence_preserved':True})
 print('CORRECTED_SOURCE_FLOOR',o.name,flush=True)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source/architecture_floor_winding.blend'))
groups={}
for p in plan['parts']:
 o=objects[p['name']];g=groups.setdefault(groupkeys[o.name],{'verts':[],'faces':[],'uv':[],'parts':[],'material':o.data.materials[0]})
 coords=[o.matrix_world@v.co for v in o.data.vertices];off=len(g['verts']);foff=len(g['faces']);g['verts'].extend(tuple(v)for v in coords);g['faces'].extend(tuple(off+j for j in f.vertices)for f in o.data.polygons);g['uv'].extend(tuple(u.uv)for u in o.data.uv_layers.active.data);g['parts'].append({'source_part_id':o.name,'vertex_start':off,'vertex_count':len(coords),'face_start':foff,'face_count':len(o.data.polygons)})
exportcol=bpy.data.collections.new('EXPORT_COMPACT_ARCHITECTURE');bpy.context.scene.collection.children.link(exportcol)
bpy.ops.object.select_all(action='DESELECT')
for i,(key,g)in enumerate(groups.items()):
 me=bpy.data.meshes.new('TG_Batch_'+str(i));me.from_pydata(g['verts'],[],g['faces']);me.materials.append(g['material']);uv=me.uv_layers.new(name='MetreScaled');assert len(uv.data)==len(g['uv'])
 for a,b in zip(uv.data,g['uv']):a.uv=b
 ob=bpy.data.objects.new('TG_Batch_'+str(i),me);exportcol.objects.link(ob);ob.select_set(True);ob['source_part_ranges']=g['parts'];ob['role']=key[0];ob['category']=key[1];ob['source_plan_sha256']=sha(SRC/'PLAN.json');ob['runtime_collision']=key[1]not in ['soil','fixture','water']
bpy.ops.export_scene.gltf(filepath=str(EXP/'architecture_floor_winding.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
assert len(groups)==339
assert all(sha(p)==h for p,h in pins.items())
report={'status':'SOURCE_DERIVATIVE_READY_FOR_RUNTIME_CHECK','purpose':'Restore explicit outward slab face winding from the retained source PLAN; no moved vertices, widened routes, or double-sided collision workaround','original_inputs':pins,'source_parts':len(names),'compact_batches':len(groups),'corrected_closed_parts':fixes,'native_sha256':sha(OUT/'source/architecture_floor_winding.blend'),'export_sha256':sha(EXP/'architecture_floor_winding.glb'),'limits':'Architecture derivative only. Full original linked house retained; no guest-unit, runtime support-transfer or final-art acceptance.'}
(OUT/'SOURCE_CORRECTION_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('TIDAL_FLOOR_CORRECTION',len(fixes),'parts',len(groups),'batches',flush=True)
