"""Additive source-rooted terminal/body weather joints; capacity stays held."""
from pathlib import Path
import hashlib,json,gzip
import numpy as np
from shapely.geometry import Polygon,box

P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
base=json.loads((C/'docs/PLAN.json').read_text())
survey=json.loads((P/'qa/ACTUAL_RECEIVERS.json').read_text())
for path in ['Game/data/hull_envelope.json','BlenderCatalogue/materials/champagne_metal.png','BlenderCatalogue/materials/ivory_enamel.png','Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',str((C/'docs/PLAN.json').relative_to(R))]:survey['source_pins'][path]=hashlib.sha256((R/path).read_bytes()).hexdigest()
for name,want in survey['source_pins'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==want
parts=[]
def loft(name,poly0,poly1,y0,y1,cell,role='metal',function='architectural_seal'):
    assert len(poly0)==len(poly1) and y1>y0
    assert Polygon(poly0).is_valid and Polygon(poly0).area>1e-5
    assert Polygon(poly1).is_valid and Polygon(poly1).area>1e-5
    n=len(poly0);v=[[x,y,z]for y,poly in [(y0,poly0),(y1,poly1)]for x,z in poly]
    faces=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
    parts.append({'name':name,'cell':cell,'role':role,'category':'solid_frame'if role=='metal'else'solid_roof','function':function,'vertices_world_xyz':v,'faces':faces,'section_polygons_xz':[poly0,poly1],'y_interval':[y0,y1]})
def boxpoly(x0,x1,z0,z1):return [[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
ys=[61,69.5,78,84,88.5,93,97.5,102,106.5]
outline=json.loads((R/'Game/data/hull_envelope.json').read_text())['plan_xz_m']
def hull_half(z):
    hits=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        if abs(a[1]-b[1])<1e-8:
            if abs(z-a[1])<1e-6:hits.extend([abs(a[0]),abs(b[0])])
        elif min(a[1],b[1])<=z<=max(a[1],b[1]):hits.append(abs(a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1])))
    return max(hits)
for term,sign in [('Fore',-1),('Aft',1)]:
    end=sign*510;cell='G7C4_'+term+'_BodySeals';neck='G7C4_'+term+'_NeckLanding'
    def panel(side,y):
        bands=[q for q in base['panels']if q['side']==side and q['z'][0]<=end<=q['z'][1] and q['y'][0]<=y+1e-6 and q['y'][1]>=y-1e-6]
        assert bands;return bands[0]
    def body(side,y,z):
        y=min(106.5,max(61,y));q=panel(side,y);u=(z-q['z'][0])/(q['z'][1]-q['z'][0]);v=(y-q['y'][0])/(q['y'][1]-q['y'][0]);a=np.array(q['quad'])
        return float((a[0]*(1-u)*(1-v)+a[1]*u*(1-v)+a[2]*u*v+a[3]*(1-u)*v)[0])
    def width(y):return abs(body(1,y,end))
    for side in [-1,1]:
        def corner(y,lower=False):
            xb=body(side,y,end-sign*.75);xe=body(side,y,end)
            if lower:
                xt=side*hull_half(end+sign*.75)*(1-.015*(y-61)/8.5)
                return [[xb,end-sign*.75],[xe,end],[xt,end+sign*.75],[xt-side*.65,end+sign*.75],[xe-side*.65,end],[xb-side*.65,end-sign*.75]]
            return [[xb,end-sign*.75],[xe,end],[xe-side*.65,end],[xb-side*.65,end-sign*.75]]
        loft(f'G7C4_{term}_CornerSeal_{side}_Lower',corner(61,True),corner(69.5,True),61,69.5,cell)
        for i,(ya,yb)in enumerate(zip(ys[1:],ys[2:])):
            loft(f'G7C4_{term}_CornerSeal_{side}_Upper_{i}',corner(ya),corner(yb),ya,yb,cell)
        loft(f'G7C4_{term}_CornerSeal_{side}_HeadLap',corner(106.5),corner(106.5),106.5,106.72,cell)
        def rail(y):
            xs=sorted([side*6.8,side*width(y)]);zs=sorted([end,end-sign*.6]);return boxpoly(*xs,*zs)
        for label,a,b in [('FootLower',69.42,69.5),('FootUpper',69.5,69.70),('HeadLower',106.28,106.5),('HeadUpper',106.5,106.72)]:
            loft(f'G7C4_{term}_Headwall{label}_{side}',rail(a),rail(b),a,b,cell,function='wall_roof_receiving_lap')
        xs=sorted([side*6.4,side*7.03]);zs=sorted([end-sign*.7,end+sign*.25]);poly=boxpoly(*xs,*zs)
        loft(f'G7C4_{term}_NeckLandingFoot_{side}',poly,poly,106.28,106.5,neck,function='neck_headwall_receiving_foot')
        loft(f'G7C4_{term}_NeckLandingJamb_{side}',poly,poly,106.5,110.3,neck,function='neck_landing_jamb')
    zs=sorted([end-sign*.7,end+sign*.25])
    poly=boxpoly(-7.03,7.03,*zs)
    loft(f'G7C4_{term}_NeckLandingHeader',poly,poly,110.3,110.5,neck,function='neck_landing_header')
    poly=boxpoly(-6.8,6.8,*zs)
    loft(f'G7C4_{term}_NeckRoofLap',poly,poly,110.5,110.78,neck,role='shell',function='neck_roof_landing_lap')
# Immutable architectural bounds are a conservative first gate. Exact compiled
# floors are receiving witnesses, not occupied room AABBs or new floor requests.
census=json.loads(gzip.decompress((C/'qa/RETAINED_RUNTIME_CENSUS.json.gz').read_bytes()))['meshes']
census=[q for q in census if 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE'not in q['path'] and 'CompiledStructuralFloors_NotFinishedRooms'not in q['path']]
lo=np.array([q['minimum']for q in census]);hi=np.array([q['maximum']for q in census]);hits=[]
for part in parts:
    a=np.array(part['vertices_world_xyz']);mn=a.min(axis=0);mx=a.max(axis=0);mask=np.all(np.minimum(mx,hi)-np.maximum(mn,lo)>1e-5,axis=1)
    if mask.any():hits.append({'part':part['name'],'conservative_candidates':[census[int(i)]['path']for i in np.where(mask)[0]]})
plan={'schema':'astraea.group7.finite-terminal-seams.v1','baseline':'affc5c807087ff87da29f3642c2d6e418241b896','retained_checkpoint':'9a32693e9ce5b5e7d86a12fb85d558dafba9cfb8','source_pins':survey['source_pins'],'parts':parts,'cells':sorted({q['cell']for q in parts}),'scope':'Continuous additive lower/upper corner weather spines, headwall foot/head roof laps, and raised neck receiving jamb/header/cap laps at Z±510. No blanket roof or private roof changes.','protected_route_x':[-4,4],'protected_original_neck_aperture_x':[-6,6],'neck_jamb_inner_abs_x':6.4,'lowest_new_central_overhead_y':110.3,'minimum_d18_central_headroom_m':3.8,'conservative_original_architecture_hits':hits,'pressure_seal_capacity_load_or_whole_group_accepted':False,'support_policy':'Geometric source contacts and receiving chain only. Architectural sealing members are not proven primary structure; receiver strength, joints, reactions and engineering capacity remain held.','interior_roof_and_main_route_join':'HELD beyond the 0.7m bodyward neck landing lap','integration_owner':'01a11d7f-8ef6-70bc-858d-bdf8deb7000b','shared_root_or_registry_edits':False,'capacity_delta':0,'new_room_ids':0}
(P/'docs/SEAM_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
assert not hits, 'Conservative original architecture hits must be resolved before source construction'
print('G7_R004_PLAN',len(parts),'parts',len(plan['cells']),'cells','original architectural hits',len(hits))
