"""Fresh-process reload verification of every source and QA Blender file."""
import bpy,bmesh,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
reports=[]
source_vertices={}
for path in sorted(list((ROOT/'source').glob('*.blend'))+list((ROOT/'qa').glob('*.blend'))):
    bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();objects=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.name.startswith('QA_ONLY'):continue
        ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
        record={'name':o.name,'source_vertices':len(o.data.vertices),'evaluated_vertices':len(me.vertices),'modifiers':[m.type for m in o.modifiers],'scale':list(o.scale),'finite_vertices':all(math.isfinite(c) for v in me.vertices for c in v.co),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'material_roles':[m.name for m in o.data.materials],'source_uv_layer':o.data.uv_layers.active.name if o.data.uv_layers.active else None}
        record['pass']=record['finite_vertices'] and record['nonmanifold_edges']==0 and record['signed_volume_m3']>0 and all(abs(s-1)<1e-7 for s in o.scale)
        if path.parent.name=='source' and 'ASSEMBLY' not in path.name:source_vertices[o.name]=[list(v.co) for v in o.data.vertices]
        objects.append(record);bm.free();ev.to_mesh_clear()
    images=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and im.name!='Render Result']
    reports.append({'file':str(path.relative_to(ROOT)),'loaded':True,'objects':objects,'packed_images':images,'all_mesh_checks_passed':all(r['pass'] for r in objects),'render_engine':bpy.context.scene.render.engine})
out={'status':'Source reload/editability/manifold verification; no engine physics acceptance','files':reports,'all_passed':all(r['all_mesh_checks_passed'] for r in reports)}
(ROOT/'qa/source_reload_validation.json').write_text(json.dumps(out,indent=2));print('RELOAD_COMPLETE',out['all_passed'])
proof=[]
for suffix,count in [('sculpted_ivory',12),('deep_timber_return',7)]:
    h=source_vertices['header_'+suffix][-count:];s=source_vertices['sill_'+suffix][-count:];j=source_vertices['jamb_'+suffix];t=source_vertices['terminal_'+suffix][:count]
    for name,a,b,az,bz in [('header_to_top_jamb',h,j[:count],2.9,2.9),('sill_to_bottom_jamb',s,j[-count:],.7,2.9),('header_to_closed_terminal',h,t,0,0)]:
        error=max(math.hypot(v[1]-w[1],v[2]+az-w[2]-bz) for v,w in zip(a,b))
        gap=(b[0][0]+(1.1 if 'jamb' in name else 2.2))-(a[0][0]+(-1.1 if 'jamb' in name else 0))
        proof.append({'join':name,'material':suffix,'cross_section_yz_max_error_m':error,'measured_cap_gap_m':gap,'matched':error<1e-6 and abs(gap-.002)<1e-6})
(ROOT/'qa/join_validation.json').write_text(json.dumps({'method':'Reloaded original Blender vertex rings compared at assembled source seam transforms; evaluated bevel only eases inside these caps','joints':proof,'all_passed':all(x['matched'] for x in proof),'terminal_endcap':'Source and evaluated terminal parts are manifold, capped meshes; checked separately by source reload.'},indent=2))
