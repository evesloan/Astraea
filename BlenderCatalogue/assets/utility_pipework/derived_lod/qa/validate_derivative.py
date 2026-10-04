"""Read actual exported triangles, attributes, textures and resolved nodes."""
import json,hashlib,io,math
from pathlib import Path
import numpy as np
from PIL import Image
from glb_tools import read,accessor,primitives,worlds
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[2];C=np.array([[1,0,0],[0,0,1],[0,-1,0.]])
def rays(tris,origins,direction,length):
 # Moller-Trumbore: bounded segment hit, double sided, exact exported geometry.
 out=[];edge1=tris[:,1]-tris[:,0];edge2=tris[:,2]-tris[:,0];direction=np.array(direction,float);p=np.cross(np.broadcast_to(direction,edge2.shape),edge2);det=(edge1*p).sum(1);valid=np.abs(det)>1e-13;inv=np.zeros(len(det));inv[valid]=1/det[valid]
 for origin in origins:
  t=np.array(origin)-tris[:,0];u=(t*p).sum(1)*inv;q=np.cross(t,edge1);v=(q*direction).sum(1)*inv;distance=(edge2*q).sum(1)*inv
  out.append(bool(np.any(valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(distance>1e-7)&(distance<length-1e-7))))
 return out

def validate(path):
 d,b=read(path);alltris=[];allpoints=[];roles={};issues=[];geometry_views=set();stats={'triangles':0,'non_unit_normals':0,'opposed_winding':0,'collapsed_uv_triangles':0,'minimum_triangle_area_m2':1e9}
 for ni,p,local,ix,v,m in primitives(d,b):
  geometry_views.update(d['accessors'][a]['bufferView']for a in list(p['attributes'].values())+[p['indices']]);n=accessor(d,b,p['attributes']['NORMAL']);uv=accessor(d,b,p['attributes']['TEXCOORD_0']);assert np.isfinite(v).all() and np.isfinite(n).all() and np.isfinite(uv).all();t=local[ix];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)*.5;stats['triangles']+=len(ix);stats['non_unit_normals']+=int((np.abs(np.linalg.norm(n,axis=1)-1)>.005).sum());stats['opposed_winding']+=int(((cross*n[ix].mean(1)).sum(1)<-1e-10).sum());a=uv[ix];delta1=a[:,1]-a[:,0];delta2=a[:,2]-a[:,0];ua=np.abs(delta1[:,0]*delta2[:,1]-delta1[:,1]*delta2[:,0]);stats['collapsed_uv_triangles']+=int((ua<1e-12).sum());stats['minimum_triangle_area_m2']=min(stats['minimum_triangle_area_m2'],float(area.min()));alltris.extend(v[ix]);allpoints.extend(v[ix].reshape(-1,3))
  mat=d['materials'][p['material']];role=mat['name'].replace('ASTRAEA_','');tex=d['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']]['source'];im=d['images'][tex];bv=d['bufferViews'][im['bufferView']];start=bv.get('byteOffset',0);actual=Image.open(io.BytesIO(b[start:start+bv['byteLength']])).convert('RGBA');original=Image.open(CAT/'materials/staff'/f'{role}.png').convert('RGBA');roles[role]={'actual_embedded_pixels_equal_shared':actual.size==original.size and actual.tobytes()==original.tobytes(),'roughness':mat['pbrMetallicRoughness'].get('roughnessFactor'),'metallic':mat['pbrMetallicRoughness'].get('metallicFactor')}
 arr=np.array(allpoints);wt=worlds(d);markers=[];determinants=[float(np.linalg.det(m[:3,:3]))for m in wt.values()]
 for i,node in enumerate(d['nodes']):
  if not node.get('name','').startswith('PORT_'):continue
  e=node['extras'];source=np.array(e['position_blender_source_m']);position=np.array(e['position_gltf_yup_m']);normal=np.array(e['normal_gltf_yup']);radial=np.array(e['radial_zero_gltf_yup']);actual=wt[i][:3,3]
  markers.append({'name':node['name'],'actual_position_gltf_yup_m':actual.tolist(),'actual_marker_position_error_m':float(np.linalg.norm(actual-C@source)),'field_position_error_m':float(np.linalg.norm(position-C@source)),'normal_conversion_error':float(np.linalg.norm(normal-C@e['normal_blender_source'])),'radial_conversion_error':float(np.linalg.norm(radial-C@e['radial_zero_blender_source'])),'wrong_source_as_native_position_error_m':float(np.linalg.norm(actual-source)),'wrong_source_as_native_normal_error':float(np.linalg.norm(normal-e['normal_blender_source'])),'wrong_source_as_native_radial_error':float(np.linalg.norm(radial-e['radial_zero_blender_source']))})
 passed=all(x>0 for x in determinants) and stats['minimum_triangle_area_m2']>1e-12 and stats['non_unit_normals']==stats['opposed_winding']==stats['collapsed_uv_triangles']==0 and all(r['actual_embedded_pixels_equal_shared']for r in roles.values()) and all(max(r[k]for k in('actual_marker_position_error_m','field_position_error_m','normal_conversion_error','radial_conversion_error'))<1e-6 for r in markers)
 return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,**stats,'finite_positions_normals_uv':True,'bounds_gltf_yup_m':{'min':arr.min(0).tolist(),'max':arr.max(0).tolist()},'materials':roles,'serialized_material_count':len(d.get('materials',[])),'serialized_image_count':len(d.get('images',[])),'used_material_count':len(roles),'used_geometry_buffer_view_bytes':sum(d['bufferViews'][i]['byteLength']for i in geometry_views),'file_bytes_scope':'Contains embedded PNGs and JSON. Near extraction retains original unused materials/images; do not interpret whole-file difference as mesh or runtime savings.','runtime_mesh_count':len(d['meshes']),'runtime_primitive_count':sum(len(m['primitives'])for m in d['meshes']),'markers':markers,'resolved_node_transform_determinants':determinants,'passed':passed},np.array(alltris)

