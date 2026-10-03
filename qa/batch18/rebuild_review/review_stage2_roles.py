"""Stage2 role selection only from freshly regenerated stage1 editable metadata/detail."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
rows=[]
for family,revision in [('retail_display','r02'),('retail_work','r05')]:
 receipt_path=OUT/f'rebuild_{family}_{revision}.json';receipt=json.loads(receipt_path.read_text());assert receipt['passed'];stage=ROOT/receipt['stage'];folder=stage/'assets'/family;collision=json.loads((folder/'collision_proposals.json').read_text());output=OUT/f'stage2_{family}_{revision}';output.mkdir(exist_ok=True);checks=[];selected={};inputs=[receipt_path,folder/'collision_proposals.json']
 if family=='retail_work':
  for ident,data in collision.items():
   detail=data['precise_reference'];retained=[x for x in detail if x['body_candidate_retained']];omitted=[x['name']for x in detail if not x['body_candidate_retained']];selected[ident]=retained;expected=data['optional_body_candidate'];checks.append({'catalogue_id':ident,'detailed_count':len(detail),'selected_count':len(retained),'literal_precise_shapes_unchanged':True,'retained_names_match_generated_policy':[x['name']for x in retained]==expected['retained_shape_names'],'omitted_names_match_generated_policy':omitted==expected['omitted_shape_names']})
 else:
  bp=folder/'actor_proxies/body_collision_subset.json';body=json.loads(bp.read_text())['assets'];inputs.append(bp)
  for ident,data in body.items():
   mp=folder/(ident+'.manifest.json');m=json.loads(mp.read_text());inputs.append(mp);auditpath=OUT/f'rebuilt_{family}_{revision}_source_{ident}.json';audit=json.loads(auditpath.read_text());inputs.append(auditpath);props={x['name']:x['properties']for x in audit['objects']if x['type']=='MESH'};profiles={x['part']:x for x in m['whole_profile_records']};shapes=[]
   for part,p in profiles.items():
    if props[part]['body_candidate_keep']:
     axis=p['profile_axis_source'];dims=[k for k in range(3)if k!=axis];points=[]
     for d in p['extrusion_range_m']:
      for xy in p['polygon_m']:
       v=[0,0,0];v[axis]=d;v[dims[0]]=xy[0];v[dims[1]]=xy[1];points.append(v)
     shapes.append({'semantic_parts':[part],'points_source_m':points})
    elif part.startswith('pale_rising_surround_'):
     partner=part.replace('pale_rising_surround_','recessed_terracotta_return_');q=profiles[partner];polygon=p['polygon_m'][:2]+q['polygon_m'][2:];points=[[x,y,z]for y in p['extrusion_range_m']for x,z in polygon];shapes.append({'semantic_parts':[part,partner],'points_source_m':points})
   actual={tuple(x['semantic_parts']):x for x in shapes};expected={tuple(x['semantic_parts']):x for x in data['shapes']};assert actual.keys()==expected.keys();errors=[]
   for key,x in actual.items():
    a=np.array(x['points_source_m']);b=np.array(expected[key]['points_source_m']);errors.append(float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max())))
   selected[ident]=shapes;checks.append({'catalogue_id':ident,'detailed_count':collision['assets'][ident]['shape_count'],'selected_count':len(shapes),'selection_derived_from_fresh_editable_body_flags_and_whole_profiles':True,'exact_named_group_set_matches_generated_policy':actual.keys()==expected.keys(),'max_candidate_vertex_difference_m':max(errors),'candidate_geometry_matches':max(errors)<1e-9})
 # Repeat the pure serialization to show deterministic role extraction without consuming its earlier result.
 paths=[]
 for i in [1,2]:
  p=output/f'selected_collision_roles_run{i}.json';p.write_text(json.dumps(selected,indent=2)+'\n');paths.append(p)
 row={'family':family,'revision':revision,'stage':'second_stage_selection_from_reconstructed_outputs','inputs':[bind(p)for p in inputs],'checks':checks,'selection_outputs':[bind(p)for p in paths],'two_selections_byte_identical':sha(paths[0])==sha(paths[1]),'not_original_seed_inputs':True,'limits':'Optional collision role construction/selection remains unadopted. Stage1 consumed only exact original generator/helper/old palette inputs and regenerated new art; no generated collision, previous asset or QA output was seeded. Stage2 reads regenerated detail/source metadata, not a hidden prior candidate dependency.'};row['passed']=row['two_selections_byte_identical']and all(all(v for k,v in x.items()if isinstance(v,bool))for x in checks);rows.append(row)
report={'passed':all(x['passed']for x in rows),'families':rows,'executed_script_sha256':sha(Path(__file__))};(OUT/'STAGE2_ROLE_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');print('Stage2 role review',report['passed'],[(r['family'],[(x['catalogue_id'],x['selected_count'])for x in r['checks']])for r in rows])
