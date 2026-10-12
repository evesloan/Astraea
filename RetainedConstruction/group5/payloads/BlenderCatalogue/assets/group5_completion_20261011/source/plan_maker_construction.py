"""Literal current maker source: nine fixture bindings and existing recessed threshold."""
from pathlib import Path
import ast,json,hashlib,struct,math
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
tree=ast.parse((P/'source/build_large_venue_lighting.py').read_text());exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')],type_ignores=[]),'literal_glb_bounds','exec'),globals())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
current=ROOT/'Game/assets/models/SOL_D09_directory_05_entry001.glb';assert sha(current)=='a71841e5d032f53d3a7157aaebbf8e5f1276008030bbaf59adbe41ae52ae5ccf'
counterpart=P/'source/retained_venue_recovery/D09_directory_05/current_counterpart_r002.blend';assert sha(counterpart)=='102043e70818ddddaa996c75d768810df42f190c01f34730d2b29622e303a4bd'
old=exported_bounds(current);prefix='D09_directory_05__'
source_definition=json.loads((P/'docs/MAKER_FOYER_SOURCES.json').read_text());source_export=ROOT/source_definition['model_path'].replace('res://','Game/')
new={n:(a+np.array(source_definition['origin_world_xyz']),b+np.array(source_definition['origin_world_xyz'])) for n,(a,b) in exported_bounds(source_export).items()}
floor_path=ROOT/'Game/data/generated/received_structural_meshes.json';floors=[r for r in json.loads(floor_path.read_text())['regions'] if r['id'].startswith('D09_directory_05_')]
assert len(floors)==2 and all(r['floor_y']==52.5 for r in floors)
floor=unary_union([Polygon(t) for r in floors for t in r['triangles']])
lights=[];mounts=[];errors=[]
for i in range(7):
    lens=prefix+'gallery_light'+str(i)+'_lens';a,b=old[lens];at=(a+b)/2;at[1]=a[1]-.03
    lights.append({'name':'MakerGallerySource_'+str(i),'source_mesh':lens,'world_xyz':at.tolist(),'color':[1,.95,.84],'range_m':21,'energy':1.1,'lens_gap_m':float(a[1]-at[1]),'source_model':'current_immutable'})
for z in [-7,7]:
    lens='MakerFoyer_'+str(z)+'_lens';a,b=new[lens];at=(a+b)/2;at[1]=a[1]-.03
    lights.append({'name':'MakerFoyerSource_'+str(z),'source_mesh':lens,'world_xyz':at.tolist(),'color':[1,.95,.88],'range_m':8,'energy':.85,'lens_gap_m':float(a[1]-at[1]),'source_model':'selected_additive'})
    mount='MakerFoyer_'+str(z)+'_wall_mount';c,d=new[mount]
    bear=[]
    for n,(e,f) in old.items():
        overlap=np.minimum(d,f)-np.maximum(c,e)
        if np.all(overlap>.0001):bear.append({'original':n,'overlap_xyz_m':overlap.tolist()})
    assert len(bear)==1 and bear[0]['original']==prefix+'threshold'+('4.5' if z>0 else '-4.5');mounts.append({'mount':mount,'bearings':bear})
for n,(a,b) in new.items():
    assert floor.buffer(.00003).covers(box(a[0],a[2],b[0],b[2]))
    if n.endswith('_wall_mount'):continue
    for k,(c,d) in old.items():
        if np.all(np.minimum(b,d)-np.maximum(a,c)>.0001):errors.append({'new':n,'old':k})
door_definition=json.loads((P/'docs/MAKER_FULL_APERTURE_DOOR.json').read_text());door_path=ROOT/door_definition['model_path'].replace('res://','Game/');door=exported_bounds(door_path);width=door_definition['width_m'];origin=np.array([-60.735,52.5,0]);yaw=math.pi/2
r=np.array([[0,0,1],[0,1,0],[-1,0,0]],float)
def pose(a,b,offset=0):
    points=np.array([[x+offset,y,z] for x in [a[0],b[0]] for y in [a[1],b[1]] for z in [a[2],b[2]]]);points=(r@points.T).T+origin;return points.min(axis=0),points.max(axis=0)
