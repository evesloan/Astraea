"""Copy exact source exports and emit an isolated, opt-in integration contract."""
from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];OLD=P.parent/'group7_hull_atrium_20261009'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
export=json.load(open(P/'docs/EXPORTS.json'));models=[]
def install(src,name,cell,expected):
    dst=R/'Game/assets/models'/name;assert sha(src)==expected
    if dst.exists():assert sha(dst)==expected
    else:shutil.copy2(src,dst)
    models.append({'file':name,'cell':cell,'sha256':expected,'source':str(src.relative_to(R)),'origin':[0,0,0],'rotation_y':0,'scale':[1,1,1]})
for row in export['exports']:install(P/row['path'],row['file'],row['cell'],row['sha256'])
# Reuse both prior enclosure generations exactly. Galleries are already installed.
for doc in ['MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json','MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json']:
    data=json.load(open(OLD/'docs'/doc))
    for row in data['exports']:
        src=OLD/row['path'];install(src,'G7_Completion_Prior_'+src.name,'Prior_'+src.stem,row['sha256'])
terminal=json.load(open(OLD/'continuation_r002/docs/TERMINAL_DELIVERY_R002.json'));doors=[];lights=json.load(open(P/'docs/LIGHT_INTERFACES.json'))
for row in terminal['assemblies']:
    src=OLD/'continuation_r002'/row['export'];install(src,'G7_Completion_Prior_'+src.name,'Prior_'+row['id'],row['export_sha256'])
    for d in row['doors']:doors.append({'id':d['id'],'family':'AST-STF-008','origin':d['origin_world_xyz'],'yaw':d['rotation_y'],'source_preview_dropped':True,'permission_acceptance':False})
    for l in row['lights']:lights.append({'id':l['id'],'position':l['position_world_xyz'],'direction':l['direction_xyz'],'range':l['range_m'],'energy':l['energy_proposal'],'angle':l['spot_angle_deg'],'color':l['color_rgb'],'source_hardware':l['id']})
out={'schema':'astraea.group7.completion.runtime.v1','baseline':'affc5c807087ff87da29f3642c2d6e418241b896','models':models,'doors':doors,'lights':lights,'source_native':export['native'],'native_sha256':export['native_sha256'],'activate_from_shared_root':False,'earlier_galleries_not_duplicated':True,'root_patch':'After independently retaining this package and reconciling interface holds, add load("res://scripts/group7_completion.gd").build(self) before retained lighting-budget configuration. If built afterwards, this module appends only its new lights. No shared registry or floor-builder edits are performed here.','floor_policy':'Existing physical roof/bridge source meshes must not be duplicated by compiler slabs. Register only planning/ownership records. All original compiled floors remain unchanged.','whole_group_accepted':False,'structural_capacity_accepted':False,'capacity_delta':0}
(R/'Game/data/architecture/GROUP7_COMPLETION.json').write_text(json.dumps(out,indent=2)+'\n');(P/'docs/RUNTIME_INTERFACE.json').write_text(json.dumps(out,indent=2)+'\n')
print('GROUP7_RUNTIME_CONTRACT',len(models),'models',len(doors),'operating door candidates',len(lights),'lights')
