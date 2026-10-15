from pathlib import Path
import json,hashlib
def rectangle_union(rects):
 xs=sorted({v for r in rects for v in r[:2]});zs=sorted({v for r in rects for v in r[2:]});edges=set();area=0
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(zs,zs[1:]):
   if not any(x0<=(a+b)/2<=x1 and z0<=(c+d)/2<=z1 for x0,x1,z0,z1 in rects):continue
   area+=(b-a)*(d-c);ring=[(a,c),(b,c),(b,d),(a,d)]
   for e,f in zip(ring,ring[1:]+ring[:1]):
    if (f,e)in edges:edges.remove((f,e))
    else:edges.add((e,f))
 outgoing={a:b for a,b in edges};assert len(outgoing)==len(edges);start=min(outgoing);ring=[start];nextpoint=outgoing[start]
 while nextpoint!=start:ring.append(nextpoint);nextpoint=outgoing[nextpoint]
 assert len(ring)==len(edges)
 simple=[]
 for i,b in enumerate(ring):
  a=ring[i-1];c=ring[(i+1)%len(ring)]
  if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))>1e-8:simple.append(list(b))
 return simple,area
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sites=[]
for key,side,clean,used,join,top in [('01',-1,-457,-417,-470,68.75),('02',1,-457,-417,-470,68.97000050544739),('03',-1,-241,-201,-176,68.75)]:
 lo=min(join,clean-5);hi=max(join,used+5);rects=[[54,66,clean-5,clean+7],[54,66,used-7,used+5],[66,70,lo-2.15,hi+2.15],[4,70,join-2.15,join+2.15]];rects=[[min(side*a,side*b),max(side*a,side*b),c,d]for a,b,c,d in rects];outline,area=rectangle_union(rects);sites.append({'key':'D10_directory_'+key,'unit':key,'side':side,'clean_z':clean,'used_z':used,'axial_join_z':join,'old_wall_top_y':top,'floor_rectangles':rects,'floor_outline_xz':outline,'floor_area_m2':area})
pins={str(p.relative_to(G)):sha(p)for p in [G/'assets/models'/f'SOL_D10_directory_{key}_remaining_batch.glb'for key in ['01','02','03']]}
for name in ['data/generated/structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json','data/architecture/group8/dining_service.json','data/architecture/group8/orchard_service.json','scripts/player.gd','scripts/service_door.gd','scripts/lower_staff_network.gd','assets/models/G8_ORCHARD_SERVICE_r004.glb']:pins[name]=sha(G/name)
plan={'sites':sites,'source_pins':pins,'floor_y':61,'ceiling_underside_y':64.8,'ceiling_top_y':64.98,'underframe_min_y':60.54,'minimum_route_clear_m':3.4,'source_native':'BlenderCatalogue/assets/group8_orchard_service_20261011/OrchardService_r003.blend','source_native_sha256':sha(R/'BlenderCatalogue/assets/group8_orchard_service_20261011/OrchardService_r003.blend'),'new_floor_area_m2':sum(s['floor_area_m2']for s in sites),'new_floor_room_ids_or_capacity':0,'primary_engineering_food_water_stock_species_save_or_final_art_accepted':False,'master_requirement':'D01 provisions/synthesis andD10 finishing galleys;distinguishable food andused returns,reachable service approach;functional fiction withabstract processing. Retained D10 axial route is the receiving landing;no staff-lift stop orpublic-core opening changed.'};(D/'NATIVE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PLAN',[(s['key'],s['floor_area_m2'])for s in sites])
