"""Bounded east bay and lift source geometry. Pure Python; no Blender, Game or Catalogue writes."""
import math,json,hashlib,struct
from pathlib import Path
S=Path(__file__).resolve().parent; P=S.parent; C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
FLOOR=52.5;parts=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scalar(x):return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def add(name,group,role,vertices,faces,support,**extra):
    # The plan and Blender use the same single-precision metre coordinates.
    v=[[scalar(x) for x in row] for row in vertices]
    p=dict(name=name,group=group,material_role=role,vertices_xyz=v,faces=faces,support=support if isinstance(support,list) else [support],parent_design_id='AST-AQU-016',collision='concave_static_surface',**extra)
    parts.append(p);return name
FACES=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,group,role,lo,hi,support,**kw):
    x,y,z=lo;X,Y,Z=hi
    return add(name,group,role,[[x,y,z],[X,y,z],[X,y,Z],[x,y,Z],[x,Y,z],[X,Y,z],[X,Y,Z],[x,Y,Z]],FACES,support,**kw)
def extrude_plan(name,group,role,poly,y0,y1,support,**kw):
    n=len(poly);vs=[[x,y,z] for y in [y0,y1] for x,z in poly]
    fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    return add(name,group,role,vs,fs,support,**kw)
def loft_closed(name,group,role,rings,support,**kw):
    n=len(rings[0]);assert all(len(r)==n for r in rings)
    vs=[v for ring in rings for v in ring];fs=[list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))]
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i
            # Explicit triangles also handle finite, twisted ruled faces.
            fs.extend([[a,b,c],[a,c,d]])
    return add(name,group,role,vs,fs,support,**kw)
def ellipse(name,group,role,cx,cz,rx,rz,y0,y1,support,segments=32,**kw):
    return extrude_plan(name,group,role,[[cx+rx*math.cos(2*math.pi*i/segments),cz+rz*math.sin(2*math.pi*i/segments)] for i in range(segments)],y0,y1,support,**kw)
# A convex, uninterrupted west relief. No entrance-shaped niche, frame or recess.
zgrid=[-414.32+i*3.84/12 for i in range(13)]
def relief_ring(y,projection):
    front=[[-17.52-projection*(.62+.38*math.sin(math.pi*i/12)),y,z] for i,z in enumerate(zgrid)]
    return [[-17.52,y,zgrid[0]]]+front+[[-17.52,y,zgrid[-1]]]
lo='lift_west_shallow_landmark';up='lift_west_upper_profile';aft='lift_aft_mounted_return';bay='upper_east_gallery_rest_bay'
loft_closed('EAST_Lift_StoneFoot','lift','warm_stone',[relief_ring(46.2,.31),relief_ring(46.62,.34)],'GP_LocalLiftRear',reservation=lo,semantic='fixed shaft foot; not guest surface')
loft_closed('EAST_Lift_ConvexIvoryBody','lift','ivory_enamel',[relief_ring(46.62,.34),relief_ring(50.50,.34)],'GP_LocalLiftRear',reservation=lo,semantic='continuous opaque vertical arrival landmark')
loft_closed('EAST_Lift_TaperedShoulder','lift','warm_stone',[relief_ring(50.50,.34),relief_ring(51.0,.16)],'GP_LocalLiftRear',reservation=lo,semantic='level transition; no shelf or floor')
loft_closed('EAST_Lift_UpperContinuation','lift','ivory_enamel',[relief_ring(51.0,.16),relief_ring(55.6,.13)],'GP_LocalLiftRear',reservation=up,semantic='wall mounted above existing void; meets retained cap underside')
# A clay face follows the actual facet profile of the lower body, with a real 22 mm edge.
zs=zgrid[2:-2];front=lambda z:-17.52-.34*(.62+.38*math.sin(math.pi*(z+414.32)/3.84))
poly=[[front(z)-.022,z] for z in zs]+[[front(z),z] for z in reversed(zs)]
extrude_plan('EAST_Lift_TerracottaFace','lift','retail_terracotta_enamel',poly,47.05,50.12,'EAST_Lift_ConvexIvoryBody',reservation=lo,semantic='warm convex facing; buried opposed back bearing, exposed finite terminations')
box('EAST_Lift_AftMountingField','lift','warm_stone',[-17.3,46.2,-410.2],[-13.55,51.,-410.165],'GP_LocalLiftSide.001',reservation=aft,semantic='shallow true wall receiver for directional boards to actual east gate')
# End returns sweep from the open mouth toward the actual enclosure. These are
# full-height architectural bodies, not a rectangular shell with decorative trim.
fore=[[-10.85,-454.0],[-9.18,-454.0],[-8.65,-453.70],[-8.31,-453.31],[-8.2,-453.05],[-8.38,-453.05],[-8.51,-453.22],[-8.80,-453.48],[-9.31,-453.70],[-10.85,-453.70]]
aftpoly=[[x,-899.0-z]for x,z in reversed(fore)]
for label,poly in [('Fore',fore),('Aft',aftpoly)]:
    extrude_plan('EAST_Bay_'+label+'SweptReturn','bay','warm_stone',poly,FLOOR,55.95,'COMPILER_FLOOR_D09_orchard_market_gallery',reservation=bay,semantic='curved room-shaping return with open upper shadow joint',grain_axis_xyz=[0,1,0])
