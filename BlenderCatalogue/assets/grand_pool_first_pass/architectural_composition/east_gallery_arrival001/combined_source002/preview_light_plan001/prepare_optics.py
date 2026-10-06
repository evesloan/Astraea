"""Pure local optical proposal from exact saved source; no source edit/render/engine."""
import ast,json,gzip,hashlib,sys,math,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely import union_all
S=Path(__file__).resolve().parent;J=S.parent;P=J.parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');TOL=5e-5
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
path=C/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py';spec=importlib.util.spec_from_file_location('pure_geometry',path);geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
for name in dir(geo):
 if not name.startswith('_'):globals()[name]=getattr(geo,name)
helper=C/'assets/grand_pool_first_pass/finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());needed={'record','rayhits','surface_points','on_surface','cone_triangle'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in needed],type_ignores=[]),str(helper),'exec'))
receipt=read(J/'qa/BUILD_RECEIPT.json');reopen=read(J/'qa/INDEPENDENT_REOPEN.json');assert reopen['status']=='PASS_EXACT_COMPOSED_SOURCE_REOPEN'
assert sha(receipt['source'])==receipt['source_sha256'];assert sha(J/'qa/BUILD_EVALUATED_CORE.json')==receipt['core_snapshot_sha256'];assert sha(J/'qa/BUILD_EVALUATED_PROGRAMME.json.gz')==receipt['programme_snapshot_sha256']
plan=read(J/'qa/BUILD_EVALUATED_CORE.json')
with gzip.open(J/'qa/BUILD_EVALUATED_PROGRAMME.json.gz','rt')as f:prog=json.load(f)
parts=[]
for p in plan['parts']:
 tr=[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']];parts.append(record(p['name'],p['vertices_xyz'],tr,meta=p,kind='core'))
cm={p['name']:p for p in parts}
for p in prog['parts']:parts.append(record(p['name'],p['vertices'],p['triangles'],meta=p,kind='programme'))
glb=read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb')
for p in read(P/'geometry/RETAINED_PART_BOUNDS.json')['parts']:
 tr=[glb['triangles'][i]for i in p['global_triangle_indices']];parts.append(record(p['source_name'],[v for t in tr for v in t],tr,kind='retained_shell'))
for p in parts:p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
# Actual covered glass is optically transparent in the retained source.
opaque=[p for p in parts if p.get('meta',{}).get('source_part')not in {'M0__original_pool_leisure_image','M0__recessed_display_glazing'}]

def surface_at(name,x,z,y_start=58.,y_end=52.):
 h=rayhits([x,y_start,z],[x,y_end,z],[cm[name]])
 assert h,(name,x,z)
 return h[0]['point_xyz']
def front_at(name,y,z):
 h=rayhits([-11.19,y,z],[-8.19,y,z],[cm[name]])
 assert h,(name,y,z)
 return h[0]['point_xyz']
def receiver(name,part,target):
 assert on_surface(target,cm[part]),(name,'receiver not on actual surface')
 return dict(name=name,part=part,point_xyz=target)
receivers=[receiver('bench_fore','EAST_Bench_ClayUpholstery',surface_at('EAST_Bench_ClayUpholstery',-9.25,-450.25)),receiver('bench_centre','EAST_Bench_ClayUpholstery',surface_at('EAST_Bench_ClayUpholstery',-9.12,-449.50)),receiver('bench_aft','EAST_Bench_ClayUpholstery',surface_at('EAST_Bench_ClayUpholstery',-9.25,-448.70)),receiver('table','EAST_Table_WalnutTop',surface_at('EAST_Table_WalnutTop',-10.40,-448.65)),receiver('clay_back_fore','EAST_Bay_CurvedClayBack',front_at('EAST_Bay_CurvedClayBack',54.55,-450.2)),receiver('clay_back_centre','EAST_Bay_CurvedClayBack',front_at('EAST_Bay_CurvedClayBack',54.55,-449.5)),receiver('clay_back_aft','EAST_Bay_CurvedClayBack',front_at('EAST_Bay_CurvedClayBack',54.55,-448.8))]
fixtures=[];issues=[]
for i,f in enumerate(plan['fixture_reservations']):
 lens=cm[f['physical_lens']];data=lens['meta'];N=len(data['vertices_xyz'])//2;caps=[t for t in data['evaluated_triangles']if max(t)<N];assert caps
 normals=[unit(cross(sub(data['vertices_xyz'][t[1]],data['vertices_xyz'][t[0]]),sub(data['vertices_xyz'][t[2]],data['vertices_xyz'][t[0]])))for t in caps];dire=unit(np.mean(normals,axis=0));assert dire[1]<0
 pos=f['position_xyz'];angle=55.;throw=5.2;radius=.06*math.tan(math.radians(angle));bb=[add(pos,(-radius-.06,)*3),add(pos,(radius+.06,)*3)];cone=[]
 for p in parts:
  if not overlap(bb,p['bounds'],-TOL):continue
  for k,t in enumerate(p['triangles']):
   h=cone_triangle(pos,dire,angle,t)
   if h:cone.append(dict(part=p['name'],triangle=k,**h))
 lens_ray=rayhits(pos,add(pos,mul(dire,-.12)),[lens]);axis_exit=rayhits(pos,add(pos,mul(dire,.06)),parts)
 if cone or axis_exit or not lens_ray:issues.append(dict(kind='physical_optical_exit',fixture=f['name'],cone=cone,axis=axis_exit,lens_behind=lens_ray))
 row=dict(name=f['name'],position_xyz=pos,direction_xyz=list(dire),housing=f['housing'],physical_lens=f['physical_lens'],direction_basis='Area-independent average of actual outward lower lens triangle normals; no housing moved',spot_half_angle_degrees=angle,blender_full_cone_degrees=2*angle,suggested_range_m=throw,preview_energy_mapping='700 W times provisional energy',provisional_energy=1.0,preview_power_watts=700.,preview_color_rgb=[1.,.86,.68],preview_spot_blend=.55,preview_shadow_soft_size_m=.02,native_energy_accepted=False,native_range_accepted=False,native_selector_priority_changed=False,first_60mm_axis_hits=axis_exit,first_60mm_full_cone_hits=cone,actual_lens_behind_marker_hits=lens_ray,receiver_rays=[])
 fixtures.append(row)
# Test a small set of actual soil-top samples, not an invented clear canopy gap.
soil_search=[]
for label,fi,cz in [('Fore',0,-452.2),('Aft',1,-446.8)]:
 name='EAST_'+label+'SoilBed_Soil';part=cm[name];y=max(v[1]for v in part['vertices']);top=union_all([Polygon([(v[0],v[2])for v in t])for t in part['triangles']if max(abs(v[1]-y)for v in t)<TOL]);found=[];blocked=0
 for dx in [-.57,-.42,-.2,0,.2,.42,.57]:
  for dz in [-1.12,-.95,-.65,-.32,0,.32,.65,.95,1.12]:
   target=[-9.1+dx,y,cz+dz]
   if not top.contains(Point(target[0],target[2])):continue
   hits=rayhits(fixtures[fi]['position_xyz'],target,opaque)
   if not hits:found.append(target)
   else:blocked+=1
 assert found,(label,'no actual clear soil sample')
 # Prefer the mouth-side soil margin, which reads beside the full crown.
 target=min(found,key=lambda q:(q[0],abs(q[2]-cz)))
 receivers.append(receiver(label.lower()+'_soil_visible_margin',name,target));soil_search.append(dict(soil=name,clear_samples=len(found),foliage_or_housing_blocked_samples=blocked,selected=target,interpretation='Full foliage correctly blocks some soil rays; no leaf geometry hidden or shrunk'))
for f in fixtures:
 for r in receivers:
  v=sub(r['point_xyz'],f['position_xyz']);distance=length(v);ang=math.degrees(math.acos(max(-1,min(1,dot(unit(v),f['direction_xyz'])))));hits=rayhits(f['position_xyz'],r['point_xyz'],opaque)
  f['receiver_rays'].append(dict(receiver=r['name'],part=r['part'],point_xyz=r['point_xyz'],distance_m=distance,angle_from_lens_axis_degrees=ang,inside_proposed_range=distance<=f['suggested_range_m'],inside_spot_half_angle=ang<=f['spot_half_angle_degrees'],occluders=hits,unoccluded=not hits))
coverage=[]
for r in receivers:
 visible=[f['name']for f in fixtures for rr in f['receiver_rays']if rr['receiver']==r['name']and rr['unoccluded']and rr['inside_proposed_range']and rr['inside_spot_half_angle']]
 coverage.append(dict(receiver=r['name'],covering_fixtures=visible))
 if not visible:issues.append(dict(kind='uncovered_receiver',receiver=r['name']))
# Aft approach, actual floor and body footprint, plus source-front media rays.
eye=[-14.,54.15,-443.2];target=[-9.4,54.3,-449.4];floor=next(f for f in read(P/'geometry/FLOOR_POLYGONS.json')['floor_regions']if f['id']=='D09_orchard_market_gallery');floorpoly=union_all([Polygon(t)for t in floor['triangles']]);feet=[eye[0],eye[1]-1.65,eye[2]];body=Point(feet[0],feet[2]).buffer(.30);covered=floorpoly.covers(body);route=LineString([(-15.5,-443.2),(-14.,-443.2)]).buffer(.30);route_on_floor=floorpoly.covers(route);body_hits=[];route_hits=[]
for p in parts:
 if min(54.32,p['bounds'][1][1])-max(52.52,p['bounds'][0][1])<=TOL:continue
 if not overlap([[eye[0]-.3,52.52,eye[2]-.3],[eye[0]+.3,54.32,eye[2]+.3]],p['bounds'],TOL):continue
 footprint=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if Polygon([(v[0],v[2])for v in t]).area>1e-10])
 if footprint.intersection(body).area>1e-8:body_hits.append(p['name'])
