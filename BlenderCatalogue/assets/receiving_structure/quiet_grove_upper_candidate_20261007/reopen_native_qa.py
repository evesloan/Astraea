import bpy,pathlib,json,collections
D=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(D/'root_build/quiet_grove_upper_receiver.blend'))
rows=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 verts=[obj.matrix_world@v.co for v in obj.data.vertices];world=[[v.x,v.z,-v.y] for v in verts];edges=collections.Counter(tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))) for p in obj.data.polygons for i in range(len(p.vertices)))
 rows.append({'id':obj.name,'vertices':world,'faces':[list(p.vertices) for p in obj.data.polygons],'bounds':[min(v[i] for v in world) for i in range(3)]+[max(v[i] for v in world) for i in range(3)],'closed_edges':all(n==2 for n in edges.values()),'material_names':[s.name for s in obj.data.materials]})
(D/'NATIVE_REOPENED_GEOMETRY.json').write_text(json.dumps(rows,indent=2));print('REOPENED_NATIVE_MESHES',len(rows),'CLOSED',all(r['closed_edges'] for r in rows))
