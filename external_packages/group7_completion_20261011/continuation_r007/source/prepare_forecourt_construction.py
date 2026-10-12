"""Large, distinct botanical courts on original floors; no new floor or room IDs."""
from pathlib import Path
import json, math, hashlib
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely import constrained_delaunay_triangles

P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
pre=json.loads((P/'docs/FORECOURT_RECEIVER_PREPLAN.json').read_text())
assert json.loads((P/'docs/GROUP4_FORECOURT_INTERFACE_CHECK.json').read_text())['status'].startswith('CLEAR_')
parts=[];plants=[];trees=[];lights=[];doors=[];terraces=[];contacts=[]
def solid(name,poly,low,high,role,category,cell):
    assert poly.is_valid and poly.geom_type=='Polygon' and poly.area>1e-6 and high>low,name
    xy=[];indices={}
    def point(q):
        key=(round(q[0],7),round(q[1],7))
        if key not in indices:indices[key]=len(xy);xy.append(list(key))
        return indices[key]
    loops=[[point(q) for q in list(r.coords)[:-1]]for r in [poly.exterior,*poly.interiors]]
    tris=[[point(q)for q in list(t.exterior.coords)[:3]]for t in constrained_delaunay_triangles(poly).geoms]
    assert abs(sum(Polygon([xy[k]for k in t]).area for t in tris)-poly.area)<1e-6
    n=len(xy);faces=[list(reversed(t))for t in tris]+[[k+n for k in t]for t in tris]
    for loop in loops:
        for a,b in zip(loop,loop[1:]+loop[:1]):faces.append([a,b,b+n,a+n])
    parts.append({'name':name,'vertices_world_xyz':[[x,y,z]for y in [low,high]for x,z in xy],
                  'faces':faces,'role':role,'category':category,'cell':cell,'volume_m3':poly.area*(high-low)})
def disk(x,z,r,n=24):return Polygon([(x+r*math.cos(i*math.tau/n),z+r*math.sin(i*math.tau/n))for i in range(n)])
def rect(name,x0,x1,z0,z1,y0,y1,role,category,cell):solid(name,box(x0,z0,x1,z1),y0,y1,role,category,cell)
def vaulted(name,x0,x1,z0,z1,y,height_min,height_max,thickness,role,cell):
    nx,nz=6,10;lower=[]
    for ix in range(nx+1):
        for iz in range(nz+1):
            t=iz/nz;lower.append([x0+(x1-x0)*ix/nx,y+height_min+(height_max-height_min)*math.sin(math.pi*t),z0+(z1-z0)*t])
    n=len(lower);verts=lower+[[x,h+thickness,z]for x,h,z in lower];faces=[]
    for ix in range(nx):
        for iz in range(nz):
            a=ix*(nz+1)+iz;b=a+nz+1;c=b+1;d=a+1
            faces.extend([[d,c,b,a],[a+n,b+n,c+n,d+n]])
    loop=list(range(nz+1))+[ix*(nz+1)+nz for ix in range(1,nx+1)]+list(range(nx*(nz+1)+nz-1,nx*(nz+1)-1,-1))+[ix*(nz+1)for ix in range(nx-1,0,-1)]
    for a,b in zip(loop,loop[1:]+loop[:1]):faces.append([a,b,b+n,a+n])
    parts.append({'name':name,'vertices_world_xyz':verts,'faces':faces,'role':role,'category':'solid_roof','cell':cell,'volume_m3':(x1-x0)*(z1-z0)*thickness})
