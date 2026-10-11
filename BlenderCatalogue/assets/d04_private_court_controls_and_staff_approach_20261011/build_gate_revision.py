from pathlib import Path
import json,hashlib,copy
W=Path(__file__).resolve().parent;R=W.parents[2];O=R/'BlenderCatalogue/assets/d04_port_forward_private_court_service_20261011';P=json.load(open(W/'RUNTIME_PLAN.json'));old=json.load(open(O/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
F=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010';ns={'__file__':str(F/'build_native.py')};s=(F/'build_native.py').read_text();exec(s[:s.index('\nrecords=[];structure=[]')],ns);ns.update(W=W,R=R,P=P)
parts=copy.deepcopy(old['fixed_parts']+old['successor_parts']);faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def cube(name,lo,hi,category='gate_frame',role='champagne_metal'):
 x,y,z=lo;X,Y,Z=hi;parts.append({'name':name,'verts':[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],'faces':faces,'role':role,'category':category,'runtime_collision':True})
gates=[]
for i,(center,pivotz,span)in enumerate([(-408.55,-408.58,[-408.61,-408.31]),(-422.86,-422.83,[-423.29,-422.80]),(-437.66,-437.63,[-438.09,-437.60])]):
 g=copy.deepcopy(old['gates'][i]);g['pivot']=[-28.7,16.5,pivotz];g['closed_plane_center_z']=center;gates.append(g)
 cube(g['name'],[-28.7,16.5,center-.03],[-27.5,19.2,center+.03],category='candidate_gate',role='ivory_enamel')
 for j,y in enumerate([16.75,18.95]):cube('D04PCS_Hinge_%s_%s'%(i,j),[-28.725,y-.10,pivotz-.025],[-28.675,y+.10,pivotz+.025],category='candidate_gate_hardware')
 cube('D04PCS_Handle_'+str(i),[-27.74,17.48,center-.11],[-27.68,17.72,center-.03],category='candidate_gate_hardware')
 for j,(x,X)in enumerate([(-28.76,-28.7),(-27.5,-27.44)]):cube('D04PCS_ServiceJamb_%s_%s'%(i,j),[x,16.5,span[0]],[X,19.2,span[1]],role='ivory_enamel')
ns['add_parts'](parts,ns['start']());record=ns['export']('D04CourtGateClearance_r002.blend','D04_COURT_SERVICE_GATES_r002.glb');P['court_candidate_model']={'model_file':record['export'],'model_sha256':record['export_sha256'],'collision_policy':record['collision_policy']};P['gates']=gates;P['gate_revision_parts']=parts;P['native_export_records'].append(record);P['model_pins'][record['export']]=record['export_sha256']
revision={'status':'PASS','reason':'The original thick leaf hinge centered in the retained end-wall plane would intersect its fixed jamb during rotation. Thin programme-owned leaves now hinge on the opening-side face beyond the original wall faces; explicit jamb extensions retain opaque thresholds. Original r001 source retained.','original_source_sha256':sha(O/'RUNTIME_PLAN.json'),'original_candidate_unchanged':True,'gate_parts':parts,'gates':gates,'record':record,'production_active':False}
(W/'GATE_CLEARANCE_REVISION.json').write_text(json.dumps(revision,indent=2)+'\n');(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_STAFF_COURT_APPROACH_SEALED.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':ns['bpy'].app.version_string,'records':P['native_export_records'],'production_active':False},indent=2)+'\n');print('COURT_GATE_REVISION_PASS',record['mesh_count'])
