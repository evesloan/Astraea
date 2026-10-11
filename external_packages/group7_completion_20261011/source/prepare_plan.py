"""Plan source-owned shell fields against the actual initialized retained ship."""
from pathlib import Path
import gzip
import json, math, hashlib
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles

P=Path(__file__).resolve().parents[1];R=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
census_file=P/'qa/RETAINED_RUNTIME_CENSUS.json'
census=json.loads(census_file.read_bytes() if census_file.exists() else gzip.decompress(census_file.with_suffix('.json.gz').read_bytes()))['meshes']
all_census=census
census=[q for q in census if 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE'not in q['path'] and 'CompiledStructuralFloors_NotFinishedRooms'not in q['path']]
lo=np.array([q['minimum'] for q in census]);hi=np.array([q['maximum'] for q in census])
floors=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:
    floors+=json.load(open(R/'Game/data/generated'/f))['regions']
floor_polys=[(f,unary_union([Polygon(t)for t in f['triangles']]))for f in floors]
outline=Polygon(json.load(open(R/'Game/data/hull_envelope.json'))['plan_xz_m'])
def half(z):
    xs=[];v=list(outline.exterior.coords)
    for a,b in zip(v,v[1:]):
        if abs(a[1]-b[1])<1e-8:
            if abs(z-a[1])<1e-7:xs.extend([abs(a[0]),abs(b[0])])
        elif min(a[1],b[1])<=z<=max(a[1],b[1]):xs.append(abs(a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1])))
    return max(xs)
ys=[61,69.5,78,84,88.5,93,97.5,102,106.5]
zs=sorted(set([-510,510,-430,-300,250,420,-275,-265,-115,-105,-468,468]+list(range(-504,505,6))))
taper={61:1,69.5:.985,78:.96,84:.94,88.5:.925,93:.91,97.5:.895,102:.88,106.5:.865}
widths={};holds=[]
non_shoulder=np.array(['TheaterWestUpperHull' not in q['path'] for q in census])
for side in [-1,1]:
    for iy,y in enumerate(ys):
        # A whole adjacent height band is screened, rather than a single datum.
        ya=ys[max(0,iy-1)];yb=ys[min(len(ys)-1,iy+1)]
        for iz,z in enumerate(zs):
            za=zs[max(0,iz-1)];zb=zs[min(len(zs)-1,iz+1)]
            mask=(hi[:,1]>=ya-1e-4)&(lo[:,1]<=yb+1e-4)&(hi[:,2]>=za)&(lo[:,2]<=zb)
            # The retained shoulder owns its actual west facade, which is never overlaid.
            mask &= non_shoulder
            need=float(max(0,np.max(hi[mask,0] if side==1 else -lo[mask,0]))) if mask.any() else 0
            strip=box(-120,za,120,zb)
            for f,poly in floor_polys:
                if ya-.3<=f['floor_y']<=yb+.3:
                    cut=poly.intersection(strip)
                    if not cut.is_empty:need=max(need,cut.bounds[2]if side==1 else -cut.bounds[0])
            target=max(half(z)*taper[y],need+.8)
            if abs(z)>=468:
                sign=1 if z>0 else -1;endpoint=49 if sign==1 else 65
                end=half(sign*510)*.985+(endpoint-half(sign*510)*.985)*(max(69.5,y)-69.5)/37
                if y<69.5:end=half(sign*510)*(1-.015*(y-61)/8.5)
                mix=(abs(z)-468)/42;target=max(target*(1-mix)+end*mix,need+.8)
            limit=half(z)
            if target>limit+.001:
                holds.append({'side':side,'z':z,'y':y,'required_outer_x':target,'maximum_hull_halfbeam':limit,'reason':'Retained conservative occupied bounds exceed shell reservation; local fields require exact owner reconciliation.'})
            widths[f'{side}:{iy}:{iz}']=min(target,limit)
panels=[];rejected=[]
for side in [-1,1]:
    for iy,(ya,yb) in enumerate(zip(ys,ys[1:])):
        for iz,(za,zb) in enumerate(zip(zs,zs[1:])):
            if side==-1 and za>=-275 and zb<=-105 and ya<92:
                # Do not duplicate the retained 170 m west shoulder. Its upper seam is separately held.
                rejected.append({'side':side,'z':[za,zb],'y':[ya,yb],'owner':'AST-HUL-002','reason':'Retained theater shoulder owns this facade.'});continue
            q=[[side*widths[f'{side}:{j}:{i}'],y,z] for j,i,y,z in [(iy,iz,ya,za),(iy,iz+1,ya,zb),(iy+1,iz+1,yb,zb),(iy+1,iz,yb,za)]]
            panels.append({'id':f'G7C3_Body_{side}_{iy:02}_{iz:03}','quad':q,'side':side,'z':[za,zb],'y':[ya,yb]})
terms=[]
for sign in [-1,1]:
    terms.append({'id':'G7C3_Fore'if sign==-1 else'G7C3_Aft','sign':sign,'neck_x':6.8,'z_inner':510,'z_end':531.5,'wall_base_y':106.5,'roof_underside_y':110.5,'roof_top_y':110.78,'route_floor_y':106.5,'clear_height_m':4.0,'protected_route_x':[-4,4],'body_seam_z':sign*510})