for row in pre['courts']:
    deck,y,cell=row['deck'],row['floor_y'],row['feature_id'];foot=Polygon(row['footprint_xz'])
    # All columns have explicit feet and heads. D16 meets the real retained
    # D17 slab underside; it receives a colonnade rather than a duplicate roof.
    head={'D06':5.76,'D09':5.63,'D12':4.72,'D16':4.26}[deck]
    for ix,x in enumerate([-39.0,-30.2,-21.4,-12.6]):
        for iz,z in enumerate([-62.3,-55.6]):
            name=f'G7C7_{deck}_FlutedPier_{ix}_{iz}'
            assert disk(x,z,.43).difference(foot).area<1e-7,name
            solid(name+'_WeightedFoot',disk(x,z,.38),y,y+.16,'stone','solid_frame',cell)
            flutes=Polygon([(x+( .21 if k%2 else .24)*math.cos(k*math.tau/24),z+( .21 if k%2 else .24)*math.sin(k*math.tau/24))for k in range(24)])
            solid(name+'_FlutedShaft',flutes,y+.16,y+head-.18,'stone','solid_frame',cell)
            solid(name+'_BronzeCollar',disk(x,z,.255),y+head-.24,y+head-.17,'metal','solid_frame',cell)
            solid(name+'_ShapedCapital',disk(x,z,.41),y+head-.18,y+head,'stone','solid_frame',cell)
            contacts.append({'part':name,'foot':[x,y,z],'head':[x,y+head,z],
                             'receiver_floor_ids':row['existing_receiver_ids'],
                             'upper_receiver':'D17_authored_atrium_terrace/StructuralSidesAndUnderside'if deck=='D16'else'Own local canopy beam and roof source',
                             'geometric_contact_only':True,'primary_capacity_accepted':False})
    for iz,z in enumerate([-62.3,-55.6]):
        rect(f'G7C7_{deck}_LongSpringing_{iz}',-39.4,-12.2,z-.15,z+.15,y+head-.13,y+head,'metal','solid_frame',cell)
    if deck in ['D06','D12']:
        low,high,t=(5.76,6.0,.18)if deck=='D06'else(4.72,5.01,.18)
        for i,(x0,x1)in enumerate([(-39.4,-30.0),(-30.4,-21.2),(-21.6,-12.2)]):
            vaulted(f'G7C7_{deck}_PetalVault_{i}',x0,x1,-62.45 if i==0 else -63.45,-55.45,y,low,high,t,'roof',cell)
        for x in [-39,-30.2,-21.4,-12.6]:
            rect(f'G7C7_{deck}_TransverseSeat_{x}',x-.10,x+.10,-62.45 if x < -36 else -63.45,-55.45,y+head-.09,y+head+.025,'metal','solid_frame',cell)
    elif deck=='D09':
        # Open pergola strips preserve sky/light gaps and differ from the vaults.
        for i in range(16):
            x=-38.9+i*1.74
            vaulted(f'G7C7_{deck}_OpenPergola_{i}',x-.28,x+.28,-62.45 if x < -36 else -63.45,-55.45,y,5.63,5.88,.12,'wood',cell)
    else:
        # The retained upper gallery is the ceiling. Thin source bearing shoes
        # meet its actual underside at102-.24=101.76; no new slab is authored.
        for i,x in enumerate([-39,-30.2,-21.4,-12.6]):
            rect(f'G7C7_{deck}_UpperGalleryBearing_{i}',x-.38,x+.38,-62.45 if x < -36 else -63.55,-55.35,y+4.12,y+4.26,'metal','solid_frame',cell)
    for i,(x,z)in enumerate([(-35.5,-59.2),(-16.5,-59.0)]):
        name=f'G7C7_{deck}_GroveIsland_{i}';outer=disk(x,z,2.15,40);inner=disk(x,z,1.92,40)
        assert outer.buffer(.28).difference(foot).area<1e-7
        solid(name+'_Foot',outer,y,y+.12,'metal','solid_planter',cell)
        solid(name+'_Plinth',outer,y+.12,y+.36,'stone','solid_planter',cell)
        solid(name+'_Soil',inner,y+.36,y+.44,'soil','solid_planter',cell)
        solid(name+'_NestedRim',outer.difference(inner),y+.36,y+.54,'stone','solid_planter',cell)
        towards=box(x,-1000,1000,1000)if i==0 else box(-1000,-1000,x,1000)
        crescent=outer.buffer(.26).difference(outer.buffer(-.08)).intersection(towards)
        solid(name+'_SeatBase',crescent,y+.12,y+.43,'stone','solid_furniture',cell)
        solid(name+'_CurvedSeatCap',crescent,y+.43,y+.49,'wood','solid_furniture',cell)
        back=outer.buffer(-.06).difference(outer.buffer(-.16)).intersection(towards)
        solid(name+'_SeatBack',back,y+.49,y+.88,'wood','solid_furniture',cell)
        if deck=='D16':
            plants.append({'id':name+'_Canopy','file':('AST-BOT-001'if i==0 else'AST-BOT-007')+'.glb','position':[x,y+.44,z],'yaw':.4+i*1.2,'scale':[1,1,1],'layer':'canopy','cell':cell})
        else:
            trees.append({'id':name+'_OriginalMediumTree','position':[x,y+.44,z],'height':(4.9 if deck in ['D06','D09']else 3.9)-i*.28,'yaw':.35+i*1.2,'cell':cell,'authorship':'New deterministic original geometry; no retained tree scaled or modified.'})
        for k in range(8):
            angle=k*math.tau/8+.18*i
            plants.append({'id':name+'_Shrub_'+str(k),'file':('AST-BOT-009'if deck=='D09'and k%2 else'AST-BOT-002')+'.glb','position':[x+1.20*math.cos(angle),y+.44,z+1.20*math.sin(angle)],'yaw':angle+.4,'scale':[1,1,1],'layer':'shrub','cell':cell})
        for k in range(12):
            angle=k*math.tau/12+.15*i
            plants.append({'id':name+'_Groundcover_'+str(k),'file':'AST-BOT-003.glb','position':[x+1.68*math.cos(angle),y+.44,z+1.68*math.sin(angle)],'yaw':angle,'scale':[1,1,1],'layer':'groundcover','cell':cell})
    # A local physical tool nook provides an operating, unscaled donor door.
    # Water/care supply and service-network provider joins remain Group3 interfaces.
    name=f'G7C7_{deck}_ToolNook';z0,z1=-64.15,-61.0
    rect(name+'_Back',-27.8,-24.2,z0-.10,z0+.10,y,y+3.12,'stone','solid_frame',cell)
    for x in [-27.7,-24.3]:rect(name+'_Side_'+str(x),x-.10,x+.10,z0,z1,y,y+3.12,'stone','solid_frame',cell)
    for x0,x1 in [(-27.8,-27.22),(-24.78,-24.2)]:rect(name+'_Jamb_'+str(x0),x0,x1,z1-.10,z1+.10,y,y+3.12,'stone','solid_frame',cell)
    rect(name+'_Head',-27.22,-24.78,z1-.10,z1+.10,y+2.70,y+3.12,'stone','solid_frame',cell)
    rect(name+'_Roof',-27.88,-24.12,z0-.16,z1+.16,y+3.12,y+3.29,'roof','solid_roof',cell)
    for i,h in enumerate([.55,1.12,1.72]):rect(name+'_ToolShelf_'+str(i),-27.45,-24.55,z0+.12,z0+.58,y+h,y+h+.05,'wood','solid_furniture',cell)
    doors.append({'id':f'G7C7_{deck}_GardenToolDoor','origin':[-26,y,z1],'yaw':0,'source':'Unscaled original AST-STF-008.glb and unchanged service_door.gd','normal_review_stance':[-26,y,-58.95],'scope':'Local garden tool feature, not a new registered room/provider or complete Group3 service connection.'})
    # Three open architectural fixtures: two grove sources and the tool arrival.
    for i,(x,z)in enumerate([(-32.65,-58.3),(-19.35,-58.1),(-26,-60.65)]):
        prefix=f'G7C7_{deck}_Lantern_{i}';px=x+(-.52 if i==0 else .52)
        solid(prefix+'_Foot',disk(px,z,.11,16),y,y+.12,'metal','solid_fixture',cell)
        solid(prefix+'_Post',disk(px,z,.045,12),y+.12,y+3.34,'metal','solid_fixture',cell)
        rect(prefix+'_Arm',min(px,x)-.035,max(px,x)+.035,z-.035,z+.035,y+3.31,y+3.39,'metal','solid_fixture',cell)
        solid(prefix+'_OpenBezel',box(x-.18,z-.20,x+.18,z+.20).difference(box(x-.13,z-.15,x+.13,z+.15)),y+3.25,y+3.35,'metal','solid_fixture',cell)
        rect(prefix+'_Opal',x-.125,x+.125,z-.145,z+.145,y+3.245,y+3.255,'opal','visual_lens',cell)
        lights.append({'id':prefix+'_Source','position':[x,y+3.23,z],'direction':[0,-1,0],'range':9,'energy':1.05,'angle':66,'color':[1,.94,.82],'source_hardware':prefix,'floor_y':y,'review_stance':[x,y,z+1.0]})
    terraces.append({'id':cell,'deck':deck,'floor_y':y,'purpose':row['purpose'],'footprint_xz':row['footprint_xz'],'existing_floor_receivers':row['existing_receiver_ids'],'new_floor':False,'public_route':[[-28.5,y,-54.0],[-28.5,y,-58.2],[-26,y,-58.2],[-23.0,y,-58.2],[-23.0,y,-54.0]],'tool_route':[[-26,y,-58.2],[-26,y,-58.95]],'roof_mode':'Retained upper gallery bearing'if deck=='D16'else'Open pergola'if deck=='D09'else'Petal vaults'})
