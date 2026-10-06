"""Pure plan checks. No source build, engine, renderer, export or project writes.
Checks authored triangles, actual reopened soil polygons and retained view/route
contracts. All output stays under this new scratch prototype directory.
"""
import sys
sys.dont_write_bytecode=True
import json,math,hashlib,importlib.util,collections
from pathlib import Path
import numpy as np
from geometry_plan import HERE,CAT,POOL,PLAN,world,local,halfplanes,build_plan

G=Path('/workspace/shared/astraea-godot-production-20261003')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
predicate=load_module(POOL/'comfort_greenery/greenery/check_planned_contacts.py','contact_predicates')
def triang(part,vertices_key='vertices'):
    v=np.asarray(part[vertices_key],float)
    if 'evaluated_triangle_indices' in part:
        return v[np.asarray(part['evaluated_triangle_indices'],dtype=np.int64)]
    return np.asarray([v[[f[0],f[i],f[i+1]]] for f in part['faces'] for i in range(1,len(f)-1)])
def overlap(a,b):return all(a[1][i]>=b[0][i] and b[1][i]>=a[0][i] for i in range(3))
def bound(points):return [np.min(points,axis=0).tolist(),np.max(points,axis=0).tolist()]
def tri_box(tri,lo,hi):
    c=(np.array(lo)+hi)*.5;e=(np.array(hi)-lo)*.5;v=np.asarray(tri)-c
    edges=[v[(i+1)%3]-v[i] for i in range(3)]
    axes=[np.eye(3)[i] for i in range(3)]+[np.cross(edges[0],edges[1])]+[np.cross(edge,b) for edge in edges for b in np.eye(3)]
    for axis in axes:
        if np.linalg.norm(axis)<1e-12:continue
        d=v@axis;r=e@np.abs(axis)
        if d.min()>r+1e-8 or d.max()<-r-1e-8:return False
    return True

def surface_distance(triangles,point):
    """Actual point-to-triangle distance, including edges/corners.
    The retained barycentric surface predicate uses a dimensionless epsilon,
    which can reject a quantized blade tip even when its physical distance is
    below the original 2e-7 m surface tolerance. This computes that same metric
    tolerance directly; it does not relax a geometric clearance threshold.
    """
    t=np.asarray(triangles,float);p=np.asarray(point,float)
    a,b,c=t[:,0],t[:,1],t[:,2];e=b-a;f=c-a;v=p-a
    n=np.cross(e,f);nn=np.sum(n*n,axis=1);vn=np.sum(v*n,axis=1)
    ee=np.sum(e*e,axis=1);ef=np.sum(e*f,axis=1);ff=np.sum(f*f,axis=1)
    ve=np.sum(v*e,axis=1);vf=np.sum(v*f,axis=1);den=ee*ff-ef*ef
    u=(ff*ve-ef*vf)/den;w=(ee*vf-ef*ve)/den
    sq=np.where((u>=0)&(w>=0)&(u+w<=1),vn*vn/nn,np.inf)
    for x,y in [(a,b),(b,c),(c,a)]:
        edge=y-x;alpha=np.clip(np.sum((p-x)*edge,axis=1)/np.sum(edge*edge,axis=1),0,1)
        delta=p-(x+edge*alpha[:,None]);sq=np.minimum(sq,np.sum(delta*delta,axis=1))
    return float(math.sqrt(max(0,float(sq.min()))))

