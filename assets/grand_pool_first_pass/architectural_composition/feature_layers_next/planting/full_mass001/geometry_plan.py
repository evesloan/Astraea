"""Pure scratch-only botanical geometry. No bpy, engine, renderer or exporter.

Run with python -B geometry_plan.py. Retained Geometry is copied byte-identically
from the verified pool authoring helper. Only a new JSON plan is written here.
The fit selects a blade's authored reach from exact polygon half-planes. It never
scales a completed plant, clips a tip, flattens a crown, or changes a material.
"""
import sys
sys.dont_write_bytecode = True
import json, math, hashlib
from pathlib import Path
from retained_geometry import Geometry, add, mul, sub, bounds

HERE = Path(__file__).resolve().parent
CAT = Path('/workspace/shared/astraea-catalogue-continuation-20261002')
POOL = CAT/'assets/grand_pool_first_pass'
PLAN = POOL/'architectural_composition/source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json'
TAU = math.tau

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def world(p, row):
    # Blender local -> glTF local -> the unchanged glTF Y-yaw instance.
    c,s=math.cos(row['yaw_radians']),math.sin(row['yaw_radians'])
    x,y,z=p; q=row['position_xyz']
    return [q[0]+c*x-s*y,q[1]+z,q[2]-s*x-c*y]
def local(p, row):
    c,s=math.cos(row['yaw_radians']),math.sin(row['yaw_radians'])
    x,y,z=sub(p,row['position_xyz'])
    return [c*x-s*z,-s*x-c*z,y]
def soil_outline(part,row):
    top=max(v[1] for v in part['vertices_xyz'])
    poly=[local(v,row)[:2] for v in part['vertices_xyz'] if abs(v[1]-top)<1e-7]
    assert len(poly)==28
    poly.sort(key=lambda p:math.atan2(p[1],p[0]))
    return poly,top-row['position_xyz'][1]
def halfplanes(poly):
    # Convex polygon CCW; n.p <= d. Entire triangle interior is contained when
    # every vertex satisfies all half-planes. Distances are in metres.
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        nx,ny=dy/length,-dx/length
        out.append((nx,ny,nx*a[0]+ny*a[1]))
    return out

def fit_reach(base,angle,length,width,poly,inset=.015,kind='broad'):
    theta=math.radians(angle);direction=[math.cos(theta),math.sin(theta)]
    side=[-direction[1],direction[0]];lo=.19;hi=length
    for t in [0,.12,.29,.49,.69,.87,1]:
        profile=math.sin(math.pi*t)**(.78 if kind=='broad' else .95)*(1.15-.38*t)
        for u in [-1,-.55,0,.55,1]:
            px=base[0]+side[0]*u*width*.5*profile
            py=base[1]+side[1]*u*width*.5*profile
            for nx,ny,d in halfplanes(poly):
                coefficient=(nx*direction[0]+ny*direction[1])*t
                remaining=d-inset-nx*px-ny*py
                if coefficient>1e-12: hi=min(hi,remaining/coefficient)
                elif coefficient< -1e-12: lo=max(lo,remaining/coefficient)
                elif remaining < -1e-9: return None
    return hi if hi>=lo else None

# Five interlocking crowns, deliberately different in plan and height. The tall
# rear/off-centre heart is surrounded by two side shoulders and two forward
# folds. Values are authored dimensions, not whole-asset scale factors.
# x=long bowl axis; positive y=wall side; negative y=pool-facing side.
VARIANTS = [
    dict(label='Fore 0 / jade heart, sage left shoulder', phase=-7,
         groups=[[-.59,.105,.99],[.025,.115,1.215],[.57,.015,.86],[-.29,-.205,.63],[.35,-.215,.72]], accents=[0,3]),
    dict(label='Fore 1 / sage heart, olive low fold', phase=9,
         groups=[[-.62,.055,.88],[-.075,.130,1.235],[.53,.105,1.03],[-.37,-.185,.69],[.29,-.235,.59]], accents=[1,4]),
    dict(label='Middle 0 / jade heart, broad sage shoulder', phase=17,
         groups=[[-.55,.100,1.03],[.120,.090,1.185],[.63,-.015,.81],[-.34,-.195,.66],[.33,-.230,.73]], accents=[0,4]),
    dict(label='Middle 1 / sage heart, unequal jade shoulders', phase=-13,
         groups=[[-.61,.005,.85],[-.095,.155,1.255],[.53,.110,.97],[-.29,-.235,.74],[.40,-.170,.61]], accents=[2,3]),
    dict(label='Aft 0 / olive rear, sage forward fold', phase=4,
         groups=[[-.56,.125,.94],[.080,.105,1.205],[.60,-.005,1.04],[-.35,-.180,.62],[.32,-.240,.70]], accents=[0,4]),
    dict(label='Aft 1 / jade rear, sage high shoulder', phase=-19,
         groups=[[-.58,.090,1.01],[-.060,.125,1.225],[.58,.045,.88],[-.36,-.205,.72],[.33,-.210,.63]], accents=[2,3]),
]
LEVELS = [.17,.26,.35,.43,.51,.60,.69,.77,.84,.91,.965,1.0]
ANGLES = [168,-34,73,-123,21,134,-70,179,43,-154,-18,104]

