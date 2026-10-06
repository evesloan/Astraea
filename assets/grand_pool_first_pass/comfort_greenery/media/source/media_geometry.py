"""Pure, original LIB-010-derived editable construction recipes. No bpy or writes.
All part coordinates are display-local (u right, v up, n toward viewer), metres.
Profiles retain the rounded shell/frame/gasket and swept bearing construction of
library_use/source/build_library_use.py; dimensions are re-authored per interface.
"""
import math

LINEAGE={
 'shell':'TERM_shaped_back_shell','frame':'TERM_walnut_display_frame',
 'gasket':'TERM_recessed_inner_gasket','glazing':'TERM_recessed_display_glazing',
 'foot':'TERM_L_sculpted_foot','pad':'TERM_L_floor_pad',
 'spine':'TERM_L_swept_load_spine','bridge':'TERM_rear_service_bridge',
 'service':'TERM_rear_fixed_service_case','fastener':'TERM_service_fastener_-0.17',
 'bearing':'TERM_display_lower_bearing',
 'image':'TERM_original_catalogue_display (plane/UV vocabulary only; original artwork replaced)',
}

def rounded(w,h,r,center=(0,0),segments=4):
 assert 0<r<min(w,h)/2
 out=[]
 for x,y,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(segments):
   t=math.radians(a+90*j/(segments-1));out.append((center[0]+x+r*math.cos(t),center[1]+y+r*math.sin(t)))
 return out

def extrude(profile,lo,hi,axis=2):
 n=len(profile)
 def v(a,b,t):
  return (a,b,t) if axis==2 else ((t,a,b) if axis==0 else (a,t,b))
 vs=[v(a,b,t)for t in [lo,hi] for a,b in profile]
 fs=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
 return vs,fs

def ring(outer,inner,lo,hi):
 n=len(outer);assert n==len(inner)
 vs=[(x,y,z)for z in [lo,hi]for arr in [outer,inner]for x,y in arr];fs=[]
 for i in range(n):
  j=(i+1)%n;fs += [[i,j,n+j,n+i],[2*n+i,3*n+i,3*n+j,2*n+j],[i,2*n+i,2*n+j,j],[n+i,n+j,3*n+j,3*n+i]]
 return vs,fs

def addpart(parts,name,geometry,role,lineage,join_to=(),kind='solid',grain_axis=0,contact=None):
 vs,fs=geometry
 p={'name':name,'vertices_local_uvn_m':[list(x)for x in vs],'faces':[list(f)for f in fs],
    'material_role':role,'lineage_object':LINEAGE[lineage],'parent_design_id':'AST-LIB-010',
    'family':'library_use','kind':kind,'grain_axis':grain_axis,'joins':list(join_to)}
 if contact:p['contact']=contact
 parts.append(p);return name

