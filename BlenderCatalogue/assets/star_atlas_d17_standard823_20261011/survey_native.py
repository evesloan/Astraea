from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2]
source=R/'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17Standard823Recess.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 vertices=[list(ob.matrix_world@v.co)for v in ob.data.vertices]
 # Native authoring axes to Godot axes.
 vertices=[[v[0],v[2],-v[1]]for v in vertices]
 rows.append({'name':ob.name,'verts':vertices,'faces':[list(p.vertices)for p in ob.data.polygons],'bounds':[[min(v[i]for v in vertices)for i in range(3)],[max(v[i]for v in vertices)for i in range(3)]],'materials':[m.name if m else None for m in ob.data.materials],'modifiers':[m.type for m in ob.modifiers]})
out={'status':'SURVEY_COMPLETE_UNMODIFIED_NATIVE','source':str(source.relative_to(R)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'meshes':rows}
(W/'ROOM823_NATIVE_GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'meshes':len(rows),'source_unchanged':out['sha256'],'floor_roof_rest_candidates':[{k:q[k]for k in ['name','bounds']}for q in rows if any(s in q['name'].lower()for s in ['floor','roof','bed','rest','light'])]}))
