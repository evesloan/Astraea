"""Offline numeric collision proposal frame and open-space checks."""
from pathlib import Path
import itertools,json,hashlib
import numpy as np
from scipy.spatial import ConvexHull
from independent_geometry import C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
def boxpoints(lo,hi):return np.asarray(list(itertools.product(*zip(lo,hi))))
def points(p,source=True):
    suffix='blender_source_m' if source else 'gltf_yup_m'
    for key in ['points_','vertices_']:
        if key+suffix in p:return np.asarray(p[key+suffix])
    if 'min_'+suffix in p:return boxpoints(p['min_'+suffix],p['max_'+suffix])
    center=np.asarray(p['centre_'+suffix]);axis=np.asarray(p['axis_'+('blender_source' if source else 'gltf_yup')]);seed=np.array([0,0,1.]) if abs(axis[2])<.9 else np.array([0,1.,0]);u=np.cross(axis,seed);u/=np.linalg.norm(u);v=np.cross(axis,u)
    return np.asarray([center+axis*d+p['radius_m']*(u*np.cos(a)+v*np.sin(a)) for d in [-p['length_m']/2,p['length_m']/2] for a in np.arange(32)*np.pi/16])
def hulls(parts):return [(p,ConvexHull(points(p)).equations) for p in parts]
def hits(hs,a,b,exclude=lambda p:False):
    a=np.asarray(a);d=np.asarray(b)-a;out=[]
    for p,planes in hs:
        if exclude(p):continue
        lo=0.;hi=1.;valid=True
        for plane in planes:
            value=plane[:3]@a+plane[3];slope=plane[:3]@d
            if abs(slope)<1e-12:
                if value>1e-8:valid=False;break
            elif slope>0:hi=min(hi,-value/slope)
            else:lo=max(lo,-value/slope)
        if valid and lo<=hi+1e-9 and hi>=0 and lo<=1:out.append(p['name'])
    return out
reports=[]
paths=[ROOT/'assets/utility_machines/collision_proposals.json',ROOT/'assets/utility_console/collision_proposals.json']
for path in paths:
    j=json.loads(path.read_text());assets={j['asset_id']:j} if 'asset_id' in j else j
    for ident,r in assets.items():
        parts=r.get('parts',r.get('primitives'));hs=hulls(parts);errs=[]
        for p in parts:
            if p['type']=='cylinder':
                errs.extend([np.linalg.norm(C@p['centre_blender_source_m']-p['centre_gltf_yup_m']),np.linalg.norm(C@p['axis_blender_source']-p['axis_gltf_yup'])])
            else:
                a=points(p)@C.T;b=points(p,False);dist=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2);errs.append(max(dist.min(axis=0).max(),dist.min(axis=1).max()))
        tests=[]
        def check(name,a,b,empty,exclude=lambda p:False):
            hh=hits(hs,a,b,exclude);tests.append({'name':name,'source_segment_m':[list(a),list(b)],'intersected_shapes':hh,'expected_empty':empty,'pass':(not hh) if empty else bool(hh)})
        if ident in ['AST-ENG-001','AST-ENG-002']:
            half=.86 if ident.endswith('001') else .65
            for rad in [0,.077]:
                for a in ([0] if rad==0 else np.arange(12)*np.pi/6):
                    y=rad*np.sin(a);z=.6+rad*np.cos(a);check('bore_'+str((rad,float(a))),[-half,y,z],[half,y,z],True)
            check('pipe_wall_negative',[-half,0,.695],[half,0,.695],False)
            for reserved in r['excluded_work_reservations']:
                lo=np.asarray(reserved['min_blender_source_m']);hi=np.asarray(reserved['max_blender_source_m']);mid=(lo+hi)/2
                check('work_reservation_'+reserved['name'],mid-(hi-lo)*.4,mid+(hi-lo)*.4,True)
            if ident.endswith('001'):
                for rad in [0,.13]:
                    for a in ([0] if rad==0 else np.arange(12)*np.pi/6):
                        x=rad*np.sin(a);z=.6+rad*np.cos(a)
                        check('cover_removed_service_'+str((rad,float(a))),[x,-.34,z],[x,-.03,z],True,lambda p:p['name']=='front_service_cover')
            else:check('lid_removed_cavity',[0,0,1.65],[0,0,1.],True,lambda p:p['name']=='removable_lid')
        else:
            for x in [-.25,-.125,0]:
                for z in [-.265,-.230]:check('hatch_removed_bay_'+str((x,z)),[x,-.23,z],[x,-.14,z],True,lambda p:p.get('follows_named_node')=='SERVICE_removable_hatch')
            check('solid_upper_face_negative',[0,-.23,0],[0,-.14,0],False)
            check('rear_closure_negative',[0,-.14,-.247],[0,-.07,-.247],False,lambda p:p.get('follows_named_node')=='SERVICE_removable_hatch')
            for x,name in [(-.263,'START'),(-.127,'HOLD'),(.009,'ISOLATE')]:
                check('button_press_clear_'+name,[x,-.218,-.133],[x,-.215,-.133],True,lambda p:p.get('follows_named_node')=='CTRL_button_'+name)
            check('front_approach',[0,-1.05,.20],[0,-.27,.20],True)
        report={'asset':ident,'proposal_path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'shape_count':len(parts),'maximum_frame_error_m':float(max(errs)),'checks':tests,'pass':max(errs)<1e-7 and all(t['pass'] for t in tests)}
        reports.append(report)
out={'assets':reports,'pass':all(r['pass'] for r in reports),'method':'Resolve explicit primitive numbers to convex halfspaces; clip source-frame segments against each shape. Check transformed source vertices/centres/directions against native GLB-frame proposal fields. Cylinders use32 sides for these sampled tests.','limits':['Numeric offline proposals only; no active engine collision, runtime attachments, actor fit, contact solver or target-PC cost claim.','Coarse omissions near service holes are deliberate and documented by the authors.','Machine compound sets have many pieces; receiving-engine simplification and performance remain pending.']}
(OUT/'independent_collision_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'assets':[{'id':r['asset'],'pass':r['pass'],'failed':[x for x in r['checks'] if not x['pass']]} for r in reports],'pass':out['pass']},indent=2))
