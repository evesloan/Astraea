"""Actual source/native placement and physical seam checks for SAL002 within SAL003."""
from pathlib import Path
import sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,SourceCache,C
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
family=ROOT/'assets/salon_threshold';ms={i:json.loads((family/(i+'.manifest.json')).read_text())for i in ['AST-SAL-002','AST-SAL-003']};src={};native={};inputs=[]
for ident,m in ms.items():
 rp=OUT/f'independent_source_{ident}.json';r=json.loads(rp.read_text());sp=family/m['source'];gp=family/m['export'];assert sha(sp)==r['sha256'];inputs.extend(bind(p)for p in [sp,gp,family/(ident+'.manifest.json'),rp]);src[ident]=SourceCache(rp);native[ident]=Native(gp)
place=np.asarray(ms['AST-SAL-002']['quiet_local_placement_source_m']);markers={i:{x['name']:x for x in m['positions_and_normals']}for i,m in ms.items()}
pairs=[('high_join','front_header_joint_-1'),('rear_shell_join','reserved_cove_rear_join'),('lower_side_bearing','low_cove_bearing')];seams=[]
for a,b in pairs:
 ma,mb=markers['AST-SAL-002'][a],markers['AST-SAL-003'][b];pa=np.asarray(ma['source_blender_xyz_m'])+place;pb=np.asarray(mb['source_blender_xyz_m']);na=np.asarray(ma['normal_source_blender']);nb=np.asarray(mb['normal_source_blender'])
 na_i={x.get('name'):i for i,x in enumerate(native['AST-SAL-002'].g.doc['nodes'])}[ma['node_name']];nb_i={x.get('name'):i for i,x in enumerate(native['AST-SAL-003'].g.doc['nodes'])}[mb['node_name']]
 ga=native['AST-SAL-002'].world[na_i][:3,3]+C@place;gb=native['AST-SAL-003'].world[nb_i][:3,3]
 r={'pair':[a,b],'source_world_points_m':[pa.tolist(),pb.tolist()],'source_gap_m':float(np.linalg.norm(pa-pb)),'actual_native_gap_m':float(np.linalg.norm(ga-gb)),'source_opposed_normal_error':float(np.linalg.norm(na+nb)),'physical_named_parts':[ma['physical_part'],mb['physical_part']]};r['passed']=max(r['source_gap_m'],r['actual_native_gap_m'],r['source_opposed_normal_error'])<1e-6;seams.append(r)
probes=[]
def probe(name,p,partA,partB):
 p=np.asarray(p,float);a=src['AST-SAL-002'].nearest(C@(p-place),node=partA);b=src['AST-SAL-003'].nearest(C@p,node=partB)
 r={'name':name,'point_quiet_source_m':p.tolist(),'named_source_distances_m':[a['distance_m'],b['distance_m']],'parts':[partA,partB]};r['passed']=max(r['named_source_distances_m'])<.0002;probes.append(r)
for y in [.05,.15,.64,1.13,1.23]:
 for z in [3.37,3.5,3.67]:probe('high_end_face',[-.7,y,z],'rising_cove_deep_structural_shoulder','quiet_front_header_reserved_cove_receiver')
for x in [.3,.6,1.2,1.8,2.1]:
 k=min(15,int(x/.15));f=x/.15-k;smooth=lambda t:2.85+.43*(3*t*t-2*t*t*t);base=smooth(k/16)*(1-f)+smooth((k+1)/16)*f;z=(max(3.28,base+.08)+base+.46)/2
 probe('rear_shell_bearing',[x-3.1,1.28,z],'rising_cove_deep_structural_shoulder','quiet_continuous_rear_cove_and_ceiling')
for x in np.linspace(0,.16,17):
 k=min(15,int(x/.15));f=x/.15-k;smooth=lambda t:2.85+.43*(3*t*t-2*t*t*t);z=smooth(k/16)*(1-f)+smooth((k+1)/16)*f
 # Core bearing begins atY.022 after its physical front inset/recess was carved.
 for y in [.04,.08,.14]:probe('low_profile_bearing',[x-3.1,y,z],'rising_cove_deep_structural_shoulder','quiet_outer_low_cove_bearing_rib')
maximum=np.asarray(ms['AST-SAL-003']['historical_authoring_maximum_xyz_m']);actual=np.asarray(ms['AST-SAL-003']['dimensions_blender_xyz_m'])
res={'passed':all(x['passed']for x in seams+probes)and bool(np.all(actual<=maximum+1e-6)),'inputs':inputs,'scope':'New proposed joined quiet/rising component arrangement. Neither recovered host geometry nor structural load certification.','placement_source_m':place.tolist(),'placement_native_m':(C@place).tolist(),'paired_actual_native_markers':seams,'physical_face_and_bearing_probes':probes,'quiet_actual_envelope_m':actual.tolist(),'later_authoring_maximum_m':maximum.tolist(),'limit':'Finite physical seam probes, no complete overlap-volume proof or installed room. Unknown real aperture/stroke/cassette/head reservations remain unknown.'}
(OUT/'independent_section_seams.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'passed':res['passed'],'paired_markers':len(seams),'physical_probes':len(probes),'max_source_surface_error_m':max(max(x['named_source_distances_m'])for x in probes),'failed':[p for p in probes if not p['passed']][:5]},indent=2))
