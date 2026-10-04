"""Actual source-mesh cross-component clearance; no host coordinates inferred."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];target=CAT/'assets/botanical_transition/source/AST-BOT-010.blend';plant=BASE/'source/AST-BOT-008.blend';placement=Vector((1.10,.690,.790))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geometry(obs,off=Vector((0,0,0))):
 vs=[];ps=[]
 for o in obs:
  n=len(vs);vs.extend(o.matrix_world@v.co+off for v in o.data.vertices);o.data.calc_loop_triangles();ps.extend(tuple(n+i for i in t.vertices)for t in o.data.loop_triangles)
 return vs,ps
bpy.ops.wm.open_mainfile(filepath=str(target));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'and o.name in ('rear_rising_coping','rear_rising_retaining_wall')];assert len(obs)==2;vs,ps=geometry(obs);surface=BVHTree.FromPolygons(vs,ps,all_triangles=True);parts=[o.name for o in obs]
bpy.ops.wm.open_mainfile(filepath=str(plant));pv,pp=geometry([o for o in bpy.context.scene.objects if o.type=='MESH'],placement);plants=BVHTree.FromPolygons(pv,pp,all_triangles=True);overlaps=surface.overlap(plants);nearest=min(surface.find_nearest(p)[3]for p in pv)
report={'scope':'Relative component proposal only, actual Blender source surfaces; final host placement unknown','plant_source_sha256':sha(plant),'transition_source_sha256':sha(target),'plant_transform_source_translation_m':list(placement),'checked_transition_parts':parts,'actual_triangle_overlap_pairs':len(overlaps),'nearest_plant_vertex_to_actual_transition_surface_m':nearest,'nearest_metric_limit':'Vertex-to-triangle samples, not exact global mesh distance','all_plant_triangles_checked_for_overlap':len(pp),'passes':len(overlaps)==0};(BASE/'qa/trailing_transition_clearance.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
