"""Original native/retained floor contacts;no original model,flora,column or footprint edit."""
from pathlib import Path
import ast,json,hashlib,struct,math
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
tree=ast.parse((P/'source/build_large_venue_lighting.py').read_text());exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')],type_ignores=[]),'literal_glb','exec'),globals())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((P/'qa/LIVING_GIFTS_ORIGINAL_SOURCE_BOUNDS.json').read_text());native=ROOT/'BlenderCatalogue/assets/living_gifts_interior/source/AST-RTL-006.blend';assert sha(native)==baseline['native_sha256']
old={r['name']:(np.array(r['world_bounds'][0]),np.array(r['world_bounds'][1])) for r in baseline['rows'] if not r['name'].startswith('RTL_Finish')}
floor_path=ROOT/'Game/data/generated/structural_meshes.json';floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_living_gifts_floor');polygon=unary_union([Polygon(t) for t in floor['triangles']]);assert floor['floor_y']==52.5
components=json.loads((P/'docs/LIVING_GIFTS_DOOR_COMPONENTS.json').read_text())['variants'];control_geometry=exported_bounds(P/'exports/retail_door_control_r001.glb');controls_bounds=control_geometry['Control_SeatedBack']
rows=[];proof=[];errors=[]
for component in components:
    kind=component['kind'];width=component['width'];height=component['height'];public=kind=='public'
    origin=np.array([47.6,52.5,236.1] if public else [52.4,52.5,242.9]);angle=-math.pi/2 if public else 0
    rotation=np.array([[math.cos(angle),0,math.sin(angle)],[0,1,0],[-math.sin(angle),0,math.cos(angle)]])
    geometry=exported_bounds(ROOT/component['model_path'].replace('res://','Game/'))
    def transform(a,b,offset=0):
        points=np.array([[x+offset,y,z] for x in [a[0],b[0]] for y in [a[1],b[1]] for z in [a[2],b[2]]]);points=(rotation@points.T).T+origin;return points.min(axis=0),points.max(axis=0)
    poses=0;contacts=[];mounts=[]
    for name,(a,b) in geometry.items():
        if name.startswith('Panel_'):
            label=name.split('_')[1]
            if public:travel=(-1 if label[0]=='L' else 1)*(width/4+.05 if label[1]=='0' else width/2+.05)
            else:travel={'L0':-.55,'L1':-1.05,'R0':-2.05,'R1':-1.55}[label]
            for fraction in np.linspace(0,1,21):
                c,d=transform(a,b,float(fraction)*travel);poses+=1
                if not polygon.buffer(.00003).covers(box(c[0],c[2],d[0],d[2])):contacts.append({'mesh':name,'fraction':float(fraction),'old':'outside_original_floor'})
                for target,(e,f) in old.items():
                    if np.all(np.minimum(d,f)-np.maximum(c,e)>.0001):contacts.append({'mesh':name,'fraction':float(fraction),'old':target})
        if name.startswith('track_wall_mount_'):
            c,d=transform(a,b);found=[]
            for target,(e,f) in old.items():
                overlap=np.minimum(d,f)-np.maximum(c,e)
                if np.all(overlap>.0001):found.append({'original':target,'overlap_xyz_m':overlap.tolist()})
            expected='RTL_PortalJamb_' if public else 'RTL_Wall_'
            assert any(r['original'].startswith(expected) for r in found),(kind,name,found)
            mounts.append({'mesh':name,'positive_original_contacts':found})
    if public:
        control_specs=[{'id':'PublicControl','local_xyz':[2,1.35,.695],'rotation_y':0,'original_mount':'RTL_PortalJamb_238.1'}, {'id':'InteriorControl','local_xyz':[2,1.35,.105],'rotation_y':math.pi,'original_mount':'RTL_PortalJamb_238.1'}]
    else:
        control_specs=[{'id':'PublicControl','local_xyz':[1.08,1.35,-.505],'rotation_y':0,'original_mount':'RTL_ServiceJamb_53.48'}, {'id':'InteriorControl','local_xyz':[1.08,1.35,-.795],'rotation_y':math.pi,'original_mount':'RTL_ServiceJamb_53.48'}]
    for control in control_specs:
        angle2=control['rotation_y'];r=np.array([[math.cos(angle2),0,math.sin(angle2)],[0,1,0],[-math.sin(angle2),0,math.cos(angle2)]])
        a,b=controls_bounds;points=np.array([[x,y,z] for x in [a[0],b[0]] for y in [a[1],b[1]] for z in [a[2],b[2]]]);points=(rotation@(r@points.T+np.array(control['local_xyz'])[:,None])).T+origin;c,d=points.min(axis=0),points.max(axis=0);e,f=old[control['original_mount']];overlap=np.minimum(d,f)-np.maximum(c,e);assert np.all(overlap>.0001),(kind,control,overlap);control['positive_contact_xyz_m']=overlap.tolist()
    row=dict(component);row.update({'door_name':'Group5LivingPublicDoor' if public else 'Group5LivingServiceCandidate','physical_id':'group5:D09_directory_08:original_'+('public' if public else 'service')+'_threshold','world_xyz':origin.tolist(),'rotation_y':-math.pi/2 if public else 0,'controls':control_specs,'mode':kind,'default':'closed','source_floor_owner':floor['id'],'source_floor_unchanged':True,'public_stance_world_xyz':[46.15,52.53,238.1] if public else [53.485,52.53,244.0],'interior_stance_world_xyz':[48.9,52.53,238.1] if public else [52.9,52.53,240.9],'cross_group_adoption_required':not public})
    rows.append(row);proof.append({'kind':kind,'moving_mesh_poses':poses,'unintended_original_contacts':contacts,'mounts':mounts,'controls':control_specs});errors.extend([{'kind':kind,'contact':r} for r in contacts])