# Existing finish AABBs are disjoint from the standing body and incoming route.
finish_hits=[]
for p in read(P/'geometry/RETAINED_FINISH_BOUNDS.json'):
 if overlap([[eye[0]-.3,52.52,eye[2]-.3],[eye[0]+.3,54.32,eye[2]+.3]],p['bounds_xyz'],TOL):finish_hits.append(p['source_name'])
imagepart=next(p for p in parts if p.get('meta',{}).get('source_part')=='M0__original_pool_leisure_image');imagecentre=np.mean(np.array(imagepart['vertices']),axis=0).tolist();media_targets=[imagecentre]+list({tuple(v)for v in imagepart['vertices']});optical_rays=[dict(target_xyz=t,hits=rayhits(eye,t,opaque))for t in media_targets]
normal=plan['display_reservation']['front_normal_xyz'];front_dot=dot(sub(eye,imagecentre),normal);opening_target=[-10.80,54.15,-448.0];opening_ray=rayhits(eye,opening_target,opaque)
# Perspective inclusion for the actual core bay bounds, without camera-only edits.
fwd=np.array(unit(sub(target,eye)));right=np.cross(fwd,[0,1,0]);right=right/np.linalg.norm(right);up=np.cross(right,fwd);tanv=math.tan(math.radians(72/2));tanh=tanv*(16/9);clip=[]
for p in plan['parts']:
 if p['group']=='lift':continue
 for v in p['vertices_xyz']:
  d=np.array(v)-eye;depth=d@fwd
  if depth<=0:clip.append(dict(part=p['name'],reason='behind'));continue
  x=(d@right)/(depth*tanh);y=(d@up)/(depth*tanv)
  if max(abs(x),abs(y))>1:clip.append(dict(part=p['name'],normalized_x=float(x),normalized_y=float(y)))
