import bpy,json
from mathutils import Vector
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]; pts=[(p.x,p.z,-p.y) for p in pts]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 rows.append({'name':o.name,'min':lo,'max':hi,'vertices':len(o.data.vertices),'properties':{k:str(o[k]) for k in o.keys()}})
open('/workspace/mineral-evidence/NATIVE_GEOMETRY.json','w').write(json.dumps(rows,indent=2)+'\n')
print('MESHES',len(rows))
for r in rows:
 if any(s in r['name'].lower() for s in ['wall','perimeter','door','screen','counter','return','threshold','floor']):print(r['name'],[round(x,3) for x in r['min']],[round(x,3) for x in r['max']])
