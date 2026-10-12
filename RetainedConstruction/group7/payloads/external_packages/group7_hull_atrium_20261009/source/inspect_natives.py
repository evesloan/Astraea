"""Blender read-only census; write QA only, never resave retained natives."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
D=P/'dependencies/canonical_77a745'
families=['lower_hull_body','upper_hull_theater_shoulders002','atrium_guard_network','atrium_daylight','atrium_garden','terrace_architecture','canopy_terrace']
rows=[]
for family in families:
    for f in sorted((D/'BlenderCatalogue/assets'/family/'source').glob('*.blend')):
        before=hashlib.sha256(f.read_bytes()).hexdigest()
        bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
        graph=bpy.context.evaluated_depsgraph_get()
        lo=[float('inf')]*3;hi=[-float('inf')]*3;triangles=0;meshes=0;nonfinite=[]
        for o in bpy.context.scene.objects:
            if o.type!='MESH':continue
            e=o.evaluated_get(graph);me=e.to_mesh();meshes+=1;me.calc_loop_triangles();triangles+=len(me.loop_triangles)
            for v in me.vertices:
                v=e.matrix_world@v.co;q=(v.x,v.z,-v.y)
                for axis in range(3):lo[axis]=min(lo[axis],q[axis]);hi[axis]=max(hi[axis],q[axis])
            e.to_mesh_clear()
        images=[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.type=='IMAGE']
        rows.append({'source':f.relative_to(D).as_posix(),'sha256_before':before,'sha256_after':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_objects':meshes,'evaluated_triangles':triangles,'source_y_up_bounds':[lo,hi],'placement_scope':'Local source bounds mapped Blender X,-Z,Y. Runtime translation/yaw remain source-owner responsibility.','images':images,'materials':sorted(m.name for m in bpy.data.materials)})
        assert rows[-1]['sha256_after']==before
(P/'qa/retained_native_census.json').write_text(json.dumps({'read_only':True,'blender_version':bpy.app.version_string,'natives':rows},indent=2)+'\n')
print('READ_ONLY_NATIVE_CENSUS',len(rows))
