from pathlib import Path
import json,hashlib,numpy as np,struct
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';U={'W':W};exec((F/'receiving_module_003/glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:(S/Path(p).name).read_bytes() if 'AST-TRM-G4-010' in p else base(p)
raw=(S/'AST-TRM-G4-010_fore_midship_source.glb').read_bytes();ln=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+ln]);mats={n['name']:g['materials'][g['meshes'][n['mesh']]['primitives'][0]['material']]['name'] for n in g['nodes'] if 'mesh' in n};old_rows={q['mesh']:q for q in json.loads((S/'MESH_PARTS.json').read_text()) if q['collection']=='FORE_MIDSHIP_STATIC_SOURCE'}
def remap(t,oldlo,oldhi,newlo,newhi):t[:,:,2]=newlo+(t[:,:,2]-oldlo)*(newhi-newlo)/(oldhi-oldlo);return t
recipes=[]
for name,t in U['triangles']('AST-TRM-G4-010_fore_midship_source.glb'):
 if name.startswith('V2_Foremid_OuterPort_'):continue
 role=old_rows[name]['role'];t=t.copy();t[:,:,2]-=25.0;changes=['Z−25m']
 if 'Emergency' in name or 'Upper_Approach' in name:t[:,:,0]-=.15;changes+=['stair/approach X−0.15m, preserving actual core wall']
 if name in ['V2__Boarding_Island_24m','V2__Platform_OuterSoffit','V2__Platform_InnerFascia','V2__Port_Edge_foot','V2__Port_Edge_infill','V2__Port_Edge_rail']:
  lo=float(t[:,:,2].min());hi=float(t[:,:,2].max());t=remap(t,lo,hi,-251.0,hi);changes+=['north-end trim toZ−251']
 elif name in ['V2__Tram_NorthGuard_foot','V2__Tram_NorthGuard_infill','V2__Tram_NorthGuard_rail']:
  lo=float(t[:,:,2].min());hi=float(t[:,:,2].max());t=remap(t,lo,hi,-251.0,hi);changes+=['north guard shortened toZ−251']
 elif name in ['V2__Canopy_Profiled_Crown','V2__Canopy_Recessed_Coral_Band']:
  lo=float(t[:,:,2].min());hi=float(t[:,:,2].max());t=remap(t,lo,hi,-251.05,hi);changes+=['canopy north end shortened toZ−251.05']
 elif name in ['V2__Port_Edge_post_-228','V2__Tram_NorthGuard_post_-228','V2__Station_Canopy_Pier_-226.8','V2__Station_Canopy_Arm_-226.8']:
  t[:,:,2]+=2.;changes+=['north end fitting moved+2m within trimmed deck']
 elif name in ['V2__Quiet_Perch_Base_-225.8','V2__Quiet_Perch_Cushion_-225.8']:
  t[:,:,2]+=.6;changes+=['north perch moved+0.6m within trimmed deck']
 recipes.append({'name':'N005_'+name,'retained_source_mesh':name,'triangles':t,'material':mats[name],'role':role,'changes':changes,'policy':old_rows[name].get('policy','static_trimesh_candidate')})
boxes=[]
def bx(n,c,size,role,mat='champagne_metal',receiver=None):boxes.append({'name':n,'center':c,'size':size,'role':role,'material':mat,'receiver':receiver})
# The staircase is unchanged in shape and lies beside the core, with a new short level return to the trimmed platform.
bx('N005_StairUpperReturn',[-10.65,55.975,-252.0],[5.4,.25,2.0],'2m level return between source-preserved upper stair approach and trimmed platform','warm_stone')
for x in [-13.29,-8.01]:
 bx('N005_ReturnGuardFoot_'+str(x),[x,56.21,-252.0],[.10,.22,2.0],'short return guard base','ivory_enamel')
 bx('N005_ReturnGuardInfill_'+str(x),[x,56.76,-252.0],[.06,.82,2.0],'short return infill','station_guard_preview')
 bx('N005_ReturnGuardRail_'+str(x),[x,57.23,-252.0],[.10,.10,2.0],'short return guard rail','champagne_metal')