def geometry_checks(plan):
    errors=[];reports=[];alltri=[]
    for a in plan['assets']:
        parts={m['name']:m for m in a['parts']};tris={n:triang(m) for n,m in parts.items()}
        assert len(parts)==len(a['parts'])
        minarea=1;mincurve=1;minmargin=1;minroot=1;worst_contact=[]
        planes=halfplanes(a['soil_polygon_local_xy']);parentmap={j['child']:j['parent'] for j in a['joints']}
        for p in a['parts']:
            v=np.asarray(p['vertices']);t=tris[p['name']]
            assert np.isfinite(v).all() and np.isfinite(np.asarray(p['loop_uvs'])).all()
            assert len(p['loop_uvs'])==sum(len(f) for f in p['faces'])
            areas=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5
            minarea=min(minarea,float(areas.min()))
            if areas.min()<1e-10:errors.append(a['name']+'/'+p['name']+' zero area')
            margin=min(d-nx*q[0]-ny*q[1] for q in v for nx,ny,d in planes)
            minmargin=min(minmargin,margin)
            if margin<.01499:errors.append(a['name']+'/'+p['name']+' exceeds 15 mm inset')
            if p['name'] in a['root_parts']:
                minroot=min(minroot,margin)
                if abs(v[:,2].min()-a['soil_surface_local_z'])>1e-8:errors.append(a['name']+'/'+p['name']+' floating root')
            if p['surface_kind']=='closed_support':
                counts=collections.Counter(tuple(sorted((x,y))) for f in p['faces'] for x,y in zip(f,f[1:]+f[:1]))
                if set(counts.values())!={2}:errors.append(a['name']+'/'+p['name']+' nonmanifold support')
                volume=np.sum(t[:,0]*np.cross(t[:,1],t[:,2]))/6
                if volume<=1e-12:errors.append(a['name']+'/'+p['name']+' nonpositive closed volume')
            else:
                singular=np.linalg.svd(v-v.mean(axis=0),compute_uv=False);ratio=float(singular[2]/singular[0]);mincurve=min(mincurve,ratio)
                if ratio<=.009:errors.append(a['name']+'/'+p['name']+' planar blade')
            node=p['name'];seen=set()
            while node not in a['root_parts'] and node not in seen:
                seen.add(node);node=parentmap.get(node)
                if node is None:break
            if node not in a['root_parts']:errors.append(a['name']+'/'+p['name']+' not rooted')
            wt=np.asarray([[world(q,a) for q in tr] for tr in t]);alltri.extend(wt)
        for j in a['joints']:
            probe=np.asarray(j['probe_local']);parent=tris[j['parent']];child=tris[j['child']]
            if not predicate.inside(parent,probe):worst_contact.append(j['child']+' parent')
            if not (predicate.inside(child,probe) if parts[j['child']]['surface_kind']=='closed_support' else surface_distance(child,probe)<2e-7):worst_contact.append(j['child']+' child')
        errors += [a['name']+'/'+e for e in worst_contact]
        if not 1.4<=a['maximum_height_above_soil_m']<=1.6:errors.append(a['name']+' height')
        fit=a['authored_leaf_fit']
        reports.append(dict(name=a['name'],bounds_local=a['bounds_local'],bounds_world=a['bounds_world'],maximum_height_above_soil_m=a['maximum_height_above_soil_m'],root_crown_count=len(a['root_parts']),rooted_joint_count=len(a['joints']),minimum_root_polygon_margin_m=minroot,minimum_all_vertices_polygon_margin_m=minmargin,minimum_triangle_area_m2=minarea,minimum_leaf_nonplanarity_singular_ratio=mincurve,authored_leaf_width_range_m=[min(x['width_m'] for x in fit),max(x['width_m'] for x in fit)],fitted_blade_reach_range_m=[min(x['fitted_reach_m'] for x in fit),max(x['fitted_reach_m'] for x in fit)],triangles=a['planned_triangle_count']))
    return errors,reports,np.asarray(alltri)

