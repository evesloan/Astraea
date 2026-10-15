from pathlib import Path
import bpy,json
D=Path(__file__).resolve().parent;p=D/'retained_source/BlenderCatalogue/assets/grand_pool_first_pass/finish_envelope/source/grand_pool_finish_envelope.blend';bpy.ops.wm.open_mainfile(filepath=str(p));print('SCENE',len(bpy.context.scene.objects),'ALL',len(bpy.data.objects));rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and('Market_2'in o.name or 'GPF_BATCH_019'in o.name):
  vs=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'blender_min':[min(v[i]for v in vs)for i in range(3)],'blender_max':[max(v[i]for v in vs)for i in range(3)]})
(D/'FINISH_SOURCE_OBJECT_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
