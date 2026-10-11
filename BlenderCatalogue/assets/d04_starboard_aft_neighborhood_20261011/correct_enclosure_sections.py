from pathlib import Path
import json,copy,ast,hashlib,shutil
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_aft_neighborhood_20261011';P=json.load(open(W/'RUNTIME_PLAN.json'));d=W/'geometry_attempt002_sections_hold';assert d.is_dir()
for f in [W/'RUNTIME_PLAN.json',R/'Game/artifacts/d04_starboard_aft_neighborhood_geometry.json',R/'Game/tests/validate_d04_starboard_aft_neighborhood_geometry.gd',Path('/tmp/starboard_aft_geometry002.log')]:assert (d/f.name).read_bytes()==f.read_bytes()
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','segment']:exec(compile(ast.get_source_segment(text,n),'<reviewed existing segment helper>','exec'))
changed=[]
for q in P['assemblies']['CO']:
 name=q['name'];height=None;thick=.16
 if name.startswith('SAC_PerimeterDado_'):height=1.2
 elif name.startswith('SAC_PerimeterGlass_'):height=1.95
 elif name.startswith('SAC_PerimeterHead_'):height=.83
 elif name.startswith('SAC_LowerScreen_'):height=3.2;thick=.12
 if height is None:continue
 assert len(q['verts'])==8;a=[sum(v[i]for v in q['verts'][:4])/4 for i in range(3)];b=[sum(v[i]for v in q['verts'][4:])/4 for i in range(3)]
 if name.startswith('SAC_PerimeterGlass_'):a[1]=b[1]=18.675
 segment(name,a,b,height,thick,q['role'],q['category']);changed.append({'name':name,'before':q,'after':parts[-1]})
new={q['name']:q for q in parts};P['assemblies']['CO']=[new.get(q['name'],q)for q in P['assemblies']['CO']];assert len(changed)==27
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'ENCLOSURE_SECTION_CORRECTION_INPUT.json').write_text(json.dumps({'prior_runtime_sha256':hashlib.sha256((W/'RUNTIME_PLAN.json').read_bytes()).hexdigest(),'changed_owned_wall_members':changed,'native_revision':'CO_r002','prior_saved_natives_preserved':22,'receiving_and_homes_unchanged':True,'source_or_player_changes':False,'section':'Dado16.5..17.7; glass17.7..19.65; head19.65..20.48. Lower screens12..15.2, physical thickness.12.'},indent=2)+'\n')
# Keep the reproducible own preparation recipe consistent; do not execute it over retained export records.
f=W/'prepare_candidate.py';s=f.read_text().replace('.16,1.2,\'warm_walnut\'','1.2,.16,\'warm_walnut\'').replace('[a[0],18.45,a[1]],[b[0],18.45,b[1]],.16,1.5','[a[0],18.675,a[1]],[b[0],18.675,b[1]],1.95,.16').replace('.16,.83,\'ivory_enamel\'','.83,.16,\'ivory_enamel\'').replace('.12,3.2,\'staff_panel\'','3.2,.12,\'staff_panel\'');f.write_text(s)
print('Corrected own enclosure members',len(changed))
