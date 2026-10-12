"""Independent source intersection witness for the retained R003 light hold."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];d=json.loads((P/'CONTRACT_02_R003_LIGHT_HELD.json').read_text());r=json.loads((R/'Game/docs/group6_completion/THERMAL_SUPPORT_LOCAL002.json').read_text());native=R/d['native'];bpy.ops.wm.open_mainfile(filepath=str(native));start=d['stations'][0]['task_light']['source_xyz'];end=r['support_evidence'][0]['supported_operator'];end=[end[0],end[1]+.8,end[2]]
def xyz(p):return Vector((p[0],-p[2],p[1]))
a=xyz(start);delta=xyz(end)-a;hits=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.get('group6_role') in ['visual_control_interface','visual_soft_furnishing','fixture_lens','visual_grip_no_contact']:continue
 tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons]);v=tree.ray_cast(a,delta.normalized(),delta.length)
 if v[0] is not None:hits.append({'part':o.name,'distance_m':v[3],'xyz':[v[0].x,v[0].z,-v[0].y]})
hits.sort(key=lambda x:x['distance_m']);assert hits and 'sling_' in hits[0]['part'],hits
(P/'LIGHT_RAY_R003_PROOF002.json').write_text(json.dumps({'status':'R003 held path blocker independently identified','native':str(native.relative_to(R)),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'start_xyz':start,'body_sample_xyz':end,'hits':hits,'nearest_blocker_is_own_fixed_hanging_sling':True,'mask_or_criterion_changed':False},indent=2)+'\n');print(hits[0])
