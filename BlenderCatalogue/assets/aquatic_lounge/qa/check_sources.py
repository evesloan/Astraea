"""Reload saved sources and verify editable semantic meshes and packed images."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for path in sorted((ROOT/'source').glob('AST-AQU-*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(path));sc=bpy.context.scene
    meshes=[o for o in bpy.data.objects if o.type=='MESH'];roles=sorted({o['semantic_role'] for o in meshes});used_images={n.image for ob in meshes for mat in ob.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'}
    issues=[]
    if abs(sc.unit_settings.scale_length-1)>1e-8:issues.append('Nonmetric source')
    if any(o.type in {'CAMERA','LIGHT'} for o in bpy.data.objects):issues.append('QA objects in source')
    if any(not o.data.uv_layers.active for o in meshes):issues.append('Missing source UV')
    if any(not i.packed_file for i in used_images):issues.append('Unpacked used image')
    if any(any(abs(v-1)>1e-6 for v in ob.scale) for ob in meshes):issues.append('Unapplied scale')
    source_nonmanifold=[]
    import bmesh
    for ob in meshes:
        bm=bmesh.new();bm.from_mesh(ob.data)
        bad=sum(not e.is_manifold for e in bm.edges)
        if bad:source_nonmanifold.append({'object':ob.name,'nonmanifold_edges':bad})
        bm.free()
    if source_nonmanifold:issues.append('Nonmanifold source solids')
    rows.append({'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'editable_meshes':len(meshes),'roles':roles,'packed_used_images':len(used_images),'all_used_images_packed':all(i.packed_file for i in used_images),'source_nonmanifold':source_nonmanifold,'issues':issues,'status':'PASS' if not issues else 'FAIL'})
(ROOT/'qa'/'source_reload_checks.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2));assert all(r['status']=='PASS' for r in rows)
