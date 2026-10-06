"""Pure Python source fit/preservation screen. No bpy, Godot, subprocess or UI."""
import argparse, json, math
from pathlib import Path
from wayfinding_geometry import *
HERE=Path(__file__).resolve().parent

def screen(contract_path=HERE/'wayfinding_contract.json',catalogue=None,game=None):
    d=json.loads(Path(contract_path).read_text());cat=Path(catalogue or d['source_defaults']['catalogue']);game=Path(game or d['source_defaults']['game'])
    issues=[];checks=[]
    def check(name,ok,**detail):
        row={'check':name,'pass':bool(ok),**detail};checks.append(row)
        if not ok:issues.append(row)
    check('exact_11_existing_family_derivatives',len(d['signs'])==11 and d['catalogue_id']=='AST-RES-001' and d['family']=='residential_wayfinding_bay' and d['new_design_ids']==0)
    check('no_unresolved_mounting_compromises',not d['unresolved_mounting_compromises'])
    for p in d['pins']:
        f=(cat if p['root']=='catalogue' else game)/p['path']
        check('preservation:'+p['path'],f.is_file() and sha(f)==p['sha256'])
    if any(not r['pass'] for r in checks):return {'pass':False,'issues':issues,'checks':checks}
    section=json.loads((cat/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text())
    runtime=json.loads((game/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json').read_text())
    adopted=json.loads((game/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text())
    for key in ['public_interfaces','accessible_ramp','door_fittings','wet_market_link','staff','source_parts']:
        check('adopted_source_contract_agreement:'+key,adopted[key]==section[key])
    for relative in ['grand_pool_orchard_section/exports/AST-AQU-016.glb','grand_pool_orchard_section/exports/AST-CIR-005_forward_pool_market.glb','aquatic_towel_use/exports/AST-AQU-007.glb','aquatic_towel_use/exports/AST-AQU-008.glb','guest_entry_door/exports/AST-DOR-002_wide.glb']:
        check('adopted_export_agreement:'+Path(relative).name,sha(cat/'assets'/relative)==sha(game/'assets/models'/Path(relative).name))
    parts={p['name']:p for p in section['source_parts'] if not p.get('export_excluded')}
    stock={p['name']:p for p in runtime['placements']}
    towel=json.loads((cat/'assets/aquatic_towel_use/qa/source_geometry.json').read_text())
    manifest=json.loads((cat/'catalogue_manifest.json').read_text())
    check('exact_catalogue_owner',any(a['catalogue_id']=='AST-RES-001' and a['family']=='residential_wayfinding_bay' for a in manifest['assets']))
    contacts=0;source_intersections=[];components=[]
    core_path='assets/grand_pool_orchard_section/exports/AST-CIR-005_forward_pool_market.glb'
    core_triangles=glb_triangles(cat/core_path,[0,0,-432])
    core_bounds=[bounds(t) for t in core_triangles]
    for s in d['signs']:
        for c in s['components']:
            if 'local_bounds_uvd' in c:
                recomputed=local_box(s,c['local_bounds_uvd'])
                check(s['id']+':component_transform:'+c['name'],all(abs(recomputed[j][i]-c['world_bounds_xyz'][j][i])<1e-8 for j in range(2) for i in range(3)))
        recomputed=local_box(s,s['glyph_envelope_local_uvd'])
        check(s['id']+':glyph_envelope_transform',all(abs(recomputed[j][i]-s['glyph_envelope_world_xyz'][j][i])<1e-8 for j in range(2) for i in range(3)))
        sid=s['id'];right,up,normal=s['right_xyz'],s['up_xyz'],s['normal_xyz']
        check(sid+':orthonormal_view_plane',all(abs(norm(v)-1)<1e-9 for v in [right,up,normal]) and norm(sub(cross(right,up),normal))<1e-9)
        check(sid+':front_facing_approach',dot(sub(s['viewpoint_xyz'],s['origin_xyz']),normal)>.05)
        for patch in s['contact_patches']:
            rec=d['supports'][patch['support']];samples=contact_samples(patch);contacts+=len(samples)
            if rec['kind']=='source_record_axis_aligned_box':
                source=parts[rec['object']];b=bounds(source['world_vertices']);axis=patch['normal_axis'];sign=patch['outward_normal_xyz'][axis];face=b[1 if sign>0 else 0][axis]
                okay=all(abs(p[axis]-face)<1e-5 and all(b[0][i]-1e-5<=p[i]<=b[1][i]+1e-5 for i in range(3)) for p in samples)
            elif rec['kind']=='source_named_export_triangles':
                tri=core_triangles
                okay=all(any(point_on_triangle(p,t) for t in tri) for p in samples)
            else:
                source=next(p for p in towel[rec['asset']]['parts'] if p['name']==rec['object']);check(sid+':fixed_support:'+rec['object'],source['motion_group']=='fixed')
                vv=[blender_to_world(v,stock[rec['placement_name']]) for v in source['vertices']]
                tri=[[vv[j] for j in t] for t in source['triangles']]
                okay=all(any(point_on_triangle(p,t) for t in tri) for p in samples)
            check(sid+':contact:'+patch['support'],okay,samples=len(samples),patch_bounds_xyz=patch['bounds_xyz'])
        # Every proposed part has a physical graph path to a support-intersecting mount.
        cc=s['components'];touched=set()
        for i,c in enumerate(cc):
            for patch in s['contact_patches']:
                b=patch['bounds_xyz'];axis=patch['normal_axis'];bb=[b[0].copy(),b[1].copy()];bb[0][axis]-=1e-5;bb[1][axis]+=1e-5
                if overlap(c['world_bounds_xyz'],bb,tol=0):touched.add(i)
        for _ in cc:
            touched|={i for i,c in enumerate(cc) if any(overlap(c['world_bounds_xyz'],cc[j]['world_bounds_xyz'],tol=-1e-7) for j in touched)}
        check(sid+':connected_mount_frame_backing_graph',len(touched)==len(cc),parts=len(cc),connected=len(touched))
        if 'arrow' in s:
            actual_route=section['public_interfaces']['D08_route_xyz'] if sid=='ramp_lower' else section['accessible_ramp']['route_xyz']
            actual_a,actual_b=(actual_route[-2],actual_route[-1]) if sid=='ramp_lower' else (actual_route[-2],actual_route[-3])
            expected=arrow_projection(actual_a,actual_b,right,up,normal)
            check(sid+':actual_route_arrow_projection',expected==s['arrow'],unit_arrow_uv=expected['unit_arrow_uv'])
        for c in cc+[{'name':'ReservedGlyphEnvelope','world_bounds_xyz':s['glyph_envelope_world_xyz']}]:
            b=c['world_bounds_xyz'];components.append((sid,c['name'],b))
            allowed={d['supports'][a['support']]['object'] for a in s['contact_patches'] if d['supports'][a['support']]['kind']=='source_record_axis_aligned_box'}
            for name,p in parts.items():
                if name not in allowed and overlap(b,bounds(p['world_vertices'])):source_intersections.append([sid,c['name'],name])
            for name,p in stock.items():
                if name!=s.get('attached_instance') and overlap(b,[p['envelope_min_xyz'],p['envelope_max_xyz']]):source_intersections.append([sid,c['name'],name])
        if s.get('attached_instance'):
            p=stock[s['attached_instance']];aid='AST-AQU-007' if s['id']=='towels' else 'AST-AQU-008';allowed={d['supports'][q['support']]['object'] for q in s['contact_patches']}
            for source in towel[aid]['parts']:
                if source['name'] in allowed:continue
                b=bounds([blender_to_world(v,p) for v in source['vertices']])
                for c in cc:
                    if overlap(c['world_bounds_xyz'],b):source_intersections.append([sid,c['name'],source['name']])
    core_hits=[]
    for sid,part,b in components:
        sign=next(s for s in d['signs'] if s['id']==sid)
        allowed=[d['supports'][p['support']]['bounds_xyz'] for p in sign['contact_patches'] if d['supports'][p['support']]['kind']=='source_named_export_triangles']
        for t,tb in zip(core_triangles,core_bounds):
            if not overlap(b,tb):continue
            if any(all(all(ab[0][i]-1e-5<=v[i]<=ab[1][i]+1e-5 for i in range(3)) for v in t) for ab in allowed):continue
            core_hits.append([sid,part,tb])
    check('forward_core_header_and_surviving_geometry_clearance',not core_hits,hits=core_hits[:20])
    check('no_nonmount_source_or_furnishing_envelope_intersections',not source_intersections,hits=source_intersections)
    reservations=[]
    def reserve(name,lo,hi):reservations.append((name,[lo,hi]))
    for floor in [44,52.5]:reserve('public_3.2m_aperture_'+str(floor),[-8.22,floor,-435],[-7.40,floor+3.2,-429])
    # Full cross-section clearance, not just route centrelines.
    for name,y,r in [('dry_east_approach',44,section['public_interfaces']['D08_dry_east_approach_clear_rect']),('ramp_bottom',44,section['accessible_ramp']['bottom_landing']['rect']),('ramp_top',46.2,section['accessible_ramp']['top_landing_and_bridge']['rect']),('dry_market_bypass',52.5,section['wet_market_link']['market_bypass_clear_rect'])]:
        reserve(name,[r[0],y+.001,r[2]],[r[1],y+3.2,r[3]])
    for door in section['door_fittings']:
        # Include all leaf travel, full cassette span, physical controls and a bounded hand-use volume.
        place={'position_xyz':door['root_xyz'],'yaw_radians':door['yaw_radians']}
        for name,b in [('full_slide_motion',[[-2.58,0,-.13],[2.58,2.5,.13]]),('outside_control',[[-2.62,.90,-.43],[-2.16,1.54,-.11]]),('inside_control',[[-2.62,.90,.11],[-2.16,1.54,.43]])]:
            bb=bounds([yaw_point(v,place) for v in corners(b)]);reserve(door['name']+':'+name,*bb)
    for floor in [46.2,52.5]:
        reserve('local_lift_gate_full_width_'+str(floor),[-13.84,floor,-414.6],[-13.10,floor+2.85,-410.2])
        reserve('local_lift_call_hand_'+str(floor),[-13.56,floor+1.0,-414.3],[-12.96,floor+1.6,-413.8])
    # All towel semantic clear volumes, complete extraction sweep and staging.
    for aid,placement_name in [('AST-AQU-007','clean_towel_retrieval'),('AST-AQU-008','used_towel_return')]:
        man=json.loads((cat/f'assets/aquatic_towel_use/{aid}.manifest.json').read_text());p=stock[placement_name]
        for clear in man['clear_volumes']:
            bb=bounds([blender_to_world(v,p) for v in corners([clear['min_m'],clear['max_m']])]);reserve(aid+':'+clear['name'],*bb)
        if 'motion' in man:
            for name in ['swept_reserve','service_staging']:
                m=man['motion'];bb=bounds([blender_to_world(v,p) for v in corners([m[name+'_min_m'],m[name+'_max_m']])]);reserve(aid+':'+name,*bb)
    for r in runtime['return_reserves']:reserve('runtime_return:'+r['name'],r['min_xyz'],r['max_xyz'])
    hits=[[sid,part,name] for sid,part,b in components for name,clear in reservations if overlap(b,clear)]
    check('all_aperture_control_motion_towel_clear_volumes',not hits,volume_count=len(reservations),hits=hits)
    routes={
      'D08_public':section['public_interfaces']['D08_route_xyz'], 'D09_public':section['public_interfaces']['D09_route_xyz'],
      'ramp':section['accessible_ramp']['route_xyz'],
      'D09_dry_loop':[[x,52.5,z] for x,z in section['market']['adopted_dry_loop_centreline_xz']],
      'local_lift_lower':section['wet_market_link']['lift']['lower_approach_xyz']+[[-13.45,46.2,-412.4]]}
    routes.update({'existing_approach_'+str(i):p['points'] for i,p in enumerate(runtime['approach_paths'])})
    for y in [46.2,52.5]:routes['staff_'+str(y)]=[[x,y,z] for x,z in section['staff']['adopted_route_xz']]
    samples=0;hits=[]
    for name,route in routes.items():
        for a,b in zip(route,route[1:]):
            n=max(1,math.ceil(norm(sub(b,a))/.05))
            for j in range(n+1):
                p=add(a,mul(sub(b,a),j/n));samples+=1;proxy=[[p[0]-.32,p[1]+.02,p[2]-.32],[p[0]+.32,p[1]+1.9,p[2]+.32]]
                for sid,part,bb in components:
                    if overlap(bb,proxy):hits.append([name,sid,part,p])
    check('retained_route_capsule_envelope_screen',not hits,samples=samples,radius_m=.32,height_m=1.9,hits=hits[:30])
    # Original 532 source cart/operator poses, elevated loaded box capped at 1.9 m.
    route_evidence=cat/'assets/grand_pool_orchard_section/qa/plan_route_verification.json'
    cart=json.loads(route_evidence.read_text())['screened_cart_proxy'];cart_hits=[]
    for y in [46.2,52.5]:
        for x,z,yaw in cart['route_poses']:
            p={'position_xyz':[x,y,z],'yaw_radians':yaw}
            # Deliberately wider than loaded tray; includes operator to rear. This is conservative geometry, not force-driven acceptance.
            bb=bounds([yaw_point(v,p) for v in corners([[-.65,.02,-2.0],[.65,1.9,.70]])])
            for sid,part,b in components:
                if overlap(b,bb):cart_hits.append([sid,part,x,y,z,yaw])
    check('retained_cart_operator_pose_screen',not cart_hits,poses=len(cart['route_poses'])*2,hits=cart_hits[:30],scope='Conservative transformed compound-envelope proxy only; real cart/reverse/regrip remains gated')
    def linear(c): c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
    def lum(rgb):return sum(w*linear(c) for w,c in zip([.2126,.7152,.0722],rgb))
    material=d['material_roles'];ratio=(lum(material['ivory_enamel']['colour_srgb_8bit'])+.05)/(lum(material['warm_walnut']['colour_srgb_8bit'])+.05)
    check('palette_nominal_glyph_contrast',ratio>=4.5,nominal_srgb_contrast=ratio,limitation='Manifest nominal colors only; texture/effects/lighting pixel legibility remains required')
    return {'pass':not issues,'status':'pure_source_screen_pass_not_engine_acceptance' if not issues else 'fail_closed','contract_sha256':sha(contract_path),'checks':checks,'issues':issues,'contact_samples':contacts,'source_pin_count':len(d['pins']),'route_samples':samples,'engine_or_blender_jobs_run':0,'required_gates':d['required_gates']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,default=HERE/'wayfinding_contract.json');p.add_argument('--catalogue',type=Path);p.add_argument('--game',type=Path);p.add_argument('--report',type=Path,default=HERE/'SOURCE_SCREEN_REPORT.json');a=p.parse_args()
    r=screen(a.contract,a.catalogue,a.game);dump(a.report,r);print(json.dumps({'pass':r['pass'],'issues':r['issues'],'checks':len(r['checks']),'contact_samples':r.get('contact_samples'),'route_samples':r.get('route_samples')},indent=2));raise SystemExit(0 if r['pass'] else 1)