# Low-concavity back wall: centre recedes toward the retained enclosure, ends
# bring the foreground forward. The retained east wall is never cut.
zback=[-453.05+i*7.1/16 for i in range(17)]
backface=[[-8.38+.12*math.sin(math.pi*i/16),z] for i,z in enumerate(zback)]
backpoly=backface+[[-8.2,zback[-1]],[-8.2,zback[0]]]
extrude_plan('EAST_Bay_CurvedClayBack','bay','retail_terracotta_enamel',backpoly,FLOOR,56.40,['GP_EastWall.002','COMPILER_FLOOR_D09_orchard_market_gallery'],reservation=bay,semantic='inhabited recess back; existing enclosure intact')
# Broad two-level swept canopy, low at the open front and rising into a deep
# warm back. Every surface is closed. Only two semantic bodies shape this roof.
n=24;zs=[-454+i*9/n for i in range(n+1)]
def canopy(z):
    s=math.sin(math.pi*(z+454)/9)
    return dict(front_x=-10.85-.30*s,front_y=56.03+.52*s,mid_x=-9.50,mid_y=56.12+.95*s,back_x=-8.2,back_y=56.25+1.30*s)
def canopy_band(name,role,left,right,thick,support):
    vs=[]
    for z in zs:
        q=canopy(z);vs += [[q[left+'_x'],q[left+'_y'],z],[q[right+'_x'],q[right+'_y'],z],[q[right+'_x'],q[right+'_y']+thick,z],[q[left+'_x'],q[left+'_y']+thick,z]]
    fs=[[3,2,1,0],[4*n,4*n+1,4*n+2,4*n+3]]
    for j in range(n):
        for i in range(4):
            a=j*4+i;b=j*4+(i+1)%4;c=(j+1)*4+(i+1)%4;d=(j+1)*4+i
            fs += [[a,b,c],[a,c,d]]
    return add(name,'bay',role,vs,fs,support,reservation=bay,semantic='swept canopy '+left+' to '+right,grain_axis_xyz=[1,0,0])
