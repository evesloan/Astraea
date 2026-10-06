"""Bounded static stair, acoustic envelope and programme partitions; no behavior."""
import math

def extend(objects,surfaces,box,prism,write,root):
 stair_records=[]
 def flight(name,x0,x1,z0,direction,nr,base,rise):
  run=(nr-1)*.32; top=base+rise
  for i in range(nr-1):
   z1=z0+direction*i*.32;z2=z0+direction*(i+1)*.32
   box(f'{name}_tread_{i+1:02}',[x0,min(z1,z2),x1,max(z1,z2)],base+(i+1)*rise/nr,.25,'stair_flight')
  stair_records.append(dict(id=name,clear_x=[x0,x1],start_z=z0,end_z=z0+direction*run,risers=nr,riser=rise/nr,tread=.32,bottom_y=base,top_y=top,clear_width=x1-x0))
  # Side guards sit OUTSIDE genuine 3.2m tread clear width. Sloping upper/lower edges.
  for x in [x0-.18,x1+.03]:
   zf=z0+direction*run
   objects.append(dict(name=name+'_guard_'+str(x),vertices_world=[[x,base,z0],[x,base+1.2,z0],[x,top+1.2,zf],[x,top,zf]],faces=[[0,2,1],[0,3,2]],role='guard_proposal',collision_owner='AST-CUL-005',material_family='hospitality_bronze'))
  return z0+direction*run,top
 # Four flights; lower pair has4.25m vertical separation from upper pair.
 z=-123.8;y=69.5
 box('D11_stair_start_landing',[-59,-123.8,-50,-122],y,.25,'stair_flight')
 for i,(nr,x0,x1,d) in enumerate([(15,-58.6,-55.4,-1),(14,-53.6,-50.4,1),(15,-58.6,-55.4,-1),(14,-53.6,-50.4,1)]):
  z,y=flight(f'D11_D12_F{i+1}',x0,x1,z,d,nr,y,nr*8.5/58)
  if i<3:
   r=[-59,z-1.8,-50,z] if d<0 else [-59,z,-50,z+1.8]
   box(f'D11_D12_turn_{i+1}',r,y,.25,'stair_flight')
 # Final flight y78 endsz-124.44; extension is flight landing, ends at exact named upper landing.
 box('D12_stair_final_flight_extension',[-53.6,z,-50.4,-123.8],78,.25,'stair_flight')
 # Upper6m rise uses four spatially distinct straight flights, avoids low stacked3m headroom.
 z=-140.72;y=78
 box('D12_stair_start_landing',[-59,z-1.8,-55.4,z],78,.25,'stair_flight')
 for i in range(4):
  z,y=flight(f'D12_D13_F{i+1}',-58.6,-55.4,z,1,10,y,1.5)
  if i<3:
   box(f'D12_D13_turn_{i+1}',[-58.6,z,-55.4,z+1.8],y,.25,'stair_flight');z+=1.8
 assert abs(z+123.8)<1e-7 and abs(y-84)<1e-7
 write(root/'contracts/stair_source_contract.json',dict(flights=stair_records,landing_owner='AST-CUL-005 stair-flight assembly except exact eight-manifest upper landing planes',D11_D12_minimum_stacked_underside_clearance=4.0,D12_D13='Four sequential flights, no3m stacked ceiling pinch',guard_height_intent=1.2,guard_certification=False,headroom_scope='Stepwise lower pair to upper pair, shaft/roof clearance; species/live capsule/cart gate remains open'))
 # West acoustic liner remains wholly inward of pressure-wall0.8 normal reservation.
 box('west_acoustic_vertical_boundary',[-117.65,-263,-117.4,-116],87,17.5,'static_structure','cultural_red')
 slope=8.9/4.5
 objects.append(dict(name='west_acoustic_tapered_return',vertices_world=[[-117.65,87,-263],[-117.65,87,-116],[-117.65+slope*4.5,91.5,-116],[-117.65+slope*4.5,91.5,-263]],faces=[[0,1,2],[0,2,3]],role='acoustic_boundary_not_pressure_hull',collision_owner='AST-CUL-005',material_family='cultural_red'))
 # East acoustic boundary split around six true doorway apertures, not decorative door dots.
 openings=[]
 for y in [69.5,78,84]:
  openings += [(-128.6,-123.4,y,y+3.4),(-172.7,-169.3,y,y+3.4)]
 zs=sorted(set([-263,-116]+[q for a,b,y,t in openings for q in [a,b]]));ys=sorted(set([69.5,91.5]+[q for a,b,y,t in openings for q in [y,t]]))
 for iz,(a,b) in enumerate(zip(zs,zs[1:])):
  for iy,(lo,hi) in enumerate(zip(ys,ys[1:])):
   if any(oa<(a+b)/2<ob and oy<(lo+hi)/2<ot for oa,ob,oy,ot in openings):continue
   box(f'east_acoustic_wall_{iz}_{iy}',[-34.75,a,-34.5,b],hi,hi-lo,'static_structure','cultural_red')
 for deck,y in [('D11',69.5),('D12',78),('D13',84)]:
  for side,z0,z1 in [('fore',-128.85,-128.6),('aft',-123.4,-123.15)]:
   box(f'{deck}_vestibule_{side}_return',[-38.4,z0,-34.5,z1],y+3.4,3.4,'static_structure','hospitality_bronze')
  box(f'{deck}_vestibule_acoustic_cap',[-38.4,-128.85,-34.5,-123.15],y+3.65,.25,'static_structure','hospitality_ivory')
 # Fitted shaft enclosure; hole stays empty. Cabin/gate/pit/headroom behavior NOT authored.
 for n,r in [('west',[-44.5,-124,-44.25,-118]),('east',[-38.75,-124,-38.5,-118]),('rear',[-44.25,-118.25,-38.75,-118])]:
  box('lift_shaft_'+n,r,87.65,18.15,'static_structure','hospitality_bronze')
 for side,r in [('port',[-44.5,-124,-43.2,-123.75]),('starboard',[-39.8,-124,-38.5,-123.75])]:
  box('lift_gate_pocket_'+side,r,87.65,18.15,'static_structure','hospitality_bronze')
 for d,y in [('D11',69.5),('D12',78),('D13',84)]:
  box(d+'_lift_gate_head',[-43.2,-124,-39.8,-123.75],y+3.65,.25,'static_structure','hospitality_bronze')
 # Backstage corridor clearz[-258.7,-255.3], bounded service programme bays behind it.
 box('backstage_fore_acoustic_wall',[-116,-263,-36,-262.75],74.3,4.8,'static_structure','suncorp_service')
 for i,x in enumerate([-96,-76,-56]):
  box(f'backstage_service_bay_partition_{i}',[x,-262.75,x+.25,-258.7],74.3,4.8,'static_structure','suncorp_service')
 # Front bay wall split with four3.4m acoustic clear openings; source functional subdivision, not canonical room-count addition.
 doors=[(-112,-108.6),(-92,-88.6),(-72,-68.6),(-52,-48.6)]
 xs=sorted(set([-116,-36]+[q for a,b in doors for q in [a,b]]))
 for i,(a,b) in enumerate(zip(xs,xs[1:])):
  if any(da<(a+b)/2<db for da,db in doors):
   box(f'backstage_bay_door_head_{i}',[a,-258.95,b,-258.7],74.3,1.4,'static_structure','suncorp_service')
  else:box(f'backstage_bay_front_{i}',[a,-258.95,b,-258.7],74.3,4.8,'static_structure','suncorp_service')
 # Two orchestra/support wings with acoustic walls and real3.4m door apertures at rear. No depressed pit.
 for name,x0,x1 in [('port',-112,-96),('starboard',-56,-40)]:
  for side,x in [('outer',x0-.25),('inner',x1)]:
   if name=='starboard' and side=='outer':
    for label,a,b in [('fore',-250,-249.4),('aft',-246,-230)]:box('orchestra_'+name+'_'+side+'_'+label,[x,a,x+.25,b],74.3,4.8,'static_structure','cultural_red')
    box('orchestra_stage_acoustic_aperture_head',[x,-249.4,x+.25,-246],74.3,.8,'static_structure','cultural_red')
   else:box('orchestra_'+name+'_'+side,[x,-250,x+.25,-230],74.3,4.8,'static_structure','cultural_red')
  box('orchestra_'+name+'_audience_screen',[x0,-230,x1,-229.75],74.3,4.8,'static_structure','cultural_red')
  mid=(x0+x1)/2
  for part,a,b in [('left',x0,mid-1.7),('right',mid+1.7,x1)]:
   box('orchestra_'+name+'_rear_'+part,[a,-250.25,b,-250],74.3,4.8,'static_structure','cultural_red')
  box('orchestra_'+name+'_rear_head',[mid-1.7,-250.25,mid+1.7,-250],74.3,1.4,'static_structure','cultural_red')
 write(root/'contracts/backstage_source_contract.json',dict(crossroute_rectangle=[-116,-258.7,-36,-255.3],clear_height=4.8,clear_width=3.4,bays='Flexible dressing/rehearsal/scenery/work/storage allocation with four bounded source compartments; no new authoritative programme IDs',orchestra='Two flanking support rooms,16x20 nominal; no pit',staff_portal='East connector to riser2 remains parent territory',service_floor='Single D11 compiler floor, not duplicated here'))
