"""Editable lift-fit successor, retaining every unaffected corrected source part."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1]
S=R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/sunset_conservatory_house/outputs/house_r002/house.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=sha(S);p=json.loads((O/'LIFT_GEOMETRY_PLAN.json').read_text());added=set(p['lift_successor']['added_source_parts']);retained=[q['name']for q in p['parts']if q['name']not in added]
assert not(O/'source/architecture_lift_fit.blend').exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(S),link=False)as(src,dst):
 assert set(retained)<=set(src.objects);dst.objects=retained
col=bpy.data.collections.new('EditableSunsetLiftSuccessor');bpy.context.scene.collection.children.link(col)
objects={o.name:o for o in dst.objects};materials={}
for q in p['parts']:
 if q['name']in objects:
  o=objects[q['name']];col.objects.link(o);materials[q['role']]=o.data.materials[0]
for q in p['parts']:
 if q['name']not in added:continue
 if q['kind']=='mesh':vs=q['verts'];fs=q['faces']
 else:
  a=Vector(q['a']);b=Vector(q['b']);t=(b-a).normalized();s=Vector((0,0,1))if abs(t.z)<.95 else Vector((1,0,0));s=(s-t*s.dot(t)).normalized();u=t.cross(s).normalized()
  vs=[tuple(pt+s*w+u*h)for pt in[a,b]for w,h in[(-q['width']/2,-q['depth']/2),(q['width']/2,-q['depth']/2),(q['width']/2,q['depth']/2),(-q['width']/2,q['depth']/2)]]
  fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(q['name']);me.from_pydata([(v[0],-v[2],v[1])for v in vs],[],fs);me.update();me.materials.append(materials[q['role']]);uv=me.uv_layers.new(name='MetreScaled')
 for face in me.polygons:
  n=face.normal;u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in face.loop_indices:
   pt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pt.dot(u),pt.dot(v))
 ob=bpy.data.objects.new(q['name'],me);col.objects.link(ob);objects[q['name']]=ob
# Carry forward the installed r002 floor-top winding correction into the editable native successor.
corrected=0
for q in p['parts']:
 if q['category']!='floor' or q['name']in added: continue
 o=objects[q['name']]; me=o.data; top=max(v.co.z for v in me.vertices)
 vs=[tuple(v.co) for v in me.vertices]; fs=[]; uvs=[]; count=0
 for face in me.polygons:
  ids=list(face.vertices); loops=list(face.loop_indices)
  if face.normal.z < -.99 and all(abs(vs[i][2]-top)<.00001 for i in ids): ids.reverse();loops.reverse();count+=1
  fs.append(ids);uvs.extend(tuple(me.uv_layers.active.data[i].uv) for i in loops)
 if not count: continue
 new=bpy.data.meshes.new(me.name+'_UpwardFloor');new.from_pydata(vs,[],fs);new.update()
 for mat in me.materials:new.materials.append(mat)
 uv=new.uv_layers.new(name='MetreScaled')
 for a,b in zip(uv.data,uvs):a.uv=b
 o.data=new;corrected+=count
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/architecture_lift_fit.blend'),compress=True)
groups={}
for q in p['parts']:
 o=objects[q['name']];coords=[o.matrix_world@v.co for v in o.data.vertices];key=(q['role'],q['category'],int((sum(v.y for v in coords)/len(coords))//25),int(((sum(v.z for v in coords)/len(coords))-78)//4.5));g=groups.setdefault(key,{'verts':[],'faces':[],'uv':[],'parts':[],'material':o.data.materials[0]});off=len(g['verts']);foff=len(g['faces']);g['verts'].extend(tuple(v)for v in coords);g['faces'].extend(tuple(off+j for j in f.vertices)for f in o.data.polygons);g['uv'].extend(tuple(u.uv)for u in o.data.uv_layers.active.data);g['parts'].append({'source_part_id':o.name,'vertex_start':off,'vertex_count':len(coords),'face_start':foff,'face_count':len(o.data.polygons)})
exp=bpy.data.collections.new('EXPORT');bpy.context.scene.collection.children.link(exp);bpy.ops.object.select_all(action='DESELECT')
for i,(key,g)in enumerate(groups.items()):
 me=bpy.data.meshes.new('SC_Batch_'+str(i));me.from_pydata(g['verts'],[],g['faces']);me.materials.append(g['material']);uv=me.uv_layers.new(name='MetreScaled');assert len(uv.data)==len(g['uv'])
 for a,b in zip(uv.data,g['uv']):a.uv=b
 ob=bpy.data.objects.new('SC_Batch_'+str(i),me);exp.objects.link(ob);ob.select_set(True);ob['source_part_ranges']=[{k:v for k,v in part.items() if k not in ['face_start','face_count']} for part in g['parts']];ob['role']=key[0];ob['category']=key[1];ob['source_plan_sha256']=sha(O/'LIFT_GEOMETRY_PLAN.json');ob['runtime_collision']=key[1]not in['soil','fixture','water']
(O/'exports').mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(O/'exports/architecture_lift_fit.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
assert sha(S)==pin
report={'status':'SOURCE_EXPORTED_NOT_ADOPTED','predecessor_native_sha256':pin,'source_plan_sha256':sha(O/'LIFT_GEOMETRY_PLAN.json'),'native_sha256':sha(O/'source/architecture_lift_fit.blend'),'export_sha256':sha(O/'exports/architecture_lift_fit.glb'),'mesh_count':len(groups),'parts':len(p['parts']),'corrected_native_floor_faces':corrected,'preserved_parts':len(retained),'limits':'Runtime movement/contact/visual checks pending. Original source unchanged.'}
(O/'SOURCE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('SUNSET_LIFT_SOURCE',json.dumps(report),flush=True)
