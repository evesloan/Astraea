"""Read-only retained source/GLB geometry and placements. Safe without Blender."""
import sys, json, hashlib, math, ast, importlib.util, collections
from pathlib import Path
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent
P=S.parent
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
F=C/'assets/grand_pool_first_pass'
FULL=F/'architectural_composition/feature_layers_next/planting/full_mass001'
BASAL=F/'comfort_greenery/greenery'
MEDIA=F/'comfort_greenery/media'
SIGNS=F/'finish_envelope/wayfinding'
CORE=P/'source_blockin001/CORE_PLAN.json'
TOL=5e-5
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def B(v):return [v[0],-v[2],v[1]]
def G(v):return [v[0],v[2],-v[1]]
geo_path=F/'finish_envelope/stock/geometry.py'
spec=importlib.util.spec_from_file_location('retained_programme_geo',geo_path)
geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
for _name in dir(geo):
    if not _name.startswith('_'):globals()[_name]=getattr(geo,_name)
def frame(origin,u,v,n):return {'origin_xyz':list(origin),'right_xyz':list(u),'up_xyz':list(v),'normal_xyz':list(n)}
def from_local(v,f):return add(f['origin_xyz'],add(add(mul(f['right_xyz'],v[0]),mul(f['up_xyz'],v[1])),mul(f['normal_xyz'],v[2])))
def to_local(v,f):
    q=sub(v,f['origin_xyz']);return [dot(q,f[k])for k in ['right_xyz','up_xyz','normal_xyz']]
def reframe(v,old,new):return from_local(to_local(v,old),new)
def plant_point(v,r):return transform(G(v),r['position_xyz'],r['yaw_radians'])
def display_frames(plan):
    d=plan['display_reservation'];n=unit(d['front_normal_xyz']);v=(0,1,0);u=cross(v,n)
    assert dot(cross(u,v),n)>0.999999999
    return frame([-51.2,54.53,-446.28],[-1,0,0],[0,1,0],[0,0,-1]),frame(d['image_origin_xyz'],u,v,n)