results=[];geometry={}
for path in sorted((BASE/'exports').glob('*.glb')):
 rec,tris=validate(path);results.append(rec);geometry[path.stem]=tris
def actual_front_profile(tris):
 front=tris[np.all(np.abs(tris[...,0])<1e-7,axis=1)];edges={}
 for tri in front:
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   a=tuple(np.round(a,7));b=tuple(np.round(b,7));key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
 boundary=[np.array(e)[:,1:]for e,count in edges.items()if count==1]
 centres=[np.array([.13*math.sin(2*math.pi*i/6),.13*math.cos(2*math.pi*i/6)])for i in range(6)]
 groups={'bore':[],'outer':[],**{f'hole_{i+1}':[]for i in range(6)}}
 for edge in boundary:
  radius=np.linalg.norm(edge,axis=1)
  if np.all(np.abs(radius-.08)<2e-6):groups['bore'].append(edge)
  elif np.all(np.abs(radius-.16)<2e-6):groups['outer'].append(edge)
  else:
   i=min(range(6),key=lambda j:np.linalg.norm(edge.mean(0)-centres[j]));assert np.max(np.linalg.norm(edge-centres[i],axis=1))<.009002;groups[f'hole_{i+1}'].append(edge-centres[i])
 out={}
 for key,group in groups.items():
  arr=np.array(group);a=arr[:,0];delta=arr[:,1]-a;t=np.clip(-(a*delta).sum(1)/(delta*delta).sum(1),0,1);closest=a+delta*t[:,None]
  out[key]={'actual_front_boundary_edges':len(arr),'maximum_vertex_radius_m':float(np.linalg.norm(arr,axis=2).max()),'minimum_edge_radius_m':float(np.linalg.norm(closest,axis=1).min())}
 return out
checks=[]
for name in('utility_flange_near_comparison','utility_flange_exact_profile_baseline','utility_flange_economical'):
 tris=geometry[name]@C # Row vectors native -> source. The source inlet n = -X.
 centreline=[[-.002,0,0]];bore=[[-.002,.078*math.cos(t),.078*math.sin(t)]for t in np.linspace(0,2*math.pi,48,endpoint=False)]
 annulus=[[-.002,.10*math.cos(t),.10*math.sin(t)]for t in np.linspace(0,2*math.pi,48,endpoint=False)]
 # Hole phase uses source radial_zero +Z, with n x u = +Y for inlet -X.
 holes=[];clearance=[];wrongphase=[]
 for i in range(6):
  a=2*math.pi*i/6;y=.13*math.sin(a);z=.13*math.cos(a);holes.append([-.002,y,z])
  clearance.extend([[-.002,y+.0086*math.cos(t),z+.0086*math.sin(t)]for t in np.linspace(0,2*math.pi,24,endpoint=False)])
  wrongphase.append([-.002,.13*math.sin(a+math.pi/6),.13*math.cos(a+math.pi/6)])
 r={'name':name,'bore_axial_open_48_samples':not any(rays(tris,bore,[1,0,0],.11)),'front_annulus_blocked_48_samples':all(rays(tris,annulus,[1,0,0],.003)),'six_front_holes_open':not any(rays(tris,holes,[1,0,0],.003)),'bolt_clearance_radius_0086m_144_samples_open_through_plate':not any(rays(tris,clearance,[1,0,0],.038)),'wrong_30degree_hole_phase_hits_plate_6_samples':all(rays(tris,wrongphase,[1,0,0],.003)),'max_source_outer_radius_m':float(np.linalg.norm(tris[...,1:3],axis=2).max()),'source_axial_minmax_m':[float(tris[...,0].min()),float(tris[...,0].max())]};r['actual_front_profile']=actual_front_profile(tris);r['passed']=all(v for k,v in r.items()if isinstance(v,bool));checks.append(r)
