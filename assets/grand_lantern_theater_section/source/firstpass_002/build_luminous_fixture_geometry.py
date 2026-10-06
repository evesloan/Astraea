"""Actual new source mesh specifications for foyer coffers and stair stringer lenses.
No engines, source overwrite or runtime mutation. Hollow housings, real mounted lenses.
"""
from pathlib import Path
import json,math,hashlib,numpy as np
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');PLAN=json.loads((R/'PROPOSED_FOYER_COFFER_COVERAGE.json').read_text());OLD=json.loads((P/'source/geometry.json').read_text())['objects'];objects=[];lights=[];bank_groups=[]
def emit(name,verts,faces,material,kind,**extra):
 v=np.array(verts,dtype=np.float32).astype(float);volume=sum(np.dot(v[f[0]],np.cross(v[f[i]],v[f[i+1]]))/6 for f in faces for i in range(1,len(f)-1))
 if volume<0:faces=[list(reversed(f))for f in faces];volume=-volume
 assert volume>1e-10,(name,volume)
 edges={}
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
 assert all(n==2 for n in edges.values()),name
 objects.append({'name':name,'vertices_world':v.tolist(),'faces':faces,'material_family':material,'role':kind,'closed_volume_m3':volume,**extra})
def rect(w,d,ch=.06):
 x=w/2;z=d/2;return [(-x+ch,-z),(x-ch,-z),(x,-z+ch),(x,z-ch),(x-ch,z),(-x+ch,z),(-x,z-ch),(-x,-z+ch)]
def prism(name,poly,y0,y1,material,kind,origin=(0,0),**extra):
 n=len(poly);x,z=origin;v=[[x+a,y,z+b]for y in[y0,y1]for a,b in poly];f=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];emit(name,v,f,material,kind,**extra)
coffers=[]
for index,coffer in enumerate(PLAN['new_coffers']):
 x,y,z=coffer['mount_centre_world'];pre=f'FP2_{coffer["deck"]}_C{index:02}';outertop=rect(3,.76);outerbottom=rect(2.88,.64);inner=rect(2.76,.50,.05);n=8
 prism(pre+'_mounted_backplate',outertop,y-.035,y,'ivory_enamel','fixed_luminaire',origin=(x,z),contact=coffer['source_support'])
 # Four corresponding closed rings: top outer/inner and lower outer/inner.
 rings=[(outertop,y-.035),(inner,y-.035),(outerbottom,y-.18),(inner,y-.18)];verts=[[x+a,h,z+b]for poly,h in rings for a,b in poly];faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([[i,j,n+j,n+i],[2*n+i,3*n+i,3*n+j,2*n+j],[i,2*n+i,2*n+j,j],[n+i,n+j,3*n+j,3*n+i]])
 emit(pre+'_hollow_profiled_frame',verts,faces,'champagne_metal','fixed_luminaire',aperture_size_xz=[2.76,.50],contact='Backplate lower face; real open optical aperture, no opaque hidden fill plane')
 prism(pre+'_fitted_opal_lens',rect(2.80,.54,.055),y-.155,y-.143,'hospitality_opal','physical_luminous_lens',origin=(x,z),contact='12mm-deep lens captured by20mm nominal perimeter into real inner frame; no light behind solid housing')
 coffers.append({**coffer,'semantic_id':coffer['id'],'mesh_prefix':pre,'native_fixture_name':pre+'_fitted_opal_lens','emitter_world':[x,y-.160,z]})
