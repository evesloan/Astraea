"""Pure retained-source/actual-GLB placement, soil, contact, route and ray gate.
No Blender/Godot invocation; writes only reports in this helper's owned directory.
"""
import sys, ast, json, math, collections
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from programme_common import *
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely import constrained_delaunay_triangles,union_all
# Import only audited pure predicates; never execute a retained review's main body.
helper=F/'finish_envelope/qa/pure_geometry/review_finish.py'
tree=ast.parse(helper.read_text());wanted={'record','rayhits','surface_points','on_surface','strict_inside','contact_pair','topology'}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in wanted],type_ignores=[]),str(helper),'exec'))
def triang_face(v,face):
    q=np.array([v[i]for i in face]);local=q-q[0];normal=np.sum(np.cross(local,np.roll(local,-1,axis=0)),axis=0)
    if len(face)==3:return [tuple(tuple(x)for x in q)]
    axis=int(np.argmax(np.abs(normal)));proj=np.delete(q,axis,1);poly=Polygon(proj);assert poly.is_valid;out=[]
    for t in constrained_delaunay_triangles(poly).geoms:
        vv=[]
        for a in list(t.exterior.coords)[:3]:
            ix=np.argmin(np.linalg.norm(proj-a,axis=1));assert np.linalg.norm(proj[ix]-a)<1e-7;vv.append(tuple(q[ix]))
        if np.dot(np.cross(np.array(vv[1])-vv[0],np.array(vv[2])-vv[0]),normal)<0:vv.reverse()
        out.append(tuple(vv))
    return out

def cache(parts):
    for p in parts:
        p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
    return parts

def actual_contact(a,b):
    # A material batch of disconnected botanical surfaces is not a single solid;
    # open leaves and image quads have no well-defined enclosed inside. Preserve
    # actual triangle tests and only ask whether their surface enters the solid.
    if not a.get('open_surface') and not b.get('open_surface'):return contact_pair(a,b)
    r=contact_pair(a,b,interior=False)
    if not overlap(a['bounds'],b['bounds'],-TOL):return r
    for x,y in [(a,b),(b,a)]:
        if y.get('open_surface'):continue
        for q in surface_points(x):
            if strict_inside(q,y):return dict(r,penetration=True,witness_part=x['name'],inside_part=y['name'],witness_xyz=list(q),method='actual surface point inside closed receiver')
        if r['touch']:
            for t in x['triangles']:
                for aa,bb in zip(t,t[1:]+t[:1]):
                    ll=length(sub(bb,aa))
                    if ll<TOL:continue
                    hs=sorted(set([0,1]+[h['distance_m']/ll for h in rayhits(aa,bb,[y])]))
                    for l,rr in zip(hs,hs[1:]):
                        q=add(aa,mul(sub(bb,aa),(l+rr)/2))
                        if strict_inside(q,y):return dict(r,penetration=True,witness_part=x['name'],inside_part=y['name'],witness_xyz=list(q),method='actual surface edge interval inside closed receiver')
    return dict(r,method='open surface triangle/closed-solid test; no fictitious open-surface interior')

def footprint(p):
    if '_footprint'not in p:p['_footprint']=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if Polygon([(v[0],v[2])for v in t]).area>1e-12])
    return p['_footprint']