# Repeated actual geometry has six seams on source Y, with transformed nonzero
# port origins. Test through all12 plates at radial position .078/.10 and all
# bolt centres plus .0086 radial clearance. No proxy geometry enters these rays.
tris=geometry['utility_flange_repeated_context']@C
openbores=[];blocked=[];holeclear=[]
for i in range(6):
 y=i*.8;openbores.append([.078,y-.10,.7]);blocked.append([.10,y-.037,.7])
 for j in range(6):
  a=2*math.pi*j/6;x=.13*math.sin(a);z=.7+.13*math.cos(a)
  holeclear.extend([[x+.0086*math.cos(t),y-.0351,z+.0086*math.sin(t)]for t in np.linspace(0,2*math.pi,24,endpoint=False)])
mating={'six_paired_bores_open':not any(rays(tris,openbores,[0,1,0],.20)),'six_paired_annuli_blocked':all(rays(tris,blocked,[0,1,0],.074)),'864_paired_hole_clearance_samples_open':not any(rays(tris,holeclear,[0,1,0],.0702)),'declared_actual_min_hole_flat_diameter_m':2*.009*math.cos(math.pi/12),'near_min_hole_flat_diameter_m':2*.009*math.cos(math.pi/24),'hole_minimum_radius_decrease_from_near_m':.009*(math.cos(math.pi/24)-math.cos(math.pi/12)),'hole_max_profile_deviation_from_near_m':.009*(1-math.cos(math.pi/12)),'minimum_hole_to_006m_shank_radial_clearance_m':.009*math.cos(math.pi/12)-.006,'bore_nominal_m':.16,'bore_actual_min_flat_diameter_m':.16*math.cos(math.pi/48),'outer_nominal_m':.32,'flange_thickness_m':.035,'rear_bevel_max_added_surface_m':.002,'neck_outer_24_vs48_max_radial_deviation_m':.112*(1-math.cos(math.pi/24)),'scope':'Finite actual-export segment samples and explicit polygon dimensions; no physical operation, pressure/load claim or engine physics test'}
# Direct native-front boundary vertex-to-edge distances, independent of the
# nominal formula. Near24 vertices at economical12 mid-flats are the extrema.
neartris=geometry['utility_flange_near_comparison']@C;ecotris=geometry['utility_flange_economical']@C
nearfront=neartris[np.all(np.abs(neartris[...,0])<1e-7,axis=1)];ecofront=ecotris[np.all(np.abs(ecotris[...,0])<1e-7,axis=1)];measured=[]
for j in range(6):
 centre=np.array([.13*math.sin(2*math.pi*j/6),.13*math.cos(2*math.pi*j/6)])
 a=nearfront[...,1:].reshape(-1,2);a=np.unique(a[np.abs(np.linalg.norm(a-centre,axis=1)-.009)<2e-6],axis=0);edges=[]
 for tri in ecofront[...,1:]:
  for x,y in zip(tri,np.roll(tri,-1,axis=0)):
   if abs(np.linalg.norm(x-centre)-.009)<2e-6 and abs(np.linalg.norm(y-centre)-.009)<2e-6:edges.append((x,y))
 edges=np.array(edges);origin=edges[:,0];delta=edges[:,1]-origin;dist=[]
 for point in a:
  t=np.clip(((point-origin)*delta).sum(1)/(delta*delta).sum(1),0,1);dist.append(float(np.linalg.norm(point-(origin+t[:,None]*delta),axis=1).min()))
 measured.append(max(dist))
mating['actual_six_hole_max_near_vertex_to_economical_edge_deviation_m']=measured
# Source -> native controls are intentionally sensitive in repeated context.
repeated=next(r for r in results if r['file']=='utility_flange_repeated_context.glb')
mating['all_repeated_wrong_axis_marker_positions_rejected']=all(m['wrong_source_as_native_position_error_m']>.5 for m in repeated['markers']);mating['all_repeated_wrong_axis_normals_rejected']=all(m['wrong_source_as_native_normal_error']>1 for m in repeated['markers']);mating['passed']=all(v for k,v in mating.items()if isinstance(v,bool))
source=json.loads((BASE/'qa/source_geometry.json').read_text());counts={r['file']:r['triangles']for r in results};near=counts['utility_flange_near_comparison.glb'];eco=counts['utility_flange_economical.glb'];out={'inspection':'Actual native GLB buffers, node hierarchy, UV/normal/embedded texture checks and bounded ray controls; never substitutes source renders','results':results,'interface_geometry_checks':checks,'mating_context_checks':mating,'source_all_closed':all(r['source_all_parts_closed']for r in source['results']),'measured_triangle_reduction':{'actual_extracted_near':near,'economical':eco,'saved':near-eco,'fraction':(near-eco)/near,'twelve_flange_near':12*near,'twelve_flange_economical':12*eco,'twelve_flange_saved':12*(near-eco),'original_helper_documented_reference':2328,'note':'The actual selected original AST-ENG-004 inlet exports2327; the shared helper reference was2328. Counts here use the immutable actual inlet export.'},'all_passed':all(r['passed']for r in results+checks)and mating['passed']and all(r['source_all_parts_closed']for r in source['results'])}
(BASE/'qa/actual_glb_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in('results',)},indent=2))
assert out['all_passed']
