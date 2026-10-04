"""Reload saved source; inspect closed meshes and actual world-space joint intersections."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];ID='AST-AQU-006';source=BASE/'source'/f'{ID}.blend';manifest=json.loads((BASE/f'{ID}.manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];records=[];trees={}
for o in parts:
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);bmesh.ops.triangulate(bm,faces=list(bm.faces));tree=BVHTree.FromBMesh(bm);trees[o.name]=tree
    records.append({'part':o.name,'vertices':len(bm.verts),'triangles':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_edges for v in bm.verts),'signed_volume_m3':bm.calc_volume(signed=True),'uv_layers':list(o.data.uv_layers.keys()),'scale':list(o.scale),'packed_textures':all(n.image.packed_file is not None for mat in o.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')});bm.free()
joins=[]
for row in manifest['support_and_join_records']:
    names=row['parts'];pairs=[]
    for a,b in zip(names,names[1:]):
        n=len(trees[a].overlap(trees[b]));pairs.append({'parts':[a,b],'surface_triangle_intersections':n,'surfaces_intersect':n>0})
    joins.append({'proposed_join':row,'actual_surface_checks':pairs})
# Independently measure grip clearance between midpoint lower surface and hull crown at matching x/y.
clear=[]
for g in manifest['design_proposals']['grips']:
    p=Vector(g['center_m']);hit=trees['continuous_oval_hull_with_raised_back_cradle'].ray_cast(p+Vector((0,0,-.03)),Vector((0,0,-1)),.4);distance=None if hit[0] is None else p.z-g['grip_diameter_m']/2-hit[0].z
    clear.append({'side':g['side'],'palm_center_lower_surface_to_coaming_m':distance,'measured_by':'Downward hull surface ray from just below grip','passes_60mm_proposal':distance is not None and distance>.06})
# Membrane perimeter terminates inside hull; a visible binding lies across its inner surface.
out={'scope':'Saved editable source independently reloaded; geometry only, no loads, buoyancy or species fit','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':records,'joins':joins,'grip_clearances':clear,'all_closed_positive_volume':all(r['nonmanifold_edges']==0 and r['loose_vertices']==0 and r['signed_volume_m3']>0 for r in records),'all_packed':all(r['packed_textures'] for r in records),'all_recorded_pairs_intersect':all(p['surfaces_intersect'] for j in joins for p in j['actual_surface_checks']),'grip_clearance_proposal_passes':all(x['passes_60mm_proposal'] for x in clear)}
(BASE/'qa/source_reload_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in('parts','joins')},indent=2))