def box(lo,hi):
 return extrude([(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],lo[2],hi[2])

def recipes(c,wall_back_planes=None,floor_y=None):
 """Planes must have been measured from retained AST-AQU-016 triangles."""
 rect=c['image_rect'];iw=rect[1]-rect[0];ih=rect[3]-rect[2]
 wall=c['axis']=='z';w=c['bounds'][1][0]-c['bounds'][0][0] if wall else 2.16
 h=c['bounds'][1][1]-c['bounds'][0][1] if wall else 1.46
 parts=[];R=lambda ww,hh,r:rounded(ww,hh,r)
 front=.020 if wall else -.001
 # Closed rear shell with small stepped shoulders, never a floating image card.
 addpart(parts,'shaped_closed_back_shell',extrude(R(w-.010,h-.010,.071),-.125,-.028),'ivory_enamel','shell')
 addpart(parts,'walnut_display_frame',ring(R(w,h,.077),R(iw+.032,ih+.032,.019),-.033,front),'warm_walnut','frame',['shaped_closed_back_shell'])
 addpart(parts,'recessed_inner_gasket',ring(R(iw+.038,ih+.038,.019),R(iw+.014,ih+.014,.012),-.026,-.0007),'dark_rubber','gasket',['walnut_display_frame'])
 addpart(parts,'recessed_display_glazing',extrude(R(iw+.016,ih+.016,.011),-.009,-.0005),'display_glass','glazing',['recessed_inner_gasket'])
 addpart(parts,'original_pool_leisure_image',([(-iw/2,-ih/2,0),(iw/2,-ih/2,0),(iw/2,ih/2,0),(-iw/2,ih/2,0)],[(0,1,2,3)]),c['content_role'],'image',['recessed_display_glazing'],kind='art')
 # Back case / seam is a genuine closed cover, plus paired exposed fixings.
 addpart(parts,'rear_fixed_service_case',extrude(R(w*.44,h*.36,.025),-.134,-.123),'ivory_enamel','service',['shaped_closed_back_shell'])
 for i,u in enumerate([-w*.18,w*.18]):
  addpart(parts,f'rear_service_fastener_{i}',extrude(rounded(.014,.014,.004,(u,h*.115)),-.138,-.132),'champagne_metal','fastener',['rear_fixed_service_case'])
 # A restrained champagne hairline is a real retaining ring, not a global palette change.
 addpart(parts,'thin_champagne_retaining_ring',ring(R(iw+.028,ih+.028,.017),R(iw+.023,ih+.023,.015),-.0013,-.0001),'champagne_metal','bearing',['recessed_inner_gasket'])
 if wall:
  assert wall_back_planes is not None and len(wall_back_planes)==4
  for i,(u,v) in enumerate([(s*iw*.32,t*ih*.30)for s in [-1,1]for t in [-1,1]]):
   n=wall_back_planes[i] # Local depth at actual retained triangle plane, not rounded label.
   plate=f'wall_backplate_{i}';arm=f'wall_bearing_arm_{i}'
   addpart(parts,plate,extrude(rounded(.12,.18,.012,(u,v)),n,n+.016),'champagne_metal','bearing',contact={'kind':'wall_triangle_contact','index':i,'local_centre':[u,v,n],'size_uv_m':[.12,.18]})
   addpart(parts,arm,box((u-.035,v-.054,n+.011),(u+.035,v+.054,-.112)),'ivory_enamel','bearing',[plate,'shaped_closed_back_shell'])
   for j,sv in enumerate([-.063,.063]):
    addpart(parts,f'wall_anchor_head_{i}_{j}',extrude(rounded(.012,.012,.003,(u,v+sv)),n+.015,n+.022),'champagne_metal','fastener',[plate])
  # Housed feed boss meets the support plane; no cable is drawn across the seat view.
  n=max(wall_back_planes)
  addpart(parts,'sealed_rear_feed_boss',extrude(rounded(.05,.058,.010,(0,-h*.27)),n,n+.061),'dark_rubber','service',['shaped_closed_back_shell'],contact={'kind':'wall_feed_contact','local_centre':[0,-h*.27,n],'size_uv_m':[.05,.058]})
 else:
  assert floor_y is not None
  fv=floor_y-c['origin_world_xyz'][1]
  for i,u in enumerate([-.73,.73]):
   # Rounded elastomer footprint, shaped ski shoe, and swept solid load spine.
   pad=f'floor_pad_{i}';foot=f'sculpted_foot_{i}';spine=f'swept_load_spine_{i}'
   # Rounded UV plane is reoriented to local (u,n), extruded upward in v.
   profile=rounded(.18,.438,.034,(u,-.241))
   vs,fs=extrude(profile,fv,fv+.026,axis=1)
   addpart(parts,pad,(vs,fs),'dark_rubber','pad',contact={'kind':'floor_triangle_contact','local_centre':[u,fv,-.241],'size_un_m':[.18,.438]})
   # Profile in (v,n), extruded in u. Counter-clockwise topology recalculated in builder.
   p=[(fv+.024,-.455),(fv+.083,-.391),(fv+.115,-.276),(fv+.082,-.142),(fv+.042,-.031),(fv+.024,-.024)]
   addpart(parts,foot,extrude(p,u-.084,u+.084,axis=0),'ivory_enamel','foot',[pad])
   p=[(fv+.072,-.292),(fv+.090,-.215),(fv+.405,-.177),(fv+.760,-.148),(-.43,-.103),(-.40,-.160),(fv+.777,-.220),(fv+.420,-.260)]
   addpart(parts,spine,extrude(p,u-.046,u+.046,axis=0),'ivory_enamel','spine',[foot,'shaped_closed_back_shell'],grain_axis=1)
   addpart(parts,f'timber_inner_join_{i}',box((u-.057,-.80,-.195),(u+.057,-.49,-.106)),'warm_walnut','bridge',[spine,'shaped_closed_back_shell'],grain_axis=1)
  addpart(parts,'rear_service_bridge',extrude(rounded(1.60,.10,.025,(0,-.76)),-.211,-.117),'warm_walnut','bridge',['swept_load_spine_0','swept_load_spine_1','shaped_closed_back_shell'])
  addpart(parts,'lower_closed_service_case',extrude(rounded(.55,.23,.034,(0,-.89)),-.236,-.150),'ivory_enamel','service',['rear_service_bridge'])
  for i,u in enumerate([-.215,.215]):
   addpart(parts,f'lower_case_fastener_{i}',extrude(rounded(.016,.016,.005,(u,-.89)),-.242,-.234),'champagne_metal','fastener',['lower_closed_service_case'])
 return parts

def local_to_world(c,p):
 return [c['origin_world_xyz'][i]+sum(c['basis_world_columns'][j][i]*p[j]for j in range(3))for i in range(3)]

def triangulate(vs,face):
 """Ear clipping on a face's dominant plane; handles concave swept foot profiles."""
 if len(face)==3:return [list(face)]
 p=[vs[i] for i in face];nn=[0,0,0]
 for a,b in zip(p,p[1:]+p[:1]):
  nn[0]+=(a[1]-b[1])*(a[2]+b[2]);nn[1]+=(a[2]-b[2])*(a[0]+b[0]);nn[2]+=(a[0]-b[0])*(a[1]+b[1])
 drop=max(range(3),key=lambda i:abs(nn[i]));axes=[i for i in range(3) if i!=drop];q={i:(vs[i][axes[0]],vs[i][axes[1]])for i in face}
 cr=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 area=sum(q[a][0]*q[b][1]-q[b][0]*q[a][1]for a,b in zip(face,list(face[1:])+[face[0]]));sign=1 if area>0 else -1
 ids=list(face);out=[]
 while len(ids)>3:
  found=False
  for k,b in enumerate(ids):
   a=ids[k-1];d=ids[(k+1)%len(ids)]
   if cr(q[a],q[b],q[d])*sign<1e-12:continue
   inside=lambda x:min(cr(q[a],q[b],q[x])*sign,cr(q[b],q[d],q[x])*sign,cr(q[d],q[a],q[x])*sign)>=-1e-12
   if any(inside(x)for x in ids if x not in (a,b,d)):continue
   out.append([a,b,d]);ids.pop(k);found=True;break
  if not found:raise ValueError('Non-simple or degenerate face: '+str(face))
 out.append(ids);return out

def triangles(part,c=None):
 vs=part['vertices_local_uvn_m'];vv=[local_to_world(c,v)for v in vs]if c else vs
 return [[vv[i]for i in t]for f in part['faces']for t in triangulate(vs,f)]
