"""Independent actual-GLB vertical contact-versus-support samples."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
path=ROOT/'exports/AST-AQU-001.glb';bpy.ops.import_scene.gltf(filepath=str(path))
trees={}
for ob in bpy.data.objects:
    if ob.type!='MESH':continue
    me=ob.data;me.calc_loop_triangles();vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
    role=ob.data.materials[0].name.replace('ASTRAEA_','');trees[role]=BVHTree.FromPolygons(vs,fs,all_triangles=True)
samples=[]
for yc in [-.90,-.54,-.13,.25,.58,.85]:
    for offset in [-.017,0,.017]:
        y=yc+offset;p=Vector((.055,y,2));d=Vector((0,0,-1))
        a=trees['aquatic_clay_sling'].ray_cast(p,d,3)[0];b=trees['aquatic_satin_alloy'].ray_cast(p,d,3)[0]
        if a is None or b is None:raise ValueError('Missing actual GLB contact/support sample')
        gap=a.z-b.z;samples.append({'sample_xy_m':[.055,y],'clay_contact_z_m':a.z,'support_top_z_m':b.z,'metal_below_contact_m':gap,'passes':gap>.007})
report={'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'18 vertical BVH rays on the actual imported GLB at X0.055, clear of slots, each crossbeam center and +/-17 mm along Y. Separately visible profile/joint evidence is required.','minimum_metal_below_contact_m':min(r['metal_below_contact_m'] for r in samples),'samples':samples,'status':'PASS' if all(r['passes'] for r in samples) else 'FAIL'}
(ROOT/'qa'/'actual_glb_contact_clearance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['status']=='PASS'