# Actual outward stringer faces. Lens/housing remain outside the3.2m walking width.
strips=[]
for o in OLD:
 if '_stringer_'not in o['name']:continue
 v=o['vertices_world'];xmin=min(q[0]for q in v);xmax=max(q[0]for q in v)
 if abs(xmin+58.8)<1e-5:side=-1;x=xmin
 elif abs(xmin+50.4)<1e-5:side=1;x=xmax
 else:continue
 # Existing corner order: top start0/top end3, bottom start4/bottom end7.
 a=np.array(v[0],float);b=np.array(v[3],float);a[0]=b[0]=x;d=b-a;length=float(np.linalg.norm(d));axis=d/length;normal=np.array([side,0.,0.]);up=np.cross(axis,normal);up/=np.linalg.norm(up)
 centre=(a+b)/2;centre[1]-=.15
 floor=69.5 if o['name'].startswith('D11_')else 78.0
 start_trim=max(.10,(floor+.05-(a[1]-.15-abs(up[1])*.07))/axis[1])
 pre='FP2_ST_'+o['name'].split('_stringer_')[0]
 def strip_box(name,w,depth,out0,mat,role):
  # Cross-section lies in the true sloping stringer side plane.
  vv=[(centre+axis*s+up*t+normal*h).tolist()for h in[out0,out0+depth]for s,t in[(-length/2+start_trim,-w/2),(length/2-.10,-w/2),(length/2-.10,w/2),(-length/2+start_trim,w/2)]]
  ff=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];emit(name,vv,ff,mat,role,contact=o['name'])
 strip_box(pre+'_metal_mount',.14,.018,0,'champagne_metal','fixed_luminaire');strip_box(pre+'_opal_face',.085,.004,.018,'hospitality_opal','physical_luminous_lens')
 emitter=(centre+normal*.027).tolist();strips.append({'id':pre,'source_stringer':o['name'],'fixture_name':pre+'_opal_face','emitter_world':emitter,'outward_world':normal.tolist(),'length_m':length-start_trim-.1,'mount_plane_x':x,'walking_width_preserved':True})
# Six foyer bank anchors per floor. They are actual coffer exits, never midair proxies.
anchor_positions=[(-96,-138),(-96,-120),(-72,-138),(-72,-120),(-40,-138),(-40,-129)]
for deck in ['D11','D12','D13']:
 anchors=[next(c for c in coffers if c['deck']==deck and c['mount_centre_world'][0]==x and c['mount_centre_world'][2]==z)for x,z in anchor_positions]
 banks=[[]for _ in anchors]
 for c in [c for c in coffers if c['deck']==deck]:
  k=min(range(6),key=lambda k:(c['emitter_world'][0]-anchors[k]['emitter_world'][0])**2+(c['emitter_world'][2]-anchors[k]['emitter_world'][2])**2);banks[k].append(c['native_fixture_name'])
 for i,(anchor,members)in enumerate(zip(anchors,banks)):
  lights.append({'id':f'FP2_{deck}_BANK_{i}','type':'OMNI','fixture_name':anchor['native_fixture_name'],'position_world':anchor['emitter_world'],'represented_fixtures':members,'range_m':90,'initial_source_watts':1800,'color_linear':[1,.91,.80],'shadow_candidate':True,'source_approximation':'One real physical lens anchor represents this local bank; not a hidden light or guaranteed photometric equivalence','runtime_budget_policy':'Existing visibility-aware8shadow policy, no unshadowed fallback'})
for s in strips:
 if '_D11_D12_F2'in s['id']or'_D11_D12_F4'in s['id']or'_D12_D13_F2'in s['id']or'_D12_D13_F4'in s['id']:
  lights.append({'id':s['id']+'_BANK','type':'OMNI','fixture_name':s['fixture_name'],'position_world':s['emitter_world'],'represented_fixtures':[q['fixture_name']for q in strips if q['source_stringer'].split('_F')[0]==s['source_stringer'].split('_F')[0]],'range_m':45,'initial_source_watts':900,'color_linear':[1,.88,.70],'shadow_candidate':True,'runtime_budget_policy':'Existing visibility-aware8shadow policy, no unshadowed fallback'})
# The first eight-source honest arrival preview uses the six D11 coffer banks and two D11/D12 outer-face stair sources.
active=[l['id']for l in lights if l['id'].startswith('FP2_D11_BANK_')or l['id'].startswith('FP2_ST_D11_D12_')];assert len(active)==8,active
out={'status':'Authored pure new source meshes; Blender build, exact surface contacts and budgeted visual acceptance pending','base_source_sha256':'a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce','objects':objects,'coffers':coffers,'stair_strips':strips,'physical_bank_light_candidates':lights,'first_arrival_eight_source_preview':active,'preview_rule':'No world/ambient/fill. Disable other analytic sources for budgeted check. Keep all visible fixture geometry; camera-only emission review shader prevents Cycles emissive GI from secretly supplementing8direct sources, matching current Compatibility limitations. This is not native Godot active-selection proof.','required_gates':['Every mounting face/lens/exit in rebuilt source','Existing-policy visibility/range ranking at arrival,seated,walking,stair points','Same-camera eight-source preview; no full62light visual acceptance','Native Godot import/collision and light-budget tests before adoption']}
(R/'LUMINOUS_FIXTURE_GEOMETRY_002.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'authored_meshes':len(objects),'coffers':len(coffers),'stair_strips':len(strips),'bank_candidates':len(lights),'arrival_direct_sources':len(active)},indent=2))
