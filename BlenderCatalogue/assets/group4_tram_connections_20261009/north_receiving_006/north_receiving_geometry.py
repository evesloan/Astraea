from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';P=F/'boarding_north_005'
IDS=['AST-TRM-G4-021'];cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
def exact_id_check(v):
 if isinstance(v,dict):
  for q in v.values():exact_id_check(q)
 elif isinstance(v,list):
  for q in v:exact_id_check(q)
 elif isinstance(v,str):assert v not in IDS,'Catalogue ID already owned: '+v
exact_id_check(cat)
U={'W':W};exec((P/'glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:(P/Path(p).name).read_bytes() if 'AST-TRM-G4-020' in p else base(p)
station=dict(U['triangles']('AST-TRM-G4-020_foremid_north_candidate.glb'))
C={};exec((F/'receiving_module_003/source_contact_math.py').read_text(),C)
regions=json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions']+json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions']
def owners(rect):
 a,c,b,d=rect;rows=[]
 for q in regions:
  if q.get('floor_y')!=52.5:continue
  ar=0
  for t in q['triangles']:
   poly=[list(p) for p in t]
   for ax,v,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=C['clip'](poly,ax,v,gt) if poly else []
   ar+=C['area'](poly)
  if ar>1e-7:rows.append({'owner':q['id'],'area_m2':ar,'floor_y':q['floor_y'],'thickness':q['thickness']})
 return rows
recipes=[];joints=[];receiving=[]
def bx(n,c,size,role,mat='champagne_metal',current_owner=None,station_receiver=None):
 c=np.array(c,dtype=float);ds=np.array(size)/2;v=np.array([c+ds*np.array(u) for u in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]);fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];t=np.array([v[[a,b,c]] for a,b,c,d in fs]+[v[[a,c,d]] for a,b,c,d in fs]);q={'name':n,'center':c.tolist(),'size':list(size),'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist(),'triangles':t,'role':role,'material':mat,'current_owner':current_owner,'station_receiver':station_receiver,'policy':'static_trimesh_candidate'};recipes.append(q);return q
rects=json.loads((P/'NORTH_STATION_LOCAL_SCREEN.json').read_text())['proposed_missing_only_floor_rectangles_xz']
for i,(a,c,b,d) in enumerate(rects):
 assert not owners([a,c,b,d]),(i,owners([a,c,b,d]));bx('N006_MissingOnlyFloor_'+str(i),[(a+b)/2,52.38,(c+d)/2],[b-a,.24,d-c],'new missing-only floor; no current floor cut or duplicated surface','warm_stone')
# All beams stay beneath D09 walking-floor top. Named receiver pads overlap the retained slab underside.
for i,z in enumerate([-264.6,-258.8,-251.,-245.,-239.,-233.,-227.,-222.]):
 owner='D09_fore_midship_public_core_floor' if z<-252 else 'D09_fore_route';x=-7.45 if z<-252 else -3.7;right=x+.3
 if i==7:
  beam=bx('N006_AnnexRingWing_7_R',[-6.2,52.2,z],[5.6,.2,.44],'right pit-ring wing; exact opening remains clear')
  leftwing=bx('N006_AnnexRingWing_7_L',[-13.5,52.2,z],[.2,.2,.44],'left pit-ring wing; exact opening remains clear')
  joints.extend([[beam['name'],'N006_LiftPitUnderbearer_1'],[leftwing['name'],'N006_LiftPitUnderbearer_1']])
 elif i<2:
  beam=bx('N006_AnnexUnderfloorTransfer_'+str(i),[-10.75,52.2,z],[5.7,.2,.44],'outside retained below-floor core wall; capacity not accepted')
  strap=bx('N006_CoreWallOvercrestStrap_'+str(i),[-7.625,52.29,z],[.85,.04,.44],'thin receiving strap inside floor depth above retained core wall top; no wall cut')
  joints.append([beam['name'],strap['name']])
 else:
  beam=bx('N006_AnnexUnderfloorTransfer_'+str(i),[(-13.6+right)/2,52.2,z],[right+13.6,.2,.44],'underfloor transverse receiving; capacity not accepted')
 pad=bx('N006_CurrentSlabReceiver_'+str(i),[x,52.27,z],[.44,.08,.64],'positive named current slab underside receiver',current_owner=owner)
 rect=[x-.22,z-.32,x+.22,z+.32];o=owners(rect);assert len(o)==1 and o[0]['owner']==owner and abs(o[0]['area_m2']-.2816)<1e-6,(rect,o);receiving.append({'mesh':pad['name'],'current_owner':owner,'rect_xz':rect,'full_area_m2':.2816,'contacts':o});joints.append([(strap if i<2 else beam)['name'],pad['name']])
# Four stair/return rows: source deck undersides are unchanged and explicitly named.
for i,(z,underside,target) in enumerate([(-264.5,54.05,'N005_V2__Emergency_MidLanding'),(-258.8,55.85,'N005_V2__Emergency_UpperLanding'),(-255.4,55.85,'N005_V2__Emergency_TopApproach'),(-252.,55.85,'N005_StairUpperReturn')]):
 beam=bx('N006_StairCrossbearer_'+str(i),[-10.74,underside-.09,z],[5.56,.22,.40],'positive retained stair/return underside receiver',station_receiver=target)
 for j,x in enumerate([-13.43,-8.1]):
  foot=bx('N006_StairFloorFoot_'+str(i)+'_'+str(j),[x,52.53,z],[.30,.10,.40],'positive new missing-only floor receiver','champagne_metal')
  post=bx('N006_StairPier_'+str(i)+'_'+str(j),[x,(52.56+underside-.10)/2,z],[.14,underside-.10-52.56,.20],'stair support outside lower axial route','ivory_enamel')
  shoe=bx('N006_StairHeadShoe_'+str(i)+'_'+str(j),[x,underside-.10,z],[.28,.12,.40],'positive pier/crossbearer joint')
  joints.extend([[foot['name'],post['name']],[post['name'],shoe['name']],[shoe['name'],beam['name']]])
# Two below-pan beams carry the retained, uncut pit proposal from retained route slab. They do not fill its void.
for i,z in enumerate([-224.6,-221.8]):
 beam=bx('N006_LiftPitUnderbearer_'+str(i),[-8.495,52.14,z],[10.19,.16,.44],'positive source pit-pan underside receiver',station_receiver='N005_V2__BoardingLift_PitPan')
 pad=bx('N006_LiftPitCurrentSlabReceiver_'+str(i),[-3.7,52.23,z],[.44,.14,.64],'pit beam received by actual D09_fore_route slab underside',current_owner='D09_fore_route')
 o=owners([-3.92,z-.32,-3.48,z+.32]);assert len(o)==1 and o[0]['owner']=='D09_fore_route' and abs(o[0]['area_m2']-.2816)<1e-6;receiving.append({'mesh':pad['name'],'current_owner':'D09_fore_route','rect_xz':[-3.92,z-.32,-3.48,z+.32],'full_area_m2':.2816,'contacts':o});joints.append([beam['name'],pad['name']])
# Accessible lift landing row stays ahead of the pit opening; no cabin/controller supplied.
z=-227.;underside=55.85;beam=bx('N006_LiftLandingCrossbearer',[-11.2,55.76,z],[4.50,.22,.4],'positive retained lift-landing underside receiver',station_receiver='N005_V2__BoardingLift_UpperLanding')
for j,x in enumerate([-13.43,-8.97]):
 foot=bx('N006_LiftLandingFloorFoot_'+str(j),[x,52.53,z],[.30,.10,.40],'positive new missing-only floor receiver')
 post=bx('N006_LiftLandingPier_'+str(j),[x,(52.56+55.75)/2,z],[.14,55.75-52.56,.20],'lift landing support outside cabin/pit opening','ivory_enamel')
 shoe=bx('N006_LiftLandingHeadShoe_'+str(j),[x,55.75,z],[.28,.12,.40],'positive lift landing pier/crossbearer joint')
 joints.extend([[foot['name'],post['name']],[post['name'],shoe['name']],[shoe['name'],beam['name']]])
# Receiver tongue bridges the exact lower-front floor-to-procedural-sill gap without changing the pit floor aperture.
threshold=bx('N006_LowerLiftThresholdTongue',[-11.2,52.4455,-225.15],[2.4,.111,.14],'fixed threshold hardware, 1mm top step; positive new-floor and existing fixed-sill bearings','ivory_enamel')
joints.append([threshold['name'],'N006_MissingOnlyFloor_1'])
plan={'schema':'astraea.group4.north_receiving.v1','source_only':True,'whole_group_complete':False,'catalogue_id':'AST-TRM-G4-021','station_identity':'FORE_MIDSHIP','master_catchment_z':-216,'unadopted_physical_boarding_z':-241,'runtime_changed':False,'proposed_new_floor_owner':'ROOT_FOREMID_NORTH_ANNEX_PROPOSAL','floor_y':52.5,'floor_thickness_m':.24,'missing_only_floor_rectangles_xz':rects,'new_floor_area_m2':sum((b-a)*(d-c) for a,c,b,d in rects),'excluded_current_core_floor_area_m2':51.3,'retained_uncut_lift_recess_xz':[-13.4,-225.2,-9,-221.2],'retained_uncut_lift_recess_area_m2':17.6,'lower_threshold_binding':{'mesh':'N006_LowerLiftThresholdTongue','top_y':52.501,'station_floor_front_z':-225.2,'existing_commons_fixed_sill_z_interval':[-225.10,-225.01],'tongue_z_interval':[-225.22,-225.08],'new_floor_overlap_m':.02,'existing_fixed_sill_overlap_m':.02,'floor_aperture_region_changed':False,'fixture_crosses_front_aperture_border':True},'current_slab_receivers':receiving,'internal_joint_pairs':joints,'member_count':len(recipes),'parts':[{k:v for k,v in q.items() if k!='triangles'} for q in recipes],'open':['Root selects physical stop and installs/binds source proposals. No runtime stop/lift/controller changes here.','Root-owned exact new floor regions and uncut pit; source floor panels require normal receiving before installation.','Named slab contacts are geometric only; primary-hull transfer, structural/mechanical capacity, low-under-stair access protection and live lift/carry remain open.']}
if __name__=='__main__':(W/'NORTH_RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('N006_SOURCE_PLAN',len(recipes),'members, new floor',plan['new_floor_area_m2'],'m2')