# Complementary top closure only where no source owns roof/occupied crown air.
top=Polygon([(side*widths[f'{side}:8:{i}'],z) for side,rr in [(1,range(len(zs))),(-1,range(len(zs)-1,-1,-1))]for i in rr for z in [zs[i]]])
roof_masks=[]
for i,q in enumerate(census):
    if hi[i,1]>=105.9 and lo[i,1]<=111:
        roof_masks.append(box(lo[i,0]-.5,lo[i,2]-.5,hi[i,0]+.5,hi[i,2]+.5))
for f in floors:
    if f['floor_y']==106.5:
        roof_masks.extend(Polygon(t).buffer(.5,join_style='mitre')for t in f['triangles'])
roof_masks.append(box(-52,-181,52,202)) # The source-owned crown and transfer zone.
# A global flat cap would violate the retained stepped-roof contract. Construct
# only the fitted perimeter head closure; internal owner seams remain explicit.
roof=top.difference(top.buffer(-2,join_style='mitre')).difference(unary_union(roof_masks))
roof_parts=[roof]if roof.geom_type=='Polygon'else list(roof.geoms)
roof_polygons=[{'exterior':list(q.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in q.interiors]}for q in roof_parts if q.area>.01]
roof_triangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(roof).geoms]
# Botanical pockets on real existing terraces, chosen outside the protected starboard tram strip.
pockets=[];pocket_holds=[]
for deck,y,purpose in [('D06',27,'Canopy study and scented grove'),('D09',52.5,'Craft and tactile garden pause'),('D12',78,'Quiet sky-reading fern court'),('D16',97.5,'Family garden refuge')]:
    union=unary_union([Polygon(t)for f in floors if abs(f['floor_y']-y)<1e-5 for t in f['triangles']])
    for n,(x,z) in enumerate([(-44,-22),(-44,22),(44,22)]):
        footprint=box(x-1.4,z-2.7,x+1.4,z+2.7)
        candidates=[]
        mask=(hi[:,1]>y+.03)&(lo[:,1]<y+2.8)&(hi[:,0]>x-1.4)&(lo[:,0]<x+1.4)&(hi[:,2]>z-2.7)&(lo[:,2]<z+2.7)
        for i in np.where(mask)[0]:candidates.append(census[int(i)]['path'])
        if footprint.difference(union).area>1e-6 or candidates:
            pocket_holds.append({'deck':deck,'origin':[x,y,z],'missing_floor_m2':footprint.difference(union).area,'conservative_occupied_candidates':candidates});continue
        pockets.append({'id':f'G7C3_{deck}_Court_{n}','deck':deck,'origin':[x,y,z],'purpose':purpose,'footprint':list(footprint.exterior.coords)[:-1],'floor_owner':'Existing exact compiled terrace triangles','no_new_floor':True})
plan={'schema':'astraea.group7.completion.v1','baseline':'affc5c807087ff87da29f3642c2d6e418241b896','prior_group7':'7f9f4777a4ae93884282155ea9d05b6ff125bd57','panels':panels,'width_holds':holds,'retained_facade_exclusions':rejected,'roof_polygons':roof_polygons,'roof_triangles':roof_triangles,'roof_area_m2':roof.area,'source_owned_roof_voids_preserved':True,'terminals':terms,'botanical_pockets':pockets,'botanical_pocket_holds':pocket_holds,'source_pins':{p:sha(R/p)for p in ['Game/scripts/ship.gd','Game/data/hull_envelope.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx','Game/scripts/service_door.gd','Game/assets/models/AST-STF-008.glb','Game/data/architecture/AFT_CROWN_SITTING_BAYS.json','Game/data/architecture/AFT_CROWN_SITTING_LIGHTING.json']},'normal_shell_depth_m':[0,.18],'frame_normal_depth_m':[.18,.4],'full_group_accepted':False,'capacity_delta':0,'new_room_ids':0,'integration_owner':'01a11d7f-8ef6-70bc-858d-bdf8deb7000b','limits':'Conservative retained mesh AABBs drive occupancy preservation. Source fields still need exact intermediate clearance, seams, supports, import, routes, reference/source pixels and owner adoption. No physics/engineering/final acceptance is inferred.'}
(P/'docs/PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({k:len(plan[k]) for k in ['panels','width_holds','retained_facade_exclusions','botanical_pockets','botanical_pocket_holds']}), 'roof_area_m2',round(roof.area,2))
(P/'qa/CENSUS_SCREEN_POLICY.json').write_text(json.dumps({'retained_meshes':len(all_census),'architectural_and_furnishing_meshes':len(census),'datum_guides_excluded_from_occupied_volume':[q['path']for q in all_census if 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE'in q['path']],'compiled_floor_mesh_aabbs_replaced_by_exact_region_triangles':True,'exact_floor_regions':len(floors),'original_guide_and_floor_source_unchanged':True},indent=2)+'\n')
