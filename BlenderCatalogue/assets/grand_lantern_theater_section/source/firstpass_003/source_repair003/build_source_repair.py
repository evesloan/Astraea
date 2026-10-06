"""Approved bounded simplification of 18 hidden nuts, into a NEW derivative only."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');BASE=P/'source/firstpass_002/source/AST-CUL-005_firstpass_002.blend';EXPECTED='dbf534bb1a9743bcf608072440680758bde94e7f58e707ca03a2934b41619a2a';OUT=R/'AST-CUL-005_firstpass_003.blend'
sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import baseline_snapshot,compare_subset,sha,verify_new_geometry
assert sha(BASE)==EXPECTED and not OUT.exists() and not (R/'BUILD_REPORT.json').exists();bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
names=['THEATER_%s_MAIN_SUSP_%02d_%s_nut'%(deck,index,side)for deck in ['D11','D12','D13']for index in [1,2,3]for side in [-1,1]];assert len(names)==18
before=baseline_snapshot(bpy);records=[];scales=json.loads((P.parents[1]/'materials/material_manifest.json').read_text())['materials']['champagne_metal']['meters_per_tile_uv']
for name in names:
 ob=bpy.data.objects[name];old=ob.data;assert ob.get('collision_role')=='static_mechanism' and not ob.get('motion_group');points=[ob.matrix_world@v.co for v in old.vertices];lo=Vector(tuple(min(p[k]for p in points)for k in range(3)));hi=Vector(tuple(max(p[k]for p in points)for k in range(3)));center=(lo+hi)*.5;low=lo-center;high=hi-center
 outer=[(low.x,low.y),(high.x,low.y),(high.x,high.y),(low.x,high.y)];inner=[(-.0035,-.0035),(.0035,-.0035),(.0035,.0035),(-.0035,.0035)]
 v=[(x,y,z)for z in [low.z,high.z]for x,y in outer+inner];faces=[]
 for i in range(4):
  j=(i+1)%4;faces.extend([(8+i,8+j,12+j,12+i),(4+i,4+j,j,i),(i,j,8+j,8+i),(4+i,12+i,12+j,4+j)])
 me=bpy.data.meshes.new(name+'_robust_square_bore');me.from_pydata(v,[],faces);me.materials.clear()
 for mat in old.materials:me.materials.append(mat)
 me.update();uv=me.uv_layers.new(name='metric_material_uv')
 for face in me.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in face.loop_indices:
   pt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pt[axes[0]]/scales[0],pt[axes[1]]/scales[1])
 ob.data=me;ob.matrix_world=Matrix.Translation(center);ob['source_revision003']='Bounded approved low-poly square through-bore nut; same outer bounds, material and mounting role; no manufacturing certification';ob['source_previous_mesh']=old.name
 bpy.context.view_layer.update();newpoints=[ob.matrix_world@v.co for v in me.vertices];error=max(abs(min(p[k]for p in newpoints)-lo[k])for k in range(3));error=max(error,max(abs(max(p[k]for p in newpoints)-hi[k])for k in range(3)));assert error<1e-5,(name,error)
 me.calc_loop_triangles();volume=sum(me.vertices[t.vertices[0]].co.dot(me.vertices[t.vertices[1]].co.cross(me.vertices[t.vertices[2]].co))/6 for t in me.loop_triangles);assert volume>0
 counts={}
 for f in me.polygons:
  ids=list(f.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
 assert all(c==2 for c in counts.values());assert len(me.loop_triangles)==32
 before['objects'].pop(name)
 records.append({'name':name,'old_vertices':len(old.vertices),'new_vertices':len(me.vertices),'new_triangles':32,'old_world_bounds_blender':[list(lo),list(hi)],'outer_bounds_error_m':error,'bore_flat_width_m':.007,'minimum_shank_diametric_clearance_m':.001,'closed_manifold_edges':len(counts),'signed_volume_m3':volume,'material_names':[m.name for m in me.materials]})
assert not compare_subset(before,baseline_snapshot(bpy));assert len([o for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003'])==2200
verify_new_geometry(bpy,names);bpy.context.scene['revision003_scope']='Only 18 hidden suspension nuts simplified; original source retained; all other objects/materials and 2200 chairs preserved.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));assert sha(BASE)==EXPECTED
report={'source':str(OUT),'source_sha256':sha(OUT),'base_source_sha256':EXPECTED,'scope':'18 approved hidden nut mesh derivatives only; no other saved geometry, material, light, camera or instance change','records':records,'preserved_snapshot':before,'expected_chairs':2200,'pending':['Independent reopened preservation and mesh checks','Strict new source/export attribute verification','Import/contact/traversal and bridge/floor adoption']};(R/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'source_sha256':report['source_sha256'],'nuts':18,'chairs':2200}))