canopy_band('EAST_Bay_WarmRearCanopy','warm_walnut','mid','back',.20,'GP_EastWall.002')
canopy_band('EAST_Bay_PaleFrontCanopy','ivory_enamel','front','mid',.28,'EAST_Bay_WarmRearCanopy')
# One integrated 2.9 m crescent bench, authored as four editable material bodies.
bzs=[-450.86+i*2.72/16 for i in range(17)]
def bench_back(z):return -8.76-.27*((z+449.5)/1.36)**2
bench_poly=lambda rear,front:[[bench_back(z)+rear,z]for z in bzs]+[[bench_back(z)-front,z]for z in reversed(bzs)]
base=extrude_plan('EAST_Bench_StonePlinth','bench','warm_stone',bench_poly(0,.64),FLOOR,52.84,'COMPILER_FLOOR_D09_orchard_market_gallery',reservation=bay,programme_entity='curved_bench',semantic='one continuous curved built-in bench')
seat=extrude_plan('EAST_Bench_WalnutSeat','bench','warm_walnut',bench_poly(0,.68),52.84,52.94,base,reservation=bay,programme_entity='curved_bench',grain_axis_xyz=[0,0,1])
extrude_plan('EAST_Bench_ClayUpholstery','bench','aquatic_clay_sling',bench_poly(-.02,.66),52.94,52.99,seat,reservation=bay,programme_entity='curved_bench')
extrude_plan('EAST_Bench_WalnutBack','bench','warm_walnut',bench_poly(.16,0),52.84,53.61,seat,reservation=bay,programme_entity='curved_bench',grain_axis_xyz=[0,0,1])
# Offset to aft; the central/fore 1.3 m approach and return remain open.
tx,tz=-10.40,-448.65
foot=ellipse('EAST_Table_WeightedFoot','table','champagne_metal',tx,tz,.25,.25,FLOOR,52.56,'COMPILER_FLOOR_D09_orchard_market_gallery',reservation=bay,programme_entity='table')
stem=ellipse('EAST_Table_Pedestal','table','champagne_metal',tx,tz,.06,.06,52.56,53.15,foot,segments=16,reservation=bay,programme_entity='table')
ellipse('EAST_Table_WalnutTop','table','warm_walnut',tx,tz,.37,.42,53.15,53.22,stem,reservation=bay,programme_entity='table',grain_axis_xyz=[0,0,1])
plants=[]
for label,cz,var in [('Fore',-452.20,'00'),('Aft',-446.80,'03')]:
    cx=-9.10;prefix='EAST_'+label+'SoilBed';N=32
    rings=[(.65,1.24,FLOOR),(.68,1.31,52.59),(.68,1.31,53.10),(.64,1.21,53.10),(.64,1.21,52.70)]
    vs=[[cx+rx*math.cos(2*math.pi*i/N),y,cz+rz*math.sin(2*math.pi*i/N)]for rx,rz,y in rings for i in range(N)]
    fs=[]
    for j in range(len(rings)-1):
        for i in range(N):fs.append([j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i])
    fs += [list(range(N-1,-1,-1)),list(range((len(rings)-1)*N,len(rings)*N))]
    bowl=add(prefix+'_Container','soilbed','warm_stone',vs,fs,'COMPILER_FLOOR_D09_orchard_market_gallery',reservation=bay,programme_entity=label.lower()+'_soilbed',semantic='closed profiled planter with open earth basin')
    # Soil matches the tapered basin bottom and contact sides exactly.
    y0,y1=52.70,53.02;rx,rz=.64,1.21
    srings=[[[cx+r0*math.cos(2*math.pi*i/N),y,cz+r1*math.sin(2*math.pi*i/N)]for i in range(N)]for r0,r1,y in [(rx,rz,y0),(rx,rz,y1)]]
    soil=loft_closed(prefix+'_Soil','soilbed','botanical_soil',srings,bowl,reservation=bay,programme_entity=label.lower()+'_soilbed',semantic='finite actual soil volume and unscaled botanical root receiver')
    plants.append(dict(name=label.lower(),variant=var,position_xyz=[cx,y1,cz],yaw_radians=math.pi/2,scale_xyz=[1,1,1],soil_object=soil,available_soil_xy_m=[2*rx,2*rz],maximum_crown_height_m=1.554))
# Exact piecewise planar underside query on the authored canopy triangles.
def canopy_under(x,z):
    j=min(n-1,max(0,int((z+454)/9*n)));t=(z-zs[j])/(zs[j+1]-zs[j]);q0=canopy(zs[j]);q1=canopy(zs[j+1]);q={k:q0[k]*(1-t)+q1[k]*t for k in q0}
    # Select actual authored triangle in the two ruled quads.
    l,r=('front','mid')if x<=q['mid_x']else('mid','back')
    a=(q0[l+'_x'],q0[l+'_y'],zs[j]);b=(q0[r+'_x'],q0[r+'_y'],zs[j]);c=(q1[r+'_x'],q1[r+'_y'],zs[j+1]);d=(q1[l+'_x'],q1[l+'_y'],zs[j+1])
    for aa,bb,cc in [(a,b,c),(a,c,d)]:
        den=(bb[2]-cc[2])*(aa[0]-cc[0])+(cc[0]-bb[0])*(aa[2]-cc[2]);u=((bb[2]-cc[2])*(x-cc[0])+(cc[0]-bb[0])*(z-cc[2]))/den;v=((cc[2]-aa[2])*(x-cc[0])+(aa[0]-cc[0])*(z-cc[2]))/den
        if min(u,v,1-u-v)>=-1e-9:return u*aa[1]+v*bb[1]+(1-u-v)*cc[1]
    raise ValueError((x,z))
