"""Coordinate unchanged rest anchors with enclosure, control and study-group fit."""
from pathlib import Path
import json,copy
G=Path(__file__).resolve().parents[2];path=G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json';p=json.loads(path.read_text())
for r in p['rooms']:
 i=r['allocation']['source_envelope_index'];sd=json.loads((G/r['source_contract']).read_text());s=next(x for x in sd['rooms'] if x['allocation']['source_envelope_index']==i-3)
 r['doors']=copy.deepcopy(s['doors']);r['lights']=copy.deepcopy(s['lights']);r['component_adjustments']=[]
 for d in r['doors']:
  d['position'][0]*=-1;d['yaw']*=-1;d['persistent_id']=d['persistent_id'].replace(s['allocation']['proposed_runtime_id'],r['allocation']['proposed_runtime_id'])
  if 'CocoonPrivacyDoor' in d['name']:
   idx=int(d['name'].split('_')[-1])-1;delta=r['rest_adjustments'][idx]['mirrored_delta'];d['position']=[d['position'][k]+delta[k] for k in range(3)]
 assert len({d['persistent_id'] for d in r['doors']})==len(r['doors'])
 for light in r['lights']:light['position'][0]*=-1
 desk=next(c for c in r['source_components'] if c['name']=='LibraryStudyEdge');old=[-desk['position'][0],desk['position'][1],desk['position'][2]]
 inner=r['allocation']['allocation_x'][0]<82;center=sum(r['allocation']['allocation_z'])/2
 new=[75.1,93,center-2.05] if inner else ([91.75,93,old[2]] if old[0]>93 else old)
 delta=[new[k]-old[k] for k in range(3)]
 group=['LibraryStudyEdge','SupportedOpenFolio','HousedStudyTaskFixture','DayReadingChair','StudyChair']
 # A source chair far from this desk belongs to a distinct sitting edge and stays put.
 for name in group:
  c=next((c for c in r['source_components'] if c['name']==name),None)
  if c is None:continue
  if 'Chair' in name and abs(c['position'][2]-desk['position'][2])>1.5:continue
  r['component_adjustments'].append({'component_name':name,'mirrored_delta':delta})
 for light in r['lights']:
  if abs(light['position'][0]-old[0])<1.3 and abs(light['position'][2]-old[2])<1.3:
   light['position']=[light['position'][k]+delta[k] for k in range(3)]
 r['fit_revision']='r002_anchor_coordinated_liners_doors_and_study_groups'
path.write_text(json.dumps(p,indent=2)+'\n')
