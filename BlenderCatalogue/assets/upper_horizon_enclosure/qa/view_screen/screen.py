#!/usr/bin/env python3
"""Read-only Upper Horizon design screening. Writes only --output scratch files.

No engine, imports, source changes, or final006 acceptance. numpy/scipy required.
All coordinates are Godot world XYZ metres. Run from any working directory.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, math, os
import numpy as np
from scipy.optimize import minimize_scalar

CAT = Path(os.environ.get('ASTRAEA_CATALOGUE_ROOT', str(Path(__file__).resolve().parents[4])))
GOD = Path(os.environ.get('ASTRAEA_GODOT_ROOT', str(CAT.parent/'astraea-godot-production-20261003')))
SRC = CAT/'assets/aft_crown_platform/source'
FACES = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
EPS=1e-9
CLEAR_Y=(107.42,111.03)
PRESERVED_005_GUARD_TOP=107.40

def native(x):
    if isinstance(x,np.ndarray): return x.tolist()
    if isinstance(x,np.generic): return x.item()
    raise TypeError(type(x).__name__)

def direction(az,el):
    a,e=map(math.radians,[az,el])
    return np.array([math.cos(e)*math.cos(a),math.sin(e),math.cos(e)*math.sin(a)])

def basis(c):
    u=np.cross(c,[0,1,0]); u/=np.linalg.norm(u)
    return u,np.cross(u,c)

def rim(c,r,t):
    u,v=basis(c); t=np.atleast_1d(t)
    return c[None,:]*np.cos(r)+(u[None,:]*np.cos(t[:,None])+v[None,:]*np.sin(t[:,None]))*np.sin(r)

def extrema(c,r):
    out={}
    for k,label in [(1,'p'),(2,'q')]:
        for mm,sgn in [('min',1),('max',-1)]:
            def objective(t):
                d=rim(c,r,[t])[0]; return sgn*d[k]/abs(d[0])
            ts=np.linspace(0,2*np.pi,2001); t=ts[np.argmin([objective(t)for t in ts])]
            fit=minimize_scalar(objective,bounds=(t-.01,t+.01),method='bounded',options={'xatol':1e-14})
            d=rim(c,r,[fit.x])[0]
            out[label+'_'+mm]={'value':float(d[k]/abs(d[0])),'direction':d}
    return out

def range_product(a,b):
    v=[x*y for x in a for y in b]; return [min(v),max(v)]

def cone_box(eye,s,p,q,out_x):
    """Conservative independent-slope AABB enclosing every continuous eye/ray.
    Overestimation is intentional; disjoint boxes prove no exact triangle hit.
    """
    dx=[max(0,out_x[0]-eye['abs_x'][1]),max(0,out_x[1]-eye['abs_x'][0])]
    py=range_product(dx,p); qz=range_product(dx,q)
    xx=[s*out_x[0],s*out_x[1]];xx.sort()
    return [xx[0],xx[1],eye['y'][0]+py[0],eye['y'][1]+py[1],eye['z'][0]+qz[0],eye['z'][1]+qz[1]]

def overlaps(a,b): return all(a[i]<=b[i+1]+EPS and b[i]<=a[i+1]+EPS for i in [0,2,4])

def continuous_candidates(parts,eye,s,p,q):
    hits=[]
    for part in parts:
        b=part['world_aabb']; xx=sorted([s*b[0],s*b[1]])
        if xx[1]<eye['abs_x'][0]:continue
        xx[0]=max(xx[0],eye['abs_x'][0]); cb=cone_box(eye,s,p,q,xx)
        if overlaps(cb,b):hits.append({'name':part['name'],'world_aabb':b,'cone_bound_at_part_x':cb})
    return hits

def triangles(parts):
    ts=[];owners=[]
    for p in parts:
        vs=np.array(p['vertices_world'],dtype=float)
        assert len(vs)==8,('Unexpected source topology',p['name'],len(vs))
        for face in FACES:
            for ids in [(face[0],face[1],face[2]),(face[0],face[2],face[3])]:
                ts.append(vs[list(ids)]);owners.append(p['name'])
    return np.array(ts),owners

def triangle_hits(eye,d,ts,owners):
    e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2)
    a=np.einsum('ij,ij->i',e1,h);good=np.abs(a)>1e-10;f=np.zeros_like(a);f[good]=1/a[good]
    ss=eye-ts[:,0];u=f*np.einsum('ij,ij->i',ss,h);qq=np.cross(ss,e1)
    v=f*np.einsum('j,ij->i',d,qq);t=f*np.einsum('ij,ij->i',e2,qq)
    good &= (u>=-EPS)&(v>=-EPS)&(u+v<=1+EPS)&(t>EPS)
    ids=np.where(good)[0];ids=ids[np.argsort(t[ids])]
    return [{'part':owners[i],'distance':float(t[i]),'point':eye+t[i]*d}for i in ids[:16]]

def point_in_polygon(x,z,poly):
    inside=False
    for p,q in zip(poly,poly[1:]+poly[:1]):
        if (p[1]>z)!=(q[1]>z) and x<(q[0]-p[0])*(z-p[1])/(q[1]-p[1])+p[0]:inside=not inside
    return inside

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='/tmp/upper_horizon_view_screen');ap.add_argument('--source-dir',type=Path,default=SRC);ap.add_argument('--label',default='selected005');args=ap.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    selected_src=args.source_dir
    parts=json.loads((selected_src/'geometry_parts.json').read_text())['parts'];ts,owners=triangles(parts)
    hull=json.loads((GOD/'data/hull_envelope.json').read_text())['plan_xz_m']
    paths=[selected_src/'geometry_parts.json',selected_src/'section_contract.json',SRC/'build_aft_crown_platform.py',GOD/'shaders/astraea_space.gdshader',GOD/'scripts/ship.gd',GOD/'data/architecture/SPACE_VIEW_COMPOSITION.json',GOD/'data/architecture/UPPER_SECTION_COORDINATION.json',GOD/'data/whole_ship_layout.json',GOD/'data/hull_envelope.json',GOD/'data/generated/structural_meshes.json',GOD/'docs/UPPER_HORIZON_ENCLOSURE_PLAN.md']
    result={'status':'Design screen only; current005 and future envelopes. No new006 triangle, runtime, visual, collision/body-route, engineering, pressure or full-ship acceptance.','source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'world_sky':{'rotation':[0,0,0],'use_radiance_cache':False,'direction_uniforms_normalized_before_use':True,'no_shader_edits':True},'aperture':{'abs_x_glass':35.7,'glass_thickness':.06,'abs_x_glass_faces':[35.67,35.73],'abs_x_reveal_faces':[35.52,35.88],'clear_y':list(CLEAR_Y),'preserved005_guard_top_y':PRESERVED_005_GUARD_TOP,'clear_z':[160.10,163.90]},'method':{'continuous_proof':'For each actual005 source AABB at outward X, intersect a conservative AABB of the entire eye-box times complete target slope intervals. Zero candidates proves no source triangles can intersect any target ray; it is stronger than the ray-grid sample.','sample_formula':'d(rho,t)=normalize(c)*cos(rho)+(u*cos(t)+v*sin(t))*sin(rho); u=normalize(cross(c,up)); v=cross(u,c); 65 rho samples, 721 t samples, plus extrema/horizon directions; 27 eye grid stations including 8 corners.','parameterization':'p=dy/d|x| and q=dz/d|x|; at outward |X|=a, hit=(sign*a,eyeY+(a-|eyeX|)*p,eyeZ+(a-|eyeX|)*q).','source_triangles':'Current005 eight-vertex hexahedra reconstructed with exact FACES list used by source builder; double-sided Moller-Trumbore checks for negative/high-ray witness failures.','future_roof':'Y106.5 horizontal conservative roof reservation clipped to historical whole-hull plan, NOT installed roof triangles or resolved per-height hull shape. Infinite-plane result also given separately. General roof outside constructed floors is a future reservation.','plane_envelope_caution':'Independent p/q bounds are conservative; extremes need not occur on one ray.'},'features':{},'witness_rays':[]}
    arrays={}
    result['selected005_label']=args.label
    result['selected005_geometry_path']=str(selected_src/'geometry_parts.json')
    result['baseline_guard_is_present']=any(p['name']=='ACP_Starboard_GuardCap_01.008'for p in parts)
    specs=[('starboard',[.9354072,-.2923717,.1988269],29,29.85,[161.05,161.35]),('port',[-.9871089,.1045285,-.1212017],7,math.degrees(math.acos(math.cos(math.radians(7))-.0006)),[162.10,162.60])]
    for side,cv,nominal_radius,support_radius,zbox in specs:
        c=np.array(cv);c/=np.linalg.norm(c);s=np.sign(c[0]);r=math.radians(support_radius);ext=extrema(c,r)
        pmax=ext['p_max']['value'];qmin=ext['q_min']['value'];qmax=ext['q_max']['value']
        eye={'abs_x':[32.7,33.1],'y':[107.95,108.35],'z':zbox}; eyes=np.array([[s*x,y,z]for x,y,z in itertools.product(*[np.linspace(*eye[k],3)for k in ['abs_x','y','z']])])
        all_rays=np.concatenate([rim(c,rr,np.linspace(0,2*np.pi,721))for rr in np.linspace(0,r,65)]+[np.array([e['direction']for e in ext.values()])]);target=all_rays[all_rays[:,1]>=-EPS]
        horizon=[]
        if side=='starboard':
            az=math.atan2(c[2],c[0]);da=math.acos(math.cos(r)/math.hypot(c[0],c[2]));aa=[az-da,az+da]
            horizon=[{'azimuth_degrees':math.degrees(a),'direction':np.array([math.cos(a),0,math.sin(a)])}for a in aa]
            qmin,qmax=[math.tan(a)for a in aa]
            target=np.concatenate([target,np.array([[math.cos(a),0,math.sin(a)]for a in np.linspace(*aa,721)])])
        p=[0,pmax];q=[qmin,qmax]
        candidates=continuous_candidates(parts,eye,s,p,q)
        assert not candidates,(side,'continuous positive-target collision candidates',candidates)
        planes=[]
        for x in [35.52,35.67,35.7,35.73,35.88,35.975,52,63,73,94,100,104,118,120]:
            b=cone_box(eye,s,p,q,[x,x]);planes.append({'abs_x':x,'y':[b[2],b[3]],'z':[b[4],b[5]]})
        aperture_checks=[]
        for x in [35.52,35.67,35.7,35.73,35.88]:
            b=cone_box(eye,s,p,q,[x,x]);ok=b[2]>=CLEAR_Y[0] and b[3]<=CLEAR_Y[1] and b[4]>=160.10 and b[5]<=163.90
            assert ok,(side,x,b)
            aperture_checks.append({'abs_x':x,'continuous_pass':ok,'margins_yz':[b[2]-CLEAR_Y[0],CLEAR_Y[1]-b[3],b[4]-160.10,163.90-b[5]]})
        future=[]
        for name,xx,zz,yy in [('central_upper_pavilion',[94,118],[22,54],[106.5,114.5]),('aft_upper_pavilion',[73,104],[400,436],[106.5,114.5]),('aft_residential_court',[63,100],[250,491.123],[84,106.5])]:
            bx=sorted([s*v for v in xx]);b=[bx[0],bx[1],yy[0],yy[1],zz[0],zz[1]];cb=cone_box(eye,s,p,q,xx)
            hit=overlaps(cb,b);assert not hit
            future.append({'name':name,'screen_aabb':b,'target_envelope_aabb':cb,'overlap':hit,'scope':'Conservative bound only; no relocation or private-space cut assumed'})
        f={'raw_direction':cv,'normalized_direction':c,'nominal_radius_degrees':nominal_radius,'support_radius_degrees':support_radius,'support_formula':'acos(cos(radians(7))-.0006)'if side=='port'else'radians(29)+radians(.85)','full_support_extrema':ext,'positive_target_p':p,'positive_target_q':q,'positive_horizon_endpoints':horizon,'eye_box':eye,'nominal_eye':[s*32.9,108.15,sum(zbox)/2],'eye_heights_above_floor':[1.45,1.85],'floor_scope':'Inside existing supported Upper Horizon wing; actual body, approach and route checks still required by parent','complete_positive_target_continuous_005_aabb_candidates':candidates,'plane_envelopes':planes,'aperture_checks':aperture_checks,'minimum_shoulder_clearance':113.4-(108.35+(52-32.7)*pmax),'new_shoulder_required_corridor':cone_box(eye,s,p,q,[35.7,52]),'future_massing':future,'sample_direction_count_positive':len(target),'sample_direction_count_full_support':len(all_rays),'sample_eye_count':len(eyes),'sample_positive_eye_ray_pairs':len(target)*len(eyes),'npz_keys':[side+'_positive_directions',side+'_full_directions',side+'_eyes']}
        if side=='port':
            fullp=[ext['p_min']['value'],pmax];fullq=[ext['q_min']['value'],ext['q_max']['value']]
            f['full_footprint_continuous_005_candidates']=continuous_candidates(parts,eye,s,fullp,fullq)
            assert not f['full_footprint_continuous_005_candidates']
            f['full_footprint_outer_reveal_bounds']=cone_box(eye,s,fullp,fullq,[35.88,35.88]);f['full_footprint_note']='Entire shader-supported footprint clears local frame/aperture/shoulder; below-horizon fringe is conditionally clipped by future D17 roof and is not promised.'
        else:
            f['rejected_inboard_x30_horizon_width']=5.7*(qmax-qmin)
            f['rejected_inboard_x30_why']='5.588m positive halo horizon width exceeds3.8m clear pane; apex alone can pass while side endpoints fail.'
        f['seated_diagnostics']=[]
        for seated_y in [107.55,107.65,107.75]:
            seye={**eye,'y':[seated_y,seated_y]}
            cp=continuous_candidates(parts,seye,s,p,q)
            # The only present005 blockers are exactly the two approved local guards.
            allowed={f'ACP_{side.title()}_GuardBack_01.008',f'ACP_{side.title()}_GuardCap_01.008'}
            assert {v['name']for v in cp}<=allowed,(side,seated_y,cp)
            pose=np.array([s*32.9,seated_y,sum(zbox)/2]);sample_blocked=np.zeros(len(target),dtype=bool)
            source_witness=[]
            for candidate in cp:
                b=candidate['world_aabb'];lo=np.array([b[0],b[2],b[4]]);hi=np.array([b[1],b[3],b[5]])
                with np.errstate(divide='ignore',invalid='ignore'):
                    tt0=(lo-pose)/target;tt1=(hi-pose)/target
                enter=np.max(np.minimum(tt0,tt1),axis=1);leave=np.min(np.maximum(tt0,tt1),axis=1)
                mask=(leave>=np.maximum(enter,0))&(leave>0)
                if mask.any():
                    ii=int(np.flatnonzero(mask)[0]);source_witness.append({'part':candidate['name'],'direction':target[ii],'point':pose+max(0,enter[ii])*target[ii]})
                sample_blocked|=mask
            b=cone_box(seye,s,p,q,[35.88,35.88])
            aperture_ok=(b[2]>=CLEAR_Y[0] and b[3]<=CLEAR_Y[1] and b[4]>=160.1 and b[5]<=163.9)
            assert aperture_ok
            # Source central guard capped atY107.40 is a required design envelope,
            # not fabricated revised005 geometry. Actual revised triangles remain pending.
            gd=cone_box(seye,s,p,q,[35.58,35.82])
            assert gd[2]>107.4 and gd[4]>160 and gd[5]<164
            centre_az=math.atan2(c[2],c[0]);cut_slope=(107.82-seated_y)/(35.58-32.9)
            diag={'eye_y':seated_y,'height_above_floor':seated_y-106.5,'eye_x_z_box':seye,'nominal_eye':pose,'positive_target_current005_candidates':cp,'current005_nominal_sample_blocked_count':int(sample_blocked.sum()),'current005_nominal_sample_total':len(target),'sampling_warning':'Directional construction sample counts are not projected image-area percentages.','current005_blocked_witnesses':source_witness,'baseline107_82_guard_centre_azimuth_crop_elevation_degrees':math.degrees(math.atan(cut_slope*abs(math.cos(centre_az)))),'positive_target_full_clear_aperture':aperture_ok,'positive_target_outer_reveal_bounds':b,'positive_target_preserved005_guard_top107_40_margin':seated_y-PRESERVED_005_GUARD_TOP,'positive_target_new006_sill_top107_42_margin':seated_y-CLEAR_Y[0],'guard_slice_ray_bounds':gd,'new_guard_contract_conclusion':('All positive target rays pass aboveY107.40 and inside preserved Z160..164 replacement slice. Baseline higher guard causes the recorded seated crop. This is a conditional lower-sill envelope proof.' if result['baseline_guard_is_present'] else 'Selected revised005 geometry has zero continuous target-cone candidates. All positive target rays pass aboveY107.40 and inside preserved Z160..164 replacement slice. See separate actual005/006 triangle results for the final source geometry screen.'),'minimum_shoulder_clearance':113.4-(seated_y+(52-32.7)*pmax)}
            if side=='port':
                fullb=cone_box(seye,s,[ext['p_min']['value'],pmax],[ext['q_min']['value'],ext['q_max']['value']],[35.88,35.88])
                diag['full_support_outer_reveal_bounds']=fullb
                diag['full_support_preserved005_guard_top107_40_margin']=fullb[2]-PRESERVED_005_GUARD_TOP
                diag['full_support_new006_sill_top107_42_margin']=fullb[2]-CLEAR_Y[0]
                assert fullb[2]>CLEAR_Y[0]
                roof_witness=[]
                for label,dd in [('nominal_minus1deg',direction(-173,-1)),('actual_support_bottom',ext['p_min']['direction'])]:
                    roofpoint=pose+((106.5-seated_y)/dd[1])*dd
                    roof_witness.append({'name':label,'point':roofpoint,'within_historical_hull_plan':point_in_polygon(roofpoint[0],roofpoint[2],hull)})
                diag['future_roof_negative_fringe_witnesses']=roof_witness
            f['seated_diagnostics'].append(diag)
        result['features'][side]=f;arrays[side+'_positive_directions']=target;arrays[side+'_full_directions']=all_rays;arrays[side+'_eyes']=eyes
    star=np.array(result['features']['starboard']['nominal_eye']);port=np.array(result['features']['port']['nominal_eye'])
    witnesses=[('starboard_planet_centre',star,np.array(specs[0][1])),('starboard_minus5deg',star,direction(12,-5)),('starboard_minus10deg',star,direction(12,-10)),('starboard_nominal_low_limb',star,direction(12,-46)),('port_nominal_low_limb',port,direction(-173,-1)),('port_actual_support_lowest_slope',port,result['features']['port']['full_support_extrema']['p_min']['direction']),('starboard_high_clear_pane_centre',star,np.array([35.7,CLEAR_Y[1],162])-star),('starboard_inboard_upper_apex',np.array([30,108.15,162]),result['features']['starboard']['full_support_extrema']['p_max']['direction']),('starboard_inboard_horizon_aft_endpoint',np.array([30,108.15,162]),result['features']['starboard']['positive_horizon_endpoints'][1]['direction'])]
    for name,eye,d in witnesses:
        d=np.array(d,dtype=float);d/=np.linalg.norm(d);s=np.sign(d[0]);t=(s*35.7-eye[0])/d[0];hit=eye+t*d;record={'name':name,'eye':eye,'direction':d,'glass_hit':hit,'inside_clear_glass_yz':bool(CLEAR_Y[0]<=hit[1]<=CLEAR_Y[1] and 160.10<=hit[2]<=163.90),'current005_triangle_hits':triangle_hits(eye,d,ts,owners)}
        if d[1]<0:
            tt=(106.5-eye[1])/d[1];rh=eye+tt*d;record['future_roof']={'infinite_plane_hit':rh,'within_historical_hull_plan':point_in_polygon(rh[0],rh[2],hull),'distance':float(tt),'reservation_only':True}
        else:record['future_roof']={'hit':False,'reason':'nonnegative elevation; eye is above roof'}
        result['witness_rays'].append(record)
    result['limitations']=['Final006 exact mesh triangles, actual transparent-glass interpretation, source/export preservation and contact proofs must be screened after final source build.','No Godot process, import, capture, tests, backing-up or production edit performed by this screening script.','Ordinary normal/effects-off standing views and slow pans remain mandatory.','Future roof model is an envelope rather than installed complete ship geometry. Shallow negative rays can cross Y106.5 beyond the finite hull plan; do not claim every negative sky ray is hidden.','Positive-horizon rays remain at eye height above roof; from these stations the complete evaluated cap/crescent lies between central and aft pavilion/court footprints. No court view is promised.','Unrelated high-angle stars near pane top remain clipped by unchanged frame and reveal depth; full-window panoramic visibility is not certified.','Eye-box approval is optical only. Player species/body size, floor contact, safe approach and all existing public/service routes belong to separate physical validation.']
    np.savez_compressed(out/'rays.npz',**arrays)
    result['sample_npz_sha256']=hashlib.sha256((out/'rays.npz').read_bytes()).hexdigest()
    (out/'results.json').write_text(json.dumps(result,indent=2,default=native)+'\n')
    print(json.dumps({'output':str(out),'features':{k:{'positive_pairs':v['sample_positive_eye_ray_pairs'],'shoulder_clearance':v['minimum_shoulder_clearance'],'005_continuous_candidates':len(v['complete_positive_target_continuous_005_aabb_candidates'])}for k,v in result['features'].items()},'results_sha256':hashlib.sha256((out/'results.json').read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