# Two small physically closed cup housings, with genuine downward apertures.
fixtures=[]
for i,j in enumerate([9,15]):
    q=canopy(zs[j]);cx=(q['front_x']+2*q['mid_x'])/3;cz=(2*zs[j]+zs[j+1])/3
    N=20;y=canopy_under(cx,cz);rad=.085;inner=.061
    # Every ring point fits the real ruled underside. Ring depth follows that plane.
    rings=[]
    for r,dy in [(rad,0),(rad,-.10),(inner,-.10),(inner,-.028)]:
        rings.append([[cx+r*math.cos(2*math.pi*k/N),canopy_under(cx+r*math.cos(2*math.pi*k/N),cz+r*math.sin(2*math.pi*k/N))+dy,cz+r*math.sin(2*math.pi*k/N)]for k in range(N)])
    name=loft_closed('EAST_Bay_FixtureCup_%d'%i,'fixtures','champagne_metal',rings,'EAST_Bay_PaleFrontCanopy',reservation=bay,semantic='closed recessed cup with open downward aperture; no light settings claimed')
    lens_rings=[[[cx+inner*math.cos(2*math.pi*k/N),canopy_under(cx+inner*math.cos(2*math.pi*k/N),cz+inner*math.sin(2*math.pi*k/N))+dy,cz+inner*math.sin(2*math.pi*k/N)]for k in range(N)]for dy in [-.067,-.055]]
    lens=loft_closed('EAST_Bay_OpalLens_%d'%i,'fixtures','lens',lens_rings,name,reservation=bay,semantic='retained opal source role; actual side bearing inside the physical cup')
    parts[-1]['collision']='visual_lens_no_contact';parts[-1]['cast_shadow']=False
    fixtures.append(dict(name='EAST_Bay_LightReserve_%d'%i,housing=name,physical_lens=lens,position_xyz=[cx,y-.095,cz],direction_xyz=[0,-1,0],candidate_only=True,range_energy_aim='deferred until actual receiver selection',maximum_active_lights_unchanged=8))
# Side display reserve: not an extra display object. A mounting cleat waits for
# exact retained-housing geometry/transform from the integration owner.
display=dict(image_origin_xyz=[-10.38,54.20,-450.99],front_normal_xyz=[.62,0,.7846018098],width_m=1.70,height_m=1.0,depth_m=.20,parent_design_id='AST-LIB-010',mounting='canopy-hung side display above fore planting; final retained housing mount pending',required_clear_bottom_y=53.70)
# The receiver plane is exactly behind the retained housing's flat backplate.
normal=(.62,0,.7846018098);width_axis=(normal[2],0,-normal[0]);origin=display['image_origin_xyz'];back_n=-.1799938965
receiver=[]
for dep in [back_n-.035,back_n]:
    for u,v in [(-.87,-.52),(.87,-.52),(.87,.52),(-.87,.52)]:
        receiver.append([origin[j]+normal[j]*dep+width_axis[j]*u+([0,1,0][j])*v for j in range(3)])
plate=add('EAST_Display_AngledReceiver','bay','warm_walnut',receiver,FACES,['EAST_Display_Hanger_Fore','EAST_Display_Hanger_Aft'],reservation=bay,semantic='real flat back receiver for retained AST-LIB-010 housing',grain_axis_xyz=[0,1,0])
# Short horizontal tabs land on the receiver top; two thin hangers return into
# the actual canopy plane. No floor pole or extra media assembly is introduced.
for label,u in [('Fore',.60),('Aft',-.60)]:
    dep=back_n-.0175;cx=origin[0]+normal[0]*dep+width_axis[0]*u;cz=origin[2]+normal[2]*dep+width_axis[2]*u
    # The metre-canonical top is resolved on the real canopy's underside.
    poly=[[cx-.018,cz-.018],[cx+.018,cz-.018],[cx+.018,cz+.018],[cx-.018,cz+.018]]
    rings=[[[x,54.72,z]for x,z in poly],[[x,canopy_under(x,z),z]for x,z in poly]]
    loft_closed('EAST_Display_Hanger_'+label,'bay','champagne_metal',rings,'EAST_Bay_PaleFrontCanopy',reservation=bay,semantic='physical canopy-to-display hanger; no floor pole')
views=[]
for label,z in [('fore',-450.40),('centre',-449.50),('aft',-448.35)]:
    views.append(dict(name='seated_'+label,eye_xyz=[bench_back(z)-.33,53.74,z],forward_xyz=[-1,0,0],market_target_xyz=[-49.5,54.,-446.],media_target_xyz=display['image_origin_xyz'],water_view_claim=False))
