"""Literal five-venue foyer plan and changed moving/fixed-source audit."""
from pathlib import Path
import ast,json,hashlib,math,struct,shutil
import numpy as np
from shapely.geometry import Polygon,box
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
parser=ast.parse((P/'source/build_large_venue_lighting.py').read_text())
fn=next(n for n in parser.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'literal_glb_bounds','exec'),globals())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
components=json.loads((P/'docs/LARGE_VENUE_DOOR_COMPONENTS.json').read_text())['variants']
sections=json.loads((ROOT/'Game/data/architecture/received_sections.json').read_text())['sections']
floors=json.loads((ROOT/'Game/data/generated/received_structural_meshes.json').read_text())['regions']
rows=[];proof=[];errors=[]
for key in ['D09_directory_02','D09_directory_03','D09_directory_07','D09_directory_09','D09_directory_10']:
    row=next(r for r in sections if r['programme_key']==key)
    folder=P/'source/retained_venue_recovery'/key
    floor_path=next(folder.rglob('floor_proposal.json'));floor=json.loads(floor_path.read_text())
    objects_path=next(folder.rglob('objects.json'));objects={o['name']:o for o in json.loads(objects_path.read_text())}
    polygon=Polygon(floor['local_xz'])
    ends=sorted(v for x,v in floor['local_xz'] if abs(x)<.00001);low,high=ends[0],ends[-1]
    width=high-low;centre=(high+low)/2;sign=1 if row['translation_xyz'][0]>0 else -1
    wall=abs(sum(objects['Perimeter_1']['bounds_blender'][0])/2)
    owner_floor=next(r for r in floors if r['id']==row['floor_owner_ids'][0])
    actual_floor=Polygon([(x-row['translation_xyz'][0],v-row['translation_xyz'][2]) for x,v in owner_floor['rings'][0]])
    assert actual_floor.symmetric_difference(polygon).area<.00001 and owner_floor['floor_y']==52.5
    pier_inward=max(abs(x) for name,item in objects.items() if name.startswith('Entry_pier_') for x in item['bounds_blender'][0])
    stand_off=1.3 if wall+.3<pier_inward+.05 else .3
    part=next(r for r in components if r['width_m']==width and abs(r.get('stand_off_m',.3)-stand_off)<.00001)
    source=P/part['export'];out=ROOT/'Game/assets/models/group5/large_venue_doors'/source.name
    out.parent.mkdir(exist_ok=True)
    if not out.exists():shutil.copyfile(source,out)
    assert sha(out)==part['export_sha256']
    source_model=ROOT/'Game/assets/models'/row['model_file'];geometry=exported_bounds(source_model)
    hardware=exported_bounds(source);controls=exported_bounds(P/'exports/retail_door_control_r001.glb')
    yaw=-sign*math.pi/2
    rotation=np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])
    origin=np.array([sign*(wall+stand_off),0,centre])
    def pose(lo,hi,offset=0):
        points=np.array([[x,y,z] for x in [lo[0]+offset,hi[0]+offset] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])
        points=(rotation@points.T).T+origin
        return points.min(axis=0),points.max(axis=0)
    moving_samples=0;contacts=[]
    for name,(lo,hi) in hardware.items():
        if not name.startswith('Panel_'):continue
        label=name.split('_')[1];idx=int(label[1]);sgn=-1 if label[0]=='L' else 1
        displacement=sgn*((width/4+.05) if idx==0 else (width/2+.05))
        for fraction in np.linspace(0,1,21):
            a,b=pose(lo,hi,displacement*fraction);moving_samples+=1
            if not polygon.buffer(.00001).covers(box(a[0],a[2],b[0],b[2])):contacts.append([name,float(fraction),'outside_owned_floor'])
            for old,(c,d) in geometry.items():
                if np.all(np.minimum(b,d)-np.maximum(a,c)>.0001):contacts.append([name,float(fraction),old])
    mounts=[]
    for name,(lo,hi) in hardware.items():
        if not name.startswith('track_wall_mount_'):continue
        a,b=pose(lo,hi)
        candidates=[]
        for original in ['Perimeter_1','Perimeter_9']:
            c,d=geometry[original];overlap=np.minimum(b,d)-np.maximum(a,c)
            if np.all(overlap>.0001):candidates.append({'original':original,'overlap_xyz_m':overlap.tolist()})
        assert len(candidates)==1,(key,name,candidates)
        mounts.append({'mount':name,'contact':candidates[0]})
    return_face=geometry['Perimeter_0'][1][2]
    lower_pier=next((item for name,item in geometry.items() if name.startswith('Entry_pier_') and item[1][2]<centre),None)
    assert lower_pier is not None
    public_face=max(return_face,lower_pier[1][2])
    public_u=wall-.25
    if lower_pier[1][2]>return_face:
        public_u=min(public_u,max(abs(lower_pier[0][0]),abs(lower_pier[1][0]))-.3)
    control_specs=[{'id':'PublicControl','local_xyz':[sign*(public_face-.005-centre),1.35,wall+stand_off-public_u],'rotation_y':sign*math.pi/2},
                   {'id':'InteriorControl','local_xyz':[sign*(width/2+width/4+.35),1.35,stand_off-.105],'rotation_y':math.pi}]
    for control in control_specs:
        angle=control['rotation_y'];r=np.array([[math.cos(angle),0,math.sin(angle)],[0,1,0],[-math.sin(angle),0,math.cos(angle)]])
        lo,hi=controls['Control_SeatedBack'];points=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])
        points=(rotation@(r@points.T+np.array(control['local_xyz'])[:,None])).T+origin
        a,b=points.min(axis=0),points.max(axis=0);candidates=[]
        for original in ['Perimeter_0','Perimeter_1','Perimeter_9','Perimeter_10']+[n for n in geometry if n.startswith('Entry_pier_')]:
            c,d=geometry[original];overlap=np.minimum(b,d)-np.maximum(a,c)
            if np.all(overlap>.0001):candidates.append({'original':original,'overlap_xyz_m':overlap.tolist()})
        assert len(candidates)==1,(key,control,candidates)
        control['mount_contact']=candidates[0]
    errors.extend([{'programme_key':key,'contact':c} for c in contacts])
    plan={'programme_key':key,'name':row['name'],'source_model':'res://assets/models/'+row['model_file'],'source_sha256':sha(source_model),
        'door_name':'Group5FoyerDoors','physical_id':'group5:'+key+':original_foyer_threshold','model_path':'res://assets/models/group5/large_venue_doors/'+source.name,
        'model_sha256':sha(source),'width':width,'height':3.9,'local_xyz':origin.tolist(),'rotation_y':yaw,'controls':control_specs,
        'wall_inward_u':wall,'mechanism_stand_off_m':stand_off,'opening_local_v':[low,high],'source_floor_owner':owner_floor['id'],'source_floor_unchanged':True,
        'public_stance_local_xyz':[sign*public_u,.03,public_face+.65],
        'interior_stance_local_xyz':[sign*(wall+stand_off+.9),.03,high+width/4+.35],
        'public_approach_world_xyz':[sign*3,52.53,row['translation_xyz'][2]+centre],
        'safe_foyer_public_local_xyz':[sign*(wall-1.2),.03,centre],
        'inside_local_xyz':[sign*(wall+stand_off+1.3),.03,centre],
        'identity':'Existing large-venue programme key plus physical foyer suffix;no new/recovered room address,capacity or source-floor identity'}
    rows.append(plan)
    proof.append({'programme_key':key,'source_floor_proposal_sha256':sha(floor_path),'source_object_bounds_sha256':sha(objects_path),
        'moving_mesh_pose_samples':moving_samples,'original_mesh_bounds':len(geometry),'moving_contacts':contacts,'wall_mounts':mounts,
        'control_contacts':[c['mount_contact'] for c in control_specs],'source_width_m':width,'source_height_preserved_m':3.9})
definition={'schema':'astraea.group5.large_venue_doors.v1','baseline_group5_commit':'e835c73535939e5788edc4cd148e618cb27fcbdf',
    'doors':rows,'door_count':5,'control_count':10,'default':'closed','scope':'Five supported original foyer thresholds;no floor/capacity/room-ID changes;role,pressure,save,cart/species and whole-group acceptance held'}
(ROOT/'Game/data/architecture/group5/LARGE_VENUE_DOORS.json').write_text(json.dumps(definition,indent=2)+'\n')
(P/'qa/LARGE_VENUE_DOOR_SOURCE_FIT.json').write_text(json.dumps({'status':'PASS' if not errors else 'HOLD','proof':proof,'errors':errors,
    'literal_retained_floor_unions_verified':5,'total_moving_mesh_pose_samples':sum(r['moving_mesh_pose_samples'] for r in proof),'scope':'Conservative actual original export bounds,owned retained floors and positive wall/control contacts;not engine/controller or final engineering/visual acceptance'},indent=2)+'\n')
print('GROUP5_LARGE_VENUE_DOOR_SOURCE_FIT',len(rows),sum(r['moving_mesh_pose_samples'] for r in proof),'errors',len(errors))
assert not errors