def run(evaluated_snapshot=None, actual_core_plan=None):
    plan=verify_inputs();issues=[];warnings=[]
    if evaluated_snapshot is None:parts=cache(mesh_geometry(plan))
    else:
        data=read(evaluated_snapshot)if isinstance(evaluated_snapshot,(str,Path))else evaluated_snapshot
        assert data['core_plan_sha256']==sha(CORE)and data['input_pins_sha256']==sha(S/'INPUT_PINS.json')
        parts=cache([dict(p)for p in data['parts']])
    core_input=plan
    if actual_core_plan is not None:
        core_input=read(actual_core_plan)if isinstance(actual_core_plan,(str,Path))else actual_core_plan
        expected={p['name']:p for p in plan['parts']}
        assert len(core_input['parts'])==len(expected) and {p['name']for p in core_input['parts']}==set(expected),'Actual core identity mismatch'
        for p in core_input['parts']:
            ref=expected[p['name']]
            assert p['vertices_xyz']==ref['vertices_xyz'],('Actual core vertices differ from pinned float32 plan',p['name'])
            assert p.get('parent_design_id')==ref.get('parent_design_id'),('Actual core family mismatch',p['name'])
            assert p.get('support')==ref.get('support'),('Actual core support identity mismatch',p['name'])
            assert p.get('evaluated_triangles'),'Actual source must provide evaluated triangle indices'
    core=[]
    for p in core_input['parts']:
        v=p['vertices_xyz'];tr=[[v[i]for i in t]for t in p['evaluated_triangles']]if 'evaluated_triangles'in p else[t for f in p['faces']for t in triang_face(v,f)]
        core.append(record(p['name'],v,tr,meta=p))
    cache(core);cm={p['name']:p for p in core}
    ss=sign_frames(plan);arrow=arrow_spec(ss[0]);outline=arrow['outline_uv'];n=len(outline);lv=[[x,y,d]for d in arrow['depth_d']for x,y in outline];fs=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
    av=[from_local(v,ss[0]['new_frame'])for v in lv];ar=record(arrow['name'],av,[t for f in fs for t in triang_face(av,f)],group='signs',instance=ss[0]['instance_name'],source_part='new closed route arrow');cache([ar]);
    if evaluated_snapshot is None:parts.append(ar)
    else:ar=next(p for p in parts if p['name']==arrow['name'])
    at=topology(ar);assert not at['degenerate_triangles']and not at['nonmanifold_edges']and not at['inconsistent_winding_edges']
    # Exact shell triangles are independently mapped to retained source names.
    retained_glb=read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb')
    old=cache([record(p['source_name'],[v for i in p['global_triangle_indices']for v in retained_glb['triangles'][i]],[retained_glb['triangles'][i]for i in p['global_triangle_indices']],meta=p)for p in read(P/'geometry/RETAINED_PART_BOUNDS.json')['parts']])
    boxmap={r['id']:r['bounds_xyz']for r in read(P/'geometry/ADDITIVE_RESERVATIONS.json')['candidates']};reservation=[]
    for group,key in [('plants','upper_east_gallery_rest_bay'),('display','upper_east_gallery_rest_bay'),('signs','lift_aft_return')]:
        # Locate approved labels by exact known bounds; IDs remain recorded.
        if key not in boxmap:
            key=next(k for k,b in boxmap.items()if (group=='signs'and abs(b[0][2]+410.2)<.001)or(group!='signs'and abs(b[0][0]+11.2)<.001))
        lo,hi=boxmap[key];subset=[p for p in parts if p['group']==group]
        bad=[p['name']for p in subset if any(v[j]<lo[j]-TOL or v[j]>hi[j]+TOL for v in p['vertices']for j in range(3))]
        reservation.append({'group':group,'reservation':key,'outside_parts':bad,'bounds_xyz':bounds([v for p in subset for v in p['vertices']])})
        if bad:issues.append({'kind':'reservation','row':reservation[-1]})
    soil=[]
    for a in source_inventory(plan):
        r=a['reservation'];s=cm[r['soil_object']];top=max(v[1]for v in s['vertices']);poly=union_all([Polygon([(v[0],v[2])for v in t])for t in s['triangles']if max(abs(v[1]-top)for v in t)<TOL]);subset=[p for p in parts if p['instance']==a['instance_name']]
        if evaluated_snapshot is None:
            markers=[plant_point(m['point_local'],r)for m in a['asset']['markers']if m['kind']=='soil_contact']
            roots=[plant_point(v,r)for p in a['asset']['parts']if p['name']in a['asset']['root_parts']for v in p['vertices']if v[2]<=min(q[2]for q in p['vertices'])+1e-7]
        else:
            marker_names={m['name']for m in a['asset']['markers']if m['kind']=='soil_contact'}
            actual_markers=[o for o in data['objects']if o['type']=='EMPTY'and o['properties'].get('programme_instance')==a['instance_name']and o['properties'].get('retained_source_object')in marker_names]
            assert {o['properties']['retained_source_object']for o in actual_markers}==marker_names,('Missing actual soil markers',a['instance_name'])
            markers=[G([o['matrix_world'][j][3]for j in range(3)])for o in actual_markers]
            root_parts=[p for p in subset if p['source_part']in a['asset']['root_parts']]
            assert {p['source_part']for p in root_parts}==set(a['asset']['root_parts']),('Missing actual botanical roots',a['instance_name'])
            roots=[v for p in root_parts for v in p['vertices']if v[1]<=min(q[1]for q in p['vertices'])+1e-7]
        gap=max(abs(v[1]-top)for v in markers+roots);bad=[v for v in roots+markers if not poly.buffer(TOL).covers(Point(v[0],v[2]))]
        # Project every leaf/root vertex onto exact actual soil, not its bounding box.
        escaped=[v for p in subset for v in p['vertices']if not poly.buffer(TOL).covers(Point(v[0],v[2]))]
        row={'instance':a['instance_name'],'soil':r['soil_object'],'soil_top_y':top,'contact_geometry_source':'evaluated root-base vertices and EMPTY world matrices'if evaluated_snapshot is not None else'pinned retained source roots/markers transformed to new soil','root_marker_count':len(markers),'root_marker_points_xyz':markers,'root_base_vertex_count':len(roots),'maximum_contact_gap_m':gap,'unsupported_root_points':bad,'projected_vertices_outside_soil_count':len(escaped),'scale_xyz':r['scale_xyz'],'world_bounds_xyz':bounds([v for p in subset for v in p['vertices']])};soil.append(row)
        if gap>TOL or bad or escaped:issues.append({'kind':'soil','row':row})
    # Actual arrow rear lies on copied backing front, never buried or floating.
    backing=next(p for p in parts if p['source_part']=='PWF_threshold_lift_MapBacking');arrow_contact=actual_contact(ar,backing)
    if not arrow_contact['touch']or arrow_contact['penetration']:issues.append({'kind':'arrow_backing_contact','row':arrow_contact})
    # Exact contact tests on the four retained backplates plus sealed feed boss.
    receiver=cm['EAST_Display_AngledReceiver'];mounts=[]
    for p in parts:
        if p['group']=='display'and ('wall_backplate_'in p['source_part']or 'sealed_rear_feed_boss'in p['source_part']):
            row={'part':p['name'],'receiver':receiver['name'],**contact_pair(p,receiver)};mounts.append(row)
            if not row['touch']or row['penetration']:issues.append({'kind':'display_mount','row':row})
    for p in parts:
        if p['group']=='signs'and 'FixedPad_'in p['source_part']:
            row={'part':p['name'],'receiver':'EAST_Lift_AftMountingField',**contact_pair(p,cm['EAST_Lift_AftMountingField'])};mounts.append(row)
            if not row['touch']or row['penetration']:issues.append({'kind':'sign_mount','row':row})
    # Existing botanical self-overlap is retained source construction. Only new
    # interference with architecture, other programmes, and retained shell is tested.
    interference=[]
    for p in parts:
        for q in core+old:
            if not overlap(p['bounds'],q['bounds'],-TOL if p.get('open_surface')or q.get('open_surface')else TOL):continue
            result=actual_contact(p,q)
            if result['penetration']:interference.append({'new':p['name'],'other':q['name'],**result})
    display=[p for p in parts if p['group']=='display'];plantparts=[p for p in parts if p['group']=='plants']
    for p in plantparts:
        for q in display:
            if overlap(p['bounds'],q['bounds'],-TOL if p.get('open_surface')or q.get('open_surface')else TOL):
                result=actual_contact(p,q)
                if result['penetration']:interference.append({'new':p['name'],'other':q['name'],**result})
    if interference:issues.append({'kind':'interpenetrations','rows':interference})
    protected=read(P/'geometry/PROTECTED_RESERVATIONS.json');routes=[]
    route_specs=[(r['id'],union_all([Polygon(p)for p in r['plan_polygon_union_xz']]),*r['y_m'])for r in protected['routes']]
    route_specs += [(r['name'],LineString([(p[0],p[2])for p in r['points_xyz']]).buffer(r['radius_m']),r['points_xyz'][0][1]+.02,r['points_xyz'][0][1]+.02+r['height_m'])for r in plan['approach_paths']]
    route_specs += [('upper_apron',Polygon([[-14.4,-454],[-11.2,-454],[-11.2,-445],[-14.4,-445]]),52.5,54.5)]
    for name,poly,yl,yh in route_specs:
        hit=[]
        for p in parts:
            if min(yh,p['bounds'][1][1])-max(yl,p['bounds'][0][1])<=TOL:continue
            if footprint(p).intersection(poly).area>1e-8:hit.append(p['name'])
        routes.append({'name':name,'hits':hit})
        if hit:issues.append({'kind':'route','row':routes[-1]})
    # Optical glazing is a legitimate transparent image cover, not an occluder.
    optical={'M0__original_pool_leisure_image','M0__recessed_display_glazing'}
    solid=[p for p in parts if not(p['group']=='display'and p['source_part']in optical)]
    imagepart=next(p for p in parts if p['source_part']=='M0__original_pool_leisure_image');oldf,newf=display_frames(plan);local=[to_local(v,newf)for v in imagepart['vertices']];ib=bounds(local)
    targets=[('centre',from_local([(ib[0][0]+ib[1][0])/2,(ib[0][1]+ib[1][1])/2,ib[0][2]],newf))]+[(f'corner_{i}',from_local([u,v,ib[0][2]],newf))for i,(u,v)in enumerate([(ib[0][0],ib[0][1]),(ib[1][0],ib[0][1]),(ib[1][0],ib[1][1]),(ib[0][0],ib[1][1])])]
    media_rays=[];market_rays=[]
    for view in plan['seated_views']:
        for name,target in targets:
            hits=rayhits(view['eye_xyz'],target,core+old+solid);row={'view':view['name'],'target':name,'target_xyz':target,'hits':hits};media_rays.append(row)
            if hits:issues.append({'kind':'media_image_occlusion','row':row})
        h=rayhits(view['eye_xyz'],view['market_target_xyz'],parts);market_rays.append({'view':view['name'],'new_programme_hits':h})
        if h:issues.append({'kind':'market_view_occlusion','row':market_rays[-1]})
    preserved=[]
    for v in read(P/'geometry/PRESERVED_VIEWS.json'):
        h=rayhits(v['eye_xyz'],v['target_xyz'],parts);preserved.append({'name':v['name'],'hits':h})
        if h:issues.append({'kind':'preserved_view_occlusion','row':preserved[-1]})
    sign_rays=[]
    eye=next(v['eye_xyz']for v in plan['standing_views']if v['name']=='retained_long_pool')
    for s in ss:
        glyph=next(p for p in parts if p['source_part']=='PWF_'+s['id']+'_Glyphs_0');target=from_local([0,0,.13],s['new_frame']);obstacles=[p for p in core+old+parts if p.get('instance')!=s['instance_name']];h=rayhits(eye,target,obstacles);sign_rays.append({'sign':s['id'],'eye_xyz':eye,'target_xyz':target,'hits':h,'scope':'Centre ray at retained long-pool eye, not full low-resolution readability'})
        if h:issues.append({'kind':'sign_view_occlusion','row':sign_rays[-1]})
    fixtures=[]
    for f in plan['fixture_reservations']:
        h=rayhits(f['position_xyz'],add(f['position_xyz'],mul(f['direction_xyz'],.06)),parts);fixtures.append({'name':f['name'],'new_programme_exit_hits':h})
        if h:issues.append({'kind':'fixture_exit','row':fixtures[-1]})
    for r in plan.get('cleaning_reaches',[]):
        h=rayhits(r['eye_xyz'],r['target_xyz'],parts)
        if h:issues.append({'kind':'cleaner_reach','name':r['name'],'hits':h})
    report={'status':'PASS_PURE_RETAINED_PROGRAMME'if not issues else'RETAINED_PROGRAMME_REQUIRES_CORRECTION','scope':'Actual evaluated combined source snapshot'if evaluated_snapshot is not None else'Pinned independently-reopened crown source meshes and actual retained GLB geometry, relocated by the same frame conventions. No Blender build/reopen or game validation.','core_plan_sha256':sha(CORE),'core_triangle_source':'actual_evaluated_source'if actual_core_plan is not None else'planned_polygon_triangulation','inputs_sha256':sha(S/'INPUT_PINS.json'),'programme_geometry_parts':len(parts),'triangles':sum(len(p['triangles'])for p in parts),'issues':issues,'warnings':warnings,'reservations':reservation,'soil_checks':soil,'physical_mounts':mounts,'interferences':interference,'route_checks':routes,'media_image_rays':media_rays,'market_rays':market_rays,'preserved_view_rays':preserved,'sign_centre_rays':sign_rays,'fixture_exits':fixtures,'display_frame':newf,'display_basis_rule':'U = world +Y cross N; U cross V = N; positive determinant, no mirrored artwork','sign_placements':[{k:v for k,v in s.items()if k not in ['meshes','source_spec']}for s in ss],'arrow':arrow,'arrow_topology':at,'arrow_backing_contact':arrow_contact,'budget':plan['budget'],'excluded_checks':['Independent Blender source build/reopen and exact transformed source validation','Full scene optical appearance/readability, normal game views','Native lighting selector and engine circulation/capsule/cart behavior','Future single-display extraction/export']}
    verify_inputs();return report
if __name__=='__main__':
    r=run();(S/'PROGRAMME_REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['status','programme_geometry_parts','triangles','issues']},indent=2));sys.exit(bool(r['issues']))