approaches=[dict(name='central_bench_approach',points_xyz=[[-13.1,52.5,-449.8],[-11.4,52.5,-449.8],[-10.15,52.5,-449.8]],radius_m=.30,height_m=1.8),dict(name='bench_return_to_apron',points_xyz=[[-10.15,52.5,-449.8],[-11.4,52.5,-449.8],[-13.1,52.5,-449.8]],radius_m=.30,height_m=1.8),dict(name='cleaning_cart_stop',points_xyz=[[-13.1,52.5,-449.7],[-11.75,52.5,-449.7]],radius_m=.60,height_m=1.82,limitation='cart stops on clear apron; cleaning reach into bay is static only, no driving between seating and table claimed')]
# Explicit use reservations are checks, not a facility capacity claim.
standing_views=[dict(name='retained_long_pool',eye_xyz=[-20.5,47.849998474121094,-405.0],forward_xyz=[0,.02998681552708149,-.9995503425598145],vertical_fov_degrees=72,provenance='geometry/LONG_VIEW_IDENTITY_RAYS.json'),dict(name='upper_gallery_approach',eye_xyz=[-14.0,54.15,-455.8],target_xyz=[-9.65,54.65,-449.5],vertical_fov_degrees=72,floor_owner='D09_orchard_market_gallery',basis='Standing 1.65 m eye on the original floor-backed apron; no camera-only opened wall')]
use_envelopes=[]
for label,z in [('fore',-450.25),('centre',-449.50)]:
    edge=bench_back(z)-.68
    use_envelopes += [dict(name=label+'_knees',bounds_xyz=[[edge-.50,52.995,z-.30],[edge-.035,53.32,z+.30]],purpose='Free knee volume outside the bench front'),dict(name=label+'_feet',bounds_xyz=[[edge-.45,52.501,z-.24],[edge-.065,52.71,z+.24]],purpose='Free foot volume on retained floor')]
approaches.append(dict(name='cleaner_bench_stance',points_xyz=[[-11.75,52.5,-449.7],[-11.4,52.5,-449.8],[-10.03,52.5,-449.8]],radius_m=.30,height_m=1.80))
approaches.append(dict(name='cleaner_table_stance',points_xyz=[[-11.75,52.5,-449.7],[-11.30,52.5,-449.7],[-11.12,52.5,-448.65]],radius_m=.30,height_m=1.80))
cleaning_reaches=[dict(name='bench_front_pad',eye_xyz=[-10.03,53.50,-449.8],target_xyz=[bench_back(-449.8)-.64,52.99,-449.8],target_part='EAST_Bench_ClayUpholstery',maximum_segment_m=.85),dict(name='table_front_top',eye_xyz=[-11.12,53.50,-448.65],target_xyz=[-10.74,53.22,-448.65],target_part='EAST_Table_WalnutTop',maximum_segment_m=.85)]
for reach in cleaning_reaches:reach['target_xyz']=[scalar(v)for v in reach['target_xyz']]
input_paths=[P/'DESIGN_BRIEF.md',P/'DESIGN_INPUT_PINS.json']+[P/'geometry'/f for f in ['ADDITIVE_RESERVATIONS.json','PROTECTED_RESERVATIONS.json','SEATED_SIGHTLINES.json','FLOOR_POLYGONS.json','RETAINED_PART_BOUNDS.json','RETAINED_FINISH_BOUNDS.json','PRESERVED_VIEWS.json','RETAINED_SUPPORT_PATHS.json']]+[C/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend',C/'assets/grand_pool_orchard_section/source/connected_contract.json',C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb',C/'assets/aquatic_lounge/source/AST-AQU-001.blend',C/'standards/aquatic_materials.py',C/'standards/materials.py',C/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py',C/'assets/grand_pool_first_pass/finish_envelope/qa/pure_geometry/review_finish.py',S.parents[1]/'pool-architectural-composition/build_blockin003.py']
for path,expected in json.loads((P/'DESIGN_INPUT_PINS.json').read_text())['files'].items():assert sha(path)==expected,(path,'design pin changed')
plan=dict(schema=1,status='PURE_CORE_PLAN_PENDING_RETAINED_PROGRAMME_INTEGRATION',coordinate_frame='Godot world XYZ metres',blender_frame_map='Godot (x,y,z) -> Blender (x,-z,y), Z up metres; inverse Blender (x,y,z) -> Godot (x,z,-y)',parts=parts,plant_reservations=plants,display_reservation=display,fixture_reservations=fixtures,seated_views=views,standing_views=standing_views,use_envelopes=use_envelopes,cleaning_reaches=cleaning_reaches,approach_paths=approaches,budget=dict(architectural_semantic_bodies=14,curved_bench_entities=1,table_entities=1,soilbed_entities=2,retained_botanical_instances=4,retained_housed_displays=1,mounted_signs=2,programme_max=11,fixture_reservations_max=2,active_light_cap_unchanged=8,candidate_cap_unchanged=32,new_unique_design_ids=0),input_sha256={str(p):sha(p)for p in input_paths},pending=['Retained plant/display/sign geometry integration and exact contact/ray review','Actual editable source build and independent reopen','Early composed source views before further detailing','No export, Game, Catalogue, floor, glazing, door, shaft, controller or renderer change'])
(S/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(len(parts),'editable closed core objects;',len(fixtures),'physical fixture reservations; no engine launched')