pins=dict(pre['source_pins'])
for path in ['Game/scripts/service_door.gd','Game/assets/models/AST-STF-008.glb','Game/tests/validate_atrium_supports.gd']+[f'Game/assets/models/{r["file"]}'for r in plants]:pins[path]=hashlib.sha256((R/path).read_bytes()).hexdigest()
plan={'schema':'astraea.group7.forecourt-source.v1','status':'SOURCE_PLANNED_IMPORT_ROUTE_VISUAL_ACCEPTANCE_PENDING','terraces':terraces,'plants':plants,'procedural_trees':trees,'lights':lights,'doors':doors,'source_pins':pins,'native_filename':'G7_ForeGardenCourts_r007b.blend','capacity_delta':0,'new_room_ids':0,'originals_overwritten':False,'primary_capacity_horticulture_gameplay_final_art_accepted':False,'source_contacts':contacts,'shared_root_or_registry_edits':False}
(P/'docs/BOTANICAL_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(P/'docs/ARCHITECTURE_PARTS.json').write_text(json.dumps({'parts':parts},separators=(',',':'))+'\n');print('G7_R007_FORECOURT_PLAN',len(parts),'architecture parts',len(plants),'rigid plants',len(trees),'original trees',len(doors),'doors',len(lights),'sources')