j={'schema':'astraea.group5.living_doors.v1','programme_key':'D09_directory_08','historical_room_id':'D09_florist7','original_model':'res://assets/models/AST-RTL-006.glb','original_model_sha256':sha(ROOT/'Game/assets/models/AST-RTL-006.glb'),'original_native':str(native.relative_to(ROOT)),'original_native_sha256':sha(native),'original_floor_source_sha256':sha(floor_path),'doors':rows,'door_count':2,'source_shared_interfaces_accepted':False,'service_interface':{'owner':'Group6 and shared integration','proposed_service_surface_plane_z':242.9,'nominal_interior_bay_z_end':242.4,'crosses_nominal_interior_bay':True,'existing_floor_owner':floor['id'],'floor_new_or_changed':False,'protected_column_xyz':[50,52.5,244],'protected_column_model':'AST-STR-001.glb','protected_column_sha256':sha(ROOT/'Game/assets/models/AST-STR-001.glb'),'existing_exterior_turn_center_xz':[51.5,247],'status':'HOLD_OWNER_ADOPTION;source/controller/column tests do not establish cross-group operational acceptance'},'scope':'Two existing openings only;public3.78m throat andservice2m throat preserved,actual curved head/stock screen/plinth/column/floor preserved.Aft surface service cassette is an explicit Group6 interface candidate;default builder skips it pending owner adoption.No room ID/capacity/sharedroot or floor edits.'}
(ROOT/'Game/data/architecture/group5/LIVING_GIFTS_DOORS.json').write_text(json.dumps(j,indent=2)+'\n');(P/'qa/LIVING_GIFTS_DOOR_SOURCE_FIT.json').write_text(json.dumps({'status':'PASS' if not errors else 'HOLD','proof':proof,'errors':errors,'moving_mesh_poses':sum(r['moving_mesh_poses'] for r in proof),'scope':'Actual unbatched immutable native component bounds and literal current floor;actual flora/display/column triangle probes and full main/controller tests are separate;cross-group adoption held'},indent=2)+'\n');print('LIVING_SOURCE_FIT',sum(r['moving_mesh_poses'] for r in proof),'errors',len(errors));assert not errors