# Three new under-wheel-depth crossbearers receive the shifted platform from existing axial D09 slab.
for j,z in enumerate([-249.,-241.,-233.]):
 bx('N005_AxialPad_'+str(j),[-2.4,52.54,z],[.42,.08,.75],'positive current D09_fore_route floor receiver',receiver='D09_fore_route')
 bx('N005_AxialPier_'+str(j),[-2.4,(52.58+55.57)/2,z],[.30,55.57-52.58,.40],'axial pier outside protected lower4m route','ivory_enamel')
 bx('N005_PlatformCantilever_'+str(j),[-7.795,55.63,z],[10.79,.16,.40],'under-wheel-depth cantilever; capacity not accepted')
 bx('N005_PlatformReceivingShoe_'+str(j),[-10.45,55.78,z],[5.5,.18,.40],'positive shifted island underside receiver')
# Box triangulation in game XYZ for the same exact-source screen that will verify exports.
for q in boxes:
 c=np.array(q['center']);ds=np.array(q['size'])/2;v=np.array([c+ds*np.array(u) for u in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]);fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];t=np.array([v[[a,b,c]] for a,b,c,d in fs]+[v[[a,c,d]] for a,b,c,d in fs]);recipes.append({'name':q['name'],'retained_source_mesh':None,'triangles':t,'material':q['material'],'role':q['role'],'changes':['new additive source connector/receiver'],'policy':'static_trimesh_candidate'})
plan={'schema':'astraea.group4.foremid.north_candidate.v1','status':'UNADOPTED_SOURCE_PROPOSAL','catalogue_id':'AST-TRM-G4-020','family':'group4_foremid_north_candidate_005','retained_station_identity':'FORE_MIDSHIP','master_catchment_z':-216,'old_physical_boarding_z':-216,'proposed_physical_boarding_z':-241,'proposed_stop_delta_z_m':-25,'actual_core_z':-272,'proposed_platform_xz':[-13.2,-251,-7.8,-229],'proposed_lift_root_xyz':[-11.2,0,-225],'proposed_lift_yaw_rad':-np.pi/2,'proposed_local_lift_stop_ids':['G4_FORE_MIDSHIP_LOWER','G4_FORE_MIDSHIP_BOARDING'],'floor_heights':[52.5,56.1],'proposed_lift_recess_xz':[-13.4,-225.2,-9,-221.2],'proposed_new_lower_annex_xz':[-13.6,-265.5,-4,-221.2],'stair_change':'Exact frozen2.4m flights, risers, stringers and landings shiftedZ−25/X−0.15;2m upper return added. No existing core geometry changes.','platform_change':'22m island shortened at north end; canopy/fittings coordinated. Source coordinates remain a proposal.','discarded_uninstalled_local_frame':'Old fore-midship axial source frames are omitted from this separate candidate, replaced by three explicitly lower under-wheel-depth cantilevers. Original files remain untouched.','root_binding_changes_required':['Keep master catchment/FORE_MIDSHIP identity while explicitly deciding whether the physical docking target may move−216→−241.','Root route docking, destination arrival/wayfinding, new two-stop lift root and persistent IDs must bind the proposed new coordinates if accepted.','No runtime stop, controller, lift, route point or protected allocation changes are made by this source proposal.'],'root_receiving_open':['New missing-only lower annex/floor and17.6m² wholly new lift recess; retain all actual generic and received floor owners.','Secondary stairs, upper return and lift frame still require physical lower-annex receivers; no capacity or runtime acceptance.'],'member_count':len(recipes),'part_recipes':[ {k:v for k,v in q.items() if k!='triangles'} for q in recipes ],'new_boxes':boxes,'source_only':True,'whole_group_complete':False}
if __name__=='__main__':(W/'NORTH_STATION_PROPOSAL.json').write_text(json.dumps(plan,indent=2)+'\n');print('NORTH_CANDIDATE_PLANNED',len(recipes),'members',plan['old_physical_boarding_z'],'to',plan['proposed_physical_boarding_z'])