def along(points,t):
    # Parameterise by stem vertical progression, not a disconnected guess.
    z=points[0][2]+t*(points[-1][2]-points[0][2])
    for a,b in zip(points,points[1:]):
        if a[2]-1e-9<=z<=b[2]+1e-9:
            return add(a,mul(sub(b,a),(z-a[2])/(b[2]-a[2])))
    raise AssertionError(t)

def flower_head(g,prefix,parent,attach,target,rotation):
    # Retained BOT-003 closed stem/receptacle + shaped five-petal construction,
    # recomposed as modest 0.12–0.15 m blush heads, not pink leaf recolouring.
    stem=prefix+'_stem';middle=add(attach,mul(sub(target,attach),.56))
    g.tube(stem,[attach,middle,target],[.007,.005,.0038],'botanical_leaf_olive',7)
    g.joint(stem,parent,attach)
    rec=prefix+'_receptacle'
    g.tube(rec,[add(target,[0,0,-.009]),target,add(target,[0,0,.017])],[.004,.016,.009],'botanical_leaf_olive',8,True)
    g.joint(rec,stem,target)
    for k in range(5):
        g.blade(prefix+'_petal_%d'%k,add(target,[0,0,.006]),rotation+k*72,
                .075,.070,.031,.021,.011,'botanical_flower',
                .004 if k%2 else -.004,'petal',rec)
    centre=prefix+'_centre'
    g.tube(centre,[add(target,[0,0,.007]),add(target,[0,0,.024])],[.011,.006],'botanical_flower',7,True)
    g.joint(centre,rec,add(target,[0,0,.007]))


def make_asset(i,row,soil):
    poly,soil_height=soil_outline(soil,row);v=VARIANTS[i]
    name='AST-BOT-002_pool_loggia_mass_%02d'%i
    g=Geometry(name,'AST-BOT-002',row['position_xyz'],row['support'],'loggia_middle_mass',i)
    g.a.update(yaw_radians=row['yaw_radians'],scale_xyz=[1,1,1],
               replaces_instance=row['name'],replaces_model_file=row['model_file'],
               source_formula_lineage=['AST-BOT-002 cupped broad-ovate blade and closed stem/petiole','AST-BOT-003 five-petal flower construction only'],
               soil_polygon_local_xy=poly,soil_surface_local_z=soil_height,
               design_intent=v,geometry_fit='Actual convex 28-gon soil inset 15 mm, every emitted foliage vertex; no mesh scaling',
               material_role_assignment='Spatial groups and upward/front blade faces, never random per-face colour',
               candidate_only=True)
    chosen=[]
    for j,(x,y,height) in enumerate(v['groups']):
        root='mass_%d_root'%j
        # Tiny Z offset matches actual reopened soil surface, leaving instance
        # transforms exactly unchanged even at Blender float precision.
        g.root(root,x,y,.052 if j==1 else .043)
        for m in g.a['parts'][-1:]:
            for p in m['vertices']:p[2]+=soil_height
            for p in m['shape_controls']['centerline']:p[2]+=soil_height
        g.a['markers'][-1]['point_local'][2]+=soil_height
        stem='mass_%d_curved_stem'%j
        bend=(-1 if (i+j)%2 else 1)
        pts=[[x,y,.035+soil_height],[x+.025*bend,y-.010,height*.31],
             [x-.030*bend,y+.020,height*.64],[x+.034*bend,y-.015,height]]
        g.tube(stem,pts,[.032,.029,.023,.012]);g.joint(stem,root,pts[0])
        # Each shoulder is a broad 3D lobe. Lower outer leaves overlap the
        # retained basal layer, and progressively folded leaves close its heart.
        for k,t in enumerate(LEVELS):
            attach=along(pts,t)
            angle=ANGLES[k]+v['phase']+[0,19,-17,31,-29][j]
            width=(.46 if j==1 else .425)+[0,.028,-.012,.018][(k+j)%4]
            wanted=(.63 if j==1 else .565)+[.025,-.015,.005][k%3]
            if j>=3: wanted-=.045; width-=.020
            # Retain a full rounded blade. If the first aim is infeasible at the
            # soil edge, choose the nearest authored inward aim; never squash it.
            options=[]
            for change in [0,12,-12,26,-26,45,-45,70,-70,100,-100,150,180]:
                a=angle+change;r=math.radians(a)
                base=add(attach,[.042*math.cos(r),.042*math.sin(r),.025])
                length=fit_reach(base,a,wanted,width,poly)
                if length is not None:
                    options.append((abs(change)+max(0,.35-length)*450,a,length,base))
            assert options,(i,j,k,'No broad leaf fits actual polygon')
            _,angle,length,base=min(options,key=lambda q:q[0])
            pet='mass_%d_petiole_%02d'%(j,k)
            g.tube(pet,[attach,add(attach,mul(sub(base,attach),.52)),base],[.011,.008,.006],'botanical_leaf_olive',7)
            g.joint(pet,stem,attach)
            # A stable colour patch per crown, highlights on the pool-facing
            # shoulder. Existing packed textures and material graphs unchanged.
            if j in [0,3]: role='sage' if k%4!=1 else 'jade'
            elif j==1: role=('sage' if i%2 else 'jade') if k%3 else 'olive'
            elif j==2: role='jade' if k%3 else 'sage'
            else: role='olive' if k%3 else 'sage'
            rise=[.095,.145,.200,.120][(k+j)%4]
            arch=[.155,.177,.143][(k+i)%3]
            cup=.060+.007*((k+j)%3);twist=(-1 if (k+j)%2 else 1)*(.018+.004*(i%3))
            leaf='mass_%d_rounded_leaf_%02d'%(j,k)
            g.blade(leaf,base,angle,length,width,rise,arch,cup,'botanical_leaf_'+role,twist,'broad',pet)
            chosen.append(dict(part=leaf,authored_reach_m=wanted,fitted_reach_m=length,width_m=width,angle_degrees=angle,role=role))
        if j in v['accents']:
            attach=along(pts,.70)
            # Small asymmetric 3-head spray beside each selected shoulder.
            for k,(dx,dy,dz) in enumerate([[-.085,-.035,.245],[.032,-.085,.315],[.104,.026,.275]]):
                target=add(attach,[dx,dy,dz])
                flower_head(g,'mass_%d_flower_%d'%(j,k),stem,attach,target,i*11+j*29+k*43)
    a=g.finish()
    a['bounds_world']=bounds([world(p,row) for m in a['parts'] for p in m['vertices']])
    a['authored_leaf_fit']=chosen
    a['maximum_height_above_soil_m']=a['bounds_local'][1][2]-soil_height
    return a

