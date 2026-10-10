from pathlib import Path
import json,hashlib,numpy as np,math
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';P=F/'boarding_north_005';Q=F/'north_receiving_006';IDS=['AST-TRM-G4-022']
def check_id(v):
 if isinstance(v,dict):
  for x in v.values():check_id(x)
 elif isinstance(v,list):
  for x in v:check_id(x)
 elif isinstance(v,str):assert v not in IDS,'ID already owned: '+v
check_id(json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text()))
U={'W':W};exec((P/'glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:((P if 'AST-TRM-G4-020' in p else Q)/Path(p).name).read_bytes() if 'AST-TRM-G4-020' in p or 'AST-TRM-G4-021' in p else base(p)
station=dict(U['triangles']('AST-TRM-G4-020_foremid_north_candidate.glb'));receiving=dict(U['triangles']('AST-TRM-G4-021_north_missing_only_receiving.glb'))
recipes=[];joints=[];posts=set()
def shape(n,v,role,mat='ivory_enamel',allowed=()):
 v=np.array(v,float);fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];t=np.array([v[[a,b,c]] for a,b,c,d in fs]+[v[[a,c,d]] for a,b,c,d in fs]);q={'name':n,'vertices':v.tolist(),'triangles':t,'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist(),'role':role,'material':mat,'allowed_retained_receiver_meshes':list(allowed),'policy':'static_trimesh_candidate'};recipes.append(q);return q
# Closed prism, top varying along Z; bottom extends20mm into new floor as a source receiving connection.
def wedge(n,x0,x1,z0,z1,y0,y1,role,allowed=()):
 return shape(n,[(x0,52.48,z0),(x1,52.48,z0),(x1,y0,z0),(x0,y0,z0),(x0,52.48,z1),(x1,52.48,z1),(x1,y1,z1),(x0,y1,z1)],role,allowed=allowed)
def bx(n,c,size,role,mat='ivory_enamel',allowed=()):
 c=np.array(c);d=np.array(size)/2;v=[c+d*np.array(a) for a in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return shape(n,v,role,mat,allowed)
# Receiver contacts are explicit, with existing stairs/crossbearers preserved unchanged.
f0=['N005_V2__Emergency_Profiled_Stringer0'];f1=['N005_V2__Emergency_Profiled_Stringer1'];mid=['N005_V2__Emergency_MidLanding','N006_StairFloorFoot_0_0','N006_StairFloorFoot_0_1','N006_StairHeadShoe_0_0','N006_StairHeadShoe_0_1','N006_StairCrossbearer_0']
f0top=lambda z:52.25+(-260-z)*(1.77/3.6)+.005;f1top=lambda z:54.05+(z+263.6)*(1.77/3.6)+.005
for label,x0,x1 in [('Outer',-13.21,-13.13),('Inner',-10.87,-10.79)]:wedge('N007_Flight0_'+label+'Skirt',x0,x1,-263.6,-260.55,f0top(-263.6),f0top(-260.55),'closed low-headroom flight0 skirt',f0)
wedge('N007_Flight0_ToeSeal',-13.2,-10.8,-260.63,-260.55,f0top(-260.63),f0top(-260.55),'low toe seal; outside first-tread approach',f0)
for label,x0,x1 in [('Outer',-10.52,-10.44),('Inner',-8.14,-8.08)]:wedge('N007_Flight1_'+label+'Skirt',x0,x1,-263.6,-260,f1top(-263.6),f1top(-260),'closed flight1 underside pocket',f1)
wedge('N007_Flight1_FrontSeal',-10.5,-8.1,-260.08,-260,f1top(-260.08),f1top(-260),'closed high front of unused flight1 pocket',f1+['N005_V2__Emergency_UpperLanding'])
for label,x0,x1 in [('Outer',-13.36,-13.28),('Inner',-8.02,-7.96)]:wedge('N007_MidLanding_'+label+'Skirt',x0,x1,-265.36,-263.6,54.06,54.06,'closed1.55m-underlanding pocket; existing piers stay inside',mid)
wedge('N007_MidLanding_RearSeal',-13.36,-7.96,-265.36,-265.28,54.06,54.06,'rear closure of low half-landing pocket',mid)
wedge('N007_MidLanding_FrontSeal',-13.36,-7.96,-263.6,-263.52,54.06,54.06,'front closure joins switchback skirts',mid+f0+f1)
bx('N007_InterflightNarrowGapSeal',[-10.575,53.09,-260.04],[.11,1.22,.08],'fixed closure of otherwise inaccessible0.3m interflight dead-end')
# Lower exposed edges only; current core/route floor seams and lift front stay open.
# Each post is authored once even where two guard runs meet.
def guard(n,a,b,allowed=()):
 axis=0 if abs(a[0]-b[0])>1e-6 else 2;length=abs(b[axis//2]-a[axis//2]);center=[(a[0]+b[0])/2,0,(a[1]+b[1])/2];size=[.08,.18,.08];size[axis]=length;center[1]=52.57;foot=bx(n+'_Base',center,size,'exposed new-floor edge guard base','ivory_enamel',allowed)
 size=[.04,.96,.04];size[axis]=length;center[1]=53.16;infill=bx(n+'_Infill',center,size,'continuous source guard infill','station_guard_preview',allowed)
 size=[.08,.10,.08];size[axis]=length;center[1]=53.70;rail=bx(n+'_Rail',center,size,'1.25m source outer-edge guard top','champagne_metal',allowed)
 count=max(1,math.ceil(length/2.8))
 for j in range(count+1):
  t=j/count;x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;key=(round(x,6),round(z,6))
  if key in posts:continue
  posts.add(key);bx(n+'_Post_'+str(j),[x,53.115,z],[.08,1.27,.08],'edge guard post received20mm into source floor','champagne_metal',allowed)
# Only low existing receiver feet may meet the new outside guard at its base.
westfeet=['N006_StairFloorFoot_'+str(i)+'_0' for i in range(4)]+['N006_LiftLandingFloorFoot_0']
guard('N007_WestEdge',(-13.56,-265.46),(-13.56,-221.24),westfeet)
guard('N007_ForeEdge',(-13.56,-265.46),(-7.94,-265.46))
bx('N007_ForeEdgeToCoreWallSeal',[-7.89,53.115,-265.46],[.02,1.27,.08],'nominal face seal against retained core wall; no wall cut')
guard('N007_SouthLeftRing',(-13.56,-221.24),(-13.44,-221.24))
guard('N007_SouthRightEdge',(-8.96,-221.24),(-4.04,-221.24))
plan={'schema':'astraea.group4.north_access_protection.v1','source_only':True,'whole_group_complete':False,'runtime_changed':False,'catalogue_id':'AST-TRM-G4-022','station_identity':'FORE_MIDSHIP','master_catchment_z':-216,'unadopted_physical_boarding_z':-241,'member_count':len(recipes),'scope':'Fixed switchback/half-landing structural skirting and lower exposed floor-edge guards only. No service-room allocation, door, contents or new control.','source_floor_owner':'ROOT_FOREMID_NORTH_ANNEX_PROPOSAL uninstalled006','guard_top_y':53.75,'guard_height_above_floor_m':1.25,'maximum_post_spacing_m':2.8,'low_pockets_closed':['Flight0 underside below the preserved inclined stringer','Flight1 unused underside pocket','1.55m underside of the switchback half-landing','0.3m interflight narrow dead-end front'],'preserved_open_interfaces':['Retained core-floor structural adjacency at X−7.8/Z−265.5..−252; west wall remains closed, no walk-through opening','Current axial route seam atX−4/Z−252..−221.2','North lift front entrance and threshold','All original stair tread and landing tops','Original station/receiver/lift/bridge sources and unadopted physical-stop identities'],'parts':[{k:v for k,v in q.items() if k not in ['triangles','vertices']} for q in recipes],'open':['Normal-world/root collision and receiving, whole-species movement and exact stop/lift/controller adoption.','Capacity and primary-hull load transfer, emergency/service arrangements, all other stations and destination links.']}
plan['retained_core_transfer_caveat']={'retained_core_west_wall_x': [-7.88, -7.72], 'retained_core_west_wall_z': [-285, -252], 'below_floor_wall_y': [44, 52.26], 'above_floor_wall_y': [52.5, 60.76], 'through_wall_opening_proposed': False, 'route_interface': 'Use the existing axial approach around the retained core wall south of Z−252, joining the unguarded X−4 route-floor seam. The structural floor adjacency is not a proposed walk-through portal.', 'root_gate': 'Root adopts or rejects physical docking −241 and binds arrival/wayfinding through the existing axial approach; source-only geometry does not adopt the stop.'}
if __name__=='__main__':(W/'NORTH_ACCESS_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('N007_ACCESS_PLAN',len(recipes),'members')
