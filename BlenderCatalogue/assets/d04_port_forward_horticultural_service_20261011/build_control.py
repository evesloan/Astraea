from pathlib import Path
import json
W=Path(__file__).resolve().parent;R=W.parents[2];O=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';ns={'__file__':str(O/'build_native.py')};s=(O/'build_native.py').read_text();exec(s[:s.index('\nmats=start();add_parts')],ns);P=json.load(open(W/'RUNTIME_PLAN.json'));ns.update(W=W,R=R,P=P)
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
parts=[]
for name,lo,hi,role in [('D04HS_ControlPlate',[-80.32,17.48,-360.255],[-79.98,17.84,-360.19],'champagne_metal'),('D04HS_ControlButton',[-80.24,17.56,-360.285],[-80.06,17.7,-360.255],'ivory_enamel'),('D04HS_ControlIndicator',[-80.21,17.75,-360.28],[-80.09,17.8,-360.255],'opal_glow')]:
 x,y,z=lo;X,Y,Z=hi;parts.append({'name':name,'verts':[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]],'faces':faces,'role':role,'category':'garden_service_control','runtime_collision':True})
(W/'SERVICE_CONTROL_ADDENDUM.json').write_text(json.dumps({'parts':parts,'control_at':[-80.15,17.65,-360.29],'reason':'Operate top-hung garden access from outside its protected dynamic sweep; no walking entrance into planted strip'},indent=2)+'\n')
ns['add_parts'](parts,ns['start']());a=ns['export']('D04GardenServiceControl.blend','D04_PORT_FORWARD_GARDEN_SERVICE_CONTROL_r001.glb');P['service_control']={'model_file':a['export'],'model_sha256':a['export_sha256'],'collision_policy':a['collision_policy']};P['control_at']=[-80.15,17.65,-360.29];P['native_export_records'].append(a);P['model_pins'][a['export']]=a['export_sha256'];(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');q=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));q['records'].append(a);(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(q,indent=2)+'\n')