def build_plan():
    pins=json.loads((HERE/'INPUT_PINS.json').read_text())['inputs']
    for path,digest in pins.items(): assert sha(path)==digest, 'Retained input changed: '+path
    data=json.loads(PLAN.read_text());parts={p['name']:p for p in data['parts']}
    middle=[p for p in data['plants'] if p['parent_design_id']=='AST-BOT-002']
    basal=[p for p in data['plants'] if p['parent_design_id']=='AST-BOT-003']
    assert len(middle)==len(basal)==6
    assert all(p['scale_xyz']==[1,1,1] for p in data['plants'])
    assets=[make_asset(i,row,parts[row['support']]) for i,row in enumerate(middle)]
    return dict(schema='astraea_loggia_plant_mass_scratch_v1',
                status='PURE_GEOMETRY_PROPOSAL_NOT_BUILT_OR_VISUALLY_ACCEPTED',
                coordinate_mapping='Blender local (x,y,z) -> glTF (x,z,-y), then unchanged +pi/2 Y-yaw and position',
                replacement_scope='Only six LOG_*_Pocket_*_middle models later. Six basal models/transforms remain byte-identical. All twelve loggia plant instances retain positions, yaw and unit scales.',
                role_source_libraries={r:str(CAT/'assets/botanical_understory/source'/'AST-BOT-002.blend') for r in ['botanical_bark','botanical_leaf_jade','botanical_leaf_sage','botanical_leaf_olive','botanical_flower']},
                role_fallback_libraries={'botanical_flower':str(CAT/'assets/botanical_understory/source/AST-BOT-003.blend')},
                material_lookup_policy='Look for each exact role in preferred BOT-002. Only botanical_flower may fall back to the exact BOT-003 role if absent; record availability and actual per-role source. Never synthesize a missing role.',
                retained_basal_instances=basal,prior_middle_instances=middle,
                instance_budget=dict(basal_retained=6,middle_replaced=6,total_loggia_plants=12,additional_instances=0),
                assets=assets,
                not_claimed=['Source build/reopen','Source material availability or graph comparison in Blender','Visual fullness, colour readability or quality acceptance','Export, runtime adoption, native collision/lighting acceptance'],
                source_plan_sha256=sha(PLAN))

def main():
    out=HERE/'plant_mass_contract.json'
    assert not out.exists(),'Preserve an existing plan; author revisions in new files'
    plan=build_plan();out.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'status':plan['status'],'assets':[{'name':a['name'],'bounds':a['bounds_local'],'height':a['maximum_height_above_soil_m'],'parts':a['part_count'],'triangles':a['planned_triangle_count']} for a in plan['assets']]},indent=2))
if __name__=='__main__':main()