def retained_screens(plan,alltri):
    """Conservative route AABBs; all protected routes must be disjoint.
    Exact rays remain independent. No wider tolerances or route rewrites.
    """
    inputpaths=[G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json',G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json',POOL/'comfort_greenery/reference_audit/SEAT_SIGHTLINES.json']
    pins={str(p):sha(p) for p in inputpaths}
    section,first,runtime,sight=[json.loads(p.read_text()) for p in inputpaths]
    parts=json.loads(PLAN.read_text())['parts'];errors=[];routes=[];rays=[];exits=[]
    access_path=POOL/'architectural_composition/revisions/blockin003/review_evidence/NEW_SEAT_ACCESS_003b.json'
    checked_access=json.loads(access_path.read_text());assert checked_access['status']=='PASS_NEW_SEAT_ACCESS_AND_PURPOSEFUL_POOL_VIEWS'
    pins[str(access_path)]=sha(access_path)
    bounds_by_asset=[a['bounds_world'] for a in plan['assets']]
    architecture_overlaps=[]
    for a in plan['assets']:
        for p in parts:
            if p['name']==a['support'] or p['name']==a['support'].replace('_Soil','_Bowl'):continue
            pb=bound(p['vertices_xyz'])
            if overlap(a['bounds_world'],pb):architecture_overlaps.append([a['name'],p['name']])
    # Every architecture AABB is separate, so no triangle can cross it.
    if architecture_overlaps:errors.append('Architecture broad-phase overlap needs exact review: '+str(architecture_overlaps))
    for label,z in [('Fore',-442.2),('Middle',-424.6),('Aft',-406.7)]:
        points=next(r['approach_xyz'] for r in checked_access['results'] if r['name']==label)
        routes.append(dict(name='loggia_'+label,points=points,r=.30,h=1.8))
        # All central seated rays and 20-degree horizontal water-view edges.
        for yaw in [-20,0,20]:
            eye=[-51.65,47.44,z];r=math.radians(yaw)
            rays.append((label+'_water_'+str(yaw),eye,[eye[0]+15.65*math.cos(r),46.25,eye[2]+15.65*math.sin(r)]))
    routes += [dict(name=p['item'],points=p['points'],r=.3,h=1.8) for p in first['approach_paths']]
    routes += [dict(name='wet_main',points=[[-45.9,46.2,-458],[-45.9,46.2,-405]],r=.5,h=2)]
    routes += [dict(name='dry_market',points=[[x,52.5,z] for x,z in section['market']['adopted_dry_loop_centreline_xz']],r=.5,h=2)]
    routes += [dict(name='stock_'+p['display'],points=p['points_xyz'],r=.3,h=1.8) for p in runtime['stock_approach_paths']]
    routes += [dict(name='ramp',points=section['accessible_ramp']['route_xyz'],r=.5,h=2)]
    routes += [dict(name='lower_lift',points=section['wet_market_link']['lift']['lower_approach_xyz'],r=.5,h=2)]
    route_results=[]
    for route in routes:
        hits=set()
        for a,b in zip(route['points'],route['points'][1:]):
            lo=[min(a[0],b[0])-route['r'],min(a[1],b[1])+.02,min(a[2],b[2])-route['r']]
            hi=[max(a[0],b[0])+route['r'],max(a[1],b[1])+route['h'],max(a[2],b[2])+route['r']]
            for asset in plan['assets']:
                if overlap([lo,hi],asset['bounds_world']):hits.add(asset['name'])
        route_results.append(dict(name=route['name'],broad_phase_hits=sorted(hits)))
        if hits:errors.append(route['name']+' protected route overlap '+str(hits))
    for screen in runtime['media_candidates']:
        for i,p in enumerate(screen['sampled_current_triangle_sightlines']):rays.append((screen['name']+'_'+str(i),p['eye_xyz'],p['target_xyz']))
    for seat in sight['seats']:
        for i,r in enumerate(seat['rays']):
            if seat['asset']!='lounger':continue
            rays.append((seat['name']+'_'+str(i),r['eye_xyz'],[x+50*d for x,d in zip(r['eye_xyz'],r['direction_xyz'])]))
    blocked=[]
    for name,a,b in rays:
        if predicate.hit(alltri,a,b):blocked.append(name)
    if blocked:errors.append('View-ray occlusion '+str(blocked))
    for fixture in section['fixtures']+runtime['fixtures']:
        start=fixture['position_xyz'];direction=fixture.get('direction_xyz',fixture.get('direction'))
        end=[x+.06*d for x,d in zip(start,direction)]
        if predicate.hit(alltri,start,end):exits.append(fixture['name']+' source exit')
        if 'receiver_xyz' in fixture and predicate.hit(alltri,start,fixture.get('visibility_sample_xyz',fixture['receiver_xyz'])):exits.append(fixture['name']+' receiver')
    if exits:errors.append('Fixture obstruction '+str(exits))
    return errors,dict(architecture_aabb_overlaps=architecture_overlaps,protected_routes=route_results,view_ray_count=len(rays),blocked_view_rays=blocked,fixture_source_receiver_issues=exits,read_only_runtime_input_pins=pins)

