import bpy,pathlib,json,sys
R=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'sections/846_deluxe/846_deluxe.blend'))
ob=bpy.data.objects['SmallDoorLabel'];results=[]
sys.path.insert(0,str(R));from editable_label import repair_label
for mode in ['sliver_repair']:
 ob.modifiers.clear();ob.data.extrude=0 if mode=='flat' else .001
 if mode=='dissolve':
  m=ob.modifiers.new('EditableLabelDissolve','DECIMATE');m.decimate_type='DISSOLVE';m.angle_limit=.02;m.use_dissolve_boundaries=True
 if mode=='sliver_repair':repair_label(ob)
 bpy.context.view_layer.update();e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();me.calc_loop_triangles();vv=[e.matrix_world@v.co for v in me.vertices]
 bad=sum((vv[t.vertices[1]]-vv[t.vertices[0]]).cross(vv[t.vertices[2]]-vv[t.vertices[0]]).length<1e-10 for t in me.loop_triangles)
 results.append({'mode':mode,'triangles':len(me.loop_triangles),'degenerate':bad});e.to_mesh_clear()
(R/'EDITABLE_LABEL_REPAIR_CHECK.json').write_text(json.dumps(results,indent=2));print(results,flush=True)