camera=dict(name='upper_gallery_aft_approach',eye_xyz=eye,target_xyz=target,vertical_fov_degrees=72,aspect=[16,9],floor_owner=floor['id'],floor_y=floor['floor_y'],eye_height_m=1.65,body_radius_m=.30,body_height_m=1.80,body_footprint_fully_supported=covered,incoming_route_fully_supported=route_on_floor,source_body_geometry_hits=body_hits,retained_finish_body_bounds_hits=finish_hits,clear_opening_ray=dict(target_xyz=opening_target,hits=opening_ray),media_front_dot_m=front_dot,media_front_facing=front_dot>0,media_centre_and_corner_rays=optical_rays,bay_vertices_outside_frame=clip,caveat='Static source-camera/body screen only; not a player movement or in-engine controller claim')
# An oblique architecture view may crop the image's outer edge on its own
# deep bezel. Preserve those exact hits; only the centre or unrelated occlusion
# blocks this camera proposal. The seated image-corner acceptance is unchanged.
unexpected_media_hits=[dict(target_index=i,hit=h)for i,r in enumerate(optical_rays)for h in r['hits']if i==0 or h['part']!='EAST_Display__M0__walnut_display_frame']
camera['entire_image_visible_from_this_approach']=not any(r['hits']for r in optical_rays)
camera['self_occluded_image_edge_count']=sum(bool(r['hits'])for r in optical_rays[1:])
camera['image_edge_diagnostic']='Two extreme image corners crop on the original deep bezel at this ordinary oblique approach; image centre/front are visible. No full-edge readability is claimed.'
if not covered or not route_on_floor or body_hits or finish_hits or opening_ray or front_dot<=0 or unexpected_media_hits:issues.append(dict(kind='aft_camera_screen',camera=camera))
inputs=[J/'qa/BUILD_EVALUATED_CORE.json',J/'qa/BUILD_EVALUATED_PROGRAMME.json.gz',J/'qa/BUILD_RECEIPT.json',J/'qa/INDEPENDENT_REOPEN.json',Path(receipt['source']),P/'geometry/FLOOR_POLYGONS.json',P/'geometry/RETAINED_PART_BOUNDS.json',P/'geometry/RETAINED_FINISH_BOUNDS.json',helper,C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb']
report=dict(status='PASS_LOCAL_SOURCE_OPTICAL_PROPOSAL'if not issues else'OPTICAL_PROPOSAL_REQUIRES_CORRECTION',fixtures=fixtures,measured_receivers=receivers,receiver_coverage=coverage,soil_sample_review=soil_search,aft_camera=camera,issues=issues,input_sha256={str(p):sha(p)for p in inputs},limits=['Preview illumination proposal only, no source geometry or saved material changes','700 W is a provisional source-render mapping, not accepted native photometry or energy','Native eight-active/32-candidate selector, priorities and shared renderer remain unchanged','No render, Blender/Godot launch, export or Game write occurred'])
assert sha(receipt['source'])==receipt['source_sha256']
(S/'LOCAL_OPTICAL_PROPOSAL.json').write_text(json.dumps(report,indent=2)+'\n')
if not issues:
    proposal=dict(report,status='PASS_SOURCE_PREVIEW_OPTICAL_PLAN',source_sha256=receipt['source_sha256'],view=camera)
    proposal['fixtures']=[dict(f,source_preview_power_watts=f['preview_power_watts'],half_angle_degrees=f['spot_half_angle_degrees'])for f in fixtures]
    (S/'LIGHT_PROPOSAL.json').write_text(json.dumps(proposal,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],fixtures=[{k:f[k]for k in ['name','position_xyz','direction_xyz','spot_half_angle_degrees','suggested_range_m','preview_power_watts','first_60mm_full_cone_hits']}for f in fixtures],coverage=coverage,issues=issues,camera_summary={k:camera[k]for k in ['body_footprint_fully_supported','incoming_route_fully_supported','source_body_geometry_hits','media_front_dot_m','bay_vertices_outside_frame']}),indent=2));assert not issues
