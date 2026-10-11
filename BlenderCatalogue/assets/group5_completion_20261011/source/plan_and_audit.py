"""Inspect retained floor ownership/connections and emit additive construction contract."""
from pathlib import Path
import hashlib,json,math,subprocess
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(path):return json.loads((ROOT/path).read_text())
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n')
d=read('BlenderCatalogue/assets/shopping_promenade_20261009/docs/PLACEMENT_AND_CONNECTORS.json')
live=read('Game/data/architecture/SHOPPING_PROMENADE.json')
components=json.loads((P/'docs/COMPONENTS.json').read_text())
control=json.loads((P/'docs/CONTROL_COMPONENT.json').read_text()) if (P/'docs/CONTROL_COMPONENT.json').exists() else None
doors=[];signs=[]
for room in d['rooms']:
    if room['retained']:continue
    sign=room['front_sign_x']
    for local,u,v,kind in [('PublicDoors',0,-6.12,'public'),('WorkBayDoors',-3.5,2.56,'service'),('StockStreetDoors',-3.5,5.44,'service')]:
        c=next(c for c in components if c['kind']==kind)
        doors.append({'chunk_id':room['chunk_id'],'local_name':local,'physical_id':room['chunk_id']+'__'+local,'stable_room_id':room['stable_room_id'],'local_xyz':[-sign*v,0,u],'rotation_y':-sign*math.pi/2,'width':c['opening_width'],'height':c['opening_height'],'model_path':'res://assets/models/group5/'+Path(c['export']).name,'model_sha256':c['sha256'],'closed_by_default':True,'route_owner':'existing immutable footprint; unapproved address never a save/stock key','permission':'normal interaction only; no staff role or pressure-control provider claimed'})
        if control:
            front,back={'PublicDoors':(.17,.56),'WorkBayDoors':(.09,.24),'StockStreetDoors':(.12,.36)}[local]
            doors[-1]['controls']=[{'id':'FrontControl','local_xyz':[c['opening_width']/2+.12,1.25,front],'rotation_y':math.pi},{'id':'BackControl','local_xyz':[c['opening_width']/2+.12,1.25,back],'rotation_y':0}]
            doors[-1]['control_model_sha256']=control['sha256']
for row in d['chunks']:
    if row['kind']!='court':continue
    # At an existing street edge, beyond its 8m central through-route and shop doors.
    px=row['position'][0];pz=row['position'][2]
    x=px-4.75 if px>0 else px+4.75
    # Panels sit between storefront rows, not across any aperture.
    shopzs=sorted(set(r['position'][2] for r in d['rooms'] if r['chunk_id'] in row['shop_chunks']))
    z=(shopzs[0]+shopzs[1])/2 if len(shopzs)>1 else shopzs[0]+4.9
    side='starboard' if px>0 else 'port';end='forward' if pz<0 else 'aft'
    guide_name='guide_'+side+'_'+end+'_r003.glb'
    signs.append({'id':row['chunk_id']+'__DistrictGuide','chunk_id':row['chunk_id'],'local_xyz':[x-px,0,z-pz],'rotation_y':0 if px>0 else math.pi,'model_path':'res://assets/models/group5/guide_'+side+'_'+end+'_r003.glb','model_sha256':hashlib.sha256((P/'exports'/guide_name).read_bytes()).hexdigest(),'readable_faces':2,'district':side+' '+end,'room_ids':None,'policy':'orientation and original venue names only; no unrecovered R-addresses'})
fitout_path=P/'docs/FITOUT_CLEARANCE.json'
fitout_revisions=json.loads(fitout_path.read_text())['rows'] if fitout_path.exists() else []
construction={'fitout_revisions':fitout_revisions,'schema':'astraea.group5.completion.v1','baseline':'affc5c807087ff87da29f3642c2d6e418241b896','doors':doors,'wayfinding':signs,'control_model':'res://assets/models/group5/retail_door_control_r001.glb','existing_light_sources':len(live['lights']),'stock_routes':'retained 36 service streets + 8 side-local staff links; survey below','preserved_R070':True,'unresolved_address_joins':84,'new_floor':False,'whole_group_accepted':False}
write(ROOT/'Game/data/architecture/group5/CONSTRUCTION.json',construction)
floors={}
for row in d['floor_proposals']:floors.setdefault(row['chunk_id'],[]).append(Polygon(row['boundary'],row['holes']))
geoms={key:unary_union(vals) for key,vals in floors.items()}
public=[];staff=[]
for row in d['chunks']:
    target=staff if row['kind'] in ['service','service_link'] else public
    target.append(row['chunk_id'])
def graph(keys):
    edges=[];adj={k:set() for k in keys}
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            # Actual floor edges, including partitioned connector ownership.
            if geoms[a].distance(geoms[b])<1e-5:
                edges.append([a,b]);adj[a].add(b);adj[b].add(a)
    groups=[];remaining=set(keys)
    while remaining:
        seen=set();todo=[min(remaining)]
        while todo:
            node=todo.pop()
            if node in seen:continue
            seen.add(node);todo.extend(adj[node]-seen)
        groups.append(sorted(seen));remaining-=seen
    return {'edges':edges,'connected_components':groups}
gpublic=graph(public);gstaff=graph(staff)
stock=[]
for r in d['rooms']:
    if r['retained']:continue
    s=r['front_sign_x'];p=r['position']
    # A stock corridor reaches the existing rear threshold at u=-3.5.
    door=Point(p[0]-s*5.8,p[2]-3.5)
    outside=Point(p[0]-s*6.2,p[2]-3.5)
    near=[k for k in staff if geoms[k].distance(outside)<.001]
    approach=LineString([(p[0]-s*5.3,p[2]-3.5),(outside.x,outside.y)])
    owned=unary_union([geoms[r['chunk_id']]]+[geoms[k] for k in near])
    supported=owned.buffer(1e-7).covers(approach)
    stock.append({'chunk_id':r['chunk_id'],'rear_threshold_xz':[door.x,door.y],'staff_floor_owners':near,'has_exact_floor_join':bool(near) and supported,'stable_room_id':r['stable_room_id'],'proof':'shop owns threshold to v=6; adjoining service owns outside approach at v=6.2; complete crossing covered by actual union'})
receipt={'status':'PASS' if all(r['has_exact_floor_join'] for r in stock) else 'HOLD','source_chunks':len(d['chunks']),'public_courts':18,'service_streets':36,'public_lateral_links':16,'staff_crosslinks':8,'stock_thresholds':stock,'public_graph':gpublic,'staff_graph':gstaff,'identity':d['identity_gate'],'shared_staff_riser_joins':'unfinished; no inferred shaft or invented connection','scope':'actual retained floor-polygon joins, not walked controller routes, loaded-cart/species or engineering acceptance'}
write(P/'qa/RETAINED_CONNECTION_SURVEY.json',receipt)
assert len(d['chunks'])==78 and len(doors)==297 and len(signs)==18
assert all(r['has_exact_floor_join'] for r in stock)
assert sum(r['stable_room_id'] is None for r in d['rooms'])==84
print('GROUP5_PLAN',len(doors),len(signs),'public components',len(gpublic['connected_components']),'staff components',len(gstaff['connected_components']))