def inputs():
    paths=[P/'DESIGN_BRIEF.md',CORE,CORE.with_name('CORE_REVIEW.json'),geo_path,F/'finish_envelope/qa/pure_geometry/review_finish.py',FULL/'source_common.py',FULL/'candidate_v001/qa/REOPENED_GEOMETRY.json',FULL/'candidate_v001/qa/SOURCE_QA.json',BASAL/'greenery_contract.json',BASAL/'candidate_v001/qa/SOURCE_QA_all.json',BASAL/'candidate_v001/qa/GLB_EQUIVALENCE_r002_all.json',MEDIA/'source_contract.json',MEDIA/'content_manifest.json',MEDIA/'source/AST-LIB-010_pool_leisure_displays.blend',MEDIA/'exports_r002/AST-LIB-010_pool_leisure_displays.glb',MEDIA/'qa/reopen_actual_image_r005/INDEPENDENT_REOPEN_QA_ACTUAL_IMAGE_001.json',MEDIA/'qa/EXPORT_002.json',SIGNS/'source/grand_pool_wayfinding.blend',SIGNS/'wayfinding_contract.json',SIGNS/'exports_r002/AST-RES-001_pool_wayfinding.glb',SIGNS/'qa/wayfinding_source_reopen004.json',C/'assets/grand_pool_orchard_section/source/connected_contract.json',C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb',P/'geometry/RETAINED_PART_BOUNDS.json',P/'geometry/PROTECTED_RESERVATIONS.json',P/'geometry/ADDITIVE_RESERVATIONS.json',P/'geometry/PRESERVED_VIEWS.json',P/'geometry/FLOOR_POLYGONS.json']
    for i in ['00','03']:
        paths += [FULL/f'candidate_v001/source/AST-BOT-002_pool_loggia_mass_{i}.blend',BASAL/f'candidate_v001/source/AST-BOT-003_pool_basal_{i}.blend',BASAL/f'candidate_v001/exports_r002/AST-BOT-003_pool_basal_{i}.glb']
    return paths

def verify_inputs(core_plan_path=CORE):
    pins=read(S/'INPUT_PINS.json');assert Path(core_plan_path).resolve()==CORE.resolve(),'This helper is pinned to one core plan'
    for p,h in pins['sha256'].items():assert sha(p)==h,'Pinned input changed: '+p
    d=read(CORE);r=read(CORE.with_name('CORE_REVIEW.json'))
    assert r['status']=='PASS_CORE_PURE_GEOMETRY' and r['plan_sha256']==sha(CORE)
    return d

def source_inventory(plan):
    full=read(FULL/'candidate_v001/qa/REOPENED_GEOMETRY.json');basal=read(BASAL/'greenery_contract.json')
    out=[]
    for r in plan['plant_reservations']:
        for kind,family,stem,root,document in [('full','AST-BOT-002','AST-BOT-002_pool_loggia_mass_',FULL,full),('basal','AST-BOT-003','AST-BOT-003_pool_basal_',BASAL,basal)]:
            name=stem+r['variant'];asset=next(a for a in document['assets']if a['name']==name)
            out.append({'kind':kind,'parent_design_id':family,'family':'botanical_understory','source_root':name,'instance_name':'EAST_'+r['name'].title()+'_'+kind.title(),'source':str(root/'candidate_v001/source'/f'{name}.blend'),'reservation':r,'asset':asset})
    return out

def sign_frames(plan):
    signs=read(SIGNS/'wayfinding_contract.json')['signs'];mesh=read_glb(SIGNS/'exports_r002/AST-RES-001_pool_wayfinding.glb')['meshes']
    field=next(p for p in plan['parts']if p['name']=='EAST_Lift_AftMountingField');face=max(v[2]for v in field['vertices_xyz']);out=[]
    for key,y in [('threshold_lift',48.1),('main_D09',48.8)]:
        s=next(s for s in signs if s['id']==key);old={k:s[k]for k in ['origin_xyz','right_xyz','up_xyz','normal_xyz']}
        subset=[m for m in mesh if m['name'].startswith('PWF_'+key+'_')]
        rear=min(to_local(v,old)[2]for m in subset for v in m['vertices']);new=frame([-15.5,y,face-rear],[1,0,0],[0,1,0],[0,0,1])
        backing=next(m for m in subset if m['name'].endswith('_MapBacking'));backing_front=max(to_local(v,old)[2]for v in backing['vertices']);glyphs=[m for m in subset if '_Glyphs_'in m['name']];gb=bounds([to_local(v,old)for m in glyphs for v in m['vertices']]);out.append({'id':key,'source_root':'SIGN_'+key,'instance_name':'EAST_Sign_'+key,'parent_design_id':'AST-RES-001','family':'residential_wayfinding_bay','source':str(SIGNS/'source/grand_pool_wayfinding.blend'),'old_frame':old,'new_frame':new,'mount_surface_z':face,'physical_rear_local_d':rear,'glyph_bounds_local_uvd':gb,'backing_front_local_d':backing_front,'lettering_translation_local_uvd':[0,0,0],'source_spec':s,'meshes':subset})
    return out

def arrow_spec(sign):
    # First leg follows +X around the shaft; the final gate is on its east face.
    section=read(C/'assets/grand_pool_orchard_section/source/connected_contract.json')
    lift=section['wet_market_link']['lift'];gate=lift['gate_centre_xz']
    mount=sign['new_frame']['origin_xyz'];waypoint=[gate[0]+1.1,46.2,-409.5];initial=[waypoint[0]-mount[0],0,0]
    direction=[dot(initial,sign['new_frame']['right_xyz']),dot(initial,sign['new_frame']['up_xyz'])];ln=math.hypot(*direction);direction=[d/ln for d in direction];assert direction==[1.0,0.0]
    base=[[-.105,-.025],[.025,-.025],[.025,-.073],[.115,0],[.025,.073],[.025,.025],[-.105,.025]]
    outline=[[.5+x,y]for x,y in base];assert min(x for x,y in outline)>sign['glyph_bounds_local_uvd'][1][0]+.025
    assert max(x for x,y in outline)<.625
    return {'name':'EAST_Sign_threshold_lift_RouteArrow','parent_design_id':'AST-RES-001','family':'residential_wayfinding_bay','outline_uv':outline,'depth_d':[sign['backing_front_local_d'],sign['glyph_bounds_local_uvd'][1][2]],'material_from':'PWF_threshold_lift_Glyphs_0','glyph_edge_gap_m':min(x for x,y in outline)-sign['glyph_bounds_local_uvd'][1][0],'unit_arrow_uv':direction,'route':{'source':str(C/'assets/grand_pool_orchard_section/source/connected_contract.json'),'source_key':'wet_market_link.lift.gate_centre_xz','actual_gate_centre_xz':gate,'first_leg_xyz':[1,0,0],'approach_waypoint_xyz':waypoint,'interpretation':'Turn right/east around the aft return to the existing east-facing gate; no west opening'}}

def mesh_geometry(plan):
    """Return source part geometry plus GLB-evaluated parts, without Blender."""
    allparts=[];plants=source_inventory(plan)
    for a in plants:
        r=a['reservation'];asset=a['asset']
        if a['kind']=='full':
            for p in asset['parts']:
                v=[plant_point(q,r)for q in p['vertices']];tr=[[v[i]for i in t]for t in p['evaluated_triangle_indices']]
                allparts.append({'name':a['instance_name']+'__'+p['name'],'vertices':v,'triangles':tr,'bounds':bounds(v),'group':'plants','instance':a['instance_name'],'source_part':p['name'],'kind':a['kind'],'open_surface':p['surface_kind'].startswith('open')})
        else:
            glb=read_glb(BASAL/'candidate_v001/exports_r002'/f"{a['source_root']}.glb")
            for p in glb['meshes']:
                conv=lambda q:transform(q,r['position_xyz'],r['yaw_radians']);v=[conv(q)for q in p['vertices']];tr=[[conv(q)for q in t]for t in p['triangles']]
                allparts.append({'name':a['instance_name']+'__'+p['name'],'vertices':v,'triangles':tr,'bounds':bounds(v),'group':'plants','instance':a['instance_name'],'source_part':p['name'],'kind':a['kind'],'open_surface':True})
    old,new=display_frames(plan)
    for p in read_glb(MEDIA/'exports_r002/AST-LIB-010_pool_leisure_displays.glb')['meshes']:
        if not p['name'].startswith('M0__'):continue
        conv=lambda q:reframe(q,old,new);v=[conv(q)for q in p['vertices']];tr=[[conv(q)for q in t]for t in p['triangles']]
        allparts.append({'name':'EAST_Display__'+p['name'],'vertices':v,'triangles':tr,'bounds':bounds(v),'group':'display','instance':'EAST_HousedDisplay','source_part':p['name'],'open_surface':p['name']=='M0__original_pool_leisure_image'})
    for s in sign_frames(plan):
        for p in s['meshes']:
            conv=lambda q:reframe(q,s['old_frame'],s['new_frame']);v=[conv(q)for q in p['vertices']];tr=[[conv(q)for q in t]for t in p['triangles']]
            allparts.append({'name':'EAST_'+p['name'],'vertices':v,'triangles':tr,'bounds':bounds(v),'group':'signs','instance':s['instance_name'],'source_part':p['name']})
    return allparts