def projected_leaf_union(asset,plane='front'):
    # Numerical silhouette diagnostic, no pixels, shading or render. It cannot
    # pass visual quality. Ignore flowers to prevent accents masking leaf mass.
    # Shapely is needed only for this optional numeric diagnostic in host
    # Python, never for the Blender source verifier. Do not import its host
    # binary extension into a potentially different Blender Python ABI.
    sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys=[]
    for p in asset['parts']:
        if not p['material_role'].startswith('botanical_leaf_') or p['surface_kind']=='closed_support':continue
        for tri in triang(p):
            coords=[(q[0],q[2]) if plane=='front' else(q[0],q[1]) for q in tri]
            poly=Polygon(coords)
            if poly.area>1e-10:polys.append(poly)
    return unary_union(polys)

def fullness_diagnostic(plan):
    retained=json.loads((POOL/'comfort_greenery/greenery/greenery_contract.json').read_text());old={a['name']:a for a in retained['assets']}
    results=[]
    for a in plan['assets']:
        b=old[a['replaces_model_file'].replace('.glb','')]
        newfront=projected_leaf_union(a);oldfront=projected_leaf_union(b)
        newtop=projected_leaf_union(a,'top');oldtop=projected_leaf_union(b,'top')
        roleareas={}
        for role in ['jade','sage','olive']:
            roleasset={'parts':[p for p in a['parts'] if p['material_role']=='botanical_leaf_'+role]}
            roleareas[role]=projected_leaf_union(roleasset).area
        results.append(dict(name=a['name'],new_leaf_front_union_m2=newfront.area,old_leaf_front_union_m2=oldfront.area,front_union_ratio=newfront.area/oldfront.area,new_leaf_top_union_m2=newtop.area,old_leaf_top_union_m2=oldtop.area,projected_role_area_without_occlusion_m2=roleareas,diagnostic_only='Unlit orthographic union of authored leaf triangles. Not a composed image and not a visual acceptance gate.'))
    return results

def main():
    path=HERE/'plant_mass_contract.json';plan=json.loads(path.read_text())
    assert json.dumps(build_plan(),sort_keys=True)==json.dumps(plan,sort_keys=True),'Nondeterministic plan'
    errors,reports,alltri=geometry_checks(plan)
    more,screen=retained_screens(plan,alltri);errors+=more
    for file,h in json.loads((HERE/'INPUT_PINS.json').read_text())['inputs'].items():assert sha(file)==h,'Input changed: '+file
    for file,h in screen['read_only_runtime_input_pins'].items():assert sha(file)==h,'Read-only runtime input changed: '+file
    report=dict(status='PASS_PURE_PLAN_ONLY' if not errors else 'REQUIRES_GEOMETRY_CORRECTION',contract_sha256=sha(path),determinism=True,original_80_inputs_byte_identical=True,assets=reports,retained_constraints=screen,numeric_fullness_diagnostics=fullness_diagnostic(plan),errors=errors,not_run=['Blender/source build or reopen','Rendered/composed image','GLB export','Game/native QA','Material graph inspection in Blender'])
    target=HERE/'PURE_PLAN_QA.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'errors':errors,'assets':reports,'fullness':report['numeric_fullness_diagnostics'],'rays':screen['view_ray_count']},indent=2))
    assert not errors
if __name__=='__main__':main()