poses=0;door_mounts=[]
for n,(a,b) in door.items():
    if n.startswith('Panel_'):
        label=n.split('_')[1];sgn=-1 if label[0]=='L' else 1;idx=int(label[1]);travel=sgn*(width/4+.05 if idx==0 else width/2+.05)
        for frac in np.linspace(0,1,21):
            c,d=pose(a,b,float(frac)*travel);poses+=1
            if not floor.buffer(.00003).covers(box(c[0],c[2],d[0],d[2])):errors.append({'new':n,'fraction':float(frac),'old':'outside_floor'})
            for k,(e,f) in old.items():
                if np.all(np.minimum(d,f)-np.maximum(c,e)>.0001):errors.append({'new':n,'fraction':float(frac),'old':k})
    if n.startswith('track_wall_mount_'):
        c,d=pose(a,b);bear=[]
        for k,(e,f) in old.items():
            over=np.minimum(d,f)-np.maximum(c,e)
            if np.all(over>.0001):bear.append({'original':k,'overlap_xyz_m':over.tolist()})
        assert len(bear)==2 and {row['original'] for row in bear}=={prefix+'threshold'+('4.5' if '_-' in n else '-4.5'),prefix+'recess_edge'+('4.5' if '_-' in n else '-4.5')};door_mounts.append({'mount':n,'bearings':bear})
controls=[{'id':'PublicControl','local_xyz':[-4.255,1.35,.985],'rotation_y':math.pi/2}, {'id':'InteriorControl','local_xyz':[-4.5,1.35,.090],'rotation_y':math.pi}]
control_bounds=exported_bounds(P/'exports/retail_door_control_r001.glb')['Control_SeatedBack'];a,b=control_bounds
for control in controls:
    angle=control['rotation_y'];rotation=np.array([[math.cos(angle),0,math.sin(angle)],[0,1,0],[-math.sin(angle),0,math.cos(angle)]])
    points=np.array([[x,y,z] for x in [a[0],b[0]] for y in [a[1],b[1]] for z in [a[2],b[2]]]);points=(r@(rotation@points.T+np.array(control['local_xyz'])[:,None])).T+origin;c,d=points.min(axis=0),points.max(axis=0)
    e,f=old[prefix+'threshold4.5'];over=np.minimum(d,f)-np.maximum(c,e);assert np.all(over>.0001),(control,over)
    control['actual_jamb_contact_xyz_m']=over.tolist()
j={'schema':'astraea.group5.maker_construction.v1','programme_key':'D09_directory_05','historical_original_correction_native_recovered':False,'current_editable_counterpart':str(counterpart.relative_to(ROOT)),'counterpart_sha256':sha(counterpart),'original_model':'res://assets/models/'+current.name,'original_model_sha256':sha(current),'foyer_source':source_definition,'fixtures':lights,'door':{'model_path':door_definition['model_path'],'model_sha256':sha(door_path),'physical_id':'group5:D09_directory_05:original_recessed_threshold','door_name':'Group5MakerFoyerDoor','width':width,'height':3.9,'world_xyz':origin.tolist(),'rotation_y':yaw,'controls':controls,'public_approach_world_xyz':[-53,52.53,0],'public_foyer_world_xyz':[-58.5,52.53,0],'public_stance_world_xyz':[-59.75,52.53,3.45],'interior_world_xyz':[-63,52.53,0],'interior_stance_world_xyz':[-62,52.53,4.5]},'door_component':door_definition,'scope':'Nine physical source lights and four-panel door in existing recessed opening;current original floor,stock/craft/work fitout,room identities/capacity unchanged;original correction-native,inventory/child use/species/save/Game/CRT/engineering/hardware acceptance held'}
ceiling_path=P/'docs/MAKER_CEILING_ENCLOSURE.json'
if ceiling_path.exists():j['ceiling_enclosure']=json.loads(ceiling_path.read_text())
(ROOT/'Game/data/architecture/group5/MAKER_CONSTRUCTION.json').write_text(json.dumps(j,indent=2)+'\n')
(P/'qa/MAKER_CONSTRUCTION_SOURCE_FIT.json').write_text(json.dumps({'status':'PASS' if not errors else 'HOLD','errors':errors,'literal_original_floor_unions':2,'floor_source_sha256':sha(floor_path),'new_foyer_mounts':mounts,'door_mounts':door_mounts,'moving_door_mesh_poses':poses,'nine_physical_lens_gaps':[r['lens_gap_m'] for r in lights],'actual_original_model_sha256':sha(current),'scope':'Actual current export/floor bounds,positive mounting contacts and moving geometry;no simulated Game acceptance'},indent=2)+'\n')
print('MAKER_CONSTRUCTION_SOURCE_FIT',poses,'errors',len(errors));assert not errors
