"""Twenty external clinical collars from exact retained clean/soiled terminals."""
from pathlib import Path
import json,hashlib,sys,math
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2];GAME=ROOT/'Game'
path=GAME/'data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json'
plan=json.loads(path.read_text());parts=[];fixtures=[];joins=[];footprints=[]
parents={q['programme_key']:box(q['envelope']['x'][0],q['envelope']['z'][0],q['envelope']['x'][1],q['envelope']['z'][1])for q in plan['programmes']}
def cube(name,b,role='staff_white_paint',category='clinical_collar'):
    parts.append({'name':name,'aabb':b,'role':role,'category':category,'batch_cell':f'{math.floor(b[0]/8)}_{math.floor(b[4]/8)}'})
for terminal in plan['terminal_interfaces']:
    parent=terminal['programme_key']
    for door in terminal['rear_doors']:
        role=door['role'];x,z=door['origin_xz'];side=-1 if x<0 else 1
        # All new solids remain outside the parent. The original rear panel is retained.
        a,b=sorted([x,x+side*3.6]);prefix=parent+'_'+role
        cube(prefix+'_ForePanel',[a,b,21,25.2,z-1.94,z-1.8])
        cube(prefix+'_AftPanel',[a,b,21,25.2,z+1.8,z+1.94])
        cube(prefix+'_Roof',[a,b,25.2,25.34,z-1.94,z+1.94],'staff_bluegrey_paint','overhead')
        # Source frame meets the real reserved programme plane without entering it.
        c,d=sorted([x,x+side*.16])
        cube(prefix+'_ReceiverLintel',[c,d,23.4,25.2,z-1.8,z+1.8])
        cube(prefix+'_ProtectedBumperFore',[a,b,21.7,21.82,z-1.8,z-1.74],'staff_rubber','clinical_utility')
        cube(prefix+'_ProtectedBumperAft',[a,b,21.7,21.82,z+1.74,z+1.8],'staff_rubber','clinical_utility')
        lx=(a+b)/2
        cube(prefix+'_LightHousing',[lx-.4,lx+.4,25.04,25.2,z-.15,z+.15],'staff_zinc','lighting_fixture')
        cube(prefix+'_LightDiffuser',[lx-.35,lx+.35,25.015,25.04,z-.11,z+.11],'staff_opal','lighting_fixture')
        cube(prefix+'_ControlBacking',[c,d,22.05,22.42,z+1.82,z+1.94],'staff_zinc','control_fixture')
        fixtures.append({'name':prefix+'_TaskLight','position':[lx,24.995,z],'color':[.8,.9,1],'range_m':5,'energy':.8,'budget_owner':'existing receiving_source_lights.gd / lighting_budget.gd'})
        footprints.append(box(a,z-1.94,b,z+1.94))
        joins.append({'programme_key':parent,'role':role,'source_origin':[x,21,z],'clear_aperture_m':door['clear_aperture_m'],'external_collar_rect':[a,b,z-1.94,z+1.94],'retained_receiver_panel_modified':False,'door_motion_and_turn_reservation':door,'controlled_crossing_dependency':terminal['controlled_crossing'] if role=='soiled' else None,'hold':'Actual retained receiver panel and source interior must be surveyed and reversibly opened by root after floor adoption. Gate operation is not installed.'})
requested=unary_union(footprints)
compiled=json.loads((GAME/'data/generated/structural_meshes.json').read_text())
old=unary_union([Polygon(t)for r in compiled['regions']if r['deck']=='D05'for t in r['triangles']])
missing=requested.difference(old)
floor={'deck':'D05','floor_y':21,'thickness':.24,'missing_only_area_m2':missing.area,'polygons':[{'boundary':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in shapely.get_parts(missing)if p.geom_type=='Polygon'and p.area>1e-7],'no_exported_floor':True,'existing_floor_retained_m2':requested.intersection(old).area}
body=json.loads((GAME/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text());inner=Polygon(next(q for q in body['levels']if q['deck']=='D05')['inner_reservation_boundary'])
overlaps=[]
for q in joins:
    a,b,c,d=q['external_collar_rect'];overlaps.append({'programme_key':q['programme_key'],'role':q['role'],'own_parent_intrusion_m2':box(a,c,b,d).intersection(parents[q['programme_key']]).area,'other_parent_intrusion_m2':sum(box(a,c,b,d).intersection(p).area for k,p in parents.items()if k!=q['programme_key'])})
spec={'schema':1,'catalogue_id':'AST-MED-G3-001','family':'group3_crew_service_20261009','coordinate_system':'Godot world metres, external D05 clinical terminals','parts':parts,'fixtures':fixtures,'terminal_interfaces':joins,'floor_proposal':floor,'source_plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_floor_sha256':hashlib.sha256((GAME/'data/generated/structural_meshes.json').read_bytes()).hexdigest(),'gate_controller_policy':'Use existing room/door mechanism only. No new interlock/controller is created by this source batch.','clinical_or_sterile_flow_certified':False,'population_beds_added':0,'unfinished':['Root actual retained rear-source receiver and floor adoption','Clean/soiled streets and staff riser links','Mutually exclusive controlled-crossing gates and signals','Real linen/supply and soiled-return hardware integration','Clinical acoustics, body/cart, operation and final visuals']}
(HERE/'source/CLINICAL_TERMINALS.json').write_text(json.dumps(spec,indent=2)+'\n')
report={'status':'PASS'if len(joins)==20 and all(q['own_parent_intrusion_m2']<1e-7 and q['other_parent_intrusion_m2']<1e-7 for q in overlaps)and requested.difference(inner).area<1e-7 and missing.intersection(old).area<1e-7 else'FAIL','terminal_collars':len(joins),'source_parts':len(parts),'plan_overlap_checks':overlaps,'outside_conservative_D05_inner_hull_m2':requested.difference(inner).area,'duplicate_floor_area_m2':missing.intersection(old).area,'floor_proposal_area_m2':missing.area,'all_current_sources_preserved':True,'scope':'External source collar geometry and missing-only floor proposal; no actual receiver opening or gate/sterile-flow acceptance.'}
(HERE/'qa/CLINICAL_TERMINAL_PLAN_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['status']=='PASS'
